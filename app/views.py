from flask import render_template, flash, redirect, session, url_for, request, jsonify, g
from flask import Response
from app import app
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from twilio import twiml
from twilio.rest import TwilioRestClient
import re

# create an authenticated client that can make requests to Twilio for your
# account.
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

# Clean up sent text
def simplify_txt(submitted_txt):
    response_letters = re.sub(r'\W+', '', submitted_txt)
    return response_letters.lower()

# Twiliocon challenge 4 - Create an sms quiz game
@app.route("/quiz_game")
def quiz_game():
    response = twiml.Response()

    from_number = str(request.values.get('From', None))
    body = request.values.get('Body', None)
    simplify_body = simplify_txt(body)

    print 1, simplify_body
    print 2, from_number

    questions = { 
            0: "What word is shorter when you add two letters to it?",
            1: "If I drink, I die. If i eat, I am fine. What am I?",
            2: "What kind of tree is carried in your hand?",
            3: "Thanks for playing.",
            4: ""
    }

    simplify_answers = { 
            1:"short", 
            2:"fire", 
            3:"palm",
            4:""
            }

    print_answers = { 
            1:"short", 
            2:"fire", 
            3:"palm",
            4:""
            }

    print 3, session

    # if from_number not in track_user:
    if from_number not in session:
        session[from_number] = 0
        counter = session.get('counter', 0)
        counter += 1
        session['counter'] = counter
        message = "Shall we play a game? %s" % questions[0]
    else:
        game_round = session['counter']

        if simplify_answers[game_round] == simplify_body:
            session[from_number] += 10
            score = session[from_number]
            message = "Correct Answer. You have %d points out of 30. %s" % (score, questions[game_round])
        else:
            score = session[from_number]
            message = "Wrong answer. We were looking for %s. Your score is %d out of 30. %s" % (print_answers[game_round], score, questions[game_round])

        session['counter'] += 1

    if session['counter'] > 3:
        session.pop(from_number, None)
        session['counter'] = 0

    print 4, session

    response.sms(message)
    return Response(str(response), mimetype='text/xml')

# Challenge 6 - Find available phone number and offer to purchase if found
@app.route("/find_number")
def find_number():
    phone_num =[]
    numbers = client.phone_numbers.search(area_code="415",
        country="US",
        type="local")

    print "find num"
    for number in numbers:
        phone_num.append(number.phone_number)

    return render_template('find_number.html', numbers=phone_num)

@app.route("/purchase", methods=['POST', 'GET'])
def purchase():
    # Purchase the first number in the list
    chosen_number = request.form['chosen_number']
    client.phone_numbers.purchase(phone_number=chosen_number)
    return render_template('purchase.html')

#Bonus
@app.route("/current_number")
def current_number():
    # Print current number
    # number = client.phone_numbers.get(TWILIO_APP_SID)

    numbers = client.phone_numbers.list()
    for number in numbers:
       print number.phone_number
    return ""
