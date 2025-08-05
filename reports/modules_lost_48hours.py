#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ZKillReports import convertISOTime, daysInPast, convertToIso, loadConfig
from datetime import datetime

import sqlite3

def get_modules_destroyed(myconfig, past_date):
    try:
        with sqlite3.connect(myconfig["db_fname"]) as conn:
            conn.row_factory = sqlite3.Row  # Enable dictionary-like access
            cursor = conn.cursor()
            
            cursor.execute("""
				SELECT
                    it.typeName AS item_type,
                    SUM(di.quantity) as total_destroyed
                FROM
                    droppedItems di
                JOIN
                    killmails km ON di.killmail_id = km.killmail_id
                JOIN
                    invTypes it ON di.typeID = it.typeID
                WHERE
                    km.time > ?
                GROUP BY
                    item_type
                ORDER BY
                    total_destroyed DESC
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
    
    my_results = get_modules_destroyed(myconfig, iso_48hoursago)

    print("%-50.50s %20.20s" % ("Module/Ammo", "Quantity"))

    for result in my_results:
        module = result["item_type"]
        quantity = result["total_destroyed"]
        quantity_f  = f"{quantity:,}"
        print("%-50.50s %20.20s" % (module, quantity_f))

