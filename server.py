import sys
import zmq
from influxdb.client import InfluxDBClientError
from influxdb import client as influxdb

influx_ip = ['ec2-52-23-246-145.compute-1.amazonaws.com',
             'ec2-52-90-226-153.compute-1.amazonaws.com',
             'ec2-52-200-205-8.compute-1.amazonaws.com']

# set up Influx database
mydb1 = influxdb.InfluxDBClient(
    influx_ip[0], 8086, 'admin', 'dubey', 'messenger')
mydb2 = influxdb.InfluxDBClient(
    influx_ip[1], 8086, 'admin', 'dubey', 'messenger')
mydb3 = influxdb.InfluxDBClient(
    influx_ip[2], 8086, 'admin', 'dubey', 'messenger')

context = zmq.Context()
socket_server = context.socket(zmq.REP)
socket_server.bind('ec2-54-164-205-229.compute-1.amazonaws.com')

round_robin = 0


def writeToDatabase(queue, message):
    # Round robin select the next Influx instance to use
    current_db = queue.popleft()
    queue.append(current_db)

    # Parse the message
    sender, receiver, msg, sg = message.split(" ")

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
        group = select('db': 'messenger').filter(exp: {'_measurement' == 'groups' and '_fields' == receiver})
        members = group['members'].split(',')
        
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


def sendMessage():
    pass


def main():

    # Create a queue of our Influx instances
    queue = deque(influx_ip)

    # Each time we recieve a message, write it to DB and send out to receivers
    while True:
        message = socket_server.recv()
        writeToDatabase(queue, messaage)
        sendMessage()


if __name__ == "__main__":
    main()
