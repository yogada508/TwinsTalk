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
class GRPC_ClientProcess:
    #def __init__(self, request_node_id, topic_info, buffer_maxlen=20, subscribe_fps=0):
    def __init__(self, node_id, connection_status,client_mode,buffer_maxlen=20):
        self.client_mode=client_mode # 0=push sender, 1= pull receiver
        #self.subscribe_fps = subscribe_fps
        self.node_id = node_id
        self.pub_topic_name = connection_status['pub_topic_name']
        self.sub_topic_name = connection_status['sub_topic_name']
        self.data_type = connection_status['topic_type']
        self.server_ip = connection_status['ip']
        self.server_port = connection_status['port']
        self.isOnline=connection_status['isOnline']

        self.read_buffer = multiprocessing.Queue(maxsize=buffer_maxlen)
        self.write_buffer = multiprocessing.Queue(maxsize=buffer_maxlen)
        # d means double
        self.stop_flag=multiprocessing.Event()
        self.process_timer = multiprocessing.Value('d', time.time())
        self.process = multiprocessing.Process(target=self.run,args=(self.stop_flag,))
        self.process.start()
        logging.debug('Start GRPC_ClientProcess: {}, {}:{}'.format(self.sub_topic_name, self.server_ip, self.server_port))
    
    def read_buffer_empty(self):
        return self.read_buffer.empty()
    def read_data(self):
        #print(self.sub_topic_name, 'queue length:', self.read_buffer.qsize())
        res=[]
        while not self.read_buffer.empty():
            data=self.read_buffer.get()
            print("get_data from process",time.time()-data.timestamp/1000000)
            res.append(self.read_buffer.get())
        return res

    def write_data(self,data):
        if self.write_buffer.full():
            self.write_buffer.get()
        self.write_buffer.put(data)
    def setStatus(self,connection_status):
        self.isOnline=connection_status['isOnline']
    
    def is_alive(self):

        logging.debug('process_timer: {}'.format(self.process_timer.value))
        print("is_alive",time.time() - self.process_timer.value<1)
        if time.time() - self.process_timer.value > 1:
            return False
        return True

    def terminate(self):
        self.process.terminate()
        print('Terminate Subscriber: {}'.format(self.sub_topic_name))

    def pull_receiver(self):
        try:
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
            for res in responses:
                if not res.data:
                    continue
                #self.process_timer.value = time.time()
                print("delay on sending",time.time()-res.timestamp/MICRO,res.data)
                if res.timestamp != self.prev_timestamp:
                    end_time = time.time()
                    if self.read_buffer.full():
                        self.read_buffer.get()
                    self.read_buffer.put(res)
                    self.prev_timestamp = res.timestamp
                    # calculate fps
                    self.start_time = time.time()
        except KeyboardInterrupt:
            print('KeyboardInterrupt Exception')
            return
        except Exception as e:
            #raise e
            #time.sleep(0)
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
        timer=time.time()
        options = [('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
                    ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH)]
        print("grpc client connection",self.server_ip, self.server_port)
        channel = grpc.insecure_channel('{}:{}'.format(self.server_ip, self.server_port))
        intercept_channel = grpc.intercept_channel(channel, interceptor.NodeInterceptor())
        self.stub = pubsub_pb2_grpc.PubSubServiceStub(channel)
        print("build stub time",time.time()-timer)
        # calculate time
        average_time = 0


        # calculate fps
        self.start_time = time.time()
        self.prev_timestamp = 0
        try:
            while not stop_flag.wait(0):     
                if self.client_mode==1:
                    self.pull_receiver()
                else:
                    self.push_sender()
        except KeyboardInterrupt:
            print('KeyboardInterrupt Exception (client process)')
        except Exception as e:
            print('GRPC_ClientProcess (run) Exception: {}'.format(e))