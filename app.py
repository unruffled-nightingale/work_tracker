import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from work_tracker import WorkTracker

# todo create route for graph data
# todo improve error handling

try:
    DB_CONNECTION = json.loads(os.environ['PROD_PG_CONNECTION'])
except KeyError:
    from GLOBALS import DEV_PG_CONNECION as DB_CONNECTION


wk = WorkTracker(DB_CONNECTION)

app = Flask(__name__)
CORS(app)


@app.route('/log_task', methods=['POST'])
def log_task():
    """
    Inserts a task into the table work_tracker_log
    """
    data = json.loads(request.data.decode('utf-8'))
    wk.log_task(data)
    return jsonify('task logged')


@app.route('/add_task', methods=['POST'])
def add_task():
    """
    Inserts a task into the table work_tracker_log
    """
    data = json.loads(request.data.decode('utf-8'))
    wk.add_task(data)
    id = wk.get_task_id(data)
    return jsonify({'task_id': id})


@app.route('/add_user', methods=['POST'])
def add_user():
    """
    Inserts a task into the table work_tracker_log
    """
    data = json.loads(request.data.decode('utf-8'))
    wk.add_user(data)
    id = wk.get_user_id(data)
    return jsonify({'user_id': id})


@app.route('/add_current_task', methods=['POST'])
def add_current_task():
    """
    Inserts a task into the table work_tracker_log
    """
    data = json.loads(request.data.decode('utf-8'))
    wk.add_current_task(data)
    return jsonify('current task added')


@app.route('/delete_current_task', methods=['POST'])
def delete_current_task():
    """
    Inserts a task into the table work_tracker_log
    """
    data = json.loads(request.data.decode('utf-8'))
    wk.delete_current_task(data)
    return jsonify('current task deleted')


@app.route('/get_current_tasks', methods=['POST'])
def get_current_tasks():
    """
    Inserts a task into the table work_tracker_log
    """
    data = json.loads(request.data.decode('utf-8'))
    current_tasks = wk.get_current_tasks(data)
    return jsonify(current_tasks)


@app.route('/get_bar_data', methods=['POST'])
def get_bar_data():
    """
    Retrieves bar graph data for a particular user
    """
    data = json.loads(request.data.decode('utf-8'))
    print(data)
    bar_data = wk.get_bar_graph_data(data)
    return jsonify(bar_data)


@app.route('/get_line_data', methods=['POST'])
def get_line_data():
    """
    Retrieves line graph data for a particular user
    """
    data = json.loads(request.data.decode('utf-8'))
    print(data)
    line_data = wk.get_line_graph_data(data)
    return jsonify(line_data)


if __name__ == '__main__':
    app.run('0.0.0.0')
