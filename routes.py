from flask import request, redirect, url_for, render_template, make_response
from time import time
from models import User, Message
from app import app, db
import requests
import datetime
from cryptography.bcrypt import Bcrypt
from cryptography.RSA import RSA


database = []
# Структура database
# {
# 'name': 'Имя',
# 'text': 'Текст сообщения.',
# 'time': Время когда отправлено сообщение
# },

@app.route("/home")
@app.route("/")
def main():
    return render_template("home.html")



@app.route("/send", methods=['POST'])
def send_message():
    data = request.json
    print(data)


    text = data['text']
    sender = data['sender']
    reciever = data['reciever']



    message = Message(
        sender=int(sender),
        reciever=int(reciever),
        text=str(text),
        time=str(time())
    )
    db.session.add(message)
    db.session.commit()


    return {'ok': True}




@app.route("/register", methods = ['POST', 'GET'])
def registaration():
    if request.method == 'POST':
        username = request.form['username']
        password = Bcrypt.hash_password(request.form['password'].encode())
        firstname = request.form['firstname']
        lastname = request.form['lastname']




        new_user = User(
            username = username,
            password = password,
            firstname = firstname,
            lastname = lastname
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main'))

    return render_template('registration.html')


@app.route("/enter", methods=['POST', 'GET'])
def enter():

    def get_user_credentials(username):
        user = User.query.filter_by(username=username).first()
        if user:
            return user.password
        else:
            None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if Bcrypt.check_password(password.encode(), get_user_credentials(str(username))):
            return redirect(url_for('profile', username=username))
        else:
            return render_template('enter.html', error="Invalid username or password. Please try again.")


    return render_template('enter.html')


@app.route('/user/<username>', methods=['GET', 'POST'])
def profile(username):
    user_data = User.query.filter_by(username=username).first()
    user_data = {'firstname': user_data.firstname, 'lastname': user_data.lastname, 'username': username}
    return render_template('profile.html', user=user_data)



@app.route('/user/<username>/send_message', methods=['GET', 'POST'])
def senddd_message(username):
    user_data = User.query.filter_by(username=username).first()
    user_data = {'firstname': user_data.firstname, 'lastname': user_data.lastname, 'id' : user_data.id, 'username': username}

    if request.method == 'POST':
        reciever_username = str(request.form['username'])
        reciever_id = User.query.filter_by(username=reciever_username).first().id

        text = request.form['text']
        print(reciever_id)
        response = requests.post(url='http://127.0.0.1:5000/send',
                                 json={
                                     'text': text,
                                     'sender': user_data['id'],
                                     'reciever': int(reciever_id)
                                 })

    return render_template('send_message.html', user = user_data)


@app.route('/user/<username>/show_messages', methods=['GET', 'POST'])
def show_messages(username):
    user_data = User.query.filter_by(username=username).first()
    user_data = {'firstname': user_data.firstname, 'lastname': user_data.lastname, 'id': user_data.id,
                 'username': username}


    messages = Message.query.filter_by(reciever=user_data['id']).all()

    sender_ids = []

    for message in messages:
        sender_ids.append(message.sender)

    sender_ids = list(set(sender_ids))
    sender_names = []
    for i in range(len(sender_ids)):
        user = User.query.filter_by(id=sender_ids[i]).first()
        sender_names.append({'firstname' : str(user.firstname), 'lastname' : str(user.lastname), 'id' : sender_ids[i]})


    return render_template('show_messages.html', sender_names=sender_names, username=username)


@app.route('/user/<username>/show_messages/<id>', methods=['GET', 'POST'])
def show_chat(username, id):
    def time_from_UNIX(unix_time: float):
        time = datetime.datetime.fromtimestamp(unix_time)
        formated_time = time.strftime('%Y-%m-%d %H:%M:%S')
        return formated_time

    me= User.query.filter_by(username=username).first()
    me_id = me.id

    messages_from = Message.query.filter_by(reciever=int(id), sender=me_id).all()
    messages_to = Message.query.filter_by(reciever=me_id, sender=int(id)).all()

    result = []
    for message in messages_from:
        sender = User.query.filter_by(id=id).first()
        result.append( { 'message' : message.text, 'sender' : username, 'time' : time_from_UNIX(float(message.time)) } )
    for message in messages_to:
        result.append( { 'message' : message.text, 'sender' : sender.username, 'time' : time_from_UNIX(float(message.time)) } )

    result = sorted(result, key=lambda x: x['time'])

    if request.method == 'POST':
        reciever_id = id

        text = request.form['text']
        print(reciever_id)
        response = requests.post(url='http://127.0.0.1:5000/send',
                                 json={
                                     'text': text,
                                     'sender': me_id,
                                     'reciever': int(reciever_id)
                                 })

        return redirect(url_for('show_chat', username=username, id=id))


    return render_template('chat.html', messages=result, sender=sender)


@app.route('/cookie/')
def cookie():
    res = make_response("Setting a cookie")
    res.set_cookie('foo', 'bar', max_age=60*60*24*365*2)
    return res


