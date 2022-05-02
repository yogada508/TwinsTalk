from twinstalk_server import TwinsTalk_Server

CONTROLLER_IP = "140.113.193.15"
CONTROLLER_PORT = 55555

SERVER_IP = "140.113.28.159"
PUB_PORT = 54321
SUB_PORT = 12345

pub_config = {
    "node_config": {
        "server_ip": CONTROLLER_IP,
        "server_port": CONTROLLER_PORT,
        "node_id": "pub/server/mediapipe",
        "node_name": "pub/server/mediapipe",
        "node_domain": "domain1"
    },
    "topic_config": {
        "mode": 1,
        "ip": SERVER_IP,
        "port": PUB_PORT,
        "topic_info": {
            "annotation": "str"
        }
    }
}

sub_config = {
    "node_config": {
        "server_ip": CONTROLLER_IP,
        "server_port": CONTROLLER_PORT,
        "node_id": "sub/server/mediapipe",
        "node_name": "sub/server/mediapipe",
        "node_domain": "domain1"
    },
    "topic_config": {
        "mode": 0,
        "ip": SERVER_IP,
        "port": SUB_PORT,
        "topic_info": {
            "videoName": "str",
            "videoData": "bytes",
        }
    }
}

config = {
    "pub_config": pub_config,
    "sub_config": sub_config
}



def main():
    tt_server = TwinsTalk_Server(config)
    tt_server.run()


if __name__ == '__main__':
    main()