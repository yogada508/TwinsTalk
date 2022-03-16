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
MAX_MESSAGE_LENGTH = 100000000
MILLI = 1000
MICRO = 1000000
class GRPC_ClientProcess2:
    #def __init__(self, request_node_id, topic_info, buffer_maxlen=20, subscribe_fps=0):
    def __init__(self, node_id, connection_status,client_mode,buffer_maxlen=20,subscribe_fps=100):
        self.client_mode=client_mode # 0=push sender, 1= pull receiver
        self.subscribe_fps=subscribe_fps
        self.node_id = node_id
        self.pub_topic_name = connection_status['pub_topic_name']
        self.sub_topic_name = connection_status['sub_topic_name']
        self.data_type = connection_status['topic_type']
        self.server_ip = connection_status['ip']
        self.server_port = connection_status['port']
        self.isOnline=connection_status['isOnline']
        self.buffer_maxlen=buffer_maxlen
        self.read_buffer = collections.deque(maxlen=buffer_maxlen)
        self.write_buffer = collections.deque(maxlen=buffer_maxlen)
        # d means double
        self.stop_flag=threading.Event()
        self.thread=threading.Thread(target=self.run,args=(self.stop_flag,))
        self.process_timer=time.time()
        self.thread.start()
    def read_buffer_empty(self):
        return len(self.read_buffer)==0
    
    def read_data(self):
        #print(self.sub_topic_name, 'queue length:', self.read_buffer.qsize())
        if self.read_buffer_empty():
            #print('queue is empty')
            return []
        res=self.read_buffer
        self.read_buffer=collections.deque(maxlen=self.buffer_maxlen)
        for data in res:
            print(time.time()-data.timestamp/1000000)
        return res

    def write_data(self,data):
        self.write_buffer.append(data)

    def setStatus(self,connection_status):
        self.isOnline=connection_status['isOnline']
    
    def is_alive(self):

        if time.time() - self.process_timer > 1:
            return False

        return True
    
    def terminate(self):
        self.stop_flag.set()
        self.thread.join()
        print('Terminate Subscriber: {}'.format(self.sub_topic_name))

    def pull_receiver(self):
        try:
            #print("pull_receiver")
            message = []
            message.append(pubsub_pb2.RequestTopicData(node_id=self.node_id, 
                                                        topic_name=self.pub_topic_name))
            #logging.debug('GRPC_ClientProcess Send Request')
            if self.data_type == 'str':
                responses = self.stub.GetStringData(iter(message))
            elif self.data_type == 'bytes':
                responses = self.stub.GetBytesData(iter(message))
            elif self.data_type == 'int':
                responses = self.stub.GetIntData(iter(message))
            elif self.data_type == 'float':
                responses = self.stub.GetFloatData(iter(message))
            elif self.data_type == 'bool':
                responses = self.stub.GetBoolData(iter(message))
            else:
                raise ("type error: {} , only 'str', 'int', 'bytes', 'float', 'bool'".format(self.topic_type))
                return
            #print("get responses")
                
            for res in responses:
                if not res.data:
                    continue
                print("delay on sending",time.time()-res.timestamp/MICRO,res.data)
                
                if res.timestamp != self.prev_timestamp:
                    # calculate time
                    end_time = time.time()
                    #logging.debug("GRPC_ClientProcess FPS={}".format(1 / (end_time - self.start_time)))
                    self.read_buffer.append(res)
                    self.prev_timestamp = res.timestamp
                    # calculate fps
                    self.start_time = time.time()
        except KeyboardInterrupt:
            print('KeyboardInterrupt Exception')
            return
        except Exception as e:
            #raise e
            print("pull_receiver",e)
            time.sleep(1)
    def push_sender(self):
        if self.data_type == 'str':
            self.push_Byte()
        elif self.data_type == 'bytes':
            self.push_Int()
        elif self.data_type == 'int':
            self.push_Float()
        elif self.data_type == 'float':
            self.push_String()
        elif self.data_type == 'bool':
            self.push_Bool()

    def push_Byte(self):
        try:
            messages = []
            while not self.write_buffer.empty():
                data=self.write_buffer.get()
                messages.append(pubsub_pb2.BytesData(   node_id=self.request_node_id,
                                                        topic_name=self.pub_topic_name,
                                                        data=data[0],
                                                        timestamp=data[1]
                                                        ))
            responses = self.stub.PostBytesData(iter(messages))
        except Exception as e:
            raise e
            print('GRPC_ClientProcess (push_sender) Exception: {}'.format(e))
    
    def push_Int(self):
        try:
            messages = []
            while not self.write_buffer.empty():
                data=self.write_buffer.get()
                messages.append(pubsub_pb2.IntData( node_id=self.request_node_id,
                                                    topic_name=self.pub_topic_name,
                                                    data=data[0],
                                                    timestamp=data[1]
                                                        ))
            responses = self.stub.PostIntData(iter(messages))
        except Exception as e:
            raise e
            print('GRPC_ClientProcess (push_sender) Exception: {}'.format(e))


    def push_Float(self):
            try:
                messages = []
                while not self.write_buffer.empty():
                    data=self.write_buffer.get()
                    messages.append(pubsub_pb2.FloatData( node_id=self.request_node_id,
                                                         topic_name=self.pub_topic_name,
                                                         data=data[0],
                                                            timestamp=data[1]
                                                            ))
                responses = self.stub.PostFloatData(iter(messages))
            except Exception as e:
                raise e
                print('GRPC_ClientProcess (push_sender) Exception: {}'.format(e))

    def push_String(self):
            try:
                messages = []
                while not self.write_buffer.empty():
                    data=self.write_buffer.get()
                    messages.append(pubsub_pb2.StringData(  node_id=self.request_node_id,
                                                            topic_name=self.pub_topic_name,
                                                            data=data[0],
                                                            timestamp=data[1]
                                                            ))
                responses = self.stub.StringData(iter(messages))
            except Exception as e:
                raise e
                print('GRPC_ClientProcess (push_sender) Exception: {}'.format(e))

    def push_Bool(self):
        try:
            messages = []
            while not self.write_buffer.empty():
                data=self.write_buffer.get()
                messages.append(pubsub_pb2.BoolData( node_id=self.request_node_id,
                                                     topic_name=self.pub_topic_name,
                                                     data=data[0],
                                                     timestamp=data[1]
                                                        ))
            responses = self.stub.PostBoolData(iter(messages))
        except Exception as e:
            raise e
            print('GRPC_ClientProcess (push_sender) Exception: {}'.format(e))

    
    def run(self,stop_flag):
        options = [('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
                    ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH)]
        print("grpc client connection",self.server_ip, self.server_port)
        channel = grpc.insecure_channel('{}:{}'.format(self.server_ip, self.server_port))
        intercept_channel = grpc.intercept_channel(channel, interceptor.NodeInterceptor())
        self.stub = pubsub_pb2_grpc.PubSubServiceStub(channel)
        # calculate time
        average_time = 0
        MILLI = 1000
        MICRO = 1000000

        # calculate fps
        self.start_time = time.time()
        self.prev_timestamp = 0
        print("start grpc client 2 Process")
        while not stop_flag.wait(0):
            try:
                if self.client_mode==1:
                    self.pull_receiver()
                else:
                    self.push_sender()
                #logging.debug('GRPC_ClientProcess Create Message')
                #logging.debug('GRPC_ClientProcess Finish')
            except Exception as e:
                #raise
                #if("failed to connect to all addresses" not in str(e)):
                print('GRPC_ClientProcess (run) Exception: {}'.format(e))
                time.sleep(1)