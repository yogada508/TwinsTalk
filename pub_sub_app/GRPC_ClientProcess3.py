# ============================================================
# import packages
# ============================================================
from pyexpat.errors import messages
from socket import timeout
import time
import base64
import sys
import logging
import threading
import multiprocessing
import collections
import os
import copy

# ============================================================
# import grpc protobuf
# ============================================================
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
_PROCESS_COUNT = 3
SmallDataSize = 8000  # 8KB
SmallBuffSize = 20
LargeDataSize = 10*1024*1024  # 10MB
LargeBuffSize = 5


ProtobufDataDict = {}
ProtobufDataDict['str'] = pubsub_pb2.StringData
ProtobufDataDict['bytes'] = pubsub_pb2.BytesData
ProtobufDataDict['int'] = pubsub_pb2.IntData
ProtobufDataDict['float'] = pubsub_pb2.FloatData
ProtobufDataDict['bool'] = pubsub_pb2.BoolData


def request_th(args):
    try:
        with grpc.insecure_channel(args[0]) as channel:
            stub = pubsub_pb2_grpc.PubSubServiceStub(channel)
            info = args[1]
            message = args[2]

            if info["client_mode"] == 1:
                responses = pull_request(stub, message, info["topic_type"])
            else:
                responses = push_request(stub, message, info["topic_type"])
            res_list = []
            for res in responses:
                if not res.data:
                    continue
                print("rec delay time:", len(res.data), res.node_id,
                      res.topic_name, res.topic_name, time.time()-res.timestamp/MICRO)
                res_list.append((info, res))
            # print(f'time:{time.time()} ,pid:{os.getpid()}, res"{res_list}')
            return res_list
    except Exception as e:
        print("request_th", e)
        return []


def pull_request(stub, message, topic_type):
    if topic_type == 'str':
        responses = stub.GetStringData(iter(message))
    elif topic_type == 'bytes':
        responses = stub.GetBytesData(iter(message))
    elif topic_type == 'int':
        responses = stub.GetIntData(iter(message))
    elif topic_type == 'float':
        responses = stub.GetFloatData(iter(message))
    elif topic_type == 'bool':
        responses = stub.GetBoolData(iter(message))

    return responses


def push_request(stub, message, topic_type):
    # print("message",len(message),message)
    if topic_type == 'str':
        responses = stub.PostStringData(iter(message))
    elif topic_type == 'bytes':
        responses = stub.PostBytesData(iter(message))
    elif topic_type == 'int':
        responses = stub.PostIntData(iter(message))
    elif topic_type == 'float':
        responses = stub.PostFloatData(iter(message))
    elif topic_type == 'bool':
        responses = stub.PostBoolData(iter(message))
    return responses


def createBytes(size):
    return b'\0'*size


def init_buf(dataSize, bufferSize):
    buff = []
    # data=b""
    data = createBytes(dataSize)
    for i in range(bufferSize):
        buff.append(data)
    return buff


