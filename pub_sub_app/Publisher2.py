# ============================================================
# import packages
# ============================================================
from flask import signals_available
from PubSubServiceServicer import PubSubServiceServicer
import time
import base64
import sys
import logging
import threading
import multiprocessing
import collections
import signal
import os

# ============================================================
# import grpc protobuf
# ============================================================
from concurrent import futures
import grpc
import node_pb2
import node_pb2_grpc
import pubsub_pb2
import pubsub_pb2_grpc
import ntp_pb2
import ntp_pb2_grpc
import interceptor

LITE = False
if LITE:
    from GRPC_ClientProcess_lite import GRPC_ClientProcess
    from GRPC_ServerProcess_lite import GRPC_ServerProcess
else:
    from GRPC_ClientProcess3 import GRPC_ClientProcess3 as GRPC_ClientProcess
    from GRPC_ServerProcess import GRPC_ServerProcess


ProtobufDataDict = {}
ProtobufDataDict['str'] = pubsub_pb2.StringData
ProtobufDataDict['bytes'] = pubsub_pb2.BytesData
ProtobufDataDict['int'] = pubsub_pb2.IntData
ProtobufDataDict['float'] = pubsub_pb2.FloatData
ProtobufDataDict['bool'] = pubsub_pb2.BoolData


def diff_dict(dict1, dict2):
    list1 = list(dict1.keys())
    list2 = list(dict2.keys())
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
        elif topic_config['mode'] == 0:
            if 'ip' not in topic_config:
                print('\'ip\' not in topic_config')
                exit(1)
            if 'port' not in topic_config:
                print('\'port\' not in topic_config')
                exit(1)
        else:
            update_timing = 0
            topic_config['ip'] = '0.0.0.0'
            topic_config['port'] = 0

        self.node = node
        self.publishment = {}
        for topic in topic_config['topic_info']:
            topicID = "{}:{}".format(node.node_id, topic)
            self.publishment[topicID] = topic_config['topic_info'][topic]

        self.topic_ip = topic_config['ip']
        self.topic_port = topic_config['port']
        self.topic_mode = topic_config['mode']
        if LITE:
            self.buffer_maxlen = 5
        else:
            self.buffer_maxlen = 20
        self.update_timing = update_timing

        # init buffer
        self.topics_buffer = {}
        self.topics_connected_nodes = {}
        self.pub_push_connection = {}
        self.connected_topic = {}

        # add topic to server
        self.publish_topic()

        # shared memory for add or delete topic
        self.topic_action_queue = multiprocessing.Queue()
        self.topic_status = multiprocessing.Manager().dict()

        # shared memory for connection info
        self.sm = multiprocessing.Manager()
        self.connection_info = self.sm.list()
        for i in range(2):
            self.connection_info.append(self.sm.dict())
        self.info_pt = self.sm.Value('i', 0)

        self.serverProcess = None

        if self.topic_mode == 0:
            self.serverProcess = GRPC_ServerProcess(
                self.node, self.topic_port, self.topics_buffer, 0)
        elif self.topic_mode == 1:
            self.clientProcess = GRPC_ClientProcess(self.node, 0)

        self.sub_stub = {}
        # self.stop_flag=threading.Event()
        self.stop_flag = multiprocessing.Event()
        if LITE:
            self.thread = threading.Thread(target=self.run)
        else:
            # self.thread = threading.Thread(target=self.run)
            self.thread = multiprocessing.Process(target=self.run)

        self.thread.start()

    def ResponseTopicInfosToDict(self, topics_info):
        res = {}
        for topic_info in topics_info:
            topic_ID = "{}:{}".format(
                topic_info.sub_node_id, topic_info.sub_topic_name)
            conn_info = {}
            conn_info['ip'] = topic_info.ip
            conn_info['port'] = topic_info.port
            res[topic_ID] = conn_info
        return res

    def get_sync_time(self):
        # return int(time.time() * MICRO + self.node.delay)
        return int(time.time() * MICRO)

