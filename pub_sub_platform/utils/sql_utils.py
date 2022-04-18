import sqlite3
import threading
'''
class DataBaseHandler():
    def __init__()
'''
class DataBase():

    def __init__(self, db_name):

        self.db_name = db_name

        #self.conn = sqlite3.connect(db_name)
        #self.cursor = self.conn.cursor()

    def select(self, sql: str):

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(sql)
            results  = cursor.fetchall()
            return results
        except Exception as e:
            print(e)
            return None

    def execute_with_commit(self, sql: str):

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute(sql)
            conn.commit()
            connection_id = cursor.lastrowid

            return connection_id
        except Exception as e:
            print("execute sql:",sql)
            print("execute_with_commit fail:", e)
            raise

    def create_all_table(self):

        # Node Table

        sql = '''
            CREATE TABLE "Node" (
            "NodeID"     TEXT NOT NULL,
            "NodeName"   TEXT NOT NULL UNIQUE,
            "NodeDomain"     TEXT NOT NULL,
            "UpdateTime" INTEGER NOT NULL,
            PRIMARY KEY("NodeID")
            );
            '''

        try:
            self.execute_with_commit(sql)
            print('Create Table: Node')
        except Exception as e:
            pass

        # Topic Table

        sql = '''
            CREATE TABLE "Topic" (
            "TopicName"  TEXT NOT NULL,
            "TopicType"  TEXT NOT NULL,
            "NodeID"     TEXT NOT NULL,
            "NodeDomain" TEXT NOT NULL,
            "UpdateTime" INTEGER NOT NULL,
            "Mode" INTEGER  NOT NULL,
            "TopicIP"    TEXT NOT NULL,
            "TopicPort"  INTEGER NOT NULL,
            
            PRIMARY KEY("TopicName")
            );
            '''

        try:
            self.execute_with_commit(sql)
            print('Create Table: Topic')
        except Exception as e:
            pass

        # SubscribeTopic Table

        sql = '''
            CREATE TABLE "SubscribeTopic" (
            "SubscribeID" INTEGER PRIMARY KEY AUTOINCREMENT,
            "TopicName"   TEXT NOT NULL,
            "TopicType"   TEXT NOT NULL,
            "NodeID"      TEXT NOT NULL,
            "NodeDomain" TEXT NOT NULL,
            "UpdateTime" INTEGER NOT NULL,
            "Mode" INTEGER  NOT NULL,
            "SubscriberIP"    TEXT NOT NULL,
            "SubscriberPort"  INTEGER NOT NULL
            );
            '''

        try:
            self.execute_with_commit(sql)
            print('Create Table: SubscribeTopic')
        except Exception as e:
            print("Create Table: SubscribeTopic fail:",e)

        # Connection Table

        sql = '''
            CREATE TABLE "Connection" (
            "ConnectID" INTEGER PRIMARY KEY AUTOINCREMENT,
            "PubTopicName" TEXT NOT NULL,
            "SubTopicName" TEXT NOT NULL,
            "TopicType" TEXT NOT NULL,
            "ConnectionMode" INTEGER NOT NULL,
            "PubNodeID" TEXT NOT NULL,
            "SubNodeID" TEXT NOT NULL,
            "isConnect" INTEGER NOT NULL
            );
            '''
        try:
            self.execute_with_commit(sql)
            print('Create Table: Connection')
        except Exception as e:
            pass
            
        sql = '''
            CREATE TABLE "ConnectionRule" (
            "ConnectID" INTEGER PRIMARY KEY AUTOINCREMENT,
            "PubTopicName" TEXT NOT NULL,
            "SubTopicName" TEXT NOT NULL,
            "TopicType" TEXT NOT NULL,
            "PubNodeID" TEXT NOT NULL,
            "SubNodeID" TEXT NOT NULL
            );
            '''

        try:
            self.execute_with_commit(sql)
            print('Create Table: Connection')
        except Exception as e:
            pass


        sql = 'DELETE FROM sqlite_sequence WHERE name="Connection" OR name="SubscribeTopic";'

        try:
            self.execute_with_commit(sql)
            print('Reset Auto Increment ID')
        except Exception as e:
            pass

    def insert_node(self, node_id, node_name, node_domain, update_time):

        sql = '''
            INSERT INTO "Node"
            ("NodeID", "NodeName", "NodeDomain", "UpdateTime")
            VALUES ("{}", "{}", "{}", {});
            '''.format(node_id, node_name, node_domain, update_time)
        
        try:
            self.execute_with_commit(sql)
            print("INSERT Node {} successfully".format(node_id))
        except Exception as e:
            pass

    def update_node_time(self, node_id, update_time):

        sql = '''
            UPDATE "Node" SET UpdateTime={} WHERE NodeID="{}";
            '''.format(update_time, node_id)

        try:
            self.execute_with_commit(sql)
            print("UPDATE Node {} Time successfully".format(node_id))
        except Exception as e:
            pass

    def update_node(self, node_id, node_name, node_domain, update_time):

        sql = '''
            UPDATE "Node" SET NodeName="{}", NodeDomain="{}", UpdateTime={} WHERE NodeID="{}";
            '''.format(node_name, node_domain, update_time, node_id)

        try:
            self.execute_with_commit(sql)
            print("UPDATE Node {} successfully".format(node_id))
        except Exception as e:
            pass

    def get_target_node(self, node_id):

        sql = 'SELECT NodeID, NodeName, NodeDomain , UpdateTime FROM Node WHERE NodeID="{}";'.format(node_id)

        node = self.select(sql)

        return node

    def get_nodes(self):

        sql = 'SELECT NodeID, NodeName, NodeDomain, UpdateTime FROM Node;'

        nodes = self.select(sql)

        return nodes

    def delete_node(self, node_id):

        sql = 'DELETE FROM Node WHERE NodeID="{}";'.format(node_id)

        try:
            self.execute_with_commit(sql)
            print("DELETE Node {} successfully".format(node_id))
            print(self.get_topics())
        except Exception as e:
            pass

    def insert_topic(self, topic_name, topic_type, node_id, node_domain, update_time, mode, topic_ip, topic_port):
        try:
            # print('AddTopic: TopicName={}, TopicType={},TopicMode={}, TopicIP={}, TopicPort={}, NodeID={}'.format(
            #     topic_name, topic_type, mode, topic_ip, topic_port, node_id))
            # print(topic_port, node_id)
            sql = '''
                INSERT INTO "Topic"
                ("TopicName", "TopicType", "NodeID", "NodeDomain", "UpdateTime", "Mode", "TopicIP", "TopicPort")
                VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}",{});
                '''.format(topic_name, topic_type, node_id, node_domain, update_time, mode, topic_ip, topic_port)
            self.execute_with_commit(sql)
            print("INSERT Topic {}/{} successfully".format(topic_name, topic_type))
        except Exception as e:
            print("INSERT Topic {}/{} fail:{}".format(topic_name, topic_type,e))
            

    def update_topic_time(self, topic_name, node_id, update_time):

        sql = '''
            UPDATE "Topic" SET UpdateTime={} WHERE TopicName="{}" AND NodeID="{}";
            '''.format(update_time, topic_name, node_id)

        try:
            self.execute_with_commit(sql)
            print("UPDATE Topic {} Time successfully".format(node_id))
        except Exception as e:
            pass

    def update_topic(self, topic_name, topic_type, node_id, node_domain, update_time, mode, topic_ip, topic_port):

        sql = '''
            UPDATE "Topic" SET TopicType="{}", Mode={}, TopicIP="{}", TopicPort={}, UpdateTime={} WHERE TopicName="{}" AND NodeID="{}";
            '''.format(topic_type, mode,topic_ip, topic_port, update_time, topic_name, node_id)

        try:
            self.execute_with_commit(sql)
            print("UPDATE Topic {} successfully".format(node_id))
        except Exception as e:
            pass

    def get_topics(self):

        sql = 'SELECT TopicName, TopicType, NodeID, UpdateTime, Mode, TopicIP, TopicPort FROM Topic;'
        topics = self.select(sql)

        return topics

    def delete_topic(self, topic_name, topic_type, node_id):

        sql = 'DELETE FROM Topic WHERE TopicName="{}" AND TopicType="{}" AND NodeID="{}";'.format(topic_name, topic_type, node_id)
        
        try:
            self.execute_with_commit(sql)
            print("DELETE Topic {} successfully".format(topic_name))
        except Exception as e:
            pass

    def delete_topic_by_nodeID(self, node_id):

        sql = 'DELETE FROM Topic WHERE NodeID="{}";'.format(node_id)

        try:
            self.execute_with_commit(sql)
            print("DELETE Topic {} successfully".format(node_id))
        except Exception as e:
            pass
    
    def delete_connection_by_topic(self, topic_name, topic_type):
        sql = 'DELETE FROM Connection WHERE PubTopicName="{}" AND TopicType="{}";'.format(topic_name, topic_type)
        
        try:
            self.execute_with_commit(sql)
            print("DELETE Connection with PubTopicName={} and TopicType={} successfully.".format(topic_name, topic_type))
        except Exception as e:
            pass

    def delete_connection_by_subscribe_topic(self, topic_name, topic_type):
        sql = 'DELETE FROM Connection WHERE SubTopicName="{}" AND TopicType="{}";'.format(topic_name, topic_type)
        
        try:
            self.execute_with_commit(sql)
            print("DELETE Connection with SubTopicName={} and TopicType={} successfully.".format(topic_name, topic_type))
        except Exception as e:
            pass
        

    def get_topic_info(self, topic_name, topic_type):

        sql = 'SELECT TopicName, TopicType, NodeID, UpdateTime, Mode, TopicIP, TopicPort FROM Topic WHERE TopicName="{}" AND TopicType="{}";'.format(topic_name, topic_type)
        
        topics = self.select(sql)

        topic_info = {}

        if topics:

            topic = topics[0]
            topic_info['TopicName'] = topic[0]
            topic_info['TopicType'] = topic[1]
            topic_info['UpdateTime']=topic[3]
            topic_info['Mode'] = topic[4]
            topic_info['TopicIP'] = topic[5]
            topic_info['TopicPort'] = topic[6]

        return topic_info

    def insert_subscribe_topic(self, topic_name, topic_type, node_id, node_domain, update_time, mode, sub_ip, sub_port):

        try:
            
            sql = '''
                SELECT SubscribeID FROM SubscribeTopic WHERE TopicName="{}" AND TopicType="{}" AND NodeID="{}" AND NodeDomain="{}";
                '''.format(topic_name, topic_type, node_id, node_domain)
            #subscribe_topics = self.select(sql)
            
            #if not subscribe_topics:

            sql = '''
                INSERT INTO "SubscribeTopic"
                ("TopicName", "TopicType", "NodeID", "NodeDomain", "UpdateTime","Mode","SubscriberIP","SubscriberPort")
                VALUES ("{}", "{}", "{}", "{}", {},{},"{}",{});
                '''.format(topic_name, topic_type, node_id, node_domain, update_time, mode, sub_ip, sub_port)
            self.execute_with_commit(sql)
            print("INSERT SubscribeTopic {}:{} successfully".format(node_id, topic_name))
            #else:
            #    print('SubscribeTopic {}:{} already exist'.format(node_id, topic_name))
        except Exception as e:
            pass

    def update_subscribe_topic(self, topic_name, topic_type, node_id, node_domain, update_time, mode, sub_ip, sub_port):

        sql = '''
            UPDATE "SubscribeTopic" SET TopicType="{}", NodeDomain="{}", Mode={}, SubscriberIP="{}",SubscriberPort={},UpdateTime={}  WHERE TopicName="{}" AND NodeID="{}";
            '''.format(topic_type, node_domain, mode, sub_ip, sub_port, update_time, topic_name, node_id)

        try:
            self.execute_with_commit(sql)
            #print("UPDATE Topic {} Time successfully".format(node_id))
        except Exception as e:
            pass

    def update_subscribe_topic_time(self, topic_name, node_id, update_time):

        sql = '''
            UPDATE "SubscribeTopic" SET UpdateTime={} WHERE TopicName="{}" AND NodeID="{}";
            '''.format(update_time, topic_name, node_id)

        try:
            self.execute_with_commit(sql)
            #print("UPDATE Topic {} Time successfully".format(node_id))
        except Exception as e:
            pass

    def get_subscribe_topics(self):

        sql = 'SELECT SubscribeID, TopicName, TopicType, NodeID, UpdateTime,Mode,SubscriberIP,SubscriberPort FROM SubscribeTopic;'

        subscribe_topics = self.select(sql)

        return subscribe_topics
    def get_subscribe_topics_info(self,topic_name, topic_type):
        sql = 'SELECT TopicName, TopicType, NodeID, UpdateTime, Mode, SubscriberIP, SubscriberPort FROM SubscribeTopic WHERE TopicName="{}" AND TopicType="{}";'.format(topic_name, topic_type)
        #print("sql",sql)
        topics = self.select(sql)

        topic_info = {}

        if topics:

            topic = topics[0]
            topic_info['TopicName'] = topic[0]
            topic_info['TopicType'] = topic[1]
            topic_info['UpdateTime']=topic[3]
            topic_info['Mode'] = topic[4]
            topic_info['TopicIP'] = topic[5]
            topic_info['TopicPort'] = topic[6]

        return topic_info        

    def delete_subscribe_topics(self, subscribe_id):

        sql = 'DELETE FROM SubscribeTopic WHERE SubscribeID="{}";'.format(subscribe_id)
        
        try:
            self.execute_with_commit(sql)
            print("DELETE SubscribeTopic {} successfully".format(subscribe_id))
        except Exception as e:
            pass

    def delete_subscribe_by_nodeID(self, node_id):

        sql = 'DELETE FROM SubscribeTopic WHERE NodeID="{}";'.format(node_id)
        
        try:
            self.execute_with_commit(sql)
            print("DELETE SubscribeTopic {} successfully".format(node_id))
        except Exception as e:
            pass

    def delete_subscribe_topic(self, topic_name, topic_type):
        sql = 'DELETE FROM SubscribeTopic WHERE TopicName="{}" AND TopicType="{}";'.format(topic_name, topic_type)

        try:
            self.execute_with_commit(sql)
            print("DELETE SubscribeTopic {} successfully".format(topic_name))
        except Exception as e:
            pass

    def insert_connection(self, pub_topic_name, sub_topic_name, topic_type, pub_node_id, sub_node_id, is_connect=0):

        sql = 'SELECT ConnectID FROM Connection WHERE PubTopicName="{}" AND SubTopicName="{}" AND TopicType="{}" AND PubNodeID="{}" AND SubNodeID="{}";'.format(pub_topic_name, sub_topic_name, topic_type, pub_node_id, sub_node_id)
        print("check sql",sql)
        try:
            connections = self.select(sql)
            if connections:
                print('PubTopicName={}, SubTopicName={}, TopicType={}, PubNodeID={}, SubNodeID={}'.format(pub_topic_name, sub_topic_name, topic_type, pub_node_id, sub_node_id))
                print("Connection already exist.")
                return
        except Exception as e:
            raise(e)

        try:
            sql='SELECT Mode FROM Topic WHERE TopicName="{}" and "NodeID"="{}"'.format(pub_topic_name,pub_node_id)
            pub_mode=self.select(sql)[0][0]
            sql='SELECT Mode FROM SubscribeTopic WHERE TopicName="{}" and "NodeID"="{}"'.format(sub_topic_name,sub_node_id)
            sub_mode=self.select(sql)[0][0]
            
            if pub_mode==1 and sub_mode==1:
                print("grpc c2c communication not support yet")
                return 

            sql = '''
                INSERT INTO "Connection"
                ("PubTopicName", "SubTopicName", "TopicType", "ConnectionMode", "PubNodeID", "SubNodeID", "IsConnect")
                VALUES ("{}", "{}", "{}", {}, "{}", "{}", {});
                '''.format(pub_topic_name, sub_topic_name, topic_type, pub_mode,pub_node_id, sub_node_id, is_connect)
            print("insert sql",sql)
        
            connection_id = str(self.execute_with_commit(sql))
            # print("INSERT Connection {} successfully".format(node_id))
            return connection_id
        except Exception as e:
            print(e)
            pass
    
    def insert_rule(self, pub_topic_name, sub_topic_name, topic_type, pub_class, sub_class, pub_node_id, sub_node_id):
        sql = 'SELECT ConnectID FROM ConnectionRule WHERE PubTopicName="{}" AND SubTopicName="{}" AND TopicType="{}" AND PubNodeID="{}" AND SubNodeID="{}";'.format(pub_topic_name, sub_topic_name, topic_type, pub_node_id, sub_node_id)
        print("check sql",sql)
        try:
            connections = self.select(sql)
            if connections:
                print('PubTopicName={}, SubTopicName={}, TopicType={}, PubNodeID={}, SubNodeID={}'.format(pub_class, sub_class, topic_type, pub_node_id, sub_node_id))
                print("Connection already exist.")
                return
        except Exception as e:
            raise(e)
        
        try:

            sql = '''
                INSERT INTO "ConnectionRule"
                ("PubTopicName", "SubTopicName", "TopicType", "PubNodeID", "SubNodeID")
                VALUES ("{}", "{}", "{}",  "{}", "{}");
                '''.format(pub_topic_name, sub_topic_name, topic_type, pub_class, sub_class)
            print("insert sql",sql)
        
            self.execute_with_commit(sql)
            print("INSERT ConnectionRule {}:{}-{}:{} successfully".format(pub_class,pub_topic_name,sub_class,sub_topic_name))
        except Exception as e:
            print(e)
            


    def delete_connection_id(self, connect_id):

        sql = 'DELETE FROM Connection WHERE ConnectID="{}";'.format(connect_id)
        
        try:
            self.execute_with_commit(sql)
            print("DELETE Connection {} successfully".format(connect_id))
        except Exception as e:
            pass

    def delete_connection_by_pubID(self, pub_node_id):

        sql = 'DELETE FROM Connection WHERE PubNodeID="{}";'.format(pub_node_id)
        
        try:
            self.execute_with_commit(sql)
            print("DELETE Connection {} successfully".format(pub_node_id))
        except Exception as e:
            pass

    def delete_connection_by_subID(self, sub_node_id):

        sql = 'DELETE FROM Connection WHERE PubNodeID="{}";'.format(sub_node_id)
        
        try:
            self.execute_with_commit(sql)
            print("DELETE Connection {} successfully".format(sub_node_id))
        except Exception as e:
            pass

    '''def delete_connection(self, topic_name, topic_type, pub_node_id, sub_node_id):

        sql = 'DELETE FROM Connection WHERE TopicName="{}" AND TopicType="{}" AND PubNodeID="{}" AND SubNodeID="{}";'.format(topic_name, topic_type, pub_node_id, sub_node_id)
        
        try:
            self.execute_with_commit(sql)
            print("DELETE Connection {}:{} successfully".format(topic_name, sub_node_id))
        except Exception as e:
            pass'''

    def get_connections(self):
        sql = 'SELECT ConnectID, PubTopicName, SubTopicName, TopicType, ConnectionMode,PubNodeID, SubNodeID, IsConnect FROM Connection;'.format()
        connections = self.select(sql)
        connections_info = []
        if connections is None:
            return connections_info
        for connection in connections:
            
            #connection_info = {'TopicName': connection[0], 'TopicType': connection[1], 'PubNodeID': connection[2], 'SubNodeID': connection[3]}
            #print('ConnectID={}, TopicName={}, TopicType={}, PubNodeID={}, SubNodeID={}'.format(connection[0], connection[1], connection[2], connection[3], connection[4]))

            info = {}
            info['ConnectID'] = connection[0]
            info['PubTopicName'] = connection[1]
            info['SubTopicName'] = connection[2]
            info['TopicType'] = connection[3]
            info['ConnectionMode'] = connection[4]
            info['PubNodeID'] = connection[5]
            info['SubNodeID'] = connection[6]
            info['IsConnect'] = connection[7]
            connections_info.append(info)
        return connections_info

    def get_connection_rule(self):
        col="ConnectID,PubTopicName,SubTopicName,TopicType,PubNodeID,SubNodeID"
        keys=col.split(',')
        sql = 'SELECT {} FROM ConnectionRule;'.format(col)
        rules = self.select(sql)
        rules_info = []
        if rules is None:
            return rules_info
        for rule in rules:
            
            #connection_info = {'TopicName': connection[0], 'TopicType': connection[1], 'PubNodeID': connection[2], 'SubNodeID': connection[3]}
            #print('ConnectID={}, TopicName={}, TopicType={}, PubNodeID={}, SubNodeID={}'.format(connection[0], connection[1], connection[2], connection[3], connection[4]))
            info = {}
            for i,k in enumerate(keys):
                info[k] = rule[i]
            rules_info.append(info)
        
        return rules_info


    def get_sub_connections(self, sub_node_id):

        sql = 'SELECT PubTopicName, SubTopicName, TopicType, ConnectionMode, PubNodeID, SubNodeID FROM Connection WHERE SubNodeID="{}";'.format(sub_node_id)
        connections = self.select(sql)

        connections_info = []

        for connection in connections:
            
            #connection_info = {'TopicName': connection[0], 'TopicType': connection[1], 'PubNodeID': connection[2], 'SubNodeID': connection[3]}
            #print('PubTopicName={}, SubTopicName={}, TopicType={}, PubNodeID={}, SubNodeID={}'.format(connection[0], connection[1], connection[2], connection[3], connection[4]))

            connection_info = {}
            connection_info['PubTopicName'] = connection[0]
            connection_info['SubTopicName'] = connection[1]
            connection_info['TopicType'] = connection[2]
            connection_info['ConnectionMode'] = connection[3]
            connection_info['PubNodeID'] = connection[4]
            connection_info['SubNodeID'] = connection[5]

            connections_info.append(connection_info)

        return connections_info

    def get_pub_connections(self, pub_node_id, is_connect=None):
        if is_connect:
            sql = 'SELECT PubTopicName, SubTopicName, TopicType, ConnectionMode, PubNodeID, SubNodeID FROM Connection WHERE PubNodeID="{}" AND IsConnect={};'.format(pub_node_id, is_connect)
        else:
            sql = 'SELECT PubTopicName, SubTopicName, TopicType, ConnectionMode, PubNodeID, SubNodeID FROM Connection WHERE PubNodeID="{}";'.format(pub_node_id)            
        connections = self.select(sql)

        connections_info = []

        for connection in connections:
            
            #print('PubTopicName={}, SubTopicName={}, TopicType={}, PubNodeID={}, SubNodeID={}'.format(connection[0], connection[1], connection[2], connection[3], connection[4]))

            connection_info = {}
            connection_info['PubTopicName'] = connection[0]
            connection_info['SubTopicName'] = connection[1]
            connection_info['TopicType'] = connection[2]
            connection_info['ConnectionMode'] = connection[3]
            connection_info['PubNodeID'] = connection[4]
            connection_info['SubNodeID'] = connection[5]

            connections_info.append(connection_info)

        return connections_info

    def update_connection_status(self, pub_topic_name, pub_node_id, sub_node_id, is_connect):

        sql = 'UPDATE "Connection" SET IsConnect={} WHERE PubTopicName="{}" AND PubNodeID="{}" AND SubNodeID="{}";'.format(is_connect, pub_topic_name, pub_node_id, sub_node_id)

        try:
            self.execute_with_commit(sql)
        except Exception as e:
            pass

        print('UPDATE Connection PubTopicName={}, PubNodeID={}, SubNodeID={}, IsConnect={} successfully'.format(pub_topic_name, pub_node_id, sub_node_id, is_connect))

if __name__ == "__main__":
    
    import time

    node1 = 'b06ebf60297d'
    node2 = 'b06ebf60297e'

    # open database
    db = DataBase('test.db')
    db.create_all_table()

    # insert node
    db.insert_node(node1, 'Node1', 'Domain1', int(time.time()))
    db.insert_node(node2, 'Node2', 'Domain1', int(time.time()))
    
    # get nodes and delete node
    db.get_nodes()
    db.delete_node('b06ebf60297e')
    db.get_nodes()
    
    # uipdate node
    db.update_node('b06ebf60297d', 'Node1', 'Domain2', int(time.time()))

    # insert topic
    db.insert_topic('yolo', 'bytes', '127.0.0.1', 55555, node1, int(time.time()))
    topic_info = db.get_topic_info('yolo', 'bytes')

    print('TopicName={}, TopicType={}, TopicIP={}, TopicPort={}'.format(topic_info['TopicName'], 
                                                                        topic_info['TopicType'], 
                                                                        topic_info['TopicIP'], 
                                                                        topic_info['TopicPort']))

    db.close()