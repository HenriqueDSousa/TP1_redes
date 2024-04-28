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
        address = server.address
        sock = server.sock
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
        sock = server.sock
        id = server.id
        try:
            response, _ = sock.recvfrom(2048)
            response = json.loads(response.decode())
            responses[id] = response

        except (socket.timeout, json.decoder.JSONDecodeError) as e:
            pass
            # print(f"Error receiving response from server {id}: {e}")
            # print(f"Received response: {response}")
            # responses[id] = {}  # Empty response or handle error as appropriate

    return responses

def quit(gas, servers):
    data = {
        "type": "quit",
        "auth": gas
    }
    json_data = json.dumps(data)
    send_to_servers(servers, json_data)
    for server in servers:
        server.sock.close()


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
    
    max_tries = 3
    

    json_data = json.dumps(data)
    send_to_servers(servers, json_data)
    
    for server_index in range(len(servers)):

        authenticated = 0
        while not (authenticated):

            count = 0
            resp = (receive_from_servers([servers[server_index]])[server_index])
            
            #check if response is empty
            if not resp and count < max_tries:
                
                resp = (receive_from_servers([servers[server_index]])[server_index])
                
                count+=1

            if resp:

                check_gameover(resp, gas, servers)

                if resp.get("type") == "authresp":
                    if resp.get("status") == 0:
                        servers[server_index].set_river(resp.get('river'))
                        authenticated = 1    
                    elif resp.get("status") == 1:
                        quit(gas, servers)
                        logexit("Authentication error")
            
            else: 
                send_to_servers(servers, json_data)



def get_cannons(gas, servers):
    data = {
            "type": "getcannons",
            "auth": gas,
        }
    
    responses = []
    max_tries = 3
    count = 0

    json_data = json.dumps(data)

    for server_index in range(len(servers)):

        fetch = 0
        while not (fetch):

            count = 0
            resp = (receive_from_servers([servers[server_index]])[server_index])
            
            
            if not resp and count < max_tries:
                resp = (receive_from_servers([servers[server_index]])[server_index])
                count+=1

            if resp:

                check_gameover(resp, gas, servers)
                if resp.get("type") == "cannons":
                    return resp.get("cannons")

            else: 
                send_to_servers(servers, json_data)
        


def get_turn(gas, servers, turn):
    data = {
            "type": "getturn",
            "auth": gas,
            "turn": turn,
        }

    json_data = json.dumps(data)
    max_tries = 3
    
    # sending to each server
    send_to_servers(servers, json_data)

    # responses template to all 4 servers
    responses = [[], [], [], []]


    for server in range(len(servers)):

        count = 0
        response = []
        
        bridges = [0, 0, 0, 0, 0, 0, 0, 0]
        # getting the 8 bridges info
        

        while not all(bridges):

            resp = (receive_from_servers([servers[server]])[server])
            
            #check if response is empty
            if not resp and count < max_tries:
                
                resp = (receive_from_servers([servers[server]])[server])
                
                count+=1

            if resp:

                check_gameover(resp, gas, servers)

                if resp.get("type") == "state" and resp.get("turn") == turn:
                    bridges[resp.get("bridge")-1] = 1
                
                response.append(resp)
                
            else: 
                send_to_servers(servers, json_data)

        responses[server] = response

    return responses

def send_shot(gas, servers, shots_list):
    
    all_responses = []
    for shot in shots_list:
        cannon = shot.get("cannon")
        server = shot.get("river")-1
        data = {
                "type": "shot",
                "auth": gas,
                "cannon": cannon,
                "id": shot.get("id")
            }      
        
        json_data = json.dumps(data)
        send_to_servers([servers[server]], json_data)
        # print("shot sent")
        server_id = servers[server].id
    
        response = {}

        while response.get("type") != "shotresp" or response.get("id") != shot.get("id"):
                
                send_to_servers([servers[server]], json_data)
                responses = receive_from_servers([servers[server]])
                response = responses[server_id]
                check_gameover(response, gas, servers)

        # if response.get("type") != "shotresp":
        #     print(f"Received non-shotresp response from server {server_id}: {response}")

        all_responses.append(responses[server_id])

    return all_responses
   

