from flask import Flask, render_template, request, jsonify, g
from flask_cors import cross_origin
import sqlite3
import logging
from logging.handlers import RotatingFileHandler
import sys
import os

# App Configuration
app = Flask(__name__)
DATABASE = 'data.db'
LOG_FILE = 'app.log'

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configure logging
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# File handler
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10000, backupCount=3)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
logger.addHandler(file_handler)

app.logger.handlers = logger.handlers

# Database Functions
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db_schema():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                ip TEXT NOT NULL,
                min INTEGER NOT NULL,
                max INTEGER NOT NULL
            )
        ''')
        db.commit()

# Request handlers
@app.before_request
def before_request():
    app.logger.info(f'Request: {request.method} {request.path} from {request.remote_addr}')

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Routes
@app.route('/')
@cross_origin()
def index():
    return render_template('./website.html')

@app.route('/init_db')
@cross_origin()
def init_db():
    try:
        init_db_schema()
        app.logger.info('Database initialized successfully')
        return jsonify({"message": "Database initialized successfully!"}), 200
    except Exception as e:
        app.logger.error(f'Database initialization failed: {str(e)}')
        return jsonify({"error": str(e)}), 500

@app.route('/entries')
@cross_origin()
def get_entries():
    try:
        db = get_db()
        cursor = db.execute('SELECT * FROM entries')
        entries = [dict(row) for row in cursor.fetchall()]
        app.logger.info(f'Retrieved {len(entries)} entries')
        return jsonify(entries), 200
    except Exception as e:
        app.logger.error(f'Failed to retrieve entries: {str(e)}')
        return jsonify({"error": str(e)}), 500

@app.route('/add_entry', methods=['POST'])
@cross_origin()
def add_entry(): 
    data = request.get_json()
    if not data or not all(key in data for key in ('title', 'ip', 'min', 'max')):
        app.logger.warning(f'Invalid input data received: {data}')
        return jsonify({"error": "Invalid input data"}), 400

    try:
        db = get_db()
        db.execute(
            'INSERT INTO entries (title, ip, min, max) VALUES (?, ?, ?, ?)',
            (data['title'], data['ip'], data['min'], data['max'])
        )
        db.commit()
        app.logger.info(f'Added new entry: {data["title"]}')
        return jsonify({"message": "Entry added successfully!"}), 201
    except Exception as e:
        app.logger.error(f'Failed to add entry: {str(e)}')
        return jsonify({"error": str(e)}), 500

@app.route('/delete_entry/<int:id>', methods=['DELETE'])
@cross_origin()
def delete_entry(id):
    try:
        db = get_db()
        cursor = db.execute('SELECT * FROM entries WHERE id = ?', (id,))
        entry = cursor.fetchone()
        if not entry:
            app.logger.warning(f'Attempted to delete non-existent entry: {id}')
            return jsonify({"error": "Entry not found"}), 404

        db.execute('DELETE FROM entries WHERE id = ?', (id,))
        db.commit()
        app.logger.info(f'Deleted entry: {id}')
        return jsonify({"message": "Entry deleted successfully!"}), 200
    except Exception as e:
        app.logger.error(f'Failed to delete entry {id}: {str(e)}')
        return jsonify({"error": str(e)}), 500

@app.route('/update_entry/<int:id>', methods=['PUT'])
@cross_origin()
def update_entry(id):
    data = request.get_json()
    if not data or not all(key in data for key in ('title', 'ip', 'min', 'max')):
        app.logger.warning(f'Invalid update data received for entry {id}: {data}')
        return jsonify({"error": "Invalid input data"}), 400

    try:
        db = get_db()
        db.execute(
            'UPDATE entries SET title = ?, ip = ?, min = ?, max = ? WHERE id = ?',
            (data['title'], data['ip'], data['min'], data['max'], id)
        )
        db.commit()
        
        if db.total_changes == 0:
            app.logger.warning(f'Attempted to update non-existent entry: {id}')
            return jsonify({"error": "Entry not found"}), 404
        
        app.logger.info(f'Updated entry: {id}')
        return jsonify({"message": "Entry updated successfully!"}), 200
    except Exception as e:
        app.logger.error(f'Failed to update entry {id}: {str(e)}')
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db_schema()
    app.run(debug=True, host='0.0.0.0', port=8001)
