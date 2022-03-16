'''
start the following server:

1. Annotation server (pub/sub node)
2. Calculation server (pub/sub node)
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
            'node_id': "pub/server/annotation",
            'node_name': "pub/server/annotation",
            'node_domain': 'Domain1',
        },
        "topic_config": {
            "topic_info": {
                "annotated_video": "bytes",
            },
            "mode": 1,
            "ip": "127.0.0.1",
            "port": 52222
        }
    },
    {
        "node_config": {
            'server_ip': '140.113.28.158',
            'server_port': 55555,
            'node_id': "pub/server/calculation",
            'node_name': "pub/server/calculation",
            'node_domain': 'Domain1',
        },
        "topic_config": {
            "topic_info": {
                "action_count": "int",
                "frequency": "float"
            },
            "mode": 1,
            "ip": "127.0.0.1",
            "port": 50003
        }
    }
]

sub_nodes = [
    {
        "node_config": {
            'server_ip': '140.113.28.158',
            'server_port': 55555,
            'node_id': "sub/server/annotation",
            'node_name': "sub/server/annotation",
            'node_domain': 'Domain1',
        },
        "topic_config": {
            "topic_info": {
                "annotation": "bytes",
                "video_data": "bytes"
            },
            "mode": 1,
            "ip": "127.0.0.1",
            "port": 52223
        }
    },
    {
        "node_config": {
            'server_ip': '140.113.28.158',
            'server_port': 55555,
            'node_id': "sub/server/calculation",
            'node_name': "sub/server/calculation",
            'node_domain': 'Domain1',
        },
        "topic_config": {
            "topic_info": {
                "annotation": "bytes"
            },
            "mode": 1,
            "ip": "127.0.0.1",
            "port": 50006
        }
    }
]

        
def main():
    pubs = []
    subs = []

    for pub_config in pub_nodes:
        node = node_api.Node(pub_config["node_config"])
        pub = Publisher.Publisher(node, pub_config["topic_config"])
        pubs.append(pub)
    
    for sub_config in sub_nodes:
        node = node_api.Node(sub_config["node_config"])
        sub = Subscriber.Subscriber(node, sub_config["topic_config"])
        subs.append(sub)
    
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

    