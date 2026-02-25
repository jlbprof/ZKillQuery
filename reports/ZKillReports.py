#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sys
import sqlite3

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from dateutil.parser import isoparse

from utils import get_data_dir, load_config, setup_logger


def convertISOTime(isotime):
    date_obj = isoparse(isotime)
    return date_obj


def daysInPast(date_obj, xdays):
    new_date = date_obj - timedelta(days=xdays)
    return new_date


def convertToIso(date_obj):
    return date_obj.isoformat()


class Report(ABC):
    """Base class for ZKill reports."""
    
    days_back = 2
    
    def __init__(self, name=None):
        self.name = name or self.__class__.__name__
        self.config = {}
        self.db_path: str = ""
        self.logger = None
        
    def setup(self):
        data_dir_path = get_data_dir()
        data_dir = str(data_dir_path) + "/"
        
        log_file = data_dir + "zkill.log"
        self.logger = setup_logger(self.name, log_file=log_file, console=True)
        
        self.config = load_config(data_dir, self.logger)
        self.db_path = data_dir + self.config["db_fname"]
        
    def get_past_date(self, days=None):
        days = days or self.days_back
        now = datetime.now()
        past = now - timedelta(days=days)
        return past.isoformat()
    
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
    
    def _row_to_dict(self, row) -> dict:
        """Convert sqlite3.Row to dict for JSON serialization."""
        return dict(row)
    
    def get_data(self, past_date) -> list[dict]:
        """Data layer - returns JSON-serializable list of dicts."""
        query = self.build_query(past_date=past_date)
        results = self.execute_query(query, (past_date,))
        if results:
            return [self._row_to_dict(row) for row in results]
        return []
    
    @abstractmethod
    def build_query(self, past_date: str) -> str | None:
        """Return SQL query string"""
        pass
    
    @abstractmethod
    def transform_row(self, row: dict) -> dict:
        """Transform a database row dict into output format"""
        pass
    
    @abstractmethod
    def format_row(self, row: dict) -> str:
        """View layer - return formatted string for a row"""
        pass
    
    def get_header(self) -> str | None:
        return None
    
    def render(self, data: list[dict]):
        """View layer - render the data"""
        header = self.get_header()
        if header:
            print(header)
        for row in data:
            print(self.format_row(row))
    
    def run(self):
        self.setup()
        past_date = self.get_past_date()
        raw_data = self.get_data(past_date)
        transformed = [self.transform_row(row) for row in raw_data]
        self.render(transformed)
    
    def to_json(self, past_date=None) -> str:
        """Return data as JSON string"""
        if past_date is None:
            past_date = self.get_past_date()
        raw_data = self.get_data(past_date)
        return json.dumps(raw_data, indent=2)
