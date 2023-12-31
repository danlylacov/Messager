from flask import request, redirect, url_for, render_template, make_response, abort, jsonify
from time import time
from models import User, Message, Keys
from app import app, db
import requests
import datetime
from cryptography.bcrypt import Bcrypt
from cryptography.RSA import RSA

from ast import literal_eval



@app.route("/home")
@app.route("/")
def main():
    return render_template("home.html")



@app.route("/send", methods=['POST'])
def send_message():
    data = request.json

    text = data['text']
    sender = data['sender']
    reciever = data['reciever']


    rsa = RSA()
    publickey = User.query.filter_by(id=reciever).first()
    publickey = literal_eval(publickey.publickey)
    encrypt_text = rsa.encrypt(text, publickey)

    message = Message(
        sender=int(sender),
        reciever=int(reciever),
        text=str(encrypt_text),
        time=str(time())
    )
    db.session.add(message)
    db.session.commit()


    return {'ok': True}




@app.route("/register", methods = ['POST', 'GET'])
def registaration():
    user_exists = False
    if request.method == 'POST':
        username = request.form['username']
        password = Bcrypt.hash_password(request.form['password'].encode())
        firstname = request.form['firstname']
        lastname = request.form['lastname']

        rsa = RSA()

        keys = rsa.create_keys()
        publickey = str(keys[0])
        privatekey = str(keys[1])

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            user_exists = True
            return render_template('registration.html', user_exists=user_exists)
        else:
            new_user = User(
                username=username,
                password=password,
                firstname=firstname,
                lastname=lastname,
                publickey=publickey
            )
            db.session.add(new_user)
            db.session.commit()

            new_key = Keys(
                user_id=User.query.filter_by(username=username).first().id,
                privateKey=privatekey
            )
            db.session.add(new_key)
            db.session.commit()

            return redirect(url_for('main'))

    return render_template('registration.html', user_exists = user_exists)


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

    try:
        if Bcrypt.check_password(password.encode(), get_user_credentials(str(username))):
            return redirect(url_for('profile', username=username))
        else:
            return render_template('enter.html', error="Invalid password. Please try again.")
    except:
        return render_template('enter.html', error="Invalid username. Please try again.")


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
        try:
            reciever_id = User.query.filter_by(username=reciever_username).first().id

            text = request.form['text']

            response = requests.post(url='http://127.0.0.1:5000/send',
                                     json={
                                         'text': text,
                                         'sender': user_data['id'],
                                         'reciever': int(reciever_id)
                                     })

            return render_template('send_message.html', user = user_data, error = False)
        except:
            return render_template('send_message.html', user=user_data, error = True)


    return render_template('send_message.html', user=user_data, error=False)


@app.route('/user/<username>/show_messages', methods=['GET', 'POST'])
def show_messages(username):
    user_object = User.query.filter_by(username=username).first()
    if user_object is None:
        abort(404)  # или другой способ обработки отсутствия пользователя

    user_data = {'firstname': user_object.firstname,
                 'lastname': user_object.lastname,
                 'id': user_object.id,
                 'username': username}

    messages = Message.query.filter_by(reciever=user_data['id']).all()

    sender_ids = set()
    for message in messages:
        sender_ids.add(message.sender)

    sender_names = []
    for sender_id in sender_ids:
        user = User.query.filter_by(id=sender_id).first()
        if user:
            sender_names.append({'firstname': user.firstname, 'lastname': user.lastname, 'id': sender_id})

    return render_template('show_messages.html', sender_names=sender_names, username=username)


@app.route('/user/<username>/delete_messages/<id>', methods=['GET', 'POST'])
def delete_message(username, id):
    me = User.query.filter_by(username=username).first()
    me_id = me.id

    Message.query.filter_by(reciever=int(id), sender=me_id).delete()
    Message.query.filter_by(reciever=me_id, sender=int(id)).delete()

    db.session.commit()

    return redirect(url_for('show_messages', username=username))



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
    sender = User.query.filter_by(id=me_id).first()
    private_key_me = Keys.query.filter_by(user_id=sender.id).first().privateKey

    private_key_send = Keys.query.filter_by(user_id=int(id)).first().privateKey


    rsa = RSA()



    for message in messages_from:
        result.append( { 'message' : rsa.decrypt(literal_eval(message.text), literal_eval(private_key_send)), 'sender' : User.query.filter_by(id=int(id)).first().username, 'time' : time_from_UNIX(float(message.time)) } )
    for message in messages_to:
        result.append( { 'message' : rsa.decrypt(literal_eval(message.text), literal_eval(private_key_me)), 'sender' : sender.username, 'time' : time_from_UNIX(float(message.time)) } )
    result = sorted(result, key=lambda x: x['time'])
    print(result)

    if request.method == 'POST':
        reciever_id = id

        text = request.form['text']

        response = requests.post(url='http://127.0.0.1:5000/send',
                                 json={
                                     'text': text,
                                     'sender': me_id,
                                     'reciever': int(reciever_id)
                                 })
        db.session.commit()

        return redirect(url_for('show_chat', username=username, id=id))

    return render_template('chat.html', messages=result, sender=sender, username=username)






