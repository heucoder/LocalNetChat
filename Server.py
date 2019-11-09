from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Condition
from queue import Queue

class sockServer(object):
    def __init__(self):
        self._client_queue = Queue()
        self._client_name2sock = {}
        self._client_sock2name = {}

    def init(self, host = "", post = 15968, nworkers = 10):
        # Run the erver
        sock = socket(AF_INET,SOCK_STREAM)
        sock.bind((host, post))
        sock.listen(5)
        for i in range(nworkers):
            t = Thread(target=self.inst_client)
            t.daemon = True
            t.start()
        print("server runing...........")
        client_name_poisx = "client"
        index = 1
        while True:
            client_sock, client_addr = sock.accept()
            client_name = client_name_poisx + str(index)
            index += 1
            self._client_name2sock[client_name] = client_sock
            self._client_sock2name[client_sock] = client_name
            self._client_queue.put((client_sock, client_addr))

    def inst_client(self):
        sock, client_addr = self._client_queue.get()
        print("Got Connection from", client_addr)
        
        read_thread = Thread(target = self.read, args = (sock, ))
        read_thread.daemon = True
        read_thread.start()

        while True:
            if not read_thread.is_alive():
                break
        client_name = self._client_sock2name[sock]
        del self._client_sock2name[sock]
        del self._client_name2sock[client_name]
        print("Connection closed: ", client_addr)

    def read(self, sock):
        while True:
            message = sock.recv(1024)
            if message == b"":
                break
            client_name = self._client_sock2name[sock]
            me_message = ("ME: "+ str(message)).encode()
            sock.sendall(me_message)
            message = str(client_name) + ": " + str(message)
            message = message.encode()
            print("message:", message)
            for client_sock in self._client_name2sock.values():
                if client_sock != sock:
                    client_sock.sendall(message)
        
if __name__ == "__main__":
    server = sockServer()
    server.init()