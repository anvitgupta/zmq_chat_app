import sys
import zmq
from influxdb import client as influxdb
from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)
db = influxdb.InfluxDBClient('ec2-52-23-246-145.compute-1.amazonaws.com',
                             8086, 'admin', 'dubey', 'messenger')


SERVER_IP = "ec2-54-164-205-229.compute-1.amazonaws.com"
PORT = "9000"

ctx = zmq.Context()
req_socket = ctx.socket(zmq.REQ)
sub_socket = ctx.socket(zmq.SUB)

print "Connecting to message server..."
req_socket.connect("tcp://{}:{}".format(SERVER_IP, PORT))
print "Subscribing to message server..."
sub_socket.connect("tcp://{}:{}".format(SERVER_IP, PORT + 1))
sub_socket.setsockopt(zmq.SUBSCRIBE, "")

my_username = ""

@app.route('/')
def my_form():
    return render_template('welcome.html')


@app.route('/', methods=['POST'])
def my_form_post():
    # Get the username from the form
    username = request.form['Username']
    # Send a create user request to the server
    req_socket.send_json({"type": "CREATE_USER", "username": username})
    resp = req_socket.recv_json()
    if resp.get("success") is True:
        print "Successfully connected as user {}".format(username)
    else:
        sys.exit("we failed")
    # Redirect to webpage to pick a chat
    return redirect(url_for('showChats', username=text))


@app.route('/pickchats', methods=['GET', 'POST'])
def showChats():
    # Get a list of chats this user belongs to
    username = str(request.form['Username'])
    global my_username 
    my_username = username
    # Send a create user request to the server
    req_socket.send_json({"type": "CREATE_USER", "username": username})
    resp = req_socket.recv_json()
    if resp.get("success") is True:
        print "Successfully connected as user {}".format(username)
    else:
        sys.exit("we failed")
    query = "SELECT DISTINCT chatname from msgs WHERE mailbox = '{}'".format(my_username)
    loadedChats = db.query(query).get_points()
    return render_template('chat_picker.html', user=username, chats=loadedChats)


@app.route('/individual', methods=['GET', 'POST'])
def indiv():
    # Get the name of the other user 
    other_user = str(request.form["chatName"])
    # Fetch the messages from DB
    query = "SELECT * from msgs WHERE \"{}\"='{}' OR {}='{}'".format("from", other_user, "mailbox", other_user)

    return render_template('results.html', user=other_user, rows=messages)

@app.route('/group', methods=['GET', 'POST'])
def grp():
    # Get the name of the group message
    group_name = str(request.form["chatName"])
    # Get the list of members in the group
    users = getFromDB(group_name)
    messages = []
    for user in users:
        messages.append(getFromDB(my_username, user))
    return render_template('results.html', user=group_name, rows=messages)

