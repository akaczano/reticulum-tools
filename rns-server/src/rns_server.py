import os
import asyncio
from threading import Thread, Event, Lock
import json
import uuid
from sqlalchemy import CursorResult, Engine, select, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import time
import datetime

import RNS
import constants
from tables import Message, Contact


class Server:
    def __init__(self, rns, database: Engine):        
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
        
    def status(self):
        return {
            "hash": RNS.prettyhexrep(self.destination.hash)[1:-1],
            "name": self.name
        }



    def run(self):
        while not self.stop_signal.is_set():
            self.destination.announce(("name:" + self.name).encode())
            time.sleep(5)
    

    def process_packet(self, message: dict, status, packet_hash, rtt=None):
        print("Packet processed", packet_hash)
        rssi = None
        snr = None                
        
        if self.reticulum.is_connected_to_shared_instance:
            rssi = self.reticulum.get_packet_rssi(packet_hash)
            snr  = self.reticulum.get_packet_snr(packet_hash)

        with Session(self.database) as session: 


            update_stmt = update(Message).where(Message.id == message["id"]).values(
                status=status,
                rtt=rtt,
                rssi=rssi,
                snr=snr,
                time_received=datetime.datetime.now()
            )
            update_result: CursorResult = session.execute(update_stmt)

            if update_result.rowcount < 1:
                # There did not already exist a matching message record
                record = Message(
                    id = message["id"],
                    source = message["source"],
                    destination = message["destination"],
                    text = message["text"],                
                    time_sent = datetime.datetime.fromisoformat(message["timestamp"]),
                    status=status,
                    rtt=rtt,
                    rssi=rssi,
                    snr=snr,
                    time_received=datetime.datetime.now()
                )
                session.add(record)
            
            session.commit()


    def packet_received(self, message, packet: RNS.Packet):
        json_str = message.decode()
        payload = json.loads(json_str)        
        self.process_packet(payload,  RNS.PacketReceipt.DELIVERED, packet.packet_hash)
        

    def received_announce(self, destination_hash, announced_identity, app_data):   
        if not app_data:
            return
    
    
        hash = RNS.prettyhexrep(destination_hash)[1:-1]            
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

    def build_message(self, hash, text):
        message = {}
        message["id"] = str(uuid.uuid4())
        message["text"] = text
        message["source"] = RNS.prettyhexrep(self.destination.hash)[1:-1]        
        message["timestamp"] = datetime.datetime.now().isoformat()

        with Session(self.database) as session:            
            user_record = session.query(Contact).where(Contact.hash == hash).one_or_none()
            if user_record:
                message["destination"] = user_record.hash
            else:
                raise ValueError("Couldn't find user with hash " + hash)     

        return message
      

    def do_send(self, hash, text, timeout, loop=None, future=None):
        message = self.build_message(hash, text)

        destination_hash_str = message["destination"]   

        
        destination_hash = bytes.fromhex(destination_hash_str)      

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
        
        packet = RNS.Packet(request_destination, payload.encode())                   


        def packet_delivered(r: RNS.PacketReceipt):   
            self.process_packet(message, r.status, r.proof_packet.packet_hash, r.get_rtt())
            if loop:
                loop.call_soon_threadsafe(future.set_result, r)

        def packet_timed_out(r: RNS.PacketReceipt): 
            with Session(self.database) as session: 
                stmt = update(Message).where(Message.id == message["id"]).values(
                    status=RNS.PacketReceipt.FAILED
                )
                session.execute(stmt)
                session.commit()  
            if loop:
                loop.call_soon_threadsafe(future.set_result, r) 


        record = Message(
            id = message["id"],
            source = message["source"],
            destination = message["destination"],
            text = message["text"],                
            time_sent = datetime.datetime.fromisoformat(message["timestamp"]),
            status = RNS.PacketReceipt.SENT
        )
        with Session(self.database) as session:
            session.add(record)
            session.commit()   

        packet_receipt: RNS.PacketReceipt = packet.send()  
        packet_receipt.set_timeout(timeout)
        packet_receipt.set_timeout_callback(packet_timed_out)
        packet_receipt.set_delivery_callback(packet_delivered)                                     
            
        return message
        

    async def send_message(self, hash, text, timeout):        
        loop = asyncio.get_running_loop()    
        future = loop.create_future()
        message = self.do_send(hash, text, timeout, loop=loop, future=future)
        result: RNS.PacketReceipt = await future

        message["status"] = result.get_status()

        return message
        