import grpc
import node_pb2
import node_pb2_grpc
import pubsub_pb2
import pubsub_pb2_grpc
import time
MICRO = 1000000

class PubSubServiceServicer(pubsub_pb2_grpc.PubSubServiceServicer):

    def __init__(self,node,topics_buffer, buffer_maxLen=20):
        # print("enable PubSubServiceServicer")
        self.node = node
        self.topics_buffer = topics_buffer
        #self.connected_topic=connected_topic
        self.topics_connected_nodes = {}
        for topic in self.topics_buffer:
            self.topics_connected_nodes[topic]=[]
        
        self.data = None
        self.topics_data = {}
        self.topics_counter = {}
        self.rec_TopicBuffer={}
        
    def update_connected_node(self, request_node_id, topic_name):

        if request_node_id not in self.topics_connected_nodes[topic_name]:
            self.topics_connected_nodes[topic_name].append(request_node_id)

    def get_topic_data(self, request):
        request_node_id = request.node_id
        topic_name = request.topic_name
        self.update_connected_node(request_node_id, topic_name)
        if topic_name in self.topics_buffer:

            ring_buffer = self.topics_buffer[topic_name]
            topics_connected_nodes_len = len(self.topics_connected_nodes[topic_name])

            if topic_name not in self.topics_counter:
                #print(request_node_id, '-', topic_name, 'initial topics_counter')
                self.topics_counter[topic_name] = topics_connected_nodes_len

            if self.topics_counter[topic_name] < topics_connected_nodes_len:
                self.data = self.topics_data[topic_name]
                self.topics_counter[topic_name] += 1
            
            elif len(ring_buffer):
                #print(request_node_id,topic_name)
                #print("ring_buffer",len(ring_buffer))
                self.data = ring_buffer.popleft()
                self.topics_data[topic_name] = self.data
                self.topics_counter[topic_name] = 1
            else:
                self.data = None
        # topic is not exist
        else:
            self.data = None

        return self.data
            
    def GetBytesData(self, request_iterator, context):
        print("GetBytesData")
        
        for request in request_iterator:
            data = self.get_topic_data(request)
            resp=pubsub_pb2.BytesData()
            if data is not None:
                resp.ParseFromString(data)
                print("sended data",time.time()-resp.timestamp/MICRO)
                
            yield resp

    def GetStringData(self, request_iterator, context):

        print('GetStringData')
        
        for request in request_iterator:
            data = self.get_topic_data(request)
            resp=pubsub_pb2.StringData()
            if data is not None:
                resp.ParseFromString(data)
            yield resp

    def GetIntData(self, request_iterator, context):
        print("IntFloatData")

        for request in request_iterator:
            data = self.get_topic_data(request)
            resp=pubsub_pb2.IntData()
            if data is not None:
                resp.ParseFromString(data)
            yield resp
    
    def GetFloatData(self, request_iterator, context):
        print("GetFloatData")

        for request in request_iterator:
            data = self.get_topic_data(request)
            resp=pubsub_pb2.FloatData()
            if data is not None:
                resp.ParseFromString(data)
            yield resp
    def GetBoolData(self, request_iterator, context):

        print('GetBoolData')
        for request in request_iterator:
            data = self.get_topic_data(request)
            resp=pubsub_pb2.BoolData()
            if data is not None:
                resp.ParseFromString(data)
            yield resp

    def post_topic_data(self,request,data_type):
        try:
            #print("post_topic_data",data_type,self.topics_buffer.keys(),request.topic_name)
            topic_name = request.topic_name
            #self.update_connected_node(post_node_id, topic_name)
            if topic_name in self.topics_buffer:
                print("rec delay",len(request.data),time.time()-request.timestamp/MICRO)
                self.topics_buffer[topic_name].append((request, data_type))
                #print("post",self.topics_buffer[topic_name])
        except Exception as e:
            print(e)    
    def PostBytesData(self, request_iterator, context):
        for request in request_iterator:
            print("request get",request.topic_name,time.time()-request.timestamp/MICRO)
            self.post_topic_data(request,'bytes');
            yield pubsub_pb2.ReplyPostData(node_id=self.node.node_id,topic_name=request.topic_name);
    def PostIntData(self, request_iterator, context):
        for request in request_iterator:
            self.post_topic_data(request,'int');
            yield pubsub_pb2.ReplyPostData(node_id=self.node.node_id,topic_name=request.topic_name);
    def PostFloatData(self, request_iterator, context):
        for request in request_iterator:
            self.post_topic_data(request,'float');
            yield pubsub_pb2.ReplyPostData(node_id=self.node.node_id,topic_name=request.topic_name);
    def PostStringData(self, request_iterator, context):
        for request in request_iterator:
            self.post_topic_data(request,'str');
            yield pubsub_pb2.ReplyPostData(node_id=self.node.node_id,topic_name=request.topic_name);
    def PostBoolData(self, request_iterator, context):
        for request in request_iterator:
            self.post_topic_data(request,'bool');
            yield pubsub_pb2.ReplyPostData(node_id=self.node.node_id,topic_name=request.topic_name);
