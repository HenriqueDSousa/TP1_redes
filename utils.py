import socket
import json
import time


SHOTS_TO_SINK = {
    'frigate': 1,
    'destroyer': 2,
    'battleship': 3
}


def logexit(msg):
    print(msg)
    exit(1)

def usage():
    print("./bridge_defense.py <host> <port> <GAS>")

def send_to_servers(servers, json_data):
    """
    Function to send the same message to all servers
    """
    for server in servers:
        address = server.get('address')
        sock = server.get('socket')
        try:
            sock.sendto(json_data.encode(), address)
        except socket.error as e:
            sock.sendto(json_data.encode(), address)

def receive_from_servers(servers):
    """
    Function to get the responses from all servers
    """
    responses = [{}, {}, {}, {}]
    for server in servers:
        sock = server.get('socket')
        id = server.get('id')
        try:
            response, _ = sock.recvfrom(1024)
            response = json.loads(response.decode())
            responses[id] = response
        except socket.timeout:
            response, _ = sock.recvfrom(1024)
            response = json.loads(response.decode())
            responses[id] = response

    return responses

def get_empty_response(responses):
    empty_responses = []
    for i, response in enumerate(responses):
        if len(response) == 0:
            empty_responses.append(i)
    return empty_responses

def auth(gas, servers):
   
    data = {
            "type": "authreq",
            "auth": gas
        }
    
    max_tries = 2
    count = 0

    json_data = json.dumps(data)
    send_to_servers(servers, json_data)
    responses = receive_from_servers(servers)
    empty_responses = get_empty_response(responses)

    while len(empty_responses) != 0 and count < max_tries:
        temp_servers = [server for server in servers if server['id'] in empty_responses]
        send_to_servers(temp_servers, json_data)
        temp_response = receive_from_servers(temp_servers)
        for i in empty_responses:
            responses[i] = temp_response[i]
        empty_responses = get_empty_response(responses)
        count+=1

    if len(get_empty_response(responses)) != 0:
        logexit("Failed to authenticate with the server")

    for i, response in enumerate(responses):
        if response.get('status', -1) != 0:
            logexit("Invalid GAS")
        servers[i]['river'] = response.get('river')

def get_cannons(gas, servers):
    data = {
            "type": "getcannons",
            "auth": gas,
        }
    
    responses = []
    max_tries = 3
    count = 0

    json_data = json.dumps(data)

    send_to_servers(servers, json_data)
    responses = receive_from_servers(servers)
    empty_responses = get_empty_response(responses)

    while len(empty_responses) == 4 and count < max_tries:
        send_to_servers(servers, json_data)
        responses = receive_from_servers(servers)
        empty_responses = get_empty_response(responses)
        count+=1

    if empty_responses == 4:
        logexit("Failed to get cannons")

    for response in responses:
        if response != {}:
            return response.get('cannons')

def get_turn(gas, servers, turn):
    data = {
            "type": "getturn",
            "auth": gas,
            "turn": turn,
        }

    json_data = json.dumps(data)
    max_tries = 3
    count = 0

    send_to_servers(servers, json_data)
    responses = receive_from_servers(servers)
    empty_responses = get_empty_response(responses)

    while len(empty_responses) != 0 and count < max_tries:
        temp_servers = [server for server in servers if server['id'] in empty_responses]
        send_to_servers(temp_servers, json_data)
        temp_response = receive_from_servers(temp_servers)
        for i in empty_responses:
            responses[i] = temp_response[i]
        empty_responses = get_empty_response(responses)
        count+=1
    empty_responses = get_empty_response(responses)

    if len(empty_responses) != 0:
        logexit(f"Failed to get all turns from servers {empty_responses}")
    return responses

def shot(gas, servers, shots_list):
    
    for shot in shots_list:
        cannon = shot.get("cannon")
        server = shot.get("river") - 1
        data = {
                "type": "shot",
                "auth": gas,
                "cannon": cannon,
                "id": shot.get("id")
            }
        
        print(cannon, shot.get('id'))

        max_tries = 10
        count = 0
        print(servers[server])
        json_data = json.dumps(data)
        send_to_servers([servers[server]], json_data)
        server_id = servers[server].get('id')
        responses = receive_from_servers([servers[server]])
        while (len(responses[server_id]) == 0 or responses[server_id].get("type") != "shotresp") and count < max_tries:
            time.sleep(2)
            print(responses[server_id].get("type"))
            send_to_servers([servers[server]], json_data)
            responses = receive_from_servers([servers[server]])
            count+=1

        if (len(responses[server_id]) == 0 or responses[server_id].get("type") != "shotresp") and count < max_tries:
            logexit(f"Failed to get shot response from server {server}")

        print(responses[server_id])

   

def get_shots_list(cannons_table, ships_table):

    """
        Function to decide the shots to be done. Find the lower life ships 
        among the cannon ranges. Those are the ones to be shot
    """
    shots_list = []
    for row in range(5):
        for bridge in range(8):
            if cannons_table[row][bridge] == 1:
                
                river = -1
                weakest_ship_life = 1000
                weakest_ship = -1
                
                # fiding a ship
                if row == 0:

                    # If the cannon is in row 0 it only shots river 1
                    if ships_table[row][bridge] != []:
                        print("ships found")
                        for ship in ships_table[row][bridge]:
                            ship_life = SHOTS_TO_SINK[ship.get('hull')] - ship.get('hits')
                            if ship_life < weakest_ship_life:
                                weakest_ship = ship.get('id')
                                river = row
                                print([bridge + 1, row], weakest_ship)
                                weakest_ship_life = ship_life
                
                # if ship is between row 4 and 0, it can shot both adjacent rivers
                if row < 4 and row > 0:
                    
                    
                    if ships_table[row][bridge] != []:
                        print("ships found")
                        for ship in ships_table[row][bridge]:
                            ship_life = SHOTS_TO_SINK[ship.get('hull')] - ship.get('hits')
                            if ship_life < weakest_ship_life:
                                weakest_ship = ship.get('id')
                                river = row
                                print([bridge + 1, row], weakest_ship)
                                weakest_ship_life = ship_life

                    if ships_table[row-1][bridge] != []:
                        print("ships found")
                        for ship in ships_table[row][bridge]:
                            ship_life = SHOTS_TO_SINK[ship.get('hull')] - ship.get('hits')
                            if ship_life < weakest_ship_life:
                                weakest_ship = ship.get('id')
                                river = row-1
                                print([bridge + 1, row], weakest_ship)
                                weakest_ship_life = ship_life
                
                # if ship is in row 4 it can shot only in river 4
                if row  == 4:
                    if ships_table[row-1][bridge] != []:
                        print("ships found")
                        for ship in ships_table[row-1][bridge]:
                            ship_life = SHOTS_TO_SINK[ship.get('hull')] - ship.get('hits')
                            if ship_life < weakest_ship_life:
                                weakest_ship = ship.get('id')
                                river = row - 1
                                print([bridge + 1, row], weakest_ship)
                                weakest_ship_life = ship_life
                if weakest_ship != -1:
                    print("shot decided!!")
                    temp_dict = {'cannon': [bridge + 1, row], 'id': weakest_ship, 'river': river+1}
                    shots_list.append(temp_dict)
                    
    return shots_list