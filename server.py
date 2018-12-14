import time
import zmq
from collections import deque
from influxdb import client as influxdb

print "A"
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
print "B"

context = zmq.Context()
# The socket used to listen for incoming messages
reply_socket = context.socket(zmq.REP)
reply_socket.bind("tcp://*:9000")
print "C"
# The socket used to send out messages
pub_socket = context.socket(zmq.PUB)
pub_socket.bind("tcp://*:9001")
print "D"


def createUser(command, current_db):
    print "Adding a user"


def createGroup(command, current_db):
    print "Creating a group..."
    group_name = command["name"]
    members = command["members"]
    for member in members:
        new_group = [{
            'measurement': 'msg_groups',
            'fields': {
                'id': group_name,
                'member': member,
            }
        }]
        current_db.write_points(new_group)

    for member in members:
        if member != members[0]:
            message = [{
                'topic': member,
                'type': 'NEW_GROUP',
                'members': list(filter(lambda x: x != member, members)),
                'name': group_name
            }]
            pub_socket.send_json(message)


def writeToDatabase(sender, recipient, msg, isGroup, current_db):

    mailbox_entries = []

    # If this is a direct message
    if not isGroup:

        # Write this message in the sender's mailbox
        mailbox_entries.append({
            'measurement': 'msgs',
            'fields': {
                'from': sender,
                'mailbox': sender,
                'msg': msg,
                'chatname': recipient
            }
        })

        # Write this message in the recipient's mailbox
        mailbox_entries.append({
            'measurement': 'msgs',
            'fields': {
                'from': sender,
                'mailbox': recipient,
                'msg': msg,
                'chatname': sender
            }
        })

    # This is a group chat
    else:
        # Find all the members in this group
        group_members = current_db.query(
            "SELECT member from msg_groups WHERE id='" + str(recipient) + "'").get_points()

        # Write this message in each of the members' mailboxes
        for val in group_members:
            mailbox_entries.append({
                'measurement': 'msgs',
                'fields': {
                    'from': sender,
                    'mailbox': val['member'],
                    'msg': msg,
                    'chatname': recipient
                }
            })

    current_db.write_points(mailbox_entries)


def sendMessage(command, isGroup, current_db):

    # Parse the command
    sender = command["sender"]
    recipient = command["recipient"]
    msg = command["msg"]

    writeToDatabase(sender, recipient, msg, isGroup, current_db)

    messages = []
    # If a direct message
    if not isGroup:
        print "Sending a direct message..."
        message = {
            'topic': recipient,
            'type': 'NEW_DIRECT_MESSAGE',
            'from': sender,
            'msg': msg,
        }
        messages.append(message)
    # If a group message
    else:
        print "Sending a group message..."
        group_members = current_db.query(
            "SELECT member from msg_groups WHERE id='" + str(recipient) + "'").get_points()
        for val in group_members:
            message = {
                'topic': val['member'],
                'type': 'NEW_GROUP_MESSAGE',
                'from': sender,
                'group': recipient,
                'msg': msg
            }
            messages.append(message)

    print messages
    for message in messages:
        print message
        pub_socket.send_json(message)


def main():
    print "Starting messaging server now..."

    # Create a queue of our Influx instances
    queue = deque([mydb1, mydb2, mydb3])

    while True:
        # Round robin select the next Influx instance to use
        current_db = queue.popleft()
        queue.append(current_db)

        message = reply_socket.recv_json()
        print "Received a message: " + str(message)

        if message["type"] == "CREATE_USER":
            createUser(message, current_db)
        elif message["type"] == "CREATE_GROUP":
            createGroup(message, current_db)
        elif message["type"] == "SEND_DIRECT_MESSAGE":
            sendMessage(message, False, current_db)
        elif message["type"] == "SEND_GROUP_MESSAGE":
            sendMessage(message, True, current_db)
        else:
            print "Invalid command type specified."
            reply_socket.send_json({"success": False})
            continue

        reply_socket.send_json({"success": True})

        time.sleep(1)
        pub_socket.send_json({"topic": "varun"})


if __name__ == "__main__":
    main()
