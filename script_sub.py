import time
from pub_sub_app import node_api2 as node_api
from pub_sub_app import Subscriber2 as Subscriber
import threading

node_config = {
    'server_ip': '127.0.0.1',
    'server_port': 55555,
    'node_id': "sub/0",
    'node_name': "sub/0",
    'node_domain': 'Domain1',
}

subscription ={
    'room1': 'str',
    'room2': 'float',
    'annotation': 'bytes'
} 

sub_topic_config = {
    'mode':1, # 0:server mode 1:client mode
    'topic_info':subscription,
    'ip': '127.0.0.1',
    'port': 50052
}


def main():
    node = node_api.Node(node_config)
    sub = Subscriber.Subscriber(node, sub_topic_config)
    # result=[]

    try:
        # new_topic = node_config["node_id"] + ":" + "hellohello"
        # sub.add_subscribe_topic(new_topic, "float")
        # print("topic added!")
        # time.sleep(20)
        # sub.delete_subscribe_topic(new_topic, "float")
        # print("topic deleted!")
    
        while True:
            try:
                sub.updata_data()
                frame_data = sub.read_topic('annotation')
                #print(threading.current_thread().name,frame_data)
                if(frame_data is not None):
                    print("get data",frame_data.data.__sizeof__(),frame_data.node_id,time.time()-frame_data.timestamp/1000000)
                    # print("get data!")
                    #result.append(frame_data.data)
                    pass
                time.sleep(1)
            except Exception as e:
                raise e
                print("main",e)
    finally:
        #sub.terminate()
        print("received",len(result))
if __name__ == "__main__":

    main()
