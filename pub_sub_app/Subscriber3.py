#============================================================
# import packages
#============================================================
import time
import base64
import sys
import logging
import threading
import multiprocessing
import collections

#============================================================
# import grpc protobuf
#============================================================
from concurrent import futures
import grpc
import node_pb2
import node_pb2_grpc
import ntp_pb2
import ntp_pb2_grpc
import pubsub_pb2
import pubsub_pb2_grpc
import interceptor
from GRPC_ClientProcess4 import GRPC_ClientProcess4 as GRPC_ClientProcess
#from GRPC_ClientProcess import GRPC_ClientProcess as GRPC_ClientProcess
from GRPC_ServerProcess import GRPC_ServerProcess
from PubSubServiceServicer import PubSubServiceServicer
from SubscribeServiceServicer import SubscribeServiceServicer

from google.protobuf.json_format import MessageToDict

ProtobufDataDict={}
ProtobufDataDict['str']=pubsub_pb2.StringData
ProtobufDataDict['bytes']=pubsub_pb2.BytesData
ProtobufDataDict['int']=pubsub_pb2.IntData
ProtobufDataDict['float']=pubsub_pb2.FloatData
ProtobufDataDict['bool']=pubsub_pb2.BoolData

def diff_dict(dict1,dict2):
    list1=list(dict1.keys())
    list2=list(dict2.keys())
    return list1-list2

MILLI = 1000
MICRO = 1000000

