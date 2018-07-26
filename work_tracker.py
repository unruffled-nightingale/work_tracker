import os
import json
from flask import Flask, jsonify, request
from db import DatabaseFactory


class WorkTracker(object):

    def __init__(self, DB_CONNECTION):

        self.db = DatabaseFactory.connect('Postgres', DB_CONNECTION)

        self.db.connect()

        # Instantiate database table object
        self.work_tracker_log = self.db.get_table(DB_CONNECTION['user'], 'work_tracker_log')
        self.tasks = self.db.get_table(DB_CONNECTION['user'], 'tasks')
        self.users = self.db.get_table(DB_CONNECTION['user'], 'users')

    def log_task(self, data):
        """
        Logs a task into the table work_tracker_log
        :param data: A python dictionary of the form {'task_id' : ${task_id}, 'user': ${user_id}}
        """
        self.work_tracker_log.insert(data)
        self.db.commit()

    def add_task(self, data):
        """
        Inserts a task into the table tasks
        :param data: A python dictionary of the form {'task' : ${task}}
        """
        self.tasks.insert(data)
        self.db.commit()

    def get_task(self, data):
        """
        Returns a task_id from table tasks
        :param data: A python dictionary of the form {'task' : ${task}}
        """
        return self.tasks.select(data)[0]['task_id']

    def add_user(self, data):
        """
        Inserts a user into the table users
        :param data: A python dictionary of the form {'user' : ${user}}
        """
        self.users.insert(data)
        self.db.commit()

    def get_user(self, data):
        """
        Returns a user_id from table users
        :param data: A python dictionary of the form {'user' : ${user}}
        """
        return self.users.select(data)[0]['user_id']

