import socket
import sys
import json
import struct


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