def ship_can_be_shot(ship_id, ships_shotted, ship_life):
    if ship_id in ships_shotted.keys():
        if ships_shotted[ship_id] >= ship_life:
            return False
    return True
            

def get_shots_list(cannons_table, ships_table):

    """
        Function to decide the shots to be done. Find the lower life ships 
        among the cannon ranges. Those are the ones to be shot
    """


    shots_list = []
    ships_shotted = {}
    for row in range(5):
        for bridge in range(8):

            river = -1
            weakest_ship_life = 1000
            weakest_ship = -1
            if cannons_table[row][bridge] == 1:

                # fiding a ship
                if row == 0:

                    # If the cannon is in row 0 it only shots river 1
                    for ship in ships_table[row][bridge]:
                        ship_life = SHOTS_TO_SINK[ship.get('hull')] - ship.get('hits')
                        ship_id = ship.get('id')

                        if ship_life < weakest_ship_life and ship_can_be_shot(ship_id, ships_shotted, ship_life):
                            weakest_ship = ship.get('id')
                            river = row
                            weakest_ship_life = ship_life
                
                # if ship is between row 4 and 0, it can shot both adjacent rivers
                elif row < 4 and row > 0:
                    for ship in ships_table[row][bridge]:
                        ship_life = SHOTS_TO_SINK[ship.get('hull')] - ship.get('hits')
                        ship_id = ship.get('id')

                        if ship_life < weakest_ship_life and ship_can_be_shot(ship_id, ships_shotted, ship_life):
                            weakest_ship = ship.get('id')
                            river = row
                            weakest_ship_life = ship_life

                    for ship in ships_table[row-1][bridge]:
                        ship_life = SHOTS_TO_SINK[ship.get('hull')] - ship.get('hits')
                        ship_id = ship.get('id')

                        if ship_life < weakest_ship_life and ship_can_be_shot(ship_id, ships_shotted, ship_life):
                            weakest_ship = ship.get('id')
                            river = row-1
                            weakest_ship_life = ship_life
                
                # if ship is in row 4 it can shot only in river 4
                elif row  == 4:
                    
                    for ship in ships_table[row-1][bridge]:
                        ship_life = SHOTS_TO_SINK[ship.get('hull')] - ship.get('hits')
                        ship_id = ship.get('id')
                        if ship_life < weakest_ship_life and ship_can_be_shot(ship_id, ships_shotted, ship_life):
                            weakest_ship = ship.get('id')
                            river = row - 1
                            weakest_ship_life = ship_life

                if weakest_ship != -1:
                    if weakest_ship in ships_shotted.keys():
                        ships_shotted[weakest_ship] += 1
                    else:
                        ships_shotted[weakest_ship] = 1
                    temp_dict = {'cannon': [bridge+1, row], 'id': weakest_ship, 'river': river+1}
                    shots_list.append(temp_dict)


    
    return shots_list


def check_gameover(json_response,gas, servers):

    
    if json_response.get("type") == "gameover":
        print("GAME OVER")
        if json_response.get("status") == 1:
            description = json_response.get("description")
            quit(gas,servers)
            logexit(f"The game terminated due to: {description}")
        
        elif json_response.get("status") == 0:
            print(json_response)
            quit(gas, servers)
            logexit("GAME OVER")


def deal_damage(ships_table, shot_list):

    for shot in shot_list:
        ship_id = shot.get("id")
        for i in range(4):
            for j in range(8): 
                
                for ship in ships_table[i][j]:

                    if ship_id == ship.get("id"):
                        
                        ship["hits"] += 1
                        
                        # if the ship was destroyed
                        if SHOTS_TO_SINK[ship.get('hull')] == ship.get("hits"):
                            
                            print(f"ship {ship_id} destroyed")
                            ships_table[i][j].remove(ship)