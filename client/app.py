import sys
import zmq

SERVER_IP = "ec2-54-164-205-229.compute-1.amazonaws.com"

if len(sys.argv) < 1:
    sys.exit("Must provide a username in order to connect to Dark Messenger.")

username = sys.argv[1]
PORT = "9000"
if len(sys.argv) > 2:
    PORT = sys.argv[2]
PORT = int(PORT)

# Socket to talk to server
ctx = zmq.Context()
req_socket = ctx.socket(zmq.REQ)
sub_socket = ctx.socket(zmq.SUB)

print "Connecting to message server..."
req_socket.connect("tcp://{}:{}".format(SERVER_IP, PORT))
print "Subscribing to message server..."
sub_socket.connect("tcp://{}:{}".format(SERVER_IP, PORT + 1))

req_socket.send_json({"type": "CREATE_USER", "username": username})
resp = req_socket.recv_json()
if resp.get("success") is True:
    print "Successfully connected as user {}".format(username)
else:
    sys.exit("we failed")

sub_socket.setsockopt(zmq.SUBSCRIBE, "5256")
while True:
    new_msg = sub_socket.recv()
    print "wat"
    print new_msg
