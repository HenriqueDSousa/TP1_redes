#!/usr/bin/env python3

import socket
import sys
from utils import *
import struct



MAX_TURNS = 10
SHOTS_TO_SINK = {
    'frigate': 1,
    'destroyer': 2,
    'battleship': 3
}

#GAS = 2021031912:1:572a662bd2b4f3729c67c2e5c011e4355b432a90f1c97e03d63b5b550b59ba38+a15ca8923705ad48e6456f27ace5695bd590c518fbe4e3f41f823f602fb2cff7

def main():

    if len(sys.argv) < 4:
        usage()
        exit(1)

    host = sys.argv[1]
    port_offset = int(sys.argv[2])

    
    gas = sys.argv[3]  # Group Authentication Sequence (GAS)

    print(gas)
    # Creating sockets for each server
    servers = [{"address": (host, port_offset+i), "id": i, "socket": socket.socket(socket.AF_INET, socket.SOCK_DGRAM)} for i in range(4)]

    for server in servers:
        server.get('socket').settimeout(1)

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
    
    # initial ships table
    
    turn = 0
    while True:

        # GETTURN
        responses = get_turn(gas, servers, turn)

        # GAMEOVER
        for response in responses:
            for resp in response:
                if resp.get("type") == "gameover" :
                    print("GAMEOVER")
                    score = resp.get("score")
                    print(f"score: {score}")
                    
                    for server in servers:
                        server.get("socket").close()
                    
                    return
        
        ships_table = [[[] for _ in range(8)] for _ in range(4)]
        for i, response in enumerate(responses):
            for resp in (response):
                
                if resp.get("type") == "state" :
                    bridge = resp.get('bridge')
                    ships = resp.get('ships')
                    if ships:
                        ships_table[i][bridge-1].extend(ships)

        for row in ships_table:
            print(row)
        print("###########")

        shots_list = get_shots_list(cannons_table, ships_table)

        print(shots_list)

        for shoot in shots_list:
            for row in range(4):
                for bridge in range(8):
                    for ship in ships_table[row][bridge]:
                        ship_id = ship.get("id")

                        if ship_id == shoot.get("id"):
                            ship_life = SHOTS_TO_SINK[ship.get('hull')] - ship.get('hits') - 1
                            print(f"Ship {ship_id} shot on { [bridge+1, row+1]}. Life = {ship_life}")
        
        print("###########")



        if len(shots_list) != 0:
            # SHOT
            print("SHOT!")
            shot(gas, servers, shots_list)

            
                        
            # deal_damage(ships_table, shots_list)
            # response = []
            # response = shot(gas, servers, shots_list)
            # print("Shot response:")
            # print(response)
            # deal_damage(ships_table, response)
            print("###########")
        
        

        turn += 1
        if turn >= MAX_TURNS: 
            quit(gas, servers)
            break
        
        time.sleep(5)
        
    for server in servers:
        server.get("socket").close()

    return


if __name__ == "__main__":
    main()