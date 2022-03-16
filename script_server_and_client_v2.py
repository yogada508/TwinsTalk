'''
For "test_config.json"
start the following server:

1. UPDRS client (pub/sub node)
2. Mediapipe server (pub/sub node)
'''

import time
from pub_sub_app import node_api2 as node_api
from pub_sub_app import Publisher2 as Publisher
from pub_sub_app import Subscriber2 as Subscriber
from pub_sub_platform.utils import image_utils
import threading
import multiprocessing
import grpc

pub_nodes = [
    # {
    #     "node_config": {
    #         'server_ip': '140.113.28.158',
    #         'server_port': 55555,
    #         'node_id': "pub/server/annotation",
    #         'node_name': "pub/server/annotation",
    #         'node_domain': 'Domain1',
    #     },
    #     "topic_config": {
    #         "topic_info": {
    #             "annotated_video": "bytes",
    #         },
    #         "mode": 1,
    #         "ip": "127.0.0.1",
    #         "port": 52222
    #     }
    # },
    # {
    #     "node_config": {
    #         'server_ip': '140.113.28.158',
    #         'server_port': 55555,
    #         'node_id': "pub/server/calculation",
    #         'node_name': "pub/server/calculation",
    #         'node_domain': 'Domain1',
    #     },
    #     "topic_config": {
    #         "topic_info": {
    #             "action_count": "int",
    #             "frequency": "float"
    #         },
    #         "mode": 1,
    #         "ip": "127.0.0.1",
    #         "port": 50003
    #     }
    # },
    {
        "node_config": {
            'server_ip': '140.113.28.158',
            'server_port': 55555,
            'node_id': "pub/client/01.UPDRS_client",
            'node_name': "pub/client/01.UPDRS_client",
            'node_domain': 'Domain1',
        },
        "topic_config": {
            "topic_info": {
                "video_name": "str",
                "video_data": "bytes"
            },
            "mode": 1,
            "ip": "127.0.0.1",
            "port": 50001
        }
    },
    {
        "node_config": {
            'server_ip': '140.113.28.158',
            'server_port': 55555,
            'node_id': "pub/server/mediapipe",
            'node_name': "pub/server/mediapipe",
            'node_domain': 'Domain1',
        },
        "topic_config": {
            "topic_info": {
                "annotation": "bytes"
            },
            "mode": 1,
            "ip": "127.0.0.1",
            "port": 50002
        }
    },
]

sub_nodes = [
    # {
    #     "node_config": {
    #         'server_ip': '140.113.28.158',
    #         'server_port': 55555,
    #         'node_id': "sub/server/annotation",
    #         'node_name': "sub/server/annotation",
    #         'node_domain': 'Domain1',
    #     },
    #     "topic_config": {
    #         "topic_info": {
    #             "annotation": "bytes",
    #             "video_data": "bytes"
    #         },
    #         "mode": 1,
    #         "ip": "127.0.0.1",
    #         "port": 52223
    #     }
    # },
    # {
    #     "node_config": {
    #         'server_ip': '140.113.28.158',
    #         'server_port': 55555,
    #         'node_id': "sub/server/calculation",
    #         'node_name': "sub/server/calculation",
    #         'node_domain': 'Domain1',
    #     },
    #     "topic_config": {
    #         "topic_info": {
    #             "annotation": "bytes"
    #         },
    #         "mode": 1,
    #         "ip": "127.0.0.1",
    #         "port": 50006
    #     }
    # },
    {
        "node_config": {
            'server_ip': '140.113.28.158',
            'server_port': 55555,
            'node_id': "sub/client/01.UPDRS_client",
            'node_name': "sub/client/01.UPDRS_client",
            'node_domain': 'Domain1',
        },
        "topic_config": {
            "topic_info": {
                "frequency": "float",
                "action_count": "int",
                "annotated_video": "bytes"
            },
            "mode": 1,
            "ip": "127.0.0.1",
            "port": 50004
        }
    },
    {
        "node_config": {
            'server_ip': '140.113.28.158',
            'server_port': 55555,
            'node_id': "sub/server/mediapipe",
            'node_name': "sub/server/mediapipe",
            'node_domain': 'Domain1',
        },
        "topic_config": {
            "topic_info": {
                "video_name": "str",
                "video_data": "bytes"
            },
            "mode": 1,
            "ip": "127.0.0.1",
            "port": 50005
        }
    },
]

def run_pub(stop_flag, pub_config):
    node = node_api.Node(pub_config["node_config"])
    pub = Publisher.Publisher(node, pub_config["topic_config"])

    try:
        while not stop_flag.wait(1):
            pass

    except Exception as e:
        print(e)

def run_sub(stop_flag, sub_config):
    node = node_api.Node(sub_config["node_config"])
    sub = Subscriber.Subscriber(node, sub_config["topic_config"])

    try:
        while not stop_flag.wait(1):
            pass
            
    except Exception as e:
        print(e)

        
def main():
    pub_ths = []
    sub_ths = []
    # stop_flag = threading.Event()
    stop_flag = multiprocessing.Event()

    for pub_config in pub_nodes:
        # th = threading.Thread(target=run_pub, args=(stop_flag, pub_config))
        th = multiprocessing.Process(target=run_pub, args=(stop_flag, pub_config))
        pub_ths.append(th)
    
    for sub_config in sub_nodes:
        # th = threading.Thread(target=run_sub, args=(stop_flag, sub_config))
        th = multiprocessing.Process(target=run_sub, args=(stop_flag, sub_config))
        sub_ths.append(th)
    
    for th in pub_ths+sub_ths:
        th.start()
    
    try:
        while True:
            time.sleep(1)
    finally:
        for pub in pubs:
            pub.terminate()
        for sub in subs:
            sub.terminate()
    
    

if __name__ == '__main__':
    main()

    