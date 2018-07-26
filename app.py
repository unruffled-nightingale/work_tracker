import os
import json
import GLOBALS
from flask import Flask, jsonify, g, request
from db import DatabaseFactory, Postgres


try:
    DB_CONNECTION = json.loads(os.environ['PROD_PG_CONNECTION'])
except KeyError:
    from GLOBALS import DEV_PG_CONNECION as DB_CONNECTION

# Connect to database
db = DatabaseFactory.connect('Postgres', DB_CONNECTION)

# Instantiate database table object
work_tracker_log = db.get_table(DB_CONNECTION['user'], 'work_tracker_log')

app = Flask(__name__)


@app.route('/log_task', methods=['POST'])
def set_task():
    """
    Inserts a task into the table work_tracker_log
    """
    data = json.loads(request.data.decode('utf-8'))
    try:
        work_tracker_log.insert(data)
        return jsonify({'status': 'record inserted'})
    except Exception as e:
        return jsonify({'error': e})


if __name__ == '__main__':
    app.run('0.0.0.0')
