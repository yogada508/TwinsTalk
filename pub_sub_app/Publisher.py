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
import pubsub_pb2
import pubsub_pb2_grpc
import interceptor
#from GRPC_ClientProcess2 import GRPC_ClientProcess2 as GRPC_ClientProcess
from GRPC_ClientProcess import GRPC_ClientProcess as GRPC_ClientProcess
from GRPC_ServerProcess import GRPC_ServerProcess
from PubSubServiceServicer import PubSubServiceServicer
from SubscribeServiceServicer import SubscribeServiceServicer



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
class Publisher():

    def __init__(self, node, topic_config, buffer_maxlen=100, update_timing=30):
        # initial variable
        if 'topic_info' not in topic_config:
            print('topic_info not in topic_config')
            exit(1)
        if 'mode' not in topic_config:
            print('\'mode\' not in topic_config')
            exit(1)
        elif topic_config['mode']==0:
            if 'ip' not in topic_config:
                print('\'ip\' not in topic_config')
                exit(1)
            if 'port' not in topic_config:
                print('\'port\' not in topic_config')
                exit(1)
        else:
            update_timing=0
            topic_config['ip']='0.0.0.0'
            topic_config['port']=0

        self.node = node
        self.topic_info = {}
        for topic in topic_config['topic_info']:
            topicID="{}:{}".format(node.node_id,topic)
            self.topic_info[topicID]=topic_config['topic_info'][topic]
        self.topic_ip = topic_config['ip']
        self.topic_port = topic_config['port']
        self.topic_mode = topic_config['mode'] 
        self.buffer_maxlen = buffer_maxlen
        self.update_timing = update_timing

        # initial topic buffer
        self.topics_buffer = {}
        self.topics_connected_nodes = {}

        # add topic to server
        self.publish_topic()
        
        self.serverProcess=None
    
        if self.topic_mode==0:
            self.serverProcess=GRPC_ServerProcess(self.node,self.topic_port,self.topics_buffer,self.topics_connected_nodes)
        
        self.sub_stub={}
        self.stop_flag=threading.Event()
        self.thread = threading.Thread(target=self.run,args=(self.stop_flag,))
        self.thread.start()

        print('Start Publisher')
    
    def ResponseTopicInfosToDict(self,topics_info):
        res={}
        for topic_info in topics_info:
            topic_ID="{}:{}".format(topic_info.sub_node_id,topic_info.sub_topic_name)
            conn_info={}
            conn_info['ip']=topic_info.ip
            conn_info['port']=topic_info.port
            res[topic_ID]=conn_info
        return res
    
    def get_sync_time(self):

        
        #return int(time.time() * MICRO + self.node.delay)
        return int(time.time() * MICRO)
    def publish_topic(self):

        try:
            for topic_name, topic_type in self.topic_info.items():
                # create topic buffer
                self.topics_buffer[topic_name] = collections.deque(maxlen=self.buffer_maxlen)
                # create topic connection subscriber
                self.topics_connected_nodes[topic_name] = []
                # add topic to server
                topic = node_pb2.TopicInfo(topic_name=topic_name, 
                                        topic_type=topic_type, 
                                        mode=self.topic_mode,
                                        ip=self.topic_ip, 
                                        port=self.topic_port, 
                                        node_id=self.node.node_id,
                                        node_domain=self.node.node_domain)
                responses = self.node.server_stub.AddTopic(topic)
        except Exception as e:
            print("publish_topic",e)

    def delete_topic(self, topic_name, topic_type):
        try:
            topic = node_pb2.Topic(topic_name=topic_name, topic_type=topic_type, node_id=self.node.node_id)
            responses = self.server_stub.DeleteTopic(topic)
        except Exception as e:
            print("delete_topic",e)

    def data_writer(self, topic_name, topic_data):
        topic_name="{}:{}".format(self.node.node_id,topic_name)
        data_type=self.topic_info[topic_name]
        
        proto_data=ProtobufDataDict[data_type](
            node_id=self.node.node_id,
            topic_name=topic_name,
            data=topic_data,
            timestamp=self.get_sync_time() 
        )

        self.serverProcess.write_data(proto_data,data_type)
        #self.topics_buffer[topic_name].append([topic_data, self.get_sync_time()])
        
    def update_subscriber(self):
        request_connection = node_pb2.RequestConnection(node_id=self.node.node_id,isSubscriber=False)
        responses = self.node.server_stub.GetConnection(request_connection)
        connected_topic_info=self.ResponseTopicInfosToDict(responses.topics_info)       
        #print(connected_topic_info)

    def run(self,stop_flag):
        while not stop_flag.wait(0):
            self.update_topic_status()
            #self.update_subscriber()
            time.sleep(1)
        print("Publisher terminated")

    def terminate(self):
        try:
            print("terminating publisher")
            if self.serverProcess is not None:
                self.serverProcess.terminate()
            self.stop_flag.set()
            self.thread.join()
        except Exception as e:
            print("terminate publisher failed",e)
    def update_topic_status(self):
        try:
            for topic_name in self.topics_connected_nodes:
                topic_status = node_pb2.TopicStatus(topic_name=topic_name, node_id=self.node.node_id)
                topic_status.connected_nodes.extend(self.topics_connected_nodes[topic_name])
                responses = self.node.server_stub.UpdateTopicStatus(topic_status)
                self.topics_connected_nodes[topic_name].clear()
        except Exception as e:
            print(e)
    def __del__(self):
        self.terminate()