#!/usr/bin/env python3

import socket
import sys
from utils import *



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
    # for server in servers:
    #     print(server)
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
    # GETTURN
    response = get_turn(gas, servers, 0)

    ships_table = [[[] for _ in range(8)] for _ in range(4)]
    for i, resp in enumerate(response):
        # print(resp)
        bridge = resp.get('bridge')
        ships = resp.get('ships')
        ships_table[i][bridge-1] = ships
    for row in ships_table:
        print(row)
    print("###########")

    shots_list = get_shots_list(cannons_table, ships_table)

    print("###########")
    for row in shots_list:
        print(row)
    # SHOT
    response = shot(gas, servers, shots_list)

    for server in servers:
        server.get("socket").close()

    return


if __name__ == "__main__":
    main()