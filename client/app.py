import sys
import zmq

SERVER_IP = "ec2-54-164-205-229.compute-1.amazonaws.com"

if len(sys.argv) < 1:
    sys.exit("Must provide a username in order to connect to Dark Messenger.")

user_id = sys.argv[1]
PORT = "5555"
if len(sys.argv) > 2:
    PORT = sys.argv[2]
    int(PORT)

# Socket to talk to server
ctx = zmq.Context()
socket = ctx.socket(zmq.SUB)

print "Receiving messages from message server..."
socket.connect("{}:{}".format(SERVER_IP, PORT))
