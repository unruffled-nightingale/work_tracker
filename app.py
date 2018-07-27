import os
import json
from flask import Flask, jsonify, request
from work_tracker import WorkTracker


try:
    DB_CONNECTION = json.loads(os.environ['PROD_PG_CONNECTION'])
except KeyError:
    from GLOBALS import DEV_PG_CONNECION as DB_CONNECTION


wt = WorkTracker(DB_CONNECTION)

app = Flask(__name__)


@app.route('/log_task', methods=['POST'])
def log_task():
    """
    Inserts a task into the table work_tracker_log
    """
    data = json.loads(request.data.decode('utf-8'))
    try:
        wk.log_task(data)
        return jsonify('task logged')
    except:
        return jsonify('log failed')

@app.route('/add_task', methods=['POST'])
def add_task():
    """
    Inserts a task into the table work_tracker_log
    """
    data = json.loads(request.data.decode('utf-8'))
    try:
        wk.add_task(data)
        id = wk.get_task_id(data)
        return jsonify({'task_id': id})
    except:
        return jsonify('adding task failed')

@app.route('/add_user', methods=['POST'])
def add_user():
    """
    Inserts a task into the table work_tracker_log
    """
    data = json.loads(request.data.decode('utf-8'))
    try:
        wk.add_user(data)
        id = wk.get_user_id(data)
        return jsonify({'user': id})
    except:
        return jsonify('ading user failed')


if __name__ == '__main__':
    app.run('0.0.0.0')
