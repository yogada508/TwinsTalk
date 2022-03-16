from concurrent import futures
import grpc

import time
import logging

class ControllerInterceptor(grpc.ServerInterceptor):

    def intercept_service(self, continuation, handler_call_details):

        start_time = time.time() 
        response_future = continuation(handler_call_details)
        elapsed_time = time.time() - start_time
        #logging.debug("invoke server method={} duration={}".format(handler_call_details.method, elapsed_time))
        
        return response_future

class PublisherInterceptor(grpc.ServerInterceptor):

    def intercept_service(self, continuation, handler_call_details):

        start_time = time.time() 
        response_future = continuation(handler_call_details)
        elapsed_time = time.time() - start_time
        #logging.debug("invoke server method={} duration={}".format(handler_call_details.method, elapsed_time))
        
        return response_future

class NodeInterceptor(grpc.UnaryUnaryClientInterceptor,
                            grpc.UnaryStreamClientInterceptor,
                            grpc.StreamUnaryClientInterceptor,
                            grpc.StreamStreamClientInterceptor):

    def intercept_unary_unary(self, continuation, client_call_details, request):

        start_time = time.time() 
        response = continuation(client_call_details, request)
        elapsed_time = time.time() - start_time
        #logging.debug("invoke server method={} duration={}".format(client_call_details.method, elapsed_time))
        
        return response

    def intercept_unary_stream(self, continuation, client_call_details, request):

        start_time = time.time() 
        response_it = continuation(client_call_details, request)
        elapsed_time = time.time() - start_time
        #logging.debug("invoke server method={} duration={}".format(client_call_details.method, elapsed_time))
        
        return response_it

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):

        start_time = time.time() 
        response = continuation(client_call_details, request_iterator)
        elapsed_time = time.time() - start_time
        #logging.debug("invoke server method={} duration={}".format(client_call_details.method, elapsed_time))
        
        return response

    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):

        start_time = time.time() 
        response_it = continuation(client_call_details, request_iterator)
        elapsed_time = time.time() - start_time
        #logging.debug("invoke server method={} duration={}".format(client_call_details.method, elapsed_time))
        
        return response_it