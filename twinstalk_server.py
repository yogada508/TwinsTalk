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

def slave_service(data, pub_queue):
    client_id = data["client_id"]
    client_name = (client_id.split("/"))[-1]
    client_data = data["client_data"]
    result_data = {
        "annotation": client_data["videoName"] + "_result"
    }

    result = {
        "client_name": client_name,
        "result_data": result_data
    }

    pub_queue.put(result)


def start_subscriber(config, sub_queue):
    sub_node = node_api.Node(config["node_config"])
    sub = Subscriber.Subscriber(sub_node, config["topic_config"])
    time.sleep(3)

    data_buffer = {}
    while True:
        try:
            sub.updata_data()

            topics = list(config["topic_config"]["topic_info"].keys())
            for topic in topics:
                info = sub.read_topic(topic)

                if info is not None:
                    if info.node_id not in data_buffer:
                        data_buffer[info.node_id] = manager.dict()
                    data_buffer[info.node_id][topic] = info.data

            # check client's datas are ready
            for node_id in list(data_buffer.keys()):
                if set(topics) == set(data_buffer[node_id].keys()):
                    data = {
                        "client_id": node_id,
                        "client_data": data_buffer[node_id]
                    }
                    sub_queue.put(data)
                    del data_buffer[node_id]

        except Exception as e:
            sub.terminate()
            raise e


def start_publisher(config, pub_queue):
    pub_node = node_api.Node(config["node_config"])
    pub = Publisher.Publisher(pub_node, config["topic_config"])
    topic_dict = config["topic_config"]["topic_info"]
    time.sleep(5)

    while True:
        data = pub_queue.get()
        client_name = data["client_name"]

        for topic in list(data["result_data"].keys()):
            client_topic = f"{client_name}_{topic}"
            result = data["result_data"][topic]

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
                pub.data_writer(client_topic, result)
            


def start_service(pub_config, sub_config, sub_queue, pub_queue):
    sub_topic_dict = sub_config["topic_config"]["topic_info"]
    pub_topic_dict = pub_config["topic_config"]["topic_info"]

    while True:
        data = sub_queue.get()
        slave = Process(target=slave_service, args=(data, pub_queue))
        slave.daemon = True
        slave.start()



class TwinsTalk_Server():
    def __init__(self, config):
        self.pub_config = config["pub_config"]
        self.sub_config = config["sub_config"]

    def run(self):
        # manager = Manager()
        sub_queue = manager.Queue()
        pub_queue = manager.Queue()

        sub_process = Process(target=start_subscriber,
                              args=(self.sub_config, sub_queue,))
        pub_process = Process(target=start_publisher,
                              args=(self.pub_config, pub_queue,))
        service_process = Process(target=start_service, args=(
            self.pub_config, self.sub_config, sub_queue, pub_queue))

        sub_process.start()
        service_process.start()
        pub_process.start()

        sub_process.join()
        service_process.join()
        pub_process.join()
