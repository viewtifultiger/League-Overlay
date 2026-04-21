from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from http.client import RemoteDisconnected
import ssl
import json
import time
import sys

myssl = ssl.create_default_context()
myssl.check_hostname = False
myssl.verify_mode=ssl.CERT_NONE

allgamedata_url = "https://127.0.0.1:2999/liveclientdata/allgamedata"

def build_snapshot(all_players, active_team):
    snapshot = {}
    for player in all_players:
        item_list = []
        if player.get("team") != active_team:
            for item in player.get("items", []):
                item_list.append(item.get("displayName"))
            item_list.sort()
            snapshot[player.get("championName")] = item_list
    return snapshot

# Initiate
while True:
    try:
        allgamedata_response = urlopen(allgamedata_url, context = myssl)
        allgamedata_json = json.loads(allgamedata_response.read())
        break
    except (URLError, HTTPError, RemoteDisconnected):
        print("Connection not found.")
        time.sleep(5)

# TeamID
# BLUE SIDE (TOP TEAM): ORDER
# RED SIDE (BOTTOM TEAM): CHAOS

# Obtain Active Player ID
active_player_riotId = allgamedata_json.get("activePlayer").get("riotId")
active_player_teamId = None
for player in allgamedata_json.get("allPlayers"):
    if player.get("riotId") == active_player_riotId:
        active_player_teamId = player.get("team")

# Build initial enemy team snapshot
saved_enemy_snapshot = build_snapshot(allgamedata_json.get("allPlayers"), active_player_teamId)

# Print Enemies and their Items
print("Enemy Team:")
for player, item_list in saved_enemy_snapshot.items():
    print("\t" + player)
    for item in item_list:
        print("\t\t" + item)

# Polling
while True:
    #JSON
    try:
        allgamedata_response = urlopen(allgamedata_url, context = myssl)
        allgamedata_json = json.loads(allgamedata_response.read())
    except (URLError, HTTPError, RemoteDisconnected):
        #URLError, HTTPError RemoteDisconnected
        print("Connection not found.")
        time.sleep(5)
        continue

    #obtain new teamID
    for player in allgamedata_json.get("allPlayers"):
        if player.get("riotId") == active_player_riotId:
            active_player_teamId = player.get("team")

    # build updated enemy team snapshot
    updated_enemy_snapshot = build_snapshot(allgamedata_json.get("allPlayers"), active_player_teamId)

    # Check enemy roster
    if saved_enemy_snapshot != updated_enemy_snapshot:
        print("Enemy Team:")
        saved_enemy_snapshot = updated_enemy_snapshot.copy()
        for player, item_list in saved_enemy_snapshot.items():
            print("\t" + player)
            for item in item_list:
                print("\t\t" + item)
    
    # add a check to see if items changed and not the champions names
    time.sleep(1)