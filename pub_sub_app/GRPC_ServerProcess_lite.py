import threading
import multiprocessing
from multiprocessing.managers import SharedMemoryManager
from concurrent import futures
import collections
import grpc
import node_pb2
import node_pb2_grpc
import pubsub_pb2
import pubsub_pb2_grpc
import interceptor
from PubSubServiceServicer import PubSubServiceServicer
import numpy as np
import time

BuffSize=5
ProtobufDataDict={}
ProtobufDataDict['str']=pubsub_pb2.StringData
ProtobufDataDict['bytes']=pubsub_pb2.BytesData
ProtobufDataDict['int']=pubsub_pb2.IntData
ProtobufDataDict['float']=pubsub_pb2.FloatData
ProtobufDataDict['bool']=pubsub_pb2.BoolData

def createBytes(size):
    return b'\0'*size

def init_buf(dataSize,bufferSize):
    buff=[]
    #data=b""
    data=createBytes(dataSize)
    for i in range(bufferSize):
        buff.append(data)
    return buff

class GRPC_ServerProcess(object):
    """docstring for GRPC_Server"""
    def __init__(self,node,port,topics_buffer,topic_info,server_mode):
        print("start grpc server")
        self.node=node
        self.port=port
        self.server_mode=server_mode # 0=sender 1=receiver
        self.topic_info=topic_info
        self.stop_flag=multiprocessing.Event()
        self.sm=multiprocessing.Manager()

        self.smm=multiprocessing.managers.SharedMemoryManager()
        self.smm.start()

        self.RingBuffer=collections.deque(maxlen=BuffSize)
        self.process=threading.Thread(target=self.run,args=(topics_buffer,))
        self.process.start()


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
                if topic not in topics_buffer:
                    topics_buffer[topic]=[]    
                topics_buffer[topic].append(data)
            return topics_buffer
        except Exception as e:
            
            print("map data failed",data_buff)
            raise e
    
    def read_data(self):
        data_buffer=self.RingBuffer.copy()
        self.RingBuffer.clear()
        return data_buffer
    
    def write_data(self,data,topic_name,data_type):
        #print("write_data in server",topic_name,data_type)

        proto_data=pubsub_pb2.ProtoData(
                type=data_type,
                name=topic_name,
                data=data.SerializeToString(),
                timestamp=time.time())
        self.RingBuffer.append(proto_data)
        
    
    def write_topics_buffer(self,topics_buffer,proto_buff):
        for data in proto_buff:
            n=data.name
            if(n not in topics_buffer):
                print("de serialize error")
                exit(1)
                continue
            topics_buffer[n].append(data.data)
    
    def read_topics_buffer(self,topics_buffer):
        for topic in topics_buffer:
            tmp=topics_buffer[topic].copy()
            topics_buffer[topic].clear()

            for data in tmp:
                self.write_data(data,topic,self.topic_info[topic])
            
        
    def run(self,topics_buffer):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        servicer=PubSubServiceServicer(self.node,topics_buffer,BuffSize)
        pubsub_pb2_grpc.add_PubSubServiceServicer_to_server(servicer, server)
        server.add_insecure_port('[::]:{}'.format(self.port))
        server.start()
        try:
            while not self.stop_flag.wait(0):
                try:
                    if self.server_mode==0:
                        sm_buf=self.read_data()
                        self.write_topics_buffer(topics_buffer,sm_buf)
                    else:
                        self.read_topics_buffer(servicer.topics_buffer)
                except Exception as e:
                    raise e
        except KeyboardInterrupt:
            server.stop(0)    
        except Exception as e:
            raise e
            print("Grpc server error",e)
        server.stop(0)
        print("server terminated")
        exit(1)
    def terminate(self):
        print("terminating grpc server")

        self.stop_flag.set()
        self.process.join()
        self.smm.shutdown()
    def __del__(self):
        self.terminate()