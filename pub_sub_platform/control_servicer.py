import time

import grpc
import node_pb2
import node_pb2_grpc

from utils import sql_utils


class ControlServicer(node_pb2_grpc.ControlServicer):

    def __init__(self, db_name: str):

        self.db_name = db_name
        self.db = sql_utils.DataBase(self.db_name)

    def get_current_time(self):

        return int(time.time())

    def Register(self, request: node_pb2.NodeInfo, context) -> node_pb2.Empty:

        print('Register: NodeID={}, NodeName={}, NodeDomain={}'.format(
            request.node_id, request.node_name, request.node_domain))

        try:
            self.db.insert_node(request.node_id, request.node_name,
                                request.node_domain, self.get_current_time())
        except Exception as e:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            #context.set_details('NodeID {} already exists {}'.format(request.node_id))
            context.set_details(str(e))
            return node_pb2.Empty()

        return node_pb2.Empty()

    def Deregister(self, request: node_pb2.NodeInfo, context) -> node_pb2.Empty:

        print('Deregister: NodeID={}'.format(request.node_id))

        try:
            # delete all information about this node
            self.db.delete_node(request.node_id)
            self.db.delete_topic_by_nodeID(request.node_id)
            self.db.delete_subscribe_by_nodeID(request.node_id)

            if "pub" in request.node_id.split("/"):
                self.db.delete_connection_by_pubID(request.node_id)
            else:
                self.db.delete_connection_by_subID(request.node_id)
        except Exception as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return node_pb2.Empty()

        return node_pb2.Empty()

    def CheckNodeStatus(self, request: node_pb2.Node, context) -> node_pb2.NodeAlive:
        print("CheckNodeStatus: NodeID-={}".format(request.node_id))
        
        if self.db.get_target_node(request.node_id):
            return node_pb2.NodeAlive(isAlive=True)
        else:
            return node_pb2.NodeAlive(isAlive=False)

    def UpdateStatus(self, request: node_pb2.NodeStatus, context) -> node_pb2.Empty:
        print('Update: UpdateStatus={}'.format(request.node_id))
        try:
            self.db.update_node_time(request.node_id, self.get_current_time())
            return node_pb2.Empty()
        except Exception as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return node_pb2.Empty()

    def AddTopic(self, request: node_pb2.Topic, context) -> node_pb2.Empty:

        print('AddTopic: TopicName={}, TopicType={},TopicMode={}, TopicIP={}, TopicPort={}, NodeID={}'.format(
            request.topic_name, request.topic_type, request.mode, request.ip,
            request.port, request.node_id))

        try:
            topic = self.db.get_topic_info(
                request.topic_name, request.topic_type)
            if len(topic) == 0:
                print('AddTopic: TopicName={}, TopicType={},TopicMode={}, TopicIP={}, TopicPort={}, NodeID={}'.format(
                    request.topic_name, request.topic_type, request.mode, request.ip,
                    request.port, request.node_id))
                self.db.insert_topic(request.topic_name, request.topic_type, request.node_id,
                                     request.node_domain, self.get_current_time(), request.mode, request.ip, request.port)
            else:
                self.db.update_topic(request.topic_name, request.topic_type, request.node_id,
                                     request.node_domain, self.get_current_time(), request.mode, request.ip, request.port)
        except Exception as e:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(str(e))
            return node_pb2.Empty()

        return node_pb2.Empty()

    def DeleteTopic(self, request: node_pb2.Topic, context) -> node_pb2.Empty:

        print('DeleteTopic: TopicName={}, TopicType={}, NodeID={}'.format(
            request.topic_name, request.topic_type, request.node_id))

        try:
            self.db.delete_topic(request.topic_name,
                                 request.topic_type, request.node_id)
            self.db.delete_connection_by_topic(
                request.topic_name, request.topic_type)

        except Exception as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return node_pb2.Empty()

        return node_pb2.Empty()

    def UpdateTopicState(self, request: node_pb2.Topic, context) -> node_pb2.TopicAlive:
        print(f"UpdateTopicState")
        try:
            topic_alive = node_pb2.TopicAlive()

            if request.topic_name.startswith("pub/server/"):
                client_name = (request.topic_name.split(":", 1)[1]).split("_")[0]

                if(client_name.endswith("Client")):
                    node_id = f"pub/client/{client_name}"
                    node = self.db.get_target_node(node_id)
                    
                    if not node:
                        self.db.delete_topic(request.topic_name, request.topic_type, request.node_id)
                        topic_alive.isAlive = False
                        return topic_alive

            self.db.update_topic_time(request.topic_name, request.node_id, self.get_current_time())
            topic_alive.isAlive = True
            
            return topic_alive

        except Exception as e:
            print(e)
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return node_pb2.TopicAlive(isAlive=True)

    def UpdateTopicStatus(self, request: node_pb2.TopicStatus, context) -> node_pb2.Empty:

        print('Update: TopicName={}, NodeID={}, ConnectedNodes={}'.format(
            request.topic_name, request.node_id, request.connected_nodes))

        try:
            self.db.update_topic_time(
                request.topic_name, request.node_id, self.get_current_time())

            for connected_node in request.connected_nodes:
                self.db.update_connection_status(
                    request.topic_name, request.node_id, connected_node, 1)

            # reset connection if not connection
            connections_info = self.db.get_pub_connections(request.node_id, 1)
            for connection_info in connections_info:
                if connection_info['PubTopicName'] == request.topic_name:
                    if connection_info['SubNodeID'] not in request.connected_nodes:
                        self.db.update_connection_status(
                            connection_info['PubTopicName'], connection_info['PubNodeID'], connection_info['SubNodeID'], 0)

        except Exception as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return node_pb2.Empty()

        return node_pb2.Empty()

    def AddSubscribeTopic(self, request: node_pb2.SubscribeTopic, context) -> node_pb2.Empty:
        print('AddSubscribeTopic: TopicName={}, TopicType={}, NodeID={}'.format(
            request.topic_name, request.topic_type, request.node_id))

        try:

            topic = self.db.get_subscribe_topics_info(
                request.topic_name, request.topic_type)
            if len(topic) == 0:
                self.db.insert_subscribe_topic(request.topic_name, request.topic_type, request.node_id,
                                               request.node_domain, self.get_current_time(), request.mode, request.ip, request.port)
            else:
                self.db.update_subscribe_topic(request.topic_name, request.topic_type, request.node_id,
                                               request.node_domain, self.get_current_time(), request.mode, request.ip, request.port)
        except Exception as e:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details(str(e))
            return node_pb2.Empty()

        return node_pb2.Empty()

    def DeleteSubscribeTopic(self, request: node_pb2.SubscribeTopicInfo, context) -> node_pb2.Empty:
        print("DeleteSubscribeTopic: TopicName={}, TopicType={}".format(
            request.topic_name, request.topic_type))

        try:
            self.db.delete_subscribe_topic(
                request.topic_name, request.topic_type)
            self.db.delete_connection_by_subscribe_topic(
                request.topic_name, request.topic_type)
            return node_pb2.Empty()

        except Exception as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return node_pb2.Empty()

    def UpdateSubscribeTopicStatus(self, request: node_pb2.SubscribeTopicStatus, context) -> node_pb2.Empty:

        #print('UpdateSubscribeTopicStatus: TopicName={}, NodeID={}'.format(request.topic_name, request.node_id))

        try:
            self.db.update_subscribe_topic_time(
                request.topic_name, request.node_id, self.get_current_time())
        except Exception as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return node_pb2.Empty()

        return node_pb2.Empty()

    def CheckOnline(self, timestamp, th=5):
        print(self.get_current_time(), timestamp)
        return self.get_current_time()-timestamp < th

    def CreateResponseConnection(self, connections_info):
        response_node_topics_info = []

        for connection_info in connections_info:
            #print('TopicName={}, TopicType={}, PubNodeID={}, SubNodeID={}'.format(connection_info['TopicName'], connection_info['TopicType'], connection_info['PubNodeID'], connection_info['SubNodeID']))
            topic_info = {}
            pub_topic_info = self.db.get_topic_info(
                connection_info['PubTopicName'], connection_info['TopicType'])
            sub_topic_info = self.db.get_subscribe_topics_info(
                connection_info['SubTopicName'], connection_info['TopicType'])
            if not pub_topic_info or not sub_topic_info:

                continue
            if(pub_topic_info["Mode"] == 1 and sub_topic_info["Mode"] == 1):
                print("c2c error")
                # return node_pb2.ResponseConnection()
                continue
            elif pub_topic_info["Mode"] == 0:
                topic_info["ConnectionMode"] = 0
                topic_info["TopicIP"] = pub_topic_info["TopicIP"]
                topic_info["TopicPort"] = pub_topic_info["TopicPort"]
                topic_info["UpdateTime"] = pub_topic_info["UpdateTime"]
            else:
                topic_info["ConnectionMode"] = 1
                topic_info["TopicIP"] = sub_topic_info["TopicIP"]
                topic_info["TopicPort"] = sub_topic_info["TopicPort"]

                topic_info["UpdateTime"] = sub_topic_info["UpdateTime"]
            if topic_info:
                nodeOnline = self.CheckOnline(topic_info['UpdateTime'])
                response_topic_info = node_pb2.ResponseTopicInfo(pub_topic_name=connection_info['PubTopicName'],
                                                                 sub_topic_name=connection_info['SubTopicName'],
                                                                 pub_node_id=connection_info['PubNodeID'],
                                                                 sub_node_id=connection_info['SubNodeID'],
                                                                 topic_type=connection_info['TopicType'],
                                                                 mode=topic_info['ConnectionMode'],
                                                                 ip=topic_info['TopicIP'],
                                                                 port=topic_info['TopicPort'],
                                                                 isOnline=nodeOnline)
                # print('response_node_topics_info:\n',response_topic_info)
                print("response connections_info",
                      response_topic_info, topic_info)
                print("-------------------------------------------------")
                response_node_topics_info.append(response_topic_info)
        return node_pb2.ResponseConnection(topics_info=response_node_topics_info)

    def GetConnection(self, request: node_pb2.RequestConnection, context) -> node_pb2.ResponseConnection:

        print('GetConnection: NodeID={} isSubscriber={}'.format(
            request.node_id, request.isSubscriber))

        try:
            if request.isSubscriber:
                connections_info = self.db.get_sub_connections(request.node_id)
            else:

                connections_info = self.db.get_pub_connections(request.node_id)
            #print("response connections_info",connections_info)
            return self.CreateResponseConnection(connections_info)

        except Exception as e:
            print("GetConnection error", e)
            raise e
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return node_pb2.ResponseConnection()

    # def AddConnection(self, request_iterator, context):
    #     for request in request_iterator:
    #         try:
    #             connection_id = self.db.insert_connection(
    #                 request.pub_topic_name,
    #                 request.sub_topic_name,
    #                 request.topic_type,
    #                 request.pub_node_id,
    #                 request.sub_node_id
    #             )
    #             if connection_id:
    #                 yield node_pb2.ConnectionID(connection_id = connection_id)
    #             else:
    #                 yield node_pb2.ConnectionID(connection_id = -1)

    #         except IndexError:
    #             context.set_code(grpc.StatusCode.NOT_FOUND)
    #             context.set_details(str(e))
    #             yield node_pb2.ConnectionID(connection_id = -1)

    #         except Exception as e:
    #             print("[Error][AddConnection]", e)
    #             yield node_pb2.ConnectionID(connection_id="-1")

    def AddConnection(self, request: node_pb2.ConnectionInfo, context):
        try:
            connection_id = self.db.insert_connection(
                request.pub_topic_name,
                request.sub_topic_name,
                request.topic_type,
                request.pub_node_id,
                request.sub_node_id
            )
            if connection_id:
                return node_pb2.ConnectionID(connection_id=connection_id)
            else:
                return node_pb2.ConnectionID(connection_id="-1")

        except IndexError:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return node_pb2.ConnectionID(connection_id="-1")

        except Exception as e:
            print("[Error][AddConnection]", e)
            return node_pb2.ConnectionID(connection_id="-1")

    def DeleteConnection(self, request: node_pb2.ConnectionID, context):
        print(f"DeleteConnection: connection_id={request.connection_id}")

        try:
            self.db.delete_connection_id(request.connection_id)

            return node_pb2.Empty()
        except Exception as e:
            print("DeleteConnection error")
            raise e
            return node_pb2.Empty()
