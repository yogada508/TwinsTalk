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
SmallDataSize=8000 #8KB
SmallBuffSize=20
LargeDataSize= 10 * 1024 * 1024 # 10MB max data size
LargeBuffSize=10

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
    def __init__(self,node,port,topics_buffer,server_mode):
        self.node=node
        self.port=port
        self.server_mode=server_mode # 0=sender 1=receiver

        self.stop_flag=multiprocessing.Event()
        self.sm=multiprocessing.Manager()

        self.smm=multiprocessing.managers.SharedMemoryManager()
        self.smm.start()

        self.SmallBuff=self.sm.list()
        self.create_buffer(self.SmallBuff,SmallBuffSize,SmallDataSize)
        self.ws_pt=self.sm.Value('i',0)

        self.LargeBuffEnabled=self.sm.Value('b',False)
        self.LargeBuff=self.sm.list()
        self.wl_pt=self.sm.Value('i',0)

        #self.LargeBuff=self.smm.ShareableList(init_buf(LargeDataSize,LargeBuffSize))
        #self.wl_pt=self.sm.Value('i',0)
    
        self.process=multiprocessing.Process(target=self.run,args=(topics_buffer,))
        self.process.start()

    def create_buffer(self,buff,leng,size):
        for i in range(leng):
            shm = self.smm.SharedMemory(size=size)
            shm=None
            buff.append(shm)
        return buff

    def enable_large_buff(self):
        self.create_buffer(self.LargeBuff,LargeBuffSize,LargeDataSize)
        self.LargeBuffEnabled.value=True  

    def read_data(self):
        #print("read_data")
        data_buffer=[]
        for i in range(SmallBuffSize):
            if i == self.ws_pt.value:
                continue
            b=self.SmallBuff[i]
            if b is not None and b:
                data=pubsub_pb2.ProtoData()
                data.ParseFromString(b)
                data_buffer.append(data)
                self.SmallBuff[i]=None
        if self.LargeBuffEnabled.value:
            for i in range(LargeBuffSize):
                if i == self.wl_pt.value:
                    continue
                b=self.LargeBuff[i]    
                if b is not None and b:
                    data=pubsub_pb2.ProtoData()
                    data.ParseFromString(b)
                    data_buffer.append(data)
                    self.LargeBuff[i]=None
        return data_buffer

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
    
    def write_data(self,data,topic_name,data_type):

        proto_byte=(pubsub_pb2.ProtoData(
            type=data_type,
            name=data.topic_name,
            data=data.SerializeToString(),
            timestamp=time.time()
        )).SerializeToString()
        if proto_byte.__sizeof__() <=SmallDataSize:
            self.write_small_data(proto_byte)
        elif proto_byte.__sizeof__() <=LargeDataSize:
            self.write_large_data(proto_byte)
        else:
            print("write data too large, discard")
    
    def write_small_data(self,proto_byte):

        self.SmallBuff[self.ws_pt.value]=proto_byte
        self.ws_pt.value+=1
        if(self.ws_pt.value>=SmallBuffSize):
            self.ws_pt.value=0

    def write_large_data(self,proto_byte):
        #print("write_large_data",len(proto_byte))
        if not self.LargeBuffEnabled.value:
            self.enable_large_buff()
        self.LargeBuff[self.wl_pt.value]=proto_byte
        self.wl_pt.value+=1
        if(self.wl_pt.value>=LargeBuffSize):
            self.wl_pt.value=0
    
    def read_small_buff(self):
        try:
            proto_datas=[]
            for i,b in enumerate(self.SmallBuff):
                if b and i!=self.ws_pt.value:
                    #print("read",i,self.ws_pt.value,b)
                    data=pubsub_pb2.ProtoData()
                    data.ParseFromString(b)
                    proto_datas.append(data)
                    self.SmallBuff[i]=b'\0'
            return proto_datas
        except Exception as e:
            raise e
        
    
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

            for data, data_type in tmp:
                self.write_data(data, topic, data_type)
            
        
    def run(self,topics_buffer):
        options = [('grpc.max_send_message_length', LargeDataSize), ('grpc.max_receive_message_length', LargeDataSize)]
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=options)
        servicer=PubSubServiceServicer(self.node,topics_buffer)
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