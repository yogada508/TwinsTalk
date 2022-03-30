from UPDRS import hand_movement
import argparse
import threading
from multiprocessing import Process, Manager
from pub_sub_app import node_api2 as node_api
from pub_sub_app import Publisher2 as Publisher
from pub_sub_app import Subscriber2 as Subscriber
import random
import numpy as np
import base64
import cv2
import time
from http import client
import sys
# ============================================================
# for IOT connection
# ============================================================

ServerURL = 'http://140.113.193.15:9999'


def publish(client_data):
    node_config = {
        'server_ip': '140.113.193.15',
        'server_port': 55555,
        'node_id': 'pub/server/mediapipe',
        'node_name': "pub/server/mediapipe",
        'node_domain': 'Domain1',
    }
    topic_config = {
        'topic_info': {
            'Skeleton': 'str',
        },
        'mode': 1,  # 0:server mode 1:client mode
        'ip': '140.113.28.159',
        'port': 54321
    }
    node = node_api.Node(node_config)
    pub = Publisher.Publisher(node, topic_config)
    time.sleep(5)

    while True:
        if client_data:
            for node in list(client_data.keys()):
                if "VideoName" in client_data[node] and "VideoFile" in client_data[node]:
                    print(node, len(client_data[node]["VideoFile"]))
                    parsed_node = node.split("/")
                    client_name = parsed_node[-1]

                    # save video
                    f = open("./client_video/" + client_name + ":" +
                             client_data[node]["VideoName"], "wb")
                    f.write(client_data[node]["VideoFile"])
                    f.close()

                    # run UPDRS hand_movement
                    # result = hand_movement.demo(
                    #     "./client_video/" + client_name + ":" + client_data[node]["VideoName"])

                    result = "123"

                    # add topic and build connection
                    pub.add_topic(f'{client_name}_annotation', 'str')
                    pub.add_connection(
                        pub_node_id="pub/server/mediapipe",
                        sub_node_id=f'sub/{parsed_node[1]}/{parsed_node[2]}',
                        pub_topic_name=f'pub/server/mediapipe:{client_name}_annotation',
                        sub_topic_name=f'sub/{parsed_node[1]}/{parsed_node[2]}:annotation_I',
                        topic_type="str"
                    )
                    time.sleep(10)
                    pub.data_writer(f'{client_name}_annotation', str(result))
                    del client_data[node]


def subscribe(client_data):
    node_config = {
        'server_ip': '140.113.193.15',
        'server_port': 55555,
        'node_id': 'sub/server/mediapipe',
        'node_name': "sub/server/mediapipe",
        'node_domain': 'Domain1',
    }
    subscription = {
        'video_name': 'str',
        'video_data': 'bytes'
    }

    sub_topic_config = {
        'mode': 0,  # 0:server mode 1:client mode
        'topic_info': subscription,
        'ip': '140.113.28.159',
        'port': 12345
    }

    node = node_api.Node(node_config)
    sub = Subscriber.Subscriber(node, sub_topic_config)

    while True:
        try:
            sub.updata_data()
            video_name = sub.read_topic('video_name')
            if video_name is not None:
                if video_name.node_id not in client_data:
                    client_data[video_name.node_id] = manager.dict()
                client_data[video_name.node_id]["VideoName"] = video_name.data

            file_data = sub.read_topic('video_data')
            if file_data is not None:
                if file_data.node_id not in client_data:
                    client_data[file_data.node_id] = manager.dict()
                client_data[file_data.node_id]["VideoFile"] = file_data.data

        except Exception as e:
            sub.terminate()
            raise e


if __name__ == "__main__":
    manager = Manager()
    d = manager.dict()

    sub_process = Process(target=subscribe, args=(d,))
    pub_process = Process(target=publish, args=(d,))
    pub_process.start()
    sub_process.start()

    sub_process.join()
    pub_process.join()

    print("server terminate")
