import RNS
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import tables
import constants
from rns_server import Server

app = Flask(__name__)
CORS(app)

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

def validate_message(data):        
    resp = None
    if "hash" not in data:
        resp = {"message": "Request must include a destination hash"}
    elif "message" not in data:
        resp = {"message": "Request must include a message"}
    if resp:
        response = jsonify(resp)
        response.status_code = 400
        abort(response)

@app.route('/status', methods=['GET'])
def status():
    global server
    return jsonify(server.status())

@app.route('/interfaces', methods=['GET'])
def interfaces():    
    global reticulum
    stats = reticulum.get_interface_stats()            
    return jsonify(cleanup_bytes(stats))

@app.route('/paths', methods=['GET'])
def paths():
    global reticulum
    table = reticulum.get_path_table()    
    return jsonify(cleanup_bytes(table))

@app.route('/send', methods=['POST'])
async def send():
    global server
    data = request.get_json()
    
    validate_message(data)

    timeout = data["timeout"] if "timeout" in data else constants.DEFAULT_TIMEOUT    
    result = await server.send_message(data["hash"], data["message"], timeout)
    return jsonify(result)    

@app.route('/submit', methods=['POST'])
def submit():
    global server
    data = request.get_json()

    validate_message(data)
    
    timeout = data["timeout"] if "timeout" in data else constants.DEFAULT_TIMEOUT    
    message = server.do_send(data["hash"], data["message"], timeout)
    return jsonify(message)

@app.route('/contacts', methods=['GET'])
def contacts():
    global engine
    results = []
    with Session(engine) as session:
        stmt = select(tables.Contact)
        for contact in session.scalars(stmt):
            results.append({                
                "hash": contact.hash,
                "name": contact.name
            })
    return jsonify(results)
        

@app.route('/messages', methods=['GET'])
def messages():
    #TODO add query params
    global engine
    results = []
    with Session(engine) as session:
        stmt = select(tables.Message)
        for msg in session.scalars(stmt):
            results.append({
                "id": msg.id,
                "text": msg.text,
                "source": msg.source,
                "destination": msg.destination,
                "status": msg.status,
                "time_sent": msg.time_sent,
                "time_received": msg.time_received,                                
                "rtt": msg.rtt,
                "rssi": msg.rssi,
                "snr": msg.snr
            })
    return jsonify(results)



if __name__ == '__main__':
    global server
    global engine 
    global reticulum
    reticulum = RNS.Reticulum()
    engine = create_engine("sqlite:///" + constants.DATABASE_PATH)
    server = Server(reticulum, engine)
    tables.Base.metadata.create_all(engine)    
    server.start_announcing()
    app.run(debug=True, host="0.0.0.0", port=5000)