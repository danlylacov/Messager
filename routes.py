from flask import request, abort, redirect, url_for, render_template
from time import time
from models import User, Message
from app import app, db
import requests


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





@app.route("/status")
def status():
    return {
        'status': True,
        'name': 'Messenger',
        'time': time(),
        'count_user': len(set(message['name'] for message in database))
    }


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


@app.route("/messages")
def get_message():
    try:
        after = float(request.args['after'])
    except Exception as ex:
        print(ex)
        return abort(400)
    messages = []

    for message in database:
        if message['time'] > after:
            messages.append(message)

    return {'messages': messages[:50]}


@app.route("/register", methods = ['POST', 'GET'])
def registaration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
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

        if get_user_credentials(str(username)) == str(password):
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