##################################################
# TOPIC OPERATION
##################################################

    # init topic
    def publish_topic(self):
        for topic_name, topic_type in self.publishment.items():
            self._add_topic_to_buffer(topic_name, topic_type)

    def add_topic(self, topic_name, topic_type):
        if self.topic_mode == 0:
            print("Add topic in publisher mode'0' not support currently!")
            return

        topic_name = self.node.node_id + ":" + topic_name
        action = {
            "action": "add_topic",
            "topic_type": topic_type,
            "topic_name": topic_name
        }
        self.topic_action_queue.put(action)
        self._add_topic_to_buffer(topic_name, topic_type)

        while True:
            if topic_name in self.topic_status.keys():
                print("add topic success")
                break

    def delete_topic(self, topic_name, topic_type):

        topic_name = self.node.node_id + ":" + topic_name
        action = {
            "action": "delete_topic",
            "topic_name": topic_name,
            "topic_type": topic_type
        }
        self.topic_action_queue.put(action)
        self._delete_topic_from_buffer(topic_name)
        del self.topic_status[topic_name]

    def _add_topic_to_buffer(self, topic_name, topic_type):
        self.publishment[topic_name] = topic_type
        self.topics_buffer[topic_name] = collections.deque(
            maxlen=self.buffer_maxlen)
        self.topics_connected_nodes[topic_name] = []
        self.pub_push_connection[topic_name] = []
        self.connected_topic[topic_name] = []

    def _delete_topic_from_buffer(self, topic_name):
        self.publishment.pop(topic_name)
        self.topics_buffer.pop(topic_name)
        self.topics_connected_nodes.pop(topic_name)
        self.pub_push_connection.pop(topic_name)
        self.connected_topic.pop(topic_name)

    # add new topic to buffer or delete topic regularly
    def _check_topic_action(self, server_stub):
        if not self.topic_action_queue.empty():
            topic = self.topic_action_queue.get()

            if topic["action"] == "add_topic":
                self._add_topic_to_buffer(
                    topic["topic_name"], topic["topic_type"])
            else:
                Topic = node_pb2.Topic(
                    topic_name=topic["topic_name"], topic_type=topic["topic_type"], node_id=self.node.node_id)
                server_stub.DeleteTopic(Topic)
                self._delete_topic_from_buffer(topic["topic_name"])

    # update or add topic from buffer regularly
    def _update_publishment(self, server_stub):
        try:
            for topic_name, topic_type in self.publishment.items():
                # create topic buffer
                # add topic to server
                topic = node_pb2.TopicInfo(topic_name=topic_name,
                                           topic_type=topic_type,
                                           mode=self.topic_mode,
                                           ip=self.topic_ip,
                                           port=self.topic_port,
                                           node_id=self.node.node_id,
                                           node_domain=self.node.node_domain)
                topic.connected_nodes.extend(self.connected_topic[topic_name])
                responses = server_stub.AddTopic(topic)
                self.topic_status[topic_name] = True
        except Exception as e:
            print("publish_topic", e)

    # not used
    def update_topic_status(self, server_stub):
        try:
            for topic_name in self.topics_connected_nodes:
                topic_status = node_pb2.TopicStatus(
                    topic_name=topic_name, node_id=self.node.node_id)
                topic_status.connected_nodes.extend(
                    self.topics_connected_nodes[topic_name])
                responses = server_stub.UpdateTopicStatus(topic_status)
                self.topics_connected_nodes[topic_name].clear()
        except Exception as e:
            print(e)

