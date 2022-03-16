'''
start the following server:
1. Mediapipe server (pub/sub node)

start the following node:
1. client node (pub/sub node)
'''

import time
from pub_sub_app import node_api2 as node_api
from pub_sub_app import Publisher2 as Publisher
from pub_sub_app import Subscriber2 as Subscriber
from pub_sub_platform.utils import image_utils
import threading
import grpc

pub_nodes = [
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

        
def main():
    pubs = []
    subs = []

    for pub_config in pub_nodes:
        node = node_api.Node(pub_config["node_config"])
        pub = Publisher.Publisher(node, pub_config["topic_config"])
        pubs.append(pub)
        time.sleep(5)
    
    for sub_config in sub_nodes:
        node = node_api.Node(sub_config["node_config"])
        sub = Subscriber.Subscriber(node, sub_config["topic_config"])
        subs.append(sub)
        time.sleep(5)
    
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

    