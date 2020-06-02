import os
from flask import Flask, session, url_for, request, render_template
from flask_socketio import SocketIO, emit
from sqlalchemy import create_engine
from database_classes import Message, Channel
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
import datetime

#os.environ.get('DB_PATH')
db = create_engine('postgres://hnulgvbhhhvrrn:2843c3b5f049942b975a6ca1ecb098caeaadd58c90c4e1d75b7e5bdb07d1cd06@ec2-23-22-156-110.compute-1.amazonaws.com:5432/d911g27f2j67g7')
Session = sessionmaker(bind=db)
s = Session()


app = Flask(__name__)
app.config["SECRET_KEY"] = '123'
socketio = SocketIO(app)

#This is an array of channel objects which store a name
# and a list of messages in the channel that represent the 
# 100 most recent messages (which can be implemented with a stack)
# 
channels = []

channels = s.query(Channel).all()
s.commit()
print(channels)

#session should store which channel the user is in... this 
#can be done with HTML5 stuff like storage or stored in session
@app.route("/")
def index():
    print("flask: running index()")
    print(session.keys())
    if 'display_name' in session.keys():
        print("flask: rendering index.html")
        channels2 = s.query(Channel).all()
        s.commit()
        channels = channels2

        messages2 = s.query(Message).all()
        s.commit()
        messages = []
        for m in messages2:
            if str(m.channel) == session['channelName']:
                messages.append([str(m.userPosted), str(m.message), str(m.timestamp)])

        return render_template('index.html', display_name=session['display_name'], channels=channels, channelName=session['channelName'], messages=messages)
    else:
        print('flask: rendering login.html...')
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    print("flask: running login()")
    if request.method == 'POST':
        session['display_name'] = request.form['display_name']
        print("flask: calling index()")
        return index()
    return ""

@app.route('/createChannel', methods=['POST'])
def createChannel():
    print("flask: running createChannel()")
    if request.method == 'POST':
        channelName = request.form["channelName"]
        try:
            session.pop('channelName', None)
        except:
            print("pop errored")
        session['channelName'] = channelName
        channel = Channel()
        channel.id = channelName

        isOkay = True
        for c in channels:
            if str(c) == channelName:
                isOkay =False 
                break
        if isOkay:
            s.add(channel)
            s.commit()

        print("finished creating channel")
        return index()
    else: 
        return ""

@app.route('/selectChannel', methods=['POST'])
def selectChannel():
    print("flask: running selectChannel()")
    if request.method == 'POST':
        channelName = request.form["channelName"]
        try:
            session.pop('channelName', None)
        except:
            print("pop errored45465765476576767657657567567657567657567657765")
        

        channels2 = s.query(Channel).all()
        s.commit()
        containsChannel = False
        for c in channels2:
            if str(c) == channelName:
                containsChannel = True
                break
        if containsChannel:
            session['channelName'] = channelName

        print("finished selecting channel")
        print("new channel name is: %s" % channelName)

        messages2 = s.query(Message).filter(Message.channel == channelName)
        s.commit()

        messages = {}
        count = 0
        for m in messages2:
            messages[str(count)] = {
                'user': str(m.userPosted), 
                'msg': str(m.message), 
                'time': str(m.timestamp)
            }
            count = count+1
        messages['count'] = count

        return messages
    else: 
        return ""

@app.route('/logout', methods=['POST'])
def logout():
    print("flask: running logout()")
    if 'display_name' in session.keys():
        print('flask: about to pop display_name for ' + session['display_name'])
        try:
            session.pop('display_name', None)
            print('flask: popped display_name for ' + session['display_name'])
        except:
            print("flask: KeyError occured")
    
        return index()
    else:
        return index()

@socketio.on('sendMessage')
def sendMessage(data):
    print("flask: running sendMessage()")
    message = data['message']
    print('a')
    userPosted = session['display_name']
    print('b')
    channel = session['channelName']
    print('flask: creating message object...')
    print(channel)
    messager = Message()
    messager.message = message
    messager.userPosted = userPosted
    messager.channel = channel
    s.add(messager)
    s.commit()

    messageRecieved = {
        "msg": message,
        "user": userPosted,
        "date": str(datetime.datetime.now())
    }
    print("now emmitting")
    #the socketio gives all of the users using the 
    socketio.emit('announce new message', {'messageForGivenChannel': messageRecieved, 'channelName': channel})


