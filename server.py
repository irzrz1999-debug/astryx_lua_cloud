from flask import Flask, request, jsonify
import time
import json

app = Flask(__name__)
users = {}
CLEANUP_INTERVAL = 30

def cleanup_stale():
    now = time.time()
    for uid in list(users.keys()):
        if now - users[uid]['last_seen'] > 30:
            del users[uid]

@app.route('/update', methods=['GET'])
def update():
    key = request.args.get('key')
    data = request.args.get('data')
    if not key or not data:
        return 'Missing key or data', 400
    try:
        payload = json.loads(data)
    except:
        return 'Invalid JSON', 400

    local = payload.get('local_player')
    if not local:
        return 'No local_player', 400
    name = local.get('name')
    server_ip = local.get('server_ip')
    if not name:
        return 'Missing name', 400

    user_id = f"{key}|{server_ip}"
    users[user_id] = {
        'name': name,
        'server_ip': server_ip,
        'last_seen': time.time(),
        'username': payload.get('username', ''),
        'version': payload.get('version', '')
    }
    cleanup_stale()
    current_names = [u['name'] for u in users.values() if u['name'] != name]
    return jsonify(current_names)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'online': len(users)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=62930)