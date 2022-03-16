#============================================================
# import packages
#============================================================
import time
import base64
import sys
import logging
import multiprocessing
import threading

#============================================================
# import grpc protobuf
#============================================================
from concurrent import futures
import grpc
import node_pb2
import node_pb2_grpc
import ntp_pb2
import ntp_pb2_grpc
import interceptor

import control_servicer
import ntp_servicer

#============================================================
# import utils
#============================================================
from utils import sql_utils

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('port', type=int, nargs='?', default=55555)
parser.add_argument('check', type=int, nargs='?', default=60)
args = parser.parse_args()

#class Controller(threading.Thread):
#class Controller(multiprocessing.Process):
class Controller():

    def __init__(self, db_name: str, port: int, time_to_live: int):
        #threading.Thread.__init__(self)
        #multiprocessing.Process.__init__(self)

        self.db_name = db_name
        self.port = port
        self.time_to_live = time_to_live

        db = sql_utils.DataBase(self.db_name)
        db.create_all_table()

    def check_node(self):

        print('check_node')

        current_time = int(time.time())

        db = sql_utils.DataBase(self.db_name)
        nodes = db.get_nodes()

        for node in nodes:
            #print('NodeID={}, NodeName={}, NodeDomain={}, UpdateTime={}'.format(node[0], node[1], node[2], node[3]))

            if current_time - node[3] > self.time_to_live:
                
                # def delete_node(self, node_id)
                db.delete_node(node[0])

    def check_topic(self):
        print('check_topic')
        current_time = int(time.time())
        db = sql_utils.DataBase(self.db_name)
        topics = db.get_topics()
        for topic in topics:
            #print('TopicName={}, TopicType={}, TopicIP={}, TopicPort={}, NodeID={}, UpdateTime={}'.format(topic[0], topic[1], topic[2], topic[3], topic[4], topic[5]))
            if current_time - topic[3] > self.time_to_live:
                # def delete_topic(self, topic_name, topic_type, node_id)
                db.delete_topic(topic[0], topic[1], topic[2])
                connections_info = db.get_pub_connections(topic[2], 1)
                for connection_info in connections_info:
                    db.update_connection_status(connection_info['PubTopicName'], connection_info['PubNodeID'], connection_info['SubNodeID'], 0)

    def check_subscribe_topic(self):

        print('check_subscribe_topic')

        current_time = int(time.time())

        db = sql_utils.DataBase(self.db_name)
        subscribe_topics = db.get_subscribe_topics()

        for subscribe_topic in subscribe_topics:

            if current_time - subscribe_topic[4] > self.time_to_live:

                db.delete_subscribe_topics(subscribe_topic[0])
    def update_connection(self):
        print("update_connection")        
        db = sql_utils.DataBase(self.db_name)
        rule=db.get_connection_rule()
        print("rule:",rule)
    def run(self):

        server = grpc.server(futures.ThreadPoolExecutor(max_workers = 10), interceptors=(interceptor.ControllerInterceptor(),))
        node_pb2_grpc.add_ControlServicer_to_server(control_servicer.ControlServicer(self.db_name), server)
        ntp_pb2_grpc.add_NtpServicer_to_server(ntp_servicer.NtpServicer(), server)

        server.add_insecure_port('[::]:{}'.format(self.port))
        server.start()

        print('Controller Start with Port {}'.format(self.port))

        #server.wait_for_termination()

        while True:
            
            time.sleep(self.time_to_live)
            self.check_node()
            self.check_topic()
            self.check_subscribe_topic()
            self.update_connection()

            

#============================================================
# main
#============================================================
if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    print('args.port={}, args.check={}'.format(args.port, args.check))
    # database, port, time_to_live(sec)
    master_server = Controller('test.db', args.port, args.check)
    #master_server.start()
    master_server.run()

    '''while True:
        try:
            pass
        except KeyboardInterrupt:
            print('KeyboardInterrupt')
            break'''


#============================================================
# after exit
#============================================================
