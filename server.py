import sys
import zmq
import json
from influxdb.client import InfluxDBClientError
from influxdb import client as influxdb

influx_ip = ['ec2-52-23-246-145.compute-1.amazonaws.com', 
            'ec2-52-90-226-153.compute-1.amazonaws.com',
            'ec2-52-200-205-8.compute-1.amazonaws.com']

# set up Influx database
mydb1 = influxdb.InfluxDBClient(influx_ip[0], 8086, 'admin', 'admin', 'data')
mydb2 = influxdb.InfluxDBClient(influx_ip[1], 8086, 'admin', 'admin', 'data') 
mydb3 = influxdb.InfluxDBClient(influx_ip[2], 8086, 'admin', 'admin', 'data')  

# create database
# mydb1.create_database('data')            
load_balancer_ip = ''
round_robin = 0

def main():

    # create sub socket and set up connection to pub 
    ctx = zmq.Context()
    socket = ctx.socket(zmq.SUB)
    socket.connect(load_balancer_ip)
    socket.setsockopt(zmq.SUBSCRIBE, '')

    while round_robin < len(influx_ip):
        
        # receiver message and parse by topic
        message = socket.recv()
        topic, sender, msg = message.split(" ")

        input_data = [{
                    'measurement': topic,
                    'fields': {
                        str(sender):msg
                    }
        }]
        
        if round_robin == 0:
            mydb1.write_points(input_data)
            round_robin = round_robin + 1
        elif cnt == 1:
            mydb2.write_points(input_data)
            round_robin = round_robin + 1
        else:
            mydb3.write_points(input_data)
            round_robin = 0

if __name__ == "__main__":
    main() 