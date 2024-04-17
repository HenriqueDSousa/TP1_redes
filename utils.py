import socket
import sys
import json
import struct


def logexit(msg):
    print(msg)
    exit(1)

def usage():
    print("./bridge_defense.py <host> <port> <GAS>")

def send_to_servers(sockets, servers, json_data):
    """
    Function to send the same message to all servers
    """

    for i, server_address in enumerate(servers):
        
        try:
            sockets[i].sendto(json_data.encode(), server_address)
        except socket.error as e:
            sockets[i].sendto(json_data.encode(), server_address)

def receive_from_servers(sockets):
    """
    Function to get the responses from all servers
    """
    responses = []
    for i, sock in enumerate(sockets):
        try:
            response, server_address = sock.recvfrom(1024)
            response = json.loads(response.decode())
            responses.append(response)
        except socket.timeout:
            response, server_address = sock.recvfrom(1024)
            response = json.loads(response.decode())
            responses.append(response)

    return responses

def auth(gas, sockets, servers):
   
    # sending the authentication to server
    data = {
            "type": "authreq",
            "auth": gas
        }
        
    json_data = json.dumps(data)
    send_to_servers(sockets, servers, json_data)
    
    # receiving authentication response from each server
    responses = receive_from_servers(sockets)
    print("sent")
    # Checking authentication status

    for i, response in enumerate(responses):
        print(response)

        if response.get('status', -1) != 0:
            logexit("Autherror")
   