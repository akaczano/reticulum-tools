import argparse
import sys
import RNS

APP_NAME = "rns_test_suite"

def client(destination_hexhash, configpath, timeout=None):    

    try:
        dest_len = (RNS.Reticulum.TRUNCATED_HASHLENGTH // 8) * 2
        if len(destination_hexhash) != dest_len:
            raise ValueError("Destination length is invalid")

        destination_hash = bytes.fromhex(destination_hexhash)
    except Exception as e:
        RNS.log("Invalid destination entered. Check your input!")
        RNS.log(str(e) + "\n")
        sys.exit(0)

    reticulum = RNS.Reticulum(configpath)

    if RNS.loglevel < RNS.LOG_INFO:
        RNS.loglevel = RNS.LOG_INFO

    RNS.log(
        "Echo client ready, hit enter to send echo request to " +
        destination_hexhash +
        " (Ctrl-C to quit)"
    )

    
    while True:
        message = input()

        if RNS.Transport.has_path(destination_hash):
            
            server_identity = RNS.Identity.recall(destination_hash)
            request_destination = RNS.Destination(
                server_identity,
                RNS.Destination.OUT,
                RNS.Destination.SINGLE,
                APP_NAME,
                "echo",
                "server"
            )


            echo_request = RNS.Packet(request_destination, RNS.Identity.get_random_hash())            
            packet_receipt = echo_request.send()

            if timeout != None:
                packet_receipt.set_timeout(timeout)
                packet_receipt.set_timeout_callback(packet_timed_out)

            #packet_receipt.set_delivery_callback(packet_delivered)

            RNS.log("Sent echo request to " + RNS.prettyhexrep(request_destination.hash))
        else:
            RNS.log("Destination is not yet known. Requesting path...")
            RNS.log("Hit enter to manually retry once an announce is received.")
            RNS.Transport.request_path(destination_hash)

def packet_timed_out(receipt):
    if receipt.status == RNS.PacketReceipt.FAILED:
        RNS.log("Packet "+RNS.prettyhexrep(receipt.hash)+" timed out")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Simple messaging client for reticulum")
        
        parser.add_argument(
            "-c",
            "--config",
            action="store"
        )

        parser.add_argument("destination")

        args = parser.parse_args()

        configarg = None
        if args.config:
            configarg = args.config
        

        client(args.destination, configarg, 2000)
    except KeyboardInterrupt:
        print("")
        sys.exit(0)

