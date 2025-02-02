from flask import Flask, render_template, request, jsonify, g
from flask_cors import cross_origin
import sqlite3


app = Flask(__name__)
DATABASE = 'data.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row 
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET'])
@cross_origin()
def index():
   return render_template('./website.html')

@app.route('/init_db', methods=['GET'])
@cross_origin()
def init_db():
    try:
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
        return jsonify({"message": "Database initialized successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/entries', methods=['GET'])
@cross_origin()
def get_entries():
    try:
        db = get_db()
        cursor = db.execute('SELECT * FROM entries')
        entries = [dict(row) for row in cursor.fetchall()]
        return jsonify(entries), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/add_entry', methods=['POST'])
@cross_origin()
def add_entry():
    data = request.get_json()
    if not data or not all(key in data for key in ('title', 'ip', 'min', 'max')):
        return jsonify({"error": "Invalid input data"}), 400

    try:
        db = get_db()
        db.execute(
            'INSERT INTO entries (title, ip, min, max) VALUES (?, ?, ?, ?)',
            (data['title'], data['ip'], data['min'], data['max'])
        )
        db.commit()
        return jsonify({"message": "Entry added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/delete_entry/<int:id>', methods=['DELETE'])
@cross_origin()
def delete_entry(id):
    try:
        db = get_db()
        cursor = db.execute('SELECT * FROM entries WHERE id = ?', (id,))
        entry = cursor.fetchone()

        if not entry:
            return jsonify({"error": "Entry not found"}), 404

        db.execute('DELETE FROM entries WHERE id = ?', (id,))
        db.commit()

        return jsonify({"message": "Entry deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/update_entry/<int:id>', methods=['PUT'])
@cross_origin()
def update_entry(id):
    data = request.get_json()
    if not data or not all(key in data for key in ('title', 'ip', 'min', 'max')):
        return jsonify({"error": "Invalid input data"}), 400

    try:
        db = get_db()
        db.execute(
            'UPDATE entries SET title = ?, ip = ?, min = ?, max = ? WHERE id = ?',
            (data['title'], data['ip'], data['min'], data['max'], id)
        )
        db.commit()
        
        # Check if any rows were updated
        if db.total_changes == 0:
            return jsonify({"error": "Entry not found"}), 404
        
        return jsonify({"message": "Entry updated successfully!"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)
