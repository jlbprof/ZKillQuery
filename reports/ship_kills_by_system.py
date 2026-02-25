#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import sqlite3
from ZKillReports import Report

class ShipKillsBySystem(Report):
    name = "ship_kills_by_system"
    days_back = 2
    
    GROUP_MAP = {
        'hauler': 28,
        'freighter': 513,
        'jump freighter': 902,
        'assault frigate': 324,
        'battleship': 27,
        'cruiser': 26,
        'frigate': 25,
        'destroyer': 420,
        'carrier': 547,
        'dreadnought': 485,
        'titan': 30,
        'supercarrier': 659,
    }
    
    SUPER_CLASSES = {
        'hauling': [28, 513, 902],
        'combat': [25, 26, 27, 324, 420, 893, 541],
    }
    
    def __init__(self, ship_filter=None):
        super().__init__(name=self.__class__.__name__)
        self.ship_filter = ship_filter
    
    def parse_args(self):
        parser = argparse.ArgumentParser(
            description='Report where ships were destroyed (system, region, security).',
            epilog='''
Examples:
  %(prog)s hauling         -- Super class: haulers, freighters, jump freighters
  %(prog)s combat          -- Super class: frigates, cruisers, battleships, etc.
  %(prog)s Freighter      -- Single group
  %(prog)s Fenrir         -- Specific ship name

Super Classes: %(prog)s -h to see list
''' % {'prog': sys.argv[0]}
        )
        parser.add_argument('ship_filter', nargs='?', help='Ship group, super class, or ship name')
        parser.add_argument('-d', '--days', type=int, default=self.days_back, 
                          help=f'Number of days to look back (default: {self.days_back})')
        args = parser.parse_args()
        
        if not args.ship_filter:
            parser.print_help()
            print("\n\nSuper Classes:")
            for name in sorted(self.SUPER_CLASSES.keys()):
                print(f"  {name}")
            print("\nShip Groups (examples):")
            for name in sorted(self.GROUP_MAP.keys())[:10]:
                print(f"  {name}")
            sys.exit(1)
        
        self.ship_filter = args.ship_filter
        self.days_back = args.days
    
    def get_group_ids(self) -> list[int] | None:
        filter_val = (self.ship_filter or "").lower()
        
        if filter_val in self.SUPER_CLASSES:
            return self.SUPER_CLASSES[filter_val]
        
        if filter_val in self.GROUP_MAP:
            return [self.GROUP_MAP[filter_val]]
        
        query = "SELECT groupID FROM invGroups WHERE LOWER(groupName) = ?"
        result = self.execute_query(query, (filter_val,))
        if result:
            return [result[0]['groupID']]
        return None
    
    def build_query(self, past_date):
        group_ids = self.get_group_ids()
        if not group_ids:
            return None
        
        placeholders = ','.join('?' * len(group_ids))
        return f"""
            SELECT
                s.solarSystemName AS system_name,
                s.security AS security_status,
                r.regionName AS region_name,
                it.typeName AS ship_type,
                km.time AS kill_time
            FROM
                killmails km
            JOIN
                solar_systems s ON km.solarSystemID = s.solarSystemID
            JOIN
                regions r ON s.regionID = r.regionID
            JOIN
                invTypes it ON km.ship_type_id = it.typeID
            JOIN
                invGroups ig ON it.groupID = ig.groupID
            WHERE
                km.time > ?
                AND ig.groupID IN ({placeholders})
            ORDER BY
                km.time DESC
        """
    
    def execute_query(self, query, params=None):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except sqlite3.Error as e:
            if self.logger:
                self.logger.error(f"Database error: {e}")
            return None
    
    def get_data(self, past_date):
        query = self.build_query(past_date)
        if not query:
            print(f"Unknown ship group: {self.ship_filter}")
            return []
        
        group_ids = self.get_group_ids()
        if not group_ids:
            return []
        params = (past_date,) + tuple(group_ids)
        results = self.execute_query(query, params)
        if results:
            return [self._row_to_dict(row) for row in results]
        return []
    
    def transform_row(self, row):
        return {
            "system": row["system_name"],
            "security": row["security_status"],
            "region": row["region_name"],
            "ship_type": row["ship_type"],
            "kill_time": row["kill_time"]
        }
    
    def get_header(self):
        return "%-30.30s %8.8s %-25.25s %-25.25s %-25.25s" % ("System", "Sec", "Region", "Ship Type", "Kill Time")
    
    def format_row(self, row):
        return "%-30.30s %8.2f %-25.25s %-25.25s %-25.25s" % (
            row["system"],
            row["security"],
            row["region"],
            row["ship_type"],
            row["kill_time"]
        )
    
    def run(self):
        self.parse_args()
        self.setup()
        past_date = self.get_past_date()
        raw_data = self.get_data(past_date)
        
        if not raw_data:
            print(f"No kills found for: {self.ship_filter}")
            return
            
        transformed = [self.transform_row(row) for row in raw_data]
        self.render(transformed)


if __name__ == "__main__":
    ShipKillsBySystem().run()
