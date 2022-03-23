import time
from pub_sub_app import node_api2 as node_api
from pub_sub_app import Publisher2 as Publisher
from pub_sub_app import Subscriber2 as Subscriber
import threading
from multiprocessing import Process, Manager
import grpc

def subscribe():
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
            
            file_data = sub.read_topic('video_data')
            if file_data is not None:
                print(file_data)

        except Exception as e:
            sub.terminate()
            raise e

if __name__ == '__main__':
    subscribe()
