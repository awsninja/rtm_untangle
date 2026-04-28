import os
from flask import Flask, request, jsonify
from state import manual_lock

app = Flask(__name__)
API_KEY = os.environ.get('API_KEY', '')
_kids = None


def init_app(kids_routine):
    global _kids
    _kids = kids_routine


def _authorized():
    if not API_KEY:
        return True
    return request.args.get('key') == API_KEY


@app.route('/lock', methods=['POST'])
def lock():
    if not _authorized():
        return jsonify({'error': 'unauthorized'}), 401
    minutes = int(request.args.get('minutes', 60))
    manual_lock.lock(minutes)
    if _kids:
        _kids.start_firewall()
    expires = manual_lock.expires_at()
    return jsonify({'status': 'locked', 'minutes': minutes, 'expires_at': str(expires)})


@app.route('/unlock', methods=['POST'])
def unlock():
    if not _authorized():
        return jsonify({'error': 'unauthorized'}), 401
    manual_lock.unlock()
    if _kids:
        _kids.stop_firewall()
    return jsonify({'status': 'unlocked'})


@app.route('/status', methods=['GET'])
def status():
    if not _authorized():
        return jsonify({'error': 'unauthorized'}), 401
    active = manual_lock.is_active()
    expires = manual_lock.expires_at()
    return jsonify({
        'manual_lock_active': active,
        'expires_at': str(expires) if expires else None,
    })
