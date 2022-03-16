from pub_sub_app import node_api2 as node_api
from pub_sub_app import Publisher2 as Publisher
import time
import cv2
import threading
from pub_sub_platform.utils import image_utils


def main(stop_flag,node_config,topic_config):
    node = node_api.Node(node_config)
    pub = Publisher.Publisher(node, topic_config)
    ID=(node_config['node_id'].split('/'))[-1]
    i=0
    img = cv2.imread("hd.jpg")
    #time.sleep(3)
    try:
        # client_node_id = "sub/0"
        # client_topic_name = f"{client_node_id}:annotation"
        # topic = "annotation"
        # topic_name = f"{node_config['node_id']}:{topic}"
        # topic_type = "bytes"

        
        # pub.add_topic(topic_name, topic_type)
        # print(f"Topic {topic_name} added!")
        # time.sleep(5)
        # pub.add_connection(
        #     pub_node_id=node_config["node_id"],
        #     sub_node_id=client_node_id,
        #     pub_topic_name=topic_name,
        #     sub_topic_name=client_topic_name,
        #     topic_type=topic_type
        # )
        # print(f"Connection added!")
        

        # bytes_img = image_utils.encode_image(img)
        # print("Start transfer image!")
        # while not stop_flag.wait(1):
        #     i += 1
        #     print('pub img:', i)
        #     pub.data_writer(topic, bytes_img)

        while not stop_flag.wait(1):
            data=1
            t=time.time()
            i+=1
            print("pub",i)
            # pub.data_writer('room1', float(i)) 
            # pub.data_writer('room2', float(i)) 
            # pub.data_writer('room3', float(i)) 
            ecd_img = image_utils.encode_image(img)
            # pub.data_writer('room1', ecd_img)
            

    except Exception as e:
        raise e
    finally:
        pub.terminate()
    
if __name__ == "__main__":
    topic_config = {
        'topic_info': {
            'room1': 'str',
            # 'room2': 'float',
            # 'room3': 'float',
        },
        'mode':0, # 0:server mode 1:client mode
        'ip': '140.113.28.158',
        'port': 50001
    }
    th_num=1;
    stop_flag=threading.Event()
    th_buff=[]
    for i in range(th_num):
        node_config = {
            'server_ip': '127.0.0.1',
            'server_port': 55555,
            'node_id': "pub/"+str(i),
            'node_name': "pub/"+str(i),
            'node_domain': 'Domain1',
        }
        th=threading.Thread(target=main,args=(stop_flag,node_config,topic_config))
        
        th_buff.append(th)
    for th in th_buff:
        th.start()
    try:
        while 1:
            time.sleep(1)
    except Exception as e:
        raise e
    finally:
        stop_flag.set()
        for th in th_buff:
            th.join()

        