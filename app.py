from flask import Flask, g

from db import connect_db, get_db

app = Flask(__name__)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        
@app.route('/members', methods=['GET'])
def get_members():
    return 'Returns all members'

@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    return 'Returns a single member'

@app.route('/members', methods=['POST'])
def add_member():
    return 'Adds a member'

@app.route('/members/<int:member_id>', methods=['PUT', 'PATCH'])
def update_member(member_id):
    return 'Updates a member'

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    return 'Deletes member'
    
if __name__ == '__main__':
    app.run(debug=True)
