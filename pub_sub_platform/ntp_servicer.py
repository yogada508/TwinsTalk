from concurrent import futures
import grpc
import ntp_pb2
import ntp_pb2_grpc

import time

MILLI = 1000
MICRO = 1000000

class NtpServicer(ntp_pb2_grpc.NtpServicer):

    def __init(self):
        pass

    def Query(self, request: ntp_pb2.NtpRequest, context: grpc.ServicerContext) -> ntp_pb2.NtpReply:

        #print(time.time())
        #print(round(time.time()*MILLI))

        return ntp_pb2.NtpReply(message=round(time.time() * MICRO))

def runServer():

    # Creates an insecure Channel to a server.
    server = grpc.server(thread_pool=futures.ThreadPoolExecutor())
    ntp_pb2_grpc.add_NtpServicer_to_server(NtpServicer(), server)
    # Opens an insecure port for accepting RPCs.
    server.add_insecure_port('[::]:8844')
    # Starts this Server.
    server.start()
    # Block current thread until the server stops.
    server.wait_for_termination()

def serverMain():
    
    try:
        runServer()
    except grpc.RpcError as e:
        print(e)


if __name__ == "__main__":
    
    serverMain()