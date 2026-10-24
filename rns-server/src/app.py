import RNS
from flask import Flask, jsonify, request, abort
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import tables
import constants
from rns_server import Server

app = Flask(__name__)


'''
    Values of the `bytes` type break the JSON serializer that flask
    uses. This function recursively replaces all of the raw hashes
    in a list or dictionary with the string representation that 
    reticulum generates.
'''
def cleanup_bytes(data):
    if isinstance(data, list):
        return [cleanup_bytes(item) for item in data]
    elif isinstance(data, dict):
        return {key: cleanup_bytes(data[key]) for key in data}
    elif isinstance(data, bytes):
        return RNS.prettyhexrep(data)
    else:
        return data


@app.route('/interfaces', methods=['GET'])
def interfaces():    
    stats = reticulum.get_interface_stats()            
    return jsonify(cleanup_bytes(stats))

@app.route('/paths', methods=['GET'])
def paths():
    table = reticulum.get_path_table()    
    return jsonify(cleanup_bytes(table))

@app.route('/send', methods=['POST'])
async def send():
    global server
    data = request.get_json()
    
    if "user" not in data:
        abort(400, "Request must include a destination")
    elif "message" not in data:
        abort(400, "Request must include a message")

    timeout = data["timeout"] if "timeout" in data else constants.DEFAULT_TIMEOUT
    try:
        result = await server.send_message(int(data["user"]), data["message"], timeout)
        return jsonify(result)
    except ValueError as e:
        abort(400, "Message validation error: " + str(e))
        

@app.route('/contacts', methods=['GET'])
def contacts():
    global engine
    results = []
    with Session(engine) as session:
        stmt = select(tables.Contact)
        for contact in session.scalars(stmt):
            results.append({
                "id": contact.id,
                "hash": contact.hash,
                "name": contact.name
            })
    return jsonify(results)
        

@app.route('/messages', methods=['GET'])
def messages():
    global engine
    results = []
    with Session(engine) as session:
        stmt = select(tables.Message)
        for msg in session.scalars(stmt):
            results.append({
                "id": msg.id,
                "text": msg.text,
                "source": msg.source,
                "timestamp": msg.timestamp
            })
    return jsonify(results)



if __name__ == '__main__':
    global server
    global engine
    reticulum = RNS.Reticulum()
    engine = create_engine("sqlite:///" + constants.DATABASE_PATH)
    server = Server(reticulum, engine)
    tables.Base.metadata.create_all(engine)    
    server.start_announcing()
    app.run(debug=True, host="0.0.0.0", port=5000)