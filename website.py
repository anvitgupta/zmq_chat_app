from influxdb import client as influxdb
from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)
db = influxdb.InfluxDBClient('ec2-52-23-246-145.compute-1.amazonaws.com',
                                 8086, 'admin', 'dubey', 'messenger')



# Methods to route username
@app.route('/')
def my_form():
    return render_template('welcome.html')

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['Username']
    print(text)
    # Call app method with username
    # return processed_text
    return redirect(url_for('showChats', username=text))

@app.route('/pickchats', methods=['GET', 'POST'])
def showChats():
    # Get a list of chats this user belongs to
    username = str(request.form['Username'])
    loadedChats = [] #TODO: Db query for chats
    return render_template('chat_picker.html', user=username, chats=loadedChats)

@app.route('/individual', methods=['GET', 'POST'])
def indiv():
    return render_template('results.html')

@app.route('/group', methods=['GET', 'POST'])
def grp():
    return render_template('results.html')



@app.route('/<string:username>/<string:chatname>')
def results(topic):
    topic = topic.upper()
    rows = db.query("SELECT * FROM {}".format(topic)).get_points()

    return render_template('results.html', topic=topic, rows=rows)


if __name__ == '__main__':
    app.run("0.0.0.0")
