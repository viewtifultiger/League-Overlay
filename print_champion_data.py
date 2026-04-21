from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from http.client import RemoteDisconnected
import ssl
import json
import time
import sys
from itertools import zip_longest

myssl = ssl.create_default_context()
myssl.check_hostname = False
myssl.verify_mode=ssl.CERT_NONE

allgamedata_url = "https://127.0.0.1:2999/liveclientdata/allgamedata"

def champion_name(player):
    return player["championName"]
def item_name(item):
    return item["displayName"]
def build_snapshot(all_players, active_team):
    snapshot = {}
    for player in all_players:
        item_list = []
        if player["team"] != active_team:
            for item in player.get("items"):
                item_list.append(item["displayName"])
            item_list.sort()
            snapshot.update({player.get("championName"): item_list})
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
active_player_riotID = allgamedata_json.get("activePlayer").get("riotId")
active_player_teamID = None
for player in allgamedata_json.get("allPlayers"):
    if player.get("riotId") == active_player_riotID:
        active_player_teamID = player.get("team")

# Build initial snapshot
saved_enemy_team_snapshot = build_snapshot(allgamedata_json.get("allPlayers"), active_player_teamID)

# Print Enemies and their Items
print("Enemy Team:")
for player, item_list in saved_enemy_team_snapshot.items():
    print("\t" + player)
    print("\t\t" + item_list)

# Polling
while True:
    restart = False
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
    for player in allgamedata_json["allPlayers"]:
        if player["riotId"] == active_player_riotID:
            active_player_teamID = player["team"]
    # create an updated_enemy_list
    updated_enemy_list = []
    for player in allgamedata_json["allPlayers"]:
        if player["team"] != active_player_teamID:
            updated_enemy_list.append(player)
    # create updated enemy list by name and sort
    updated_enemy_list.sort(key=champion_name)

    # Check enemy roster
    for updated_enemy, current_enemy in zip_longest(updated_enemy_list, current_enemy_list, fill_value={}):
        if updated_enemy.get("championName") != current_enemy.get("championName"):
            print("different roster")
            print("Enemy Team:")
            for player in updated_enemy_list:
                print("\t" + player["championName"])
                for item in player["items"]:
                    print("\t\t" + item["displayName"])
            current_enemy_list = updated_enemy_list.copy()
            restart = True
            break

    if restart:
        continue

    # Check Each Item List
    for updated_enemy, current_enemy in zip_longest(updated_enemy_list, current_enemy_list, fill_value={"items": []}):
        if sorted(updated_enemy.get("items"), key=item_name) != sorted(current_enemy.get("items"), key=item_name):
            print("Enemy Team:")
            for player in updated_enemy_list:
                print("\t" + player["championName"])
                for item in sorted(player["items"], key=item_name):
                    print("\t\t" + item["displayName"])
            current_enemy_list = updated_enemy_list.copy()
            break

    # add a check to see if items changed and not the champions names
    time.sleep(1)