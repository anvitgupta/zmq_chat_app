from influxdb import client as influxdb
from flask import Flask, render_template
app = Flask(__name__)
ALLOWED = ["LIGHTS", "HUMIDITY", "TEMP"]


@app.route('/<string:topic>')
def results(topic):
    topic = topic.upper()
    if topic not in ALLOWED:
        return "Must be one of: [{}]".format(", ".join(ALLOWED)), 404
    rows = mydb.query("SELECT * FROM {}".format(topic)).get_points()

    return render_template('results.html', topic=topic, rows=rows)


if __name__ == '__main__':
    mydb = influxdb.InfluxDBClient('127.0.0.1', 8086, 'rds', '2018', 'mqtt')
    mydb.create_database('mqtt')

    app.run("0.0.0.0")
