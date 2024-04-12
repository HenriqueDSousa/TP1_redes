#!/usr/bin/env python3

import socket
import sys
import json
import struct

def logexit(msg):
    print(msg)
    exit(1)

def usage():
    print("./bridge_defense.py <host> <port> <GAS>")

def main():

    if len(sys.argv) < 4:
        usage()
        exit(1)

    host = sys.argv[1]
    port_offset = int(sys.argv[2])
    gas = sys.argv[3]  # Group Authentication Sequence (GAS)

 # List of server addresses and ports
    servers = [
        (host, port_offset + i) for i in range(4)
    ]

    # Creating sockets for each server
    sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(4)]
    
    try: 
        # sending the authentication to server
        for i, server_address in enumerate(servers):
            data = {
                "type": "authreq",
                "auth": gas
            }
            json_data = json.dumps(data)
            sockets[i].sendto(json_data.encode(), server_address)
            print(f"Sent authentication request to server {i+1}")

        # receiving authentication response from each server
        auth_responses = []
        for i, sock in enumerate(sockets):
            response, server_address = sock.recvfrom(1024)
            print(f"Received authentication response from server {i+1}: {response.decode()}")

            auth_response = json.loads(response.decode())
            auth_responses.append(auth_response)

        # Checking authentication status
        for i, response in enumerate(auth_responses):
            if response.get("type") == "authresp":
                if response.get("status") == 0:
                    print(f"Authentication with server {i+1} succeeded.")
                    print(f"River controlled by server {i+1}: {response.get('river')}")
                else:
                    print(f"Authentication with server {i+1} failed.")
            else:
                print(f"Unexpected response from server {i+1}")
        

    except socket.error as e:
        logexit(f"Socket error: {e}")

    finally:
        for sock in sockets:
            sock.close()

    


    return


if __name__ == "__main__":
    main()