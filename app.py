from functools import wraps
from flask import Flask, g, request, jsonify

from db import connect_db, get_db

app = Flask(__name__)


api_user = 'admin'
api_password = 'admin'

def protected(view):
    @wraps(view)
    def decorated_view(*args, **kwargs):
        auth = request.authorization

        if not auth:
            return jsonify({'message': 'No authentication headers present in request.'}), 403

        if auth.username == api_user and auth.password == api_password:
            return view(*args, **kwargs)
        else:
            return jsonify({'message': 'Authentication failed.'}), 403

    return decorated_view
    
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/members', methods=['GET'])
@protected
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

    return jsonify({'members': members_list})

@app.route('/members/<int:member_id>', methods=['GET'])
@protected
def get_member(member_id):
    db = get_db()
    member_query = db.execute('select id, name, email, level from members where id = ?', [int(member_id)])
    member_record = member_query.fetchone()

    if not member_record:
        return jsonify({'error': f'No member found with id {member_id}'}), 404

    member = {
        'id': member_record['id'],
        'name': member_record['name'],
        'email': member_record['email'],
        'level': member_record['level']
    }

    return jsonify({'member': member})

@app.route('/members', methods=['POST'])
@protected
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
@protected
def update_member(member_id):
    db = get_db()

    if request.method == 'PUT':
        error = None
        fields = ['name', 'email', 'level']
        request_json = request.get_json()

        for field in fields:
            if not field in request_json:
                error = f'Some required fields missing. If you are trying to update a single field, please make a PATCH request instead of PUT. Missing field: {field}'
                return jsonify({'error': error}), 400

        name = request_json['name']
        email = request_json['email']
        level = request_json['level']

        db.execute('update members set name = ?, email = ?, level = ? where id = ?', [name, email, level, member_id])
        db.commit()

    if request.method == 'PATCH':
        update_json = request.get_json()
        existing_member_query = db.execute('select id, name, email, level from members where id = ?', [member_id])
        existing_member = existing_member_query.fetchone()
        name = 'name' in update_json and update_json['name'] or existing_member['name']
        email = 'email' in update_json and update_json['email'] or existing_member['email']
        level = 'level' in update_json and update_json['level'] or existing_member['level']

        db.execute('update members set name = ?, email = ?, level = ? where id = ?', [name, email, level, member_id])
        db.commit()

    # Always query for and return the updated member record, regardless of method
    member_query = db.execute('select id, name, email, level from members where id = ?', [member_id])
    member_record = member_query.fetchone()
    result = {
        'id': member_record['id'],
        'name': member_record['name'],
        'email': member_record['email'],
        'level': member_record['level']
    }

    return jsonify({'member': result})

@app.route('/members/<int:member_id>', methods=['DELETE'])
@protected
def delete_member(member_id):
    db = get_db()
    member_query = db.execute('select id, name, email, level from members where id = ?', [member_id])
    member_record = member_query.fetchone()

    if not member_record:
        return jsonify({'error': f'No member found with id: {member_id}'}), 404

    result = {
        'id': member_record['id'],
        'name': member_record['name'],
        'email': member_record['email'],
        'level': member_record['level']
    }

    db.execute('delete from members where id = ?', [member_id])
    db.commit()

    return jsonify({'message': f'Deleted member number {member_id}', 'member': result})

if __name__ == '__main__':
    app.run()
