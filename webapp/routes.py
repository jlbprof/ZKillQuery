import sys
import os
import sqlite3
import signal
import threading
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'reports'))

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

def get_db_path():
    from utils import get_data_dir
    data_dir_path = get_data_dir()
    data_dir = str(data_dir_path) + "/"
    from utils import load_config
    import logging
    logger = logging.getLogger('webapp')
    config = load_config(data_dir, logger)
    return data_dir + config["db_fname"]

def get_stats():
    db_path = get_db_path()
    past_date = (datetime.now() - timedelta(days=7)).isoformat()
    
    stats = {
        'total_kills': 0,
        'hauler_kills': 0,
        'deadliest_system': 'N/A',
        'top_ship': 'N/A'
    }
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Total kills
            cursor.execute("SELECT COUNT(*) as cnt FROM killmails WHERE time > ?", (past_date,))
            stats['total_kills'] = cursor.fetchone()['cnt']
            
            # Hauler kills
            cursor.execute("""
                SELECT COUNT(*) as cnt FROM killmails km
                JOIN invTypes it ON km.ship_type_id = it.typeID
                JOIN invGroups ig ON it.groupID = ig.groupID
                WHERE km.time > ? AND ig.groupID IN (28, 513, 902)
            """, (past_date,))
            stats['hauler_kills'] = cursor.fetchone()['cnt']
            
            # Deadliest system
            cursor.execute("""
                SELECT s.solarSystemName as name, COUNT(*) as cnt
                FROM killmails km
                JOIN solar_systems s ON km.solarSystemID = s.solarSystemID
                WHERE km.time > ?
                GROUP BY s.solarSystemName
                ORDER BY cnt DESC
                LIMIT 1
            """, (past_date,))
            row = cursor.fetchone()
            if row:
                stats['deadliest_system'] = row['name']
            
            # Top ship
            cursor.execute("""
                SELECT it.typeName as name, COUNT(*) as cnt
                FROM killmails km
                JOIN invTypes it ON km.ship_type_id = it.typeID
                WHERE km.time > ?
                GROUP BY it.typeName
                ORDER BY cnt DESC
                LIMIT 1
            """, (past_date,))
            row = cursor.fetchone()
            if row:
                stats['top_ship'] = row['name']
                
    except Exception as e:
        print(f"Error getting stats: {e}")
    
    return stats

@bp.route('/')
def index():
    stats = get_stats()
    return render_template('index.html', stats=stats)

@bp.route('/ships_by_group')
def ships_by_group():
    ship = request.args.get('ship', 'hauling')
    days = int(request.args.get('days', 7))
    region = request.args.get('region', '')
    
    from reports.ships_by_group import ShipsByGroup
    report = ShipsByGroup()
    report.setup()
    report.group_filter = ship
    report.days_back = days
    if region:
        report.region_filter = region
    
    data = report.get_data(report.get_past_date())
    transformed = [report.transform_row(row) for row in data]
    
    return render_template('report.html', 
                         report_name='Ships by Group',
                         ship=ship,
                         days=days,
                         region=region,
                         data=transformed,
                         columns=[('Category', 'category'), ('Ship Type', 'ship_type'), ('Kills', 'total_kills')])

@bp.route('/ship_kills_by_system')
def ship_kills_by_system():
    ship = request.args.get('ship', 'hauling')
    days = int(request.args.get('days', 7))
    region = request.args.get('region', '')
    
    from reports.ship_kills_by_system import ShipKillsBySystem
    report = ShipKillsBySystem()
    report.setup()
    report.ship_filter = ship
    report.days_back = days
    if region:
        report.region_filter = region
    
    data = report.get_data(report.get_past_date())
    transformed = [report.transform_row(row) for row in data]
    
    return render_template('report.html',
                         report_name='Ship Kills by System',
                         ship=ship,
                         days=days,
                         region=region,
                         data=transformed,
                         columns=[('System', 'system'), ('Sec', 'security'), ('Region', 'region'), ('Ship Type', 'ship_type'), ('Kill Time', 'kill_time')])

@bp.route('/api/ships_by_group')
def api_ships_by_group():
    ship = request.args.get('ship', 'hauling')
    days = int(request.args.get('days', 7))
    region = request.args.get('region', '')
    
    from reports.ships_by_group import ShipsByGroup
    report = ShipsByGroup()
    report.setup()
    report.group_filter = ship
    report.days_back = days
    if region:
        report.region_filter = region
    
    return jsonify(report.to_json())

@bp.route('/api/ship_kills_by_system')
def api_ship_kills_by_system():
    ship = request.args.get('ship', 'hauling')
    days = int(request.args.get('days', 7))
    region = request.args.get('region', '')
    
    from reports.ship_kills_by_system import ShipKillsBySystem
    report = ShipKillsBySystem()
    report.setup()
    report.ship_filter = ship
    report.days_back = days
    if region:
        report.region_filter = region
    
    return jsonify(report.to_json())

@bp.route('/shutdown', methods=['POST'])
def shutdown():
    def _kill():
        time.sleep(0.5)
        os.kill(os.getpid(), signal.SIGINT)
    threading.Thread(target=_kill, daemon=True).start()
    return render_template('down.html')
