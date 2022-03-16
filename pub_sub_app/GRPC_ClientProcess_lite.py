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
MILLI = 1000
MICRO = 1000000
MAX_MESSAGE_LENGTH = 100000000
_PROCESS_COUNT=10
'''
SmallDataSize=8000 #8KB
SmallBuffSize=10
LargeDataSize= 4000000 #4MB 
LargeBuffSize=3
'''
BuffSize=3

ProtobufDataDict={}
ProtobufDataDict['str']=pubsub_pb2.StringData
ProtobufDataDict['bytes']=pubsub_pb2.BytesData
ProtobufDataDict['int']=pubsub_pb2.IntData
ProtobufDataDict['float']=pubsub_pb2.FloatData
ProtobufDataDict['bool']=pubsub_pb2.BoolData


def pull_request(stub,message,topic_type):
    if topic_type == 'str':
        responses = stub.GetStringData(iter(message),timeout=2)
    elif topic_type == 'bytes':
        responses = stub.GetBytesData(iter(message),timeout=2)
    elif topic_type == 'int':
        responses = stub.GetIntData(iter(message),timeout=2)
    elif topic_type == 'float':
        responses = stub.GetFloatData(iter(message),timeout=2)
    elif topic_type == 'bool':
        responses = stub.GetBoolData(iter(message),timeout=2)
    return responses

def push_request(stub,message,topic_type):
    #print("message",len(message),message)
    print("push delay",len(message),len(message[0].data),message[0].topic_name,time.time()-message[0].timestamp/MICRO)
    
    if topic_type == 'str':
        responses = stub.PostStringData(iter(message),timeout=2)
    elif topic_type == 'bytes':
        responses = stub.PostBytesData(iter(message),timeout=2)
    elif topic_type == 'int':
        responses = stub.PostIntData(iter(message),timeout=2)
    elif topic_type == 'float':
        responses = stub.PostFloatData(iter(message),timeout=2)
    elif topic_type == 'bool':
        responses = stub.PostBoolData(iter(message),timeout=2)
    return responses

def createBytes(size):
    return b'\0'*size
def init_buf(dataSize,bufferSize):
    buff=[]
    #data=b""
    data=createBytes(dataSize)
    for i in range(bufferSize):
        buff.append(data)
    return buff

