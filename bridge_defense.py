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

#GAS = 2021031890:42:908687141401e1279d3f20850d626082cc4b50e8aa95366ac4dbaa0b1c2e1dac+2021031912:42:73651ac75ee9f68e8f8cd5e1160516a0f815a2e6c525b8b464ccf0d5d79b0e73+460f84c417b7f8bfdb21d2689dc3ff5621cd7c7fc80a0ca01398ae4b9c8116d3


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

    try:
        host = socket.getaddrinfo(sys.argv[1], None, socket.AF_INET)[0][4][0]
        # print(host)
        ipv = socket.AF_INET
    except:
        host = socket.getaddrinfo(sys.argv[1], None, socket.AF_INET6)[0][4][0]
        # print(host)
        ipv = socket.AF_INET6

    port_offset = int(sys.argv[2])
    print(host, ipv)
    
    gas = sys.argv[3]  # Group Authentication Sequence (GAS)


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
        #             # print("GAMEOVER")
        #             # score = resp.get("score")
        #             # print(f"score: {score}")
        #             # quit(gas, servers)
        #             print(resp) 
                check_gameover(resp, gas, servers)
                    
        #             # for server in servers:
        #             #     server.get("socket").close()
                    
        #             # return
        
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

        # for row in ships_table:
        #     print(row)
        # print("###########")

        shots_list = get_shots_list(cannons_table, ships_table)

        # print(shots_list)
        # for shot in shots_list:
        #     print(f"Cannon {shot.get('cannon')} shot ship {shot.get('id')} at river {shot.get('river')}")    

        print("###########")



        if len(shots_list) != 0:
            # SHOT
            print("SHOT!")
            send_shot(gas, servers, shots_list)

            
                        
            # deal_damage(ships_table, shots_list)
            # response = []
            # response = shot(gas, servers, shots_list)
            # print("Shot response:")
            # print(response)
            
            print("###########")
        
        

        turn += 1
        # if turn >= MAX_TURNS: 
        #     quit(gas, servers)
        #     break
        
        time.sleep(0)
        
    for server in servers:
        server.sock.close()

    return


if __name__ == "__main__":
    main()