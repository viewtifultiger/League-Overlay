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

def fetch_allgamedata():
    try:
        allgamedata_response = urlopen(allgamedata_url, context = myssl)
        allgamedata_json = json.loads(allgamedata_response.read())
        return allgamedata_json
    except (URLError, HTTPError, RemoteDisconnected):
        print("Connection not found.")
        time.sleep(5)
        return None
    
def get_active_teamId(allgamedata_json):
    active_teamId = None
    active_player_riotId = allgamedata_json.get("activePlayer").get("riotId")
    for player in allgamedata_json.get("allPlayers"):
        if player.get("riotId") == active_player_riotId:
            active_teamId = player.get("team")
        return active_teamId

def print_snapshot(snapshot):
    print("Enemy Team:")
    for player, item_list in snapshot.items():
        print("\t" + player)
        for item in item_list:
            print("\t\t" + item)

# Initiate
while True:
    allgamedata_json = fetch_allgamedata()
    if allgamedata_json:
        break

# TeamID
# BLUE SIDE (TOP TEAM): ORDER
# RED SIDE (BOTTOM TEAM): CHAOS

# Obtain Active Player ID
active_teamId = get_active_teamId(allgamedata_json)

# Build initial enemy team snapshot
saved_enemy_snapshot = build_snapshot(allgamedata_json.get("allPlayers"), active_teamId)

# Print Enemies and their Items
print_snapshot(saved_enemy_snapshot)

# Polling
while True:
    allgamedata_json = fetch_allgamedata()
    if not allgamedata_json:
        continue

    active_teamId = get_active_teamId(allgamedata_json)

    updated_enemy_snapshot = build_snapshot(allgamedata_json.get("allPlayers"), active_teamId)

    if saved_enemy_snapshot != updated_enemy_snapshot:
        saved_enemy_snapshot = updated_enemy_snapshot.copy()
        print_snapshot(saved_enemy_snapshot)
    
    time.sleep(1)