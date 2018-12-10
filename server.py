import sys
import zmq
from influxdb.client import InfluxDBClientError
from influxdb import client as influxdb

influx_ip = ['ec2-52-23-246-145.compute-1.amazonaws.com', 
            'ec2-52-90-226-153.compute-1.amazonaws.com',
            'ec2-52-200-205-8.compute-1.amazonaws.com']

# set up Influx database
mydb1 = influxdb.InfluxDBClient(influx_ip[0], 8086, 'admin', 'dubey', 'messenger')
mydb2 = influxdb.InfluxDBClient(influx_ip[1], 8086, 'admin', 'dubey', 'messenger') 
mydb3 = influxdb.InfluxDBClient(influx_ip[2], 8086, 'admin', 'dubey', 'messenger')  

context = zmq.Context() 
socket_server = context.socket(zmq.REP)
socket_server.bind('ec2-54-164-205-229.compute-1.amazonaws.com')

round_robin = 0

def main():

    while round_robin < len(influx_ip):
        
        message = socket_server.recv()
        sender, receiver, msg, sg = message.split(" ")

        if sg == '0':
            
            sender_mailbox = [{
                    'measurement': 'msgs',
                    'fields': {
                        'from': sender
                        'mailbox': sender
                        'msg': msg
                        'chatname': receiver
                    }
            }]
            
            receiver_mailbox = [{
                    'measurement': 'msgs',
                    'fields': {
                        'from': sender
                        'mailbox': receiver
                        'msg': msg
                        'chatname': sender
                    }
            }]

            if round_robin == 0:
                mydb1.write_points(sender_mailbox)
                mydb1.write_points(receiver_mailbox)
                round_robin = round_robin + 1

            elif round_robin == 1:
                mydb2.write_points(sender_mailbox)
                mydb2.write_points(receiver_mailbox)
                round_robin = round_robin + 1
            else:
                mydb3.write_points(sender_mailbox)
                mydb3.write_points(receiver_mailbox)
                round_robin = 0
        
        elif sg == '1':
            
            group = select(db: 'messenger')
            .filter(exp:{'_measurement' == 'groups' and '_fields' == receiver})

            members = group['members'].split(',')        

            if round_robin == 0:
                
                mydb1.write_points(sender_mailbox)
                
                for i in members:
                    mydb1.write_points([{
                        'measurement': 'msgs',
                        'fields': {
                            'from': sender
                            'mailbox': i
                            'msg': msg
                            'chatname': receiver
                        }
                    }])

                round_robin = round_robin + 1    

            elif round_robin == 1:
                
                mydb2.write_points(sender_mailbox)
                
                for i in members:
                    mydb2.write_points([{
                        'measurement': 'msgs',
                        'fields': {
                            'from': sender
                            'mailbox': i
                            'msg': msg
                            'chatname': receiver
                        }
                    }])

                round_robin = round_robin + 1

            else:
                
                mydb3.write_points(sender_mailbox)
                
                for i in members:
                    mydb3.write_points([{
                        'measurement': 'msgs',
                        'fields': {
                            'from': sender
                            'mailbox': i
                            'msg': msg
                            'chatname': receiver
                        }
                    }])

                round_robin = 0

if __name__ == "__main__":
    main() 