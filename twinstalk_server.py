'''
TwinsTalk Server
'''

from pub_sub_app import node_api2 as node_api
from pub_sub_app import Publisher2 as Publisher
from pub_sub_app import Subscriber2 as Subscriber
from multiprocessing import Process, Manager
import threading
import time
import json
import sys

manager = Manager()


def start_subscriber(config, buffer):
    sub_node = node_api.Node(config["node_config"])
    sub = Subscriber.Subscriber(sub_node, config["topic_config"])
    time.sleep(3)

    while True:
        try:
            sub.updata_data()

            topics = list(config["topic_config"]["topic_info"].keys())
            for topic in topics:
                info = sub.read_topic(topic)

                if info is not None:
                    if info.node_id not in buffer:
                        buffer[info.node_id] = manager.dict()
                    buffer[info.node_id][topic] = info.data

        except Exception as e:
            sub.terminate()
            raise e


def start_publisher(config, buffer):
    pub_node = node_api.Node(config["node_config"])
    pub = Publisher.Publisher(pub_node, config["topic_config"])
    topic_dict = config["topic_config"]["topic_info"]
    time.sleep(5)

    while True:
        # if not buffer: continue

        del_node_list = []
        for node_id in list(buffer.keys()):
            if set(topic_dict.keys()) != set(buffer[node_id].keys()):
                continue

            # del_topic_list = []
            for topic in list(buffer[node_id].keys()):
                client_name = (node_id.split("/"))[-1]
                client_topic = f"{client_name}_{topic}"

                pub.add_topic(client_topic, topic_dict[topic])

                pub_topic_name = f"{config['node_config']['node_id']}:{client_topic}"
                sub_topic_name = f"sub/agent/{client_name}:{topic}_I"
                connection_id = pub.add_connection(
                    pub_node_id=config['node_config']['node_id'],
                    sub_node_id=f"sub/agent/{client_name}",
                    pub_topic_name=pub_topic_name,
                    sub_topic_name=sub_topic_name,
                    topic_type=topic_dict[topic]
                )

                if connection_id != "-1":
                    pub.data_writer(client_topic, buffer[node_id][topic])
                    # del_topic_list.append(topic)

            # delete topic in buffer
            # for d in del_topic_list:
            #     if d in buffer[node_id]:
            #         del buffer[node_id][d]
            # print(del_topic_list)
            # print(buffer)
            # if len(buffer[node_id].keys()) == 0:
            del_node_list.append(node_id)

        # delete node in buffer
        for d in del_node_list:
            if d in buffer:
                del buffer[d]


def start_service(pub_config, sub_config, buffer1, buffer2):
    sub_topic_dict = sub_config["topic_config"]["topic_info"]
    pub_topic_dict = pub_config["topic_config"]["topic_info"]

    while True:
        del_node_list = []
        for node_id in list(buffer1.keys()):
            if set(buffer1[node_id].keys()) != set(sub_topic_dict.keys()):
                continue

            # ==================================
            # Data processing...
            # buffer1[node_id] --> get args
            result = {
                "annotation": "I got annoatation result!!"
            }
            # ==================================

            if set(result.keys()) != set(pub_topic_dict.keys()):
                print("Service result key not match.")
                continue

            if node_id not in buffer2:
                buffer2[node_id] = manager.dict()
            buffer2[node_id] = result

            del_node_list.append(node_id)

        for d in del_node_list:
            if d in buffer1:
                del buffer1[d]


class TwinsTalk_Server():
    def __init__(self, config):
        self.pub_config = config["pub_config"]
        self.sub_config = config["sub_config"]

    def run(self):
        # manager = Manager()
        buffer1 = manager.dict()
        buffer2 = manager.dict()

        sub_process = Process(target=start_subscriber,
                              args=(self.sub_config, buffer1,))
        pub_process = Process(target=start_publisher,
                              args=(self.pub_config, buffer2,))
        service_process = Process(target=start_service, args=(
            self.pub_config, self.sub_config, buffer1, buffer2))

        sub_process.start()
        service_process.start()
        pub_process.start()

        sub_process.join()
        service_process.join()
        pub_process.join()
