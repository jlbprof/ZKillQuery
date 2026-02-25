#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ZKillReports import Report

class ModulesLost48Hours(Report):
    name = "modules_lost_48hours"
    days_back = 2
    
    def build_query(self, past_date):
        return """
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
        """
    
    def transform_row(self, row):
        return {
            "item_type": row["item_type"],
            "total_destroyed": row["total_destroyed"]
        }
    
    def get_header(self):
        return "%-50.50s %20.20s" % ("Module/Ammo", "Quantity")
    
    def format_row(self, row):
        return "%-50.50s %20.20s" % (row["item_type"], f"{row['total_destroyed']:,}")


if __name__ == "__main__":
    ModulesLost48Hours().run()