##################################################
# CONNECTION OPERATION
##################################################

    def has_connection(self, pub_topic_name, sub_topic_name):
        connection_info = self.connection_info[self.info_pt.value]
        if pub_topic_name in connection_info:
            if sub_topic_name in [conn["topic_name"] for conn in connection_info[pub_topic_name]]:
                return True

        return False

    def set_connection(self, connections):
        pt = self.info_pt.value+1
        if(pt >= 2):
            pt = 0
        self.connection_info[pt].clear()
        for conn in connections:
            self.connection_info[pt][conn] = connections[conn].copy()
        self.info_pt.value = pt

    def add_connection(self, **args):

        ConnectionInfo = node_pb2.ConnectionInfo(
            pub_node_id=args["pub_node_id"],
            sub_node_id=args["sub_node_id"],
            pub_topic_name=args["pub_topic_name"],
            sub_topic_name=args["sub_topic_name"],
            topic_type=args["topic_type"]
        )

        try:
            with grpc.insecure_channel('{}:{}'.format(self.node.server_ip, self.node.server_port)) as channel:
                server_stub = node_pb2_grpc.ControlStub(channel)
                response = server_stub.AddConnection(ConnectionInfo)

                connection_id = response.connection_id
                print(f"added ConnectionID = {connection_id}.")

                return connection_id

        except grpc.RpcError as e:
            print(e.details())
            return "-1"

    def delete_connection(self, connection_id):
        ConnectionID = node_pb2.ConnectionID(connection_id=connection_id)

        with grpc.insecure_channel('{}:{}'.format(self.node.server_ip, self.node.server_port)) as channel:
            server_stub = node_pb2_grpc.ControlStub(channel)
            response = server_stub.DeleteConnection(ConnectionID)
            print(f"connection_id = {connection_id} is deleted!")

    def _get_connection(self, server_stub):
        try:
            # update node status (alive)
            request_connection = node_pb2.RequestConnection(
                node_id=self.node.node_id, isSubscriber=False)
            responses = server_stub.GetConnection(request_connection)

            for topic in self.pub_push_connection:
                self.topics_buffer[topic] = collections.deque(
                    maxlen=self.buffer_maxlen)
                self.pub_push_connection[topic] = []
                self.connected_topic[topic] = []
            # connection information

            for topic_info in responses.topics_info:
                if topic_info.pub_topic_name not in self.publishment:
                    continue
                pub_name = topic_info.pub_topic_name
                topicID = "{}:{}".format(
                    topic_info.sub_node_id, topic_info.sub_topic_name)

                if topicID not in self.connected_topic[pub_name]:
                    self.connected_topic[pub_name].append(topicID)
                if topic_info.mode == 1:
                    info = {}
                    info["topic_node"] = topic_info.sub_node_id
                    info["topic_name"] = topic_info.sub_topic_name
                    info["topic_type"] = topic_info.topic_type
                    info["isOnline"] = topic_info.isOnline
                    info["ip"] = topic_info.ip
                    info["port"] = topic_info.port
                    self.pub_push_connection[pub_name].append(info)
            # print("get_connection",self.pub_push_connection)

            self.clientProcess.set_connection(self.pub_push_connection)
            self.set_connection(self.pub_push_connection)

        except Exception as e:
            raise e
            print('Publisher (get_connection) Exception: {}'.format(e))
            time.sleep(1)

    # write data to topic
    def data_writer(self, topic_name, topic_data):
        topic_name = "{}:{}".format(self.node.node_id, topic_name)
        # print("topic_name",topic_name)
        data_type = self.publishment[topic_name]

        proto_data = ProtobufDataDict[data_type](
            node_id=self.node.node_id,
            topic_name=topic_name,
            data=topic_data,
            timestamp=self.get_sync_time()
        )
        if self.topic_mode == 0:
            self.serverProcess.write_data(proto_data, topic_name, data_type)
        else:
            self.clientProcess.write_data(proto_data, topic_name, data_type)
        #self.topics_buffer[topic_name].append([topic_data, self.get_sync_time()])

    def terminate(self):
        try:
            print("terminating publisher")
            if self.serverProcess is not None:
                self.serverProcess.terminate()
            self.stop_flag.set()
            self.thread.join()
        except Exception as e:
            print("terminate publisher failed", e)

    def run(self):
        print(f"Publisher {self.node.node_id} started!")

        try:
            with grpc.insecure_channel('{}:{}'.format(self.node.server_ip, self.node.server_port)) as channel:
                server_stub = node_pb2_grpc.ControlStub(channel)
                ntp_stub = ntp_pb2_grpc.NtpStub(channel)

                while not self.stop_flag.wait(1):
                    self.node.update_node_status(server_stub)
                    self.node.ntp_sync(ntp_stub)
                    self._check_topic_action(server_stub)
                    self._update_publishment(server_stub)
                    if self.topic_mode == 1:
                        self._get_connection(server_stub)
                    # time.sleep(0.001)

        except Exception as e:
            #raise e
            print('GRPC_ClientProcess (run) Exception: {}'.format(e))
            time.sleep(1)
        else:
            pass

        print("Publisher terminated")

    def __del__(self):
        self.terminate()
