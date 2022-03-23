from asyncio.subprocess import Process
import sys
sys.path.append('..')
from pub_sub_app import node_api2 as node_api
from pub_sub_app import Publisher2 as Publisher
from pub_sub_app import Subscriber2 as Subscriber
import cv2
import numpy as np
import json
import time
from multiprocessing import Process
import threading
import argparse
#============================================================
# for IOT connection
#============================================================

def subscribe():
    node_config = {
        'server_ip': '140.113.193.15',
        'server_port': 55555,
        'node_id': 'pub/client/01.UPDRS_client',
        'node_name': "pub/client/01.UPDRS_client",
        'node_domain': 'Domain1',
    }
    subscription ={
        'Skeleton_ODF': 'str',
    } 

    sub_topic_config = {
        'mode':1, # 0:server mode 1:client mode
        'subscription':subscription,
        'ip': '140.113.28.159',
        'port': 12300
    }
    node = node_api.Node(node_config)
    sub = Subscriber.Subscriber(node, sub_topic_config)
    time.sleep(5)

    while True:
        sub.updata_data()
        skeleton = sub.read_topic('Skeleton_ODF')
        if skeleton is not None:
            print(skeleton)
            print("receive time: ", time.time())  
            #break
    
    sub.terminate()

def main():
    node_config = {
        'server_ip': '140.113.193.15',
        'server_port': 55555,
        'node_id': 'pub/client/01.UPDRS_client',
        'node_name': "pub/client/01.UPDRS_client",
        'node_domain': 'Domain1',
    }

    topic_config = {
        'topic_info': {
            'video_name': 'str',
            'video_data' : 'bytes'
        },
        'mode':1, # 0:server mode 1:client mode
        'ip': '0.0.0.0',
        'port': 0
    }
    node = node_api.Node(node_config)
    pub = Publisher.Publisher(node, topic_config)
    time.sleep(10)

    i = 0
    file = open("two-hands_edited.mp4","rb")
    data = file.read()

    while(1):
        print("send time: ", time.time())  
        pub.data_writer('video_name',"two-hands_edited.mp4")
        pub.data_writer('video_data', data)
            
        print("end, len of file", len(data))
        time.sleep(15)

if __name__ == "__main__":
    #sub_thread = Process(target=subscribe)
    #sub_thread.start()
    main()
    #sub_thread.join()

    print("client terminate")