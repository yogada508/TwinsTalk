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
        self.topic_info = topic_config['topic_info']
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

        print('Start Publisher'.format())
    
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
            print(e)

    def delete_topic(self, topic_name, topic_type):
        try:
            topic = node_pb2.Topic(topic_name=topic_name, topic_type=topic_type, node_id=self.node.node_id)
            responses = self.server_stub.DeleteTopic(topic)
        except Exception as e:
            print("delete_topic",e)

    def data_writer(self, topic_name, topic_data):
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
            self.update_subscriber()
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
        if 'topic_info' not in sub_topic_config:
            print("'topic_info' is not in sub_topic_config")
            exit(1)

        self.node = node
        self.sub_topic_config = sub_topic_config
        self.subcribe_mode=sub_topic_config['mode']
        self.subcribe_ip=sub_topic_config['ip']
        self.subcribe_port=sub_topic_config['port']
        self.subscription=sub_topic_config['topic_info']
        self.update_timing = update_timing
        self.buffer_maxlen=buffer_maxlen

        self.topics_buffer = {}
        self.topics_connected_nodes = {}
        self.serverProcess=None
        
        if self.subcribe_mode==0:
            self.serverProcess=GRPC_ServerProcess(self.node,self.subcribe_port,self.topics_buffer,self.topics_connected_nodes)        
        self.subscriber = {}
        self.subscribe_topic()

        self.stop_flag=threading.Event()
        self.thread = threading.Thread(target=self.run,args=(self.stop_flag,))
        self.thread.start()
        print('Start Subscriber'.format())
        
    def subscribe_topic(self):
        try:
            for topic_name in self.subscription:
                self.topics_buffer[topic_name]=[]
                topic_type = self.subscription[topic_name]
                # add subscribe topic to server
                topic = node_pb2.SubscribeTopic(topic_name=topic_name, 
                                                topic_type=topic_type, 
                                                node_id=self.node.node_id,
                                                node_domain=self.node.node_domain,
                                                mode=self.subcribe_mode,
                                                ip=self.subcribe_ip,
                                                port=self.subcribe_port)
                responses = self.node.server_stub.AddSubscribeTopic(topic)
        except Exception as e:
            print(e)

    def update_subscribe_topic_status(self):

        try:
            for topic_name in self.subscription:
                topic_status = node_pb2.SubscribeTopicStatus(topic_name=topic_name, node_id=self.node.node_id)
                responses = self.node.server_stub.UpdateSubscribeTopicStatus(topic_status)
        except Exception as e:
            print(e)
    
    def get_connection(self):
        try:
            # update node status (alive)
            request_connection = node_pb2.RequestConnection(node_id=self.node.node_id,isSubscriber=True)
            responses = self.node.server_stub.GetConnection(request_connection)

            # connection information
            current_connections = []
            for topic_info in responses.topics_info:
                if topic_info.sub_topic_name not in self.subscription:
                    continue
                current_connections.append(topic_info.sub_topic_name)
                if topic_info.mode == 0:
                    status={
                            'pub_topic_name': topic_info.pub_topic_name,
                            'sub_topic_name': topic_info.sub_topic_name,
                            'topic_type': topic_info.topic_type,
                            'mode':topic_info.mode,
                            'ip': topic_info.ip,
                            'port': topic_info.port,
                            'isOnline':topic_info.isOnline
                            }
                    if topic_info.sub_topic_name not in self.subscriber:
                        self.subscriber[topic_info.sub_topic_name] = GRPC_ClientProcess(
                                self.node.node_id,
                                status,
                                1,
                                self.buffer_maxlen)
                    else:
                        self.subscriber[topic_info.sub_topic_name].setStatus(status)

            # check subscriber is alive
            for topic_name in list(self.subscriber.keys()):
                logging.debug('{}-{}'.format(topic_name, self.subscriber[topic_name].is_alive()))
                #print('{}-{}'.format(topic_name, self.subscriber[topic_name].is_alive()))
            # check connection information and terminate not used process
            '''
            for topic_name in list(self.subscriber.keys()):
                if topic_name not in current_connections:
                    self.subscriber[topic_name].terminate()
                    del self.subscriber[topic_name]
            '''
        except Exception as e:
            print('Subscriber (get_connection) Exception: {}'.format(e))
            time.sleep(1)

    def data_reader(self, topic_name):
        try:

            if topic_name in self.topics_buffer:
                if len(self.topics_buffer[topic_name])>0:
                    return self.topics_buffer[topic_name].pop(0)
            return None
        except Exception as e:
            print("data_reader",e)
        return None
    
    def terminate(self):
        try:
            print("terminating Subscriber..")
            if self.serverProcess is not None:
                self.serverProcess.terminate()
            self.stop_flag.set()
            self.thread.join()
        except Exception as e:
            print("terminate Subscriber fail:",e)

    def run(self,stop_flag):
        th_timer=0
        print("Subscriber run")
        
        try:
            while not stop_flag.wait(1):
                if time.time()-th_timer >1:
                    self.update_subscribe_topic_status()
                    self.get_connection()
                    th_timer=time.time()        
                for sub in self.subscriber:
                    self.topics_buffer[sub].extend(self.subscriber[sub].read_data())
                    #print(threading.current_thread(),sub,len(self.topics_buffer[sub]))
                
                #time.sleep(0)    
            for sub in self.subscriber:
                print("terminate grpc process",sub)
                self.subscriber[sub].terminate()
        
        except Exception as e:
            print("Subscriber",e)
        
        finally:
            print("Subscriber terminated")
    def __del__(self):
        try:
            self.terminate()
        except Exception as e:
            print("del Subscriber failed",e)

            