class GRPC_ClientProcess:
    #def __init__(self, request_node_id, topic_info, buffer_maxlen=20, subscribe_fps=0):
    def __init__(self, node,client_mode,buffer_maxlen=20,subscribe_fps=100):
        print("start GRPC client lite")
        self.client_mode=client_mode # 0=push sender, 1= pull receiver
        self.subscribe_fps=subscribe_fps
        self.node = node
        self.node_id = self.node.node_id

        self.buffer_maxlen=buffer_maxlen
        
        self.sm=multiprocessing.Manager()

        
        # d means double
        self.stub={}
        self.stop_flag=multiprocessing.Event()
        self.update_conn_nock=multiprocessing.Event()
        
        #elf.connected_stub={}
        #self.topic_timestamp=self.sm.dict()
        self.smm=multiprocessing.managers.SharedMemoryManager()
        self.smm.start()    

        self.RingBuffer=collections.deque(maxlen=BuffSize)
        

        self.connection_info=self.sm.list()
        for i in range(2):
            self.connection_info.append(self.sm.dict())
        self.info_pt=self.sm.Value('i',0)

        self.process=threading.Thread(target=self.run)
        self.process.start()
        
    def read_data(self):
        data_buffer=self.RingBuffer.copy()
        self.RingBuffer.clear()
        return data_buffer
    
    def write_data(self,data,topic_name,data_type):

        proto_data=pubsub_pb2.ProtoData(
                type=data_type,
                name=topic_name,
                data=data.SerializeToString(),
                timestamp=time.time())
        self.RingBuffer.append(proto_data)
    

    def terminate(self):
        self.stop_flag.set()
        self.process.join()
        self.smm.shutdown()
        print('Terminate Subscriber: {}'.format(self.sub_topic_name))
    
    def set_connection(self,connection):

        pt=self.info_pt.value+1
        if(pt>=2):
            pt=0
        self.connection_info[pt].clear()
        for conn in connection:
            self.connection_info[pt][conn]=connection[conn].copy()
        self.info_pt.value=pt

    def map_data_to_topic(self,data_buff):
        try:
            topics_buffer={}
            #print(data_buff)
            for d in data_buff:
                #print("d",d)
                topic=d.name
                data_type=d.type
                #if data_type not in ProtobufDataDict:
                #    print("error packages",d)
                #    continue
                data=ProtobufDataDict[data_type]()
                data.ParseFromString(d.data)
                print("map data",time.time()-data.timestamp/MICRO)
                if topic not in topics_buffer:
                    topics_buffer[topic]=[]    
                topics_buffer[topic].append(data)
            return topics_buffer
        except Exception as e:        
            print("map data failed")
            raise e

    def get_sync_time(self):
        #return int(time.time() * MICRO + self.node.delay)
        return int(time.time() * MICRO)    
    
    def pull_receiver(self):
        connection_list=[]
        connection_info=self.connection_info[self.info_pt.value]
        for topic in connection_info.keys():
            for info in connection_info[topic]:
                if not info["isOnline"]:
                    continue
                addr="{}:{}".format(info["ip"],info["port"])
                conn={}
                conn["topic_type"]=info["topic_type"]
                conn["client_mode"]=1
                conn["pub_name"]=info["topic_name"]
                conn["sub_name"]=topic
                message = []
                message.append(pubsub_pb2.RequestTopicData(node_id=self.node_id, 
                                                        topic_name=info["topic_name"]))       
                connection_list.append((addr,conn,message))
        self.update_conn_nock.clear()
        return connection_list
    
    def push_sender(self):
        connection_list=[]
        connection_info=self.connection_info[self.info_pt.value]
        topics_buffer=self.map_data_to_topic(self.read_data())
        #if len(topics_buffer)>0:
        #    print("push data",topics_buffer.keys())
        i=0
        for topic in connection_info.keys():
            if topic not in topics_buffer:
                continue
            #print("topics_buffer",topic,len(topics_buffer[topic]))
        
            for info in connection_info[topic]:
                #print("topic_info",topic,info)
                if not info["isOnline"]:
                    continue
                addr="{}:{}".format(info["ip"],info["port"])
                conn={}
                conn["topic_type"]=info["topic_type"]
                conn["client_mode"]=0
                conn["pub_name"]=topic
                conn["sub_name"]=info["topic_name"]
                
                messages=topics_buffer[topic]
                connection_list.append((addr,conn,messages))
       
        return connection_list
    def request(self,args):
        try:

            #with grpc.insecure_channel(args[0]) as channel:
            #    stub=pubsub_pb2_grpc.PubSubServiceStub(channel)
            addr=args[0]
            info=args[1]
            messages=args[2]
            if addr not in self.stub:
                channel=grpc.insecure_channel(args[0])
                self.stub[addr]=pubsub_pb2_grpc.PubSubServiceStub(channel)
                
            stub=self.stub[addr]
            if info["client_mode"]==1:
                responses=pull_request(stub,messages,info["topic_type"])
            else:
                #print("send",addr,info["sub_name"],messages[0].topic_name)
                for msg in messages:
                    msg.topic_name=info["sub_name"]
                responses=push_request(stub,messages,info["topic_type"])
            res_list=[]
            for res in responses:
                if not res.data:
                    continue
                print("rec delay time:",len(res.data),info['sub_name'],res.node_id,res.topic_name,time.time()-res.timestamp/MICRO)
                res_list.append((info,res))
            #print(res_list)
            return res_list
        except Exception as e:
            print("request_th",e) 
            return []

    def run(self):
        # calculate time
        average_time = 0
        # calculate fps
        self.start_time = time.time()
        self.prev_timestamp = 0
        print("start GRPC client Process")
        try:
            while not self.stop_flag.wait(0.001):
                try:
                    if self.client_mode==1:
                        connection_info=self.pull_receiver()
                    else:
                        connection_info=self.push_sender()
                    responses=[]
                    for arg in connection_info:
                        responses.extend(self.request(arg))
                    if self.client_mode==1:
                        for info,res in responses:
#                            print("delay time:",len(res.data),res.node_id,res.topic_name,res.topic_name,time.time()-res.timestamp/MICRO)
                            self.write_data(res,info['sub_name'],info["topic_type"])
                except Exception as e:
                    #raise e
                    print('GRPC_ClientProcess (run) Exception: {}'.format(e))
                    time.sleep(1)
            
        finally:
            print("terminating worker_pool")
            #worker_pool.terminate()
            #worker_pool.close()
            #worker_pool.join()
            print("worker_pool terminated")