class Subscriber():

    def __init__(self, node, sub_topic_config,buffer_maxlen=20, update_timing=1):
        if 'mode' not in sub_topic_config:
            print("'mode' is not in sub_topic_config")
            exit(1)
        elif sub_topic_config['mode'] ==1:
            sub_topic_config['ip']='0.0.0.0'
            sub_topic_config['port']=0
        else:
            if 'ip' not in sub_topic_config:
                print("'ip' is not in sub_topic_config'")
                exit(1)
            if 'port' not in sub_topic_config:
                print("'port' is not in sub_topic_config")
                exit(1)
        if 'subscription' not in sub_topic_config:
            print("'subscription' is not in sub_topic_config")
            exit(1)

        self.node = node
        self.sub_topic_config = sub_topic_config
        self.subcribe_mode=sub_topic_config['mode']
        self.subcribe_ip=sub_topic_config['ip']
        self.subcribe_port=sub_topic_config['port']
        self.subscription={}
        
        for topic in sub_topic_config['topic_info']:
            topicID="{}:{}".format(self.node.node_id,topic)
            self.subscription[topicID]=sub_topic_config['topic_info'][topic]
        self.update_timing = update_timing
        self.buffer_maxlen=buffer_maxlen


        self.topics_buffer = {}
        self.topics_connected_nodes = {}
        self.serverProcess=None
        
        
        self.clientProcess=GRPC_ClientProcess(self.node.node_id,1)

        self.rec_data_buffer={}
        self.connected_topic={}
        self.sub_pull_connection={} #connection_info
        self.subscriber = {}
        self.subscribe_topic()

        if self.subcribe_mode==0:
            self.serverProcess=GRPC_ServerProcess(self.node,self.subcribe_port,self.topics_buffer,1)     
        
        self.stop_flag=threading.Event()
        
        #self.thread = threading.Thread(target=self.run)
        self.thread=multiprocessing.Process(target=self.run)
        self.thread.start()
       
        print('Start Subscriber'.format())
        time.sleep(5)
    def subscribe_topic(self):
        try:
            with grpc.insecure_channel('{}:{}'.format(self.node.server_ip, self.node.server_port)) as channel: 
                server_stub = node_pb2_grpc.ControlStub(channel)
                for topic_name in self.subscription:
                    self.topics_buffer[topic_name]=collections.deque(maxlen=self.buffer_maxlen)
                    self.rec_data_buffer[topic_name]=[]
                    self.sub_pull_connection[topic_name]=[]
                    self.connected_topic[topic_name]=[]
                    topic_type = self.subscription[topic_name]
                    # add subscribe topic to server
                    topic = node_pb2.SubscribeTopic(topic_name=topic_name, 
                                                    topic_type=topic_type, 
                                                    node_id=self.node.node_id,
                                                    node_domain=self.node.node_domain,
                                                    mode=self.subcribe_mode,
                                                    ip=self.subcribe_ip,
                                                    port=self.subcribe_port)
                    responses = server_stub.AddSubscribeTopic(topic)
        except Exception as e:
            print("subscribe_topic",e)

    def update_subscribe_topic_status(self,server_stub):
        try:
            for topic_name in self.subscription:
                topic_status = node_pb2.SubscribeTopicStatus(topic_name=topic_name, node_id=self.node.node_id)
                responses = server_stub.UpdateSubscribeTopicStatus(topic_status)
        except Exception as e:
            print("update_subscribe_topic_status",e)
    
    def get_connection(self,server_stub):
        try:
            # update node status (alive)
            request_connection = node_pb2.RequestConnection(node_id=self.node.node_id,isSubscriber=True)
            responses = server_stub.GetConnection(request_connection)

            for topic in self.sub_pull_connection:
                self.topics_buffer[topic]=collections.deque(maxlen=self.buffer_maxlen)
                self.sub_pull_connection[topic]=[]
                self.connected_topic[topic]=[]
            # connection information
            
            for topic_info in responses.topics_info:
                if topic_info.sub_topic_name not in self.subscription:
                    continue
                topicID="{}:{}".format(topic_info.pub_node_id,topic_info.pub_topic_name)

                if topicID not in self.connected_topic[topic_info.sub_topic_name]:
                    self.connected_topic[topic_info.sub_topic_name].append(topicID)
                if topic_info.mode == 0:
                    info={}
                    info["topic_node"]=topic_info.pub_node_id
                    info["topic_name"]=topic_info.pub_topic_name
                    info["topic_type"]=topic_info.topic_type
                    info["isOnline"]=topic_info.isOnline
                    info["ip"]=topic_info.ip
                    info["port"]=topic_info.port
                    self.sub_pull_connection[topic_info.sub_topic_name].append(info)
            self.clientProcess.set_connection(self.sub_pull_connection)
        except Exception as e:    
            print('Subscriber (get_connection) Exception: {}'.format(e))
            time.sleep(1)
    
    def updata_data(self):
        topics_buffer=self.clientProcess.map_data_to_topic(self.clientProcess.read_data())
        for topic in topics_buffer:
            self.topics_buffer[topic]+=topics_buffer[topic]
        if self.subcribe_mode ==0:
            topics_buffer=self.serverProcess.map_data_to_topic(self.serverProcess.read_data())
            for topic in topics_buffer:
                self.topics_buffer[topic]+=topics_buffer[topic]
            
    def read_topic(self, topic_name):
        topic_name="{}:{}".format(self.node.node_id,topic_name)
        if topic_name in self.topics_buffer:
            if len(self.topics_buffer[topic_name])>0:
                return self.topics_buffer[topic_name].popleft()
        
        
    def read_topic_buffer(self,topic_name):
        topic_name="{}:{}".format(self.node.node_id,topic_name)
        data_buff=self.clientProcess.read_data()
        if topic_name in self.topics_buffer:
            buff=self.topics_buffer[topic_name]
            self.topics_buffer[topic_name].clear()
            return buff
        print("{} is not subcribed",topic_name)
        return []
    def terminate(self):
        try:
            print("terminating Subscriber..")
            if self.serverProcess is not None:
                self.serverProcess.terminate()
            self.stop_flag.set()
            self.thread.join()
        except Exception as e:
            print("terminate Subscriber fail:",e)

    def run(self):
        th_timer=0
        print("Subscriber run")
        try:
            with grpc.insecure_channel('{}:{}'.format(self.node.server_ip, self.node.server_port)) as channel: 
                while not self.stop_flag.wait(1):

                    server_stub = node_pb2_grpc.ControlStub(channel)
                    ntp_stub = ntp_pb2_grpc.NtpStub(channel)
                    self.node.update_node_status(server_stub)
                    self.node.ntp_sync(ntp_stub)
                    
                    self.update_subscribe_topic_status(server_stub)
                    
                    self.get_connection(server_stub)
                    
        except Exception as e:
            print("Subscriber",e)
        
        finally:
            print("Subscriber terminated")
    def __del__(self):
        try:
            self.terminate()
        except Exception as e:
            print("del Subscriber failed",e)

