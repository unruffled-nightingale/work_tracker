import os
import json
from flask import Flask, jsonify, request
from db import DatabaseFactory


try:
    DB_CONNECTION = json.loads(os.environ['PROD_PG_CONNECTION'])
except KeyError:
    from GLOBALS import DEV_PG_CONNECION as DB_CONNECTION

# Connect to database
db = DatabaseFactory.connect('Postgres', DB_CONNECTION)

# Instantiate database table object
work_tracker_log = db.get_table(DB_CONNECTION['user'], 'work_tracker_log')
tasks = db.get_table(DB_CONNECTION['user'], 'tasks')
users = db.get_table(DB_CONNECTION['user'], 'users')

app = Flask(__name__)


@app.route('/log_task', methods=['POST'])
def log_task():
    """
    Inserts a task into the table work_tracker_log
    """
    data = json.loads(request.data.decode('utf-8'))
    try:
        work_tracker_log.insert(data)
        db.commit()
        return jsonify({'record inserted'})
    except Exception as e:
        return jsonify({'error': e})

@app.route('/add_task', methods=['POST'])
def add_task():
    """
    Inserts a task into the table work_tracker_log
    """
    data = json.loads(request.data.decode('utf-8'))
    try:
        tasks.insert(data)
        task_id = tasks.select(data)['id']
        db.commit()
        return jsonify({'task_id': task_id})
    except Exception as e:
        return jsonify({'error': e})

@app.route('/add_user', methods=['POST'])
def add_task():
    """
    Inserts a task into the table work_tracker_log
    """
    data = json.loads(request.data.decode('utf-8'))
    try:
        users.insert(data)
        user_id = users.select(data)['id']
        db.commit()
        return jsonify({'user_id': user_id})
    except Exception as e:
        return jsonify({'error': e})


if __name__ == '__main__':
    app.run('0.0.0.0')