class GRPC_ClientProcess3:
    # def __init__(self, request_node_id, topic_info, buffer_maxlen=20, subscribe_fps=0):
    def __init__(self, node, client_mode, buffer_maxlen=20, subscribe_fps=100):
        self.client_mode = client_mode  # 0=push sender, 1= pull receiver
        self.subscribe_fps = subscribe_fps
        self.node_id = node.node_id

        self.buffer_maxlen = buffer_maxlen

        self.sm = multiprocessing.Manager()

        # d means double
        self.stop_flag = multiprocessing.Event()
        self.update_conn_nock = multiprocessing.Event()

        self.topic_addr = {}
        self.connected_stub={}
        # self.topic_timestamp=self.sm.dict()

        self.smm = multiprocessing.managers.SharedMemoryManager()
        self.smm.start()

        self.SmallBuff = self.sm.list()
        self.create_buffer(self.SmallBuff, SmallBuffSize, SmallDataSize)
        self.ws_pt = self.sm.Value('i', 0)

        self.LargeBuffEnabled = self.sm.Value('b', False)
        self.LargeBuff = self.sm.list()
        self.wl_pt = self.sm.Value('i', 0)

        self.connection_info = self.sm.list()
        for i in range(2):
            self.connection_info.append(self.sm.dict())
        self.info_pt = self.sm.Value('i', 0)

        self.process = multiprocessing.Process(target=self.run)
        self.process.start()

    def create_buffer(self, buff, leng, size):
        for i in range(leng):
            shm = self.smm.SharedMemory(size=size)
            shm = None
            buff.append(shm)
        return buff

    def enable_large_buff(self):
        self.create_buffer(self.LargeBuff, LargeBuffSize, LargeDataSize)
        self.LargeBuffEnabled.value = True

    def read_data(self):
        # print("read_data")
        data_buffer = []
        for i in range(SmallBuffSize):
            if i == self.ws_pt.value:
                continue
            b = self.SmallBuff[i]
            if b is not None and b:
                data = pubsub_pb2.ProtoData()
                data.ParseFromString(b)
                data_buffer.append(data)
                self.SmallBuff[i] = None
        if self.LargeBuffEnabled.value:
            for i in range(LargeBuffSize):
                if i == self.wl_pt.value:
                    continue
                b = self.LargeBuff[i]
                if b is not None and b:
                    data = pubsub_pb2.ProtoData()
                    data.ParseFromString(b)
                    data_buffer.append(data)
                    self.LargeBuff[i] = None
        return data_buffer

    def write_data(self, data, topic_name, data_type):
        proto_byte = (pubsub_pb2.ProtoData(
            type=data_type,
            name=topic_name,
            data=data.SerializeToString(),
            timestamp=time.time()
        )).SerializeToString()
        if proto_byte.__sizeof__() <= SmallDataSize:
            self.write_small_data(proto_byte)
        elif proto_byte.__sizeof__() <= LargeDataSize:
            self.write_large_data(proto_byte)
        else:
            print("write data too large, discard")

    def write_small_data(self, proto_byte):
        # print("write_small_data",proto_byte)
        self.SmallBuff[self.ws_pt.value] = proto_byte
        self.ws_pt.value += 1
        if(self.ws_pt.value >= SmallBuffSize):
            self.ws_pt.value = 0

    def write_large_data(self, proto_byte):
        # print("write_small_data",proto_byte)
        if not self.LargeBuffEnabled.value:
            self.enable_large_buff()
        self.LargeBuff[self.wl_pt.value] = proto_byte
        self.wl_pt.value += 1
        if(self.wl_pt.value >= LargeBuffSize):
            self.wl_pt.value = 0

    def terminate(self):
        self.stop_flag.set()
        self.process.join()
        self.smm.shutdown()
        print('Terminate grpc client')

    def set_connection(self, connection):

        pt = self.info_pt.value+1
        if(pt >= 2):
            pt = 0
        self.connection_info[pt].clear()
        for conn in connection:
            self.connection_info[pt][conn] = connection[conn].copy()
        self.info_pt.value = pt

    def map_data_to_topic(self, data_buff):
        try:
            topics_buffer = {}
            # print(data_buff)
            for d in data_buff:
                # print("d",d)
                topic = d.name
                data_type = d.type
                # if data_type not in ProtobufDataDict:
                #    print("error packages",d)
                #    continue
                data = ProtobufDataDict[data_type]()
                data.ParseFromString(d.data)
                if topic not in topics_buffer:
                    topics_buffer[topic] = []
                topics_buffer[topic].append(data)
            return topics_buffer
        except Exception as e:

            print("map data failed", data_buff)
            raise e

    def pull_receiver(self):
        connection_list = []
        connection_info = self.connection_info[self.info_pt.value]
        # print(connection_info)
        for topic in connection_info.keys():
            for info in connection_info[topic]:
                if not info["isOnline"]:
                    continue
                addr = "{}:{}".format(info["ip"], info["port"])
                conn = {}
                conn["topic_type"] = info["topic_type"]
                conn["client_mode"] = 1
                conn["src_topic"] = topic
                conn["dst_topic"] = info["topic_name"]
                message = []
                message.append(pubsub_pb2.RequestTopicData(node_id=self.node_id,
                                                           topic_name=info["topic_name"]))

                connection_list.append((addr, conn, message))
        self.update_conn_nock.clear()
        return connection_list

    def push_sender(self):
        connection_list = []
        connection_info = self.connection_info[self.info_pt.value]
        topics_buffer = self.map_data_to_topic(self.read_data())

        # if len(topics_buffer)>0:
        #    print("push data",topics_buffer.keys())
        for topic in connection_info.keys():
            if topic not in topics_buffer:
                continue
            # print("topics_buffer",topic,len(topics_buffer[topic]))

            for info in connection_info[topic]:
                # print("topic_info",topic,info)
                if not info["isOnline"]:
                    continue
                addr = "{}:{}".format(info["ip"], info["port"])
                conn = {}
                conn["topic_type"] = info["topic_type"]
                conn["client_mode"] = 0
                conn["src_topic"] = topic
                conn["dst_topic"] = info["topic_name"]
                messages = copy.deepcopy(topics_buffer[topic])
                # print("messages",messages)
                for message in messages:
                    message.topic_name = info["topic_name"]

                connection_list.append((addr, conn, messages))
        return connection_list

    def connect_rpcServer(self, connection_info):
        addr_list = []
        dst_topic_list = []

        for connection in connection_info:
            addr, conn = connection[0], connection[1]
            dst_topic = conn["dst_topic"]
            addr_list.append(addr)
            dst_topic_list.append(dst_topic)

            # create new stub when the new address appear.
            if addr not in self.connected_stub.keys():
                options = [('grpc.max_send_message_length', LargeDataSize), ('grpc.max_receive_message_length', LargeDataSize)]
                channel = grpc.insecure_channel(addr, options=options)
                stub = pubsub_pb2_grpc.PubSubServiceStub(channel)
                self.connected_stub[addr] = stub
            
            # new topic connection or existed topic connection reset
            if dst_topic not in self.topic_addr.keys() or addr != self.topic_addr[dst_topic]:
                self.topic_addr[dst_topic] = addr

    def remove_disconnect_stub(self):
        connection_info = self.connection_info[self.info_pt.value]
        addr_list = []
        dst_topic_list = []

        # get existing connection
        for topic in connection_info.keys():
            for info in connection_info[topic]:
                addr = "{}:{}".format(info["ip"], info["port"])
                dst_topic = info["topic_name"]
                addr_list.append(addr)
                dst_topic_list.append(dst_topic)

        # delete disconnected stub
        for topic in list(self.topic_addr.keys()):
            if topic not in dst_topic_list:
                print("delete disconnected topic", topic)
                del self.topic_addr[topic]

        for addr in list(self.connected_stub.keys()):
            if addr not in addr_list:
                print("delete disconnected addr", addr)
                del self.connected_stub[addr]
        

    def request(self, args):
        try:
            info, message = args[1], args[2]
            dst_topic = info["dst_topic"]

            addr = self.topic_addr[dst_topic]
            stub = self.connected_stub[addr]

            if info["client_mode"] == 1:
                responses = pull_request(stub, message, info["topic_type"])
            else:
                responses = push_request(stub, message, info["topic_type"])

            res_list = []
            for res in responses:
                if not res.data:
                    continue
                # print("rec delay time:", len(res.data), res.node_id,
                #       res.topic_name, res.topic_name, time.time()-res.timestamp/MICRO)
                res_list.append((info, res))
            # print(f'time:{time.time()} ,pid:{os.getpid()}, res"{res_list}')
            return res_list

        except Exception as e:
            print("request_th", e)
            return []

    def run(self):
        # calculate time
        average_time = 0
        # calculate fps
        self.prev_timestamp = 0
        print(f"[Success] gRPC Client process {self.node_id} is started.")

        self.start_time = time.time()
        count = 0
        try:
            while not self.stop_flag.wait(0):
                try:
                    if self.client_mode == 1:
                        connection_info = self.pull_receiver()
                    else:
                        connection_info = self.push_sender()

                    if connection_info:
                        self.connect_rpcServer(connection_info)

                    self.remove_disconnect_stub()

                    for connection in connection_info:
                        response = self.request(connection)
                        if response:
                            # print(response)
                            if self.client_mode == 1:
                                for info, res in response:
                                    # print("delay time:", len(
                                    #     res.data), res.node_id, res.topic_name, res.topic_name, time.time()-res.timestamp/MICRO)
                                    self.write_data(
                                        res, info['src_topic'], info["topic_type"])

                except Exception as e:
                    raise e
                    print("clientProcess run: ", e)
                    count += 1
                    cur_time = time.time()

                    if self.client_mode == 1:
                        print(
                            f"[pull error], [{self.node_id}], interval = {round(cur_time-self.start_time)}")
                    else:
                        print(
                            f"[push error], [{self.node_id}], interval = {round(cur_time-self.start_time)}")

                    self.start_time = cur_time
                    time.sleep(1)

        finally:
            print("terminating grpc client process")
