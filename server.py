import sys
import zmq
from collections import deque
from influxdb.client import InfluxDBClientError
from influxdb import client as influxdb

influx_ip = ['ec2-52-23-246-145.compute-1.amazonaws.com',
             'ec2-52-90-226-153.compute-1.amazonaws.com',
             'ec2-52-200-205-8.compute-1.amazonaws.com']

# set up Influx databases
mydb1 = influxdb.InfluxDBClient(
    influx_ip[0], 8086, 'admin', 'dubey', 'messenger')
mydb2 = influxdb.InfluxDBClient(
    influx_ip[1], 8086, 'admin', 'dubey', 'messenger')
mydb3 = influxdb.InfluxDBClient(
    influx_ip[2], 8086, 'admin', 'dubey', 'messenger')

context = zmq.Context()
# The socket used to listen for incoming messages
reply_socket = context.socket(zmq.REP)
reply_socket.bind("tcp://*:9000")

# The socket used to send out messages
pub_socket = context.socket(zmq.PUB)
pub_socket.bind("tcp://*:9001")


def createUser(message, current_db):
    # topic_name = message[7, :]
    # topics.append(topic_name)
    print "Adding a user"


def createGroup(message, current_db):
    print "Creating a group..."
    group_name = message["name"]
    members = message["members"]
    for member in members:
        new_group = [{
            'measurement': 'groups',
            'fields': {
                'id': group_name,
                'members': member,
            }
        }]
        current_db.write_points(new_group)

    for member in members:
        if member != members[0]:
            topic = "/" + str(member)
            message = [{
                'type': 'NEW_GROUP',
                'members': members.filter(lambda x: x != member),
                'name': group_name
            }]
            socket_server_pub.send_json(topic, message)


def writeToDatabase(message, current_db):

    # Parse the message
    sender = message["sender"]
    receiver = message["receiver"]
    message = message["message"]
    isGroup = message["isGroup"]

    # If this is a one-to-one message
    if not isGroup:

        # Write this message in the reciever's mailbox
        sender_mailbox = [{
            'measurement': 'msgs',
            'fields': {
                'from': sender,
                'mailbox': sender,
                'msg': msg,
                'chatname': receiver
            }
        }]

        # Write this message in the sender's mailbox
        receiver_mailbox = [{
            'measurement': 'msgs',
            'fields': {
                'from': sender,
                'mailbox': receiver,
                'msg': msg,
                'chatname': sender
            }
        }]

        current_db.write_points(sender_mailbox)
        current_db.write_points(receiver_mailbox)

    # This is a group chat
    else:

        # Find all the members in this group
        group_members = list(current_db.query("SELECT * from msg_groups WHERE id='" + str(receiver) + "'").get_points())

        # Write this message in each of the members' mailboxes
        for mem in group_members:
            current_db.write_points([{
                'measurement': 'msgs',
                'fields': {
                    'from': sender,
                    'mailbox': mem,
                    'msg': msg,
                    'chatname': receiver
                }
            }])


def sendMessage(message, current_db):

    # Parse the message
    sender = message["sender"]
    receiver = message["receiver"]
    message = message["message"]
    isGroup = message["isGroup"]

    topics = []
    # If a single message
    if not isGroup:
        print "Sending a one-to-one message..."
        topics.append("/" + str(receiver))
    # If a group message
    else:
        print "Sending a group message..."
        group_members = list(current_db.query("SELECT * from msg_groups WHERE id='" + str(receiver) + "'").get_points())
        for member in group_members:
            topics.append(i)

    for topic in topics:
        pub_socket.send("%d %d" % (topic, message))


def main():
    print "Starting messaging server now..."

    # Create a queue of our Influx instances
    queue = deque([mydb1, mydb2, mydb3])

    while True:
        # Round robin select the next Influx instance to use
        current_db = queue.popleft()
        queue.append(current_db)

        message = reply_socket.recv_json()
        print "Recieved a message: " + str(message)

        if message["type"] == "CREATE_USER":
            createUser(message, current_db)
        elif message["type"] == "CREATE_GROUP":
            createGroup(message, current_db)
        else:
            writeToDatabase(message, current_db)
            sendMessage(message, current_db)
        reply_socket.send_json({"success": True})


if __name__ == "__main__":
    main()
