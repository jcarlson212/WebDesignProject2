import os
from flask import Flask, session, url_for, request, render_template
from flask_socketio import SocketIO, emit
from sqlalchemy import create_engine
from database_classes import Message, Channel
from sqlalchemy.orm import sessionmaker

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
        print("channels: ")
        print(channels2)
        channels = channels2
        return render_template('index.html', display_name=session['display_name'], channels=channels)
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
        s.add(channel)
        s.commit()
        return index()
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
def sendMessage():
    print("flask: running sendMessage()")
    message = request.form['message']
    userPosted = session['display_name']
    channel = session['channel']
    messager = Message()
    messager.message = message
    messager.userPosted = userPosted
    messager.channel = channel
    s.add(messager)
    s.commit()

    #gets messages for a specific channel
    messages = s.query(Message).filter_by(channel=channel)

    #the socketio gives all of the users using the 
    socketio.emit('My response', {'messagesForGivenChannel': messages, 'channelName': channel})


