import sys
import zmq

SERVER_IP = "ec2-54-164-205-229.compute-1.amazonaws.com"

if len(sys.argv) < 2:
    sys.exit("Must provide a username in order to connect to Dark Messenger.")

username = sys.argv[1]
PORT = "9000"
if len(sys.argv) > 3:
    PORT = sys.argv[2]
PORT = int(PORT)

ctx = zmq.Context()
req_socket = ctx.socket(zmq.REQ)
sub_socket = ctx.socket(zmq.SUB)

print "Connecting to message server..."
req_socket.connect("tcp://{}:{}".format(SERVER_IP, PORT))
print "Subscribing to message server..."
sub_socket.connect("tcp://{}:{}".format(SERVER_IP, PORT + 1))
sub_socket.setsockopt(zmq.SUBSCRIBE, "")

req_socket.send_json({"type": "CREATE_USER", "username": username})
resp = req_socket.recv_json()
if resp.get("success") is True:
    print "Successfully connected as user {}".format(username)
else:
    sys.exit("we failed")

groups = []
while True:
    resp = sub_socket.recv_json()
    resp = resp[0] if type(resp) == list else resp
    if resp.get("topic") != username:
        continue

    if resp.get("type") == "NEW_DIRECT_MESSAGE":
        print "Received new message from {}: {}".format(resp["from"], resp["msg"])
    elif resp.get("type") == "NEW_GROUP_MESSAGE":
        print "Received new message from {} in group {}: {}".format(
            resp["from"], resp["group"], resp["msg"])
    elif resp.get("type") == "NEW_GROUP":
        groups.append(resp["name"])
        print "Created a new group {} with members {}".format(resp["name"], resp["members"])
    else:
        print "Invalid message from server: {}".format(resp)

    resp = raw_input("Would you like to send a message? (Y/N) ")
    if resp.strip()[0].upper() != "Y":
        continue

    req = {"sender": username}
    resp = raw_input("Would you like to send your message to a new group(0), an existing group(1),"
                     + " or individual(2)? ")
    if resp.strip()[0] == "0":
        resp = raw_input("What is the name of the group you would like to create? ")
        req["type"] = "SEND_GROUP_MESSAGE"
        req["recipient"] = resp.strip()

        resp = raw_input("Enter the names of the users you would like in the group, not including"
                         + " yourself, separated by the pipe symbol (|): ")
        req["members"] = resp.split("|")

        req_socket.send_json({
            "type": "CREATE_GROUP",
            "name": req["recipient"],
            "members": map(lambda member: member.strip(), req["members"])}
        )
        resp = req_socket.recv_json()
        if resp.get("success") is True:
            print "Successfully created group {}".format(req["recipient"])
        else:
            sys.exit("we failed")
    elif resp.strip()[0] == "1":
        resp = raw_input("What group would you like to send your message to? ")
        req["type"] = "SEND_GROUP_MESSAGE"
        if resp.strip() in groups:
            req["recipient"] = resp.strip()
        else:
            sys.exit("You are not a member of that group.")
    elif resp.strip()[0] == "2":
        resp = raw_input("Who would you like to send your message to? ")
        req["type"] = "SEND_DIRECT_MESSAGE"
        req["recipient"] = resp.strip()
    else:
        print "Invalid option."
        continue

    resp = raw_input("Enter the message you'd like to send:\n")
    req["msg"] = resp.strip()
    print req
    req_socket.send_json(req)
    resp = req_socket.recv_json()
    if resp.get("success") is True:
        print "Successfully sent message to {}".format(req["recipient"])
    else:
        sys.exit("we failed")
