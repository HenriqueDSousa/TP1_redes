#!/usr/bin/env python3

import socket
import sys
import json
import struct
from utils import *


def main():

    if len(sys.argv) < 4:
        usage()
        exit(1)

    host = sys.argv[1]
    port_offset = int(sys.argv[2])
    gas = sys.argv[3]  # Group Authentication Sequence (GAS)

    print(gas)
    # List of server addresses and ports
    servers = [
        (host, port_offset + i) for i in range(4)
    ]

    # Creating sockets for each server
    sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(4)]
    # AUTHENTICATION
     
    auth(gas, sockets, servers)

    # GETCANNONS

    data = {
            "type": "getcannons",
            "auth": gas,
        }
    
    json_data = json.dumps(data)
    #sending to one server
    send_to_servers(sockets, [servers[0]], json_data)
    responses = receive_from_servers([sockets[0]])

    print(responses)    


    for sock in sockets:
        sock.close()

    
    return


if __name__ == "__main__":
    main()