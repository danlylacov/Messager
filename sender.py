import requests

name = input('Введите имя: ')

while True:
    text = input("Введите текст: ")
    response = requests.post(url='http://127.0.0.1:5000/send',
                             json={'text': text, 'sender' : 0, 'reciever' : 1})
