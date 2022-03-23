import time
from pub_sub_app import node_api2 as node_api
from pub_sub_app import Publisher2 as Publisher
from pub_sub_app import Subscriber2 as Subscriber
import threading
from multiprocessing import Process, Manager
import grpc

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

    while True:
        print(f'data:{str(i)}, send time: {time.time()}')  
        pub.data_writer("video_name", str(i))
        i+=1

        time.sleep(2)
        

if __name__ == "__main__":
    main()