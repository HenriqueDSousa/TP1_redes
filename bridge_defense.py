#!/usr/bin/env python3

import socket
import sys
from utils import *
import struct



MAX_TURNS = 0
SHOTS_TO_SINK = {
    'frigate': 1,
    'destroyer': 2,
    'battleship': 3
}
#GAS = teste:42:01b6e855db069213ebe27fbd0f4154ee46f6991919b5bc63ca72433d907d08a4+c37e8a64ccde01926cfc1fcf2052df18c1189f3386197e21d8c9e8f1bfb3c22e
#GAS = 2021031912:1:572a662bd2b4f3729c67c2e5c011e4355b432a90f1c97e03d63b5b550b59ba38+a15ca8923705ad48e6456f27ace5695bd590c518fbe4e3f41f823f602fb2cff7



class Server:
    
    def __init__(self, host, port, id, sock):
        self.address = (host, port)
        self.id = id
        self.sock = sock
        self.river = -1
    
    def set_river(self, river):
        self.river = river

    def __str__(self):
        return f"Server {self.id}:\n\tAddress: ({self.address})\n\tRiver: {self.river}"

def main():

    if len(sys.argv) < 4:
        usage()
        exit(1)

    host = socket.gethostbyname(sys.argv[1])
    port_offset = int(sys.argv[2])

    ipv = socket.AF_INET if ':' not in host else socket.AF_INET6
    gas = sys.argv[3]  # Group Authentication Sequence (GAS)

    print(gas)
    # Creating sockets for each server
    servers = [Server(host, port_offset+i, i, socket.socket(ipv, socket.SOCK_DGRAM)) for i in range(4)]

    
    for server in servers:
        server.sock.settimeout(1)


    # AUTHENTICATION
    auth(gas, servers)
    for server in servers:
        print(server)
    print("###########")
   
    # GETCANNONS
    cannons = get_cannons(gas, servers)
    print(cannons)

    cannons_table = [[0 for _ in range(8)] for _ in range(5)]
    for coordinate in cannons:
        cannons_table[coordinate[1]][coordinate[0]-1] = 1
    for row in cannons_table:
        print(row)

    print("###########")
    
    # # initial ships table
    
    turn = 0
    while True:

        print(turn)

        # GETTURN
        responses = get_turn(gas, servers, turn)
    
        # GAMEOVER
    
        for response in responses:
            for resp in response:
        #             
                check_gameover(resp, gas, servers)
        
        ships_table = [[[] for _ in range(8)] for _ in range(4)]
        for i, response in enumerate(responses):
            for resp in (response):
                # print(resp)
                if resp.get("type") == "state" :
                    if resp.get("turn") == turn:
                        bridge = resp.get('bridge')
                        ships = resp.get('ships')
                        if ships:
                            ships_table[i][bridge-1].extend(ships)

        for row in ships_table:
            print(row)


        shots_list = get_shots_list(cannons_table, ships_table)

        for shot in shots_list:
            print(shot.get("cannon"), shot.get("id"), shot.get("river"))
    

        print("###########")



        if len(shots_list) != 0:
            # SHOT
            send_shot(gas, servers, shots_list)

        turn += 1        
        time.sleep(0)
        
    for server in servers:
        server.sock.close()

    return


if __name__ == "__main__":
    main()