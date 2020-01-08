from flask import Flask, g, request, jsonify

from db import connect_db, get_db

app = Flask(__name__)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        
@app.route('/members', methods=['GET'])
def get_members():
    db = get_db()
    members_query = db.execute('select id, name, email, level from members')
    members_result = members_query.fetchall()

    members_list = [
        {
            'id': m['id'],
            'name': m['name'],
            'email': m['email'],
            'level': m['level']
        } for m in members_result
    ]

    return jsonify(members_list)

@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    return 'Returns a single member'

@app.route('/members', methods=['POST'])
def add_member():
    db = get_db()

    new_member = request.get_json()
    name = new_member['name']
    email = new_member['email']
    level = new_member['level']

    existing_member_query = db.execute('select name, id from members where email = ?', [email])
    already_exists = existing_member_query.fetchone()

    if already_exists:
        return 'A member with that email address already exists', 409

    db.execute('insert into members (name, email, level) values (?, ?, ?)', [name, email, level])
    db.commit()

    member_query = db.execute('select id, name, email, level from members where email = ?', [email])
    member_record = member_query.fetchone()
    member_response = {
        'id': member_record['id'],
        'email': member_record['email'],
        'name': member_record['name'],
        'level': member_record['level']
    }

    return jsonify(member_response)

@app.route('/members/<int:member_id>', methods=['PUT', 'PATCH'])
def update_member(member_id):
    return 'Updates a member'

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    return 'Deletes member'
    
if __name__ == '__main__':
    app.run(debug=True)
