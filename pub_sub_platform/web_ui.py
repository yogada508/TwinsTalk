from flask import Flask, request
from flask import redirect, url_for
from flask import render_template

from utils import sql_utils
import time
server="http://140.113.28.158:5000"
app = Flask(__name__)

def time_format(sec):

    #return time.strftime("%m/%d/%Y, %H:%M:%S", time.gmtime(sec))
    print('sec',sec)
    return time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime(sec))

app.jinja_env.globals.update(time_format=time_format)

@app.route('/map', methods=["GET", "POST"])
def map():

    db = sql_utils.DataBase('test.db')

    nodes = db.get_nodes()
    topics = db.get_topics()
    subscribe_topics = db.get_subscribe_topics()
    connections_info = db.get_connections()

    return render_template("map.html", nodes=nodes, topics=topics, subscribe_topics=subscribe_topics, connections_info=connections_info)

@app.route('/connection', methods=["GET", "POST"])
def connection():
    pub_topics_name = set()
    sub_topics_name = set()
    topics_type = set()
    pub_nodes = set()
    sub_nodes = set()
    
    db = sql_utils.DataBase('test.db')

    # NodeID, NodeName, NodeDomain, UpdateTime
    nodes = db.get_nodes()

    # TopicName, TopicType, NodeID, UpdateTime, Mode, TopicIP, TopicPort
    topics = db.get_topics()

    #print('topics:', topics)
    
    for topic in topics:
        pub_topics_name.add(topic[0])
        topics_type.add(topic[1])
        pub_nodes.add(topic[2])

    # SubscribeID, TopicName, TopicType, NodeID, UpdateTime
    subscribe_topics = db.get_subscribe_topics()
    #print('subscribe_topics:', subscribe_topics)
    for subscribe_topic in subscribe_topics:
        sub_topics_name.add(subscribe_topic[1])
        sub_nodes.add(subscribe_topic[3])

    # ConnectID, TopicName, TopicType, PubNodeID, SubNodeID, IsConnect
    connections_info = db.get_connections()
    '''
    print('pub_topics_name:', pub_topics_name)
    print('sub_topics_name:', sub_topics_name)
    print('topics_type:', topics_type)
    print('pub_nodes', pub_nodes)
    print('sub_nodes:', sub_nodes)
    print('connections_info:', connections_info)
    '''
    return render_template("web.html",
                            nodes=nodes,
                            topics=topics,
                            subscribe_topics=subscribe_topics,
                            pub_topics_name=list(pub_topics_name),
                            sub_topics_name=list(sub_topics_name),
                            topics_type=list(topics_type),
                            pub_nodes=list(pub_nodes),
                            sub_nodes=list(sub_nodes),
                            connections_info=connections_info,
                            server=server
                        )


@app.route('/add', methods=["GET", "POST"])
def add_connection():
    
    db = sql_utils.DataBase('test.db')

    pub_topic_name = request.values.get('PubTopicName')
    sub_topic_name = request.values.get('SubTopicName')
    print("add connection",pub_topic_name,sub_topic_name)
    #if pub_topic_name.split(':')[0] != sub_topic_name.split(':')[0]:

    #    return redirect(url_for('connection'))

    if request.method == "POST":

        db.insert_connection(request.values.get('PubTopicName'),
                            request.values.get('SubTopicName'),
                            request.values.get('TopicType'), 
                            request.values.get('PubNodeID'), 
                            request.values.get('SubNodeID'))

    return redirect(url_for('connection'))
                            
@app.route('/delete', methods=["GET", "POST"])
def delete_connection():

    db = sql_utils.DataBase('test.db')
    
    selected_connect_id = request.form.getlist('connect-id')
    
    for connect_id in selected_connect_id:
        db.delete_connection_id(int(connect_id))

    return redirect(url_for('connection'))

@app.route('/', methods=["GET", "POST"])
def index():

    db = sql_utils.DataBase('test.db')
    connections_info = db.get_connections()
    #print(connections_info)

    if request.method == "POST":
        
        connection_info = {}
        connection_info['ConnectID'] = request.values.get('ConnectID')
        connection_info['PubTopicName'] = request.values.get('PubTopicName')
        connection_info['SubTopicName'] = request.values.get('SubTopicName')
        connection_info['TopicType'] = request.values.get('TopicType')
        connection_info['PubNodeID'] = request.values.get('PubNodeID')
        connection_info['SubNodeID'] = request.values.get('SubNodeID')
        connection_info['ConnectionMode'] = request.values.get('mode')
        connection_info['IsConnect'] = request.values.get('IsConnect')

        connections_info.append(connection_info)
        return render_template("web.html", connections_info=connections_info)

    return render_template("web.html", connections_info=connections_info)

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000, debug = True)