from pub_sub_app import node_api2 as node_api
from pub_sub_app import Publisher2 as Publisher

import grpc
import json
import threading
import agent
import configurationParser as cp
import time

def run_agent(config):
    ag = agent.Agent(config)
    ag.start()

def main():
    with open("test_config.json") as f:
        config = json.load(f)
        result = cp.ConfigurationParser(config).get_parse_result()
    print(result)
    
    threads = []
    # stop_flag = threading.Event()
    thread = threading.Thread(target=run_agent, args=(result,))
    threads.append(thread)

    thread.start()

    while True:
        time.sleep(1)

    for t in threads:
        t.join()

if __name__ == '__main__':
    main()




    # RequestAddConnection = node_pb2.RequestAddConnection(pub_node_id=pub_node_id, sub_node_id=sub_node_id, pub_topic_name=pub_topic_name, sub_topic_name=sub_topic_name, topic_type=topic_type)

    # connection_id = None
    # with grpc.insecure_channel(SERVER_ADDRESS) as channel:
    #     stub = node_pb2_grpc.ControlStub(channel)
    #     response = stub.AddConnection(RequestAddConnection)
    #     # time.sleep(2)
    #     connection_id = response.connection_id
    #     print(connection_id)


        # if connection_id:
    #     RequestDelConnection = node_pb2.RequestDelConnection(connection_id = str(connection_id))
    #     with grpc.insecure_channel(SERVER_ADDRESS) as channel:
    #         stub = node_pb2_grpc.ControlStub(channel)
    #         stub.DeleteConnection(RequestDelConnection)