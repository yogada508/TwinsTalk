from http import client
import sys
sys.path.append("..")
import time
import cv2
import base64
import numpy as np
import random
from pub_sub_app import node_api2 as node_api
from pub_sub_app import Subscriber2 as Subscriber
from pub_sub_app import Publisher2 as Publisher
from multiprocessing import Process, Manager
import threading
import argparse
#============================================================
# for IOT connection
#============================================================
from UPDRS import hand_movement

ServerURL = 'http://140.113.193.15:9999'


def publish(client_data):
    node_config = {
        'server_ip': '140.113.193.15',
        'server_port': 55555,
        'node_id': 'sub/server/mediapipe',
        'node_name': "sub/server/mediapipe",
        'node_domain': 'Domain1',
    }
    topic_config = {
        'topic_info': {
            'Skeleton': 'str',
        },
        'mode':0, # 0:server mode 1:client mode
        'ip': '140.113.28.159',
        'port': 54321
    }
    node = node_api.Node(node_config)
    pub = Publisher.Publisher(node, topic_config)
    time.sleep(7)

    while True:
        if client_data:
            for node in list(client_data.keys()):
                if "VideoName" in client_data[node] and "VideoFile" in client_data[node]:
                    print(node, len(client_data[node]["VideoFile"]))

                    # save video
                    f = open("./client_video/" + str(node) + ":" +  client_data[node]["VideoName"],"wb")
                    f.write(client_data[node]["VideoFile"])
                    f.close()

                    # run UPDRS hand_movement
                    result = hand_movement.demo("./client_video/" + str(node) + ":" + client_data[node]["VideoName"])
                    pub.data_writer('Skeleton',str(result))
                    del client_data[node]

def subscribe(client_data):
    node_config = {
        'server_ip': '140.113.193.15',
        'server_port': 55555,
        'node_id': 'sub/server/mediapipe',
        'node_name': "sub/server/mediapipe",
        'node_domain': 'Domain1',
    }
    subscription ={
    'video_name': 'str',
    'video_data' : 'bytes'
    } 

    sub_topic_config = {
        'mode':0, # 0:server mode 1:client mode
        'topic_info':subscription,
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
                print(video_name)
                # if video_name.node_id not in client_data:
                #     client_data[video_name.node_id] = manager.dict()
                # client_data[video_name.node_id]["VideoName"] = video_name.data
            
            file_data = sub.read_topic('video_data')
            if file_data is not None:
                print(f'node_id: {file_data.node_id}\ntopic_name: {file_data.topic_name}\ndata: {len(file_data.data)}\ntimestamp: {file_data.timestamp}')
                # if file_data.node_id not in client_data:
                #     client_data[file_data.node_id] = manager.dict()
                # client_data[file_data.node_id]["VideoFile"] = file_data.data

        except Exception as e:
            sub.terminate()
            raise e


if __name__ == "__main__":
    manager = Manager()
    d = manager.dict()

    sub_process = Process(target=subscribe, args=(d,))
    # pub_process = Process(target=publish, args=(d,))
    # pub_process.start()
    sub_process.start()

    sub_process.join()
    # pub_process.join()

    
    print("server terminate")