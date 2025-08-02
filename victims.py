
import requests
import json

# Define the endpoint for Providence region killmails
url = "https://zkillboard.com/api/kills/regionID/10000047/page/1/"
headers = {'User-Agent': 'bodgerquery/1.0 (jbrown@jlbprof.com)'}

response = requests.get(url, headers=headers)
killmails = response.json()

print(response.json ())

# Iterate through each killmail and pull out the victim's items
#for km in killmails:
#    kill_id = km.get("killmail_id")
#    victim = km.get("victim", {})
#    ship_id = victim.get("ship_type_id")
#    system_id = km.get("solar_system_id")
#    items = victim.get("items", [])
#
#    print(kill_id, victim)

