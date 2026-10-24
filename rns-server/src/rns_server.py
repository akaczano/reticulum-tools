import os
import asyncio
from threading import Thread, Event, Lock
import json
import uuid
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import time
import datetime

import RNS
import constants
from tables import Message, Contact


class Server:
    def __init__(self, rns: RNS.Reticulum, database: Engine):        
        self.reticulum = rns
        self.database = database
        self.identity = self.__load_identity()
        self.name = os.getenv("USERNAME")
        if not self.name:
            self.name = RNS.prettyhexrep(self.identity.full_hash())
        print("Running messages app for user:  " + self.name)

        # Setup destination
        self.destination = RNS.Destination(
            self.identity,
            RNS.Destination.IN,
            RNS.Destination.SINGLE,
            constants.APP_NAME,
            *constants.ASPECTS
        )
        # Setup packet handler 
        self.destination.set_proof_strategy(RNS.Destination.PROVE_ALL)
        self.destination.set_packet_callback(self.packet_received)

        # Setup announce handler        
        self.announce_lock = Lock()
        self.processed_announces = set()
        self.aspect_filter = constants.APP_NAME + "." + ".".join(constants.ASPECTS)        
        RNS.Transport.register_announce_handler(self)


    def start_announcing(self):
        self.stop_signal = Event()
        self.announce_loop = Thread(target = self.run)
        self.announce_loop.start()        

    def stop_announcing(self):
        self.stop_signal.set()


    def __load_identity(self) -> RNS.Identity:
        if os.path.exists(constants.IDENTITY_PATH):        
            return RNS.Identity.from_file(constants.IDENTITY_PATH)
        else:
            server_identity = RNS.Identity()
            RNS.Identity.to_file(server_identity, constants.IDENTITY_PATH)
            return server_identity
        

    def run(self):
        while not self.stop_signal.is_set():
            self.destination.announce(("name:" + self.name).encode())
            time.sleep(5)

    def packet_received(self, message, packet):
        json_str = message.decode()
        payload = json.loads(json_str)
        print(payload)
        record = Message(
            id = payload["id"],
            source = payload["source"],
            text = payload["text"],
            timestamp = datetime.datetime.fromisoformat(payload["timestamp"])
        )
        with Session(self.database) as session:
            session.add(record)
            session.commit()

    def received_announce(self, destination_hash, announced_identity, app_data):   
        if not app_data:
            return
    
    
        hash = RNS.prettyhexrep(destination_hash)            
        info: str = app_data.decode()
        
        if not "name:" in info:
            return 

        name = info.split(":")[1]

        # TODO if name different than the one stored updated it
        with Session(self.database) as session:
            stmt = select(Contact).where(Contact.hash == hash).exists()

            if not session.scalar(select(stmt)):
                contact = Contact(
                    hash=hash,
                    name = name,
                    last_updated = datetime.datetime.now()
                )
                try:
                    session.add(contact)
                    session.commit()
                except IntegrityError:
                    print("Caught duplicate announce")                    

    async def send_message(self, user_id, text, timeout):        
        message = {}
        message["id"] = str(uuid.uuid4())
        message["text"] = text
        message["source"] = RNS.prettyhexrep(self.destination.hash)
        message["timestamp"] = datetime.datetime.now().isoformat()

        destination_hash_str = None

        with Session(self.database) as session:            
            user_record = session.query(Contact).where(Contact.id == user_id).one_or_none()
            if user_record:
                destination_hash_str = user_record.hash
            else:
                raise ValueError("Couldn't find user with ID " + str(user_id))           

        destination_hash = bytes.fromhex(destination_hash_str[1:-1])      

        if not RNS.Transport.await_path(destination_hash, timeout=timeout):
            return {
                "status": RNS.PacketReceipt.FAILED, 
                "message": "Timed out while finding path"
            }
        
        server_identity = RNS.Identity.recall(destination_hash)
        request_destination = RNS.Destination(
            server_identity,
            RNS.Destination.OUT,
            RNS.Destination.SINGLE,
            constants.APP_NAME,
            *constants.ASPECTS
        )
        payload = json.dumps(message)
        print(payload)
        
        
        echo_request = RNS.Packet(request_destination, payload.encode())   
        packet_receipt = echo_request.send()    

        loop = asyncio.get_running_loop()    
        future = loop.create_future()


        def packet_delivered(r: RNS.PacketReceipt):                
            loop.call_soon_threadsafe(future.set_result, r)

        def packet_timed_out(r: RNS.PacketReceipt):        
            loop.call_soon_threadsafe(future.set_result, r) 
        
        packet_receipt.set_timeout(timeout)
        packet_receipt.set_timeout_callback(packet_timed_out)
        packet_receipt.set_delivery_callback(packet_delivered)                                     

        result: RNS.PacketReceipt = await future
        
        return {
            "status": result.get_status(),
            "rtt": result.get_rtt()
        } 
        