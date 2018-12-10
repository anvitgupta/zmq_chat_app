import sys
import zmq
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
socket_server_sub.bind('ec2-54-164-205-229.compute-1.amazonaws.com:9000')

# The socket used to send out messages
socket_server_pub = context.socket(zmq.PUB)


def createUser(message, current_db):
    # topic_name = message[7, :]
    # topics.append(topic_name)


def createGroup(message, current_db):
    parts = message.split("|")
    group_members = '|'.join(map(str, parts[2, :]))
    new_group = [{
            'measurement': 'groups',
            'fields': {
                'id': str(parts[1]),
                'members': group_members,
            }
        }]
    current_db.write_points(new_group)

    for member in group_members:
                if member != sender
                    message = '|'.join(map(str, list(filter(lambda x: x != member, group)))) 
                    topic = "/" + str(member)
                    socket_server_pub.send("%d %d" % (topic, message))


def writeToDatabase(message, current_db):

    # Parse the message
    action, sender, receiver, msg, sg = message.split(" ")

    # If this is a one-to-one message
    if sg == '0':

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
        group = list(current_db.query("SELECT * from groups WHERE id='" + str(receiver) + "'").get_points())
        members = group['members'].split('|')

        # Write this message in each of the members' mailboxes
        for i in members:
            current_db.write_points([{
                'measurement': 'msgs',
                'fields': {
                    'from': sender
                    'mailbox': i
                    'msg': msg
                    'chatname': receiver
                }
            }])
            
            
        


def sendMessage(message, current_db):
    parts = message.split("|")
    topics = []
    message = parts[3]
    # If a single message
    if message[:-1] == '0':
        topics.append("/" + str(parts[2]))
    # If a group message
    else:
        result_set = current_db.query('SELECT * from groups WHERE id=' + str(receiver))
        # TODO: Do a DB lookup for members of group
        for i in topics:
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

        message = reply_socket.recv()

        if str(message[0:5]) == "CREATE":
            createUser(message, current_db)
        elif str(message[0:5]) == "MAKE":
            createGroup(message, current_db)
        else:
            writeToDatabase(message, current_db)
            sendMessage(message, current_db)
        reply_socket.send("Message: " + message + "recieved.")

if __name__ == "__main__":
    main()
