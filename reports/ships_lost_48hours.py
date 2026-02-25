#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ZKillReports import Report

class ShipsLost48Hours(Report):
    name = "ships_lost_48hours"
    days_back = 2
    
    def build_query(self, past_date):
        return """
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
        """
    
    def transform_row(self, row):
        return {
            "ship_type": row["ship_type"],
            "total_kills": row["total_kills"]
        }
    
    def get_header(self):
        return "%-30.30s %20.20s" % ("Ship Type", "Quantity")
    
    def format_row(self, row):
        return "%-30.30s %20.20s" % (row["ship_type"], f"{row['total_kills']:,}")


if __name__ == "__main__":
    ShipsLost48Hours().run()
