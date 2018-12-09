import sys
import zmq
import json
from influxdb.client import InfluxDBClientError
from influxdb import client as influxdb

influx_ip = ''
load_balancer_ip = ''

def main():
    
    # set up Influx database
    mydb = influxdb.InfluxDBClient(influx_ip, 8086, 'admin', 'admin', 'data') 
    mydb.create_database('data')

    # create sub socket and set up connection to pub 
    ctx = zmq.Context()
    socket = ctx.socket(zmq.SUB)
    socket.connect(load_balancer_ip)
    socket.setsockopt(zmq.SUBSCRIBE, '')

    while True:
        
        # receiver message and parse by topic
        message = socket.recv()
        topic, sender, msg = message.split(" ")

        input_data = [{
                    'measurement': topic,
                    'fields': {
                        str(sender):msg
                    }
        }]
        
        mydb.write_points(input_data)

if __name__ == "__main__":
    main() 