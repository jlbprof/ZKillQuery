#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ZKillReports import convertISOTime, daysInPast, convertToIso, loadConfig
from datetime import datetime

import sqlite3

def get_ship_kills(myconfig, past_date):
    try:
        with sqlite3.connect(myconfig["db_fname"]) as conn:
            conn.row_factory = sqlite3.Row  # Enable dictionary-like access
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT
                    it.typeName AS ship_type,
                    COUNT(*) AS total_kills
                FROM
                    killmails km
                JOIN
                    solar_systems s ON km.solarSystemID = s.solarSystemID
                JOIN
                    invTypes it ON km.ship_type_id = it.typeID
                WHERE
                    km.time > ?
                GROUP BY
                    ship_type
                ORDER BY
                    total_kills DESC
            """, (past_date,))
            
            return cursor.fetchall()
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None    



if __name__ == "__main__":
    now_time = datetime.now ()
    time_48hoursago = daysInPast(now_time, 2)
    iso_48hoursago = convertToIso(time_48hoursago);
    myconfig = loadConfig()
    
    my_results = get_ship_kills(myconfig, iso_48hoursago)

    print("%-30.30s %20.20s" % ("Ship Type", "Quantity"))

    for result in my_results:
        ship_type = result["ship_type"]
        quantity = result["total_kills"]
        quantity_f  = f"{quantity:,}"
        print("%-30.30s %20.20s" % (ship_type, quantity_f))

