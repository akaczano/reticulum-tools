import argparse
import sys
import RNS

APP_NAME = "rns_test_suite"

def server(configpath):
    global reticulum

    reticulum = RNS.Reticulum(configpath)
    server_identity = RNS.Identity()

    echo_destination = RNS.Destination(
        server_identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        "echo",
        "server"
    )


    echo_destination.set_proof_strategy(RNS.Destination.PROVE_ALL)
    echo_destination.set_packet_callback(server_callback)

    announceLoop(echo_destination)


def announceLoop(destination):
    RNS.log(
        "Echo server " + 
        RNS.prettyhexrep(destination.hash) +
        " running, hit enter to manually send an announce (Ctrl-C to quit)"
    )

    while True:
        input()
        destination.announce()
        RNS.log("Sent announce from " + RNS.prettyhexrep(destination.hash))

def server_callback(message, packet):
    global reticulum    

    reception_stats = ""    
    
    if reticulum.is_connected_to_shared_instance:
        reception_rssi = reticulum.get_packet_rssi(packet.packet_hash)
        reception_snr = reticulum.get_packet_snr(packet.packet_hash)

        if reception_rssi != None:
            reception_stats += " [RSS " + str(reception_rssi) + " dBm]"

        if reception_snr != None:
            reception_stats += " [SNR " + str(reception_snr) + " dBm]"

    else:
        if packet.rssi != None:
            reception_stats += " [RRSI " + str(packet.rssi) + " dBm]"
        if packet.snr != None:
            reception_stats += " [SNR " + str(packet.snr) + " dB]"

    RNS.log("Received packet from echo client, proof sent" + reception_stats + str(len(message)))

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Simple messaging client for reticulum")
        
        parser.add_argument(
            "-c",
            "--config",
            action="store"
        )
        
        

        args = parser.parse_args()

        configarg = None
        if args.config:
            configarg = args.config
        

        server(configarg)
    except KeyboardInterrupt:
        print("")
        sys.exit(0)


