# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, session, url_for, request, jsonify, g
from flask import Response
from app import app
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER
from twilio import twiml
from twilio.rest import TwilioRestClient
import re, random


client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

# Clean up sent text
def simplify_txt(submitted_txt):
    response_letters = re.sub(r'\W+', '', submitted_txt)
    return response_letters.lower()

def questions(counter):
    questions = { 
        0: "What word is shorter when you add two letters to it?",
        1: "If I drink, I die. If i eat, I am fine. What am I?",
        2: "What kind of tree is carried in your hand?",
        3: "Thanks for playing.",
        4: ""
    }

    return questions[counter] 

def answers(counter):
    answers = { 
            1:"short", 
            2:"fire", 
            3:"palm",
            4:""
            }

    return answers[counter]

@app.route("/quiz_game_emoji")
def quiz_game_emoji():
    '''
    Quiz game with emoji results
    '''

    response = twiml.Response()

    from_number = str(request.values.get('From', None))
    body = request.values.get('Body', None)
    simplify_body = simplify_txt(body)

    trophies = [u'👍', u'🏆', u'🌟']
    trophy_piece = ""

    chosen_trophy = random.randint(0, len(trophies)-1)

    counter = session.get('counter', 0)
    
    if from_number not in session:
        session[from_number] = 0
        counter += 1
        session['counter'] = counter
        message = u"Shall we play a game? %s "  % questions(0)
    else:
        game_round = session['counter']

        if answers(game_round) == simplify_body:
            session[from_number] += 10
            score = session[from_number]
            message = u"Correct Answer! " + trophies[chosen_trophy] + " You have %d points out of 30. %s" % (score, questions(game_round))
        else:
            score = session[from_number]
            message = u"Wrong answer. 👿 We were looking for %s. Your score is %d out of 30. %s" % (answers(game_round), score, questions(game_round))
            
        session['counter'] += 1

    if session['counter'] > 3:
        session.pop(from_number, None)
        session['counter'] = 0

    print 101, from_number, counter, message
    client.messages.create(
        from_ = TWILIO_NUMBER,
        to = from_number,
        body = message
    )
    return ''

@app.route("/quiz_game")
def quiz_game():
    '''
    Quiz game just text response version
    '''

    response = twiml.Response()

    from_number = str(request.values.get('From', None))
    body = request.values.get('Body', None)
    simplify_body = simplify_txt(body)

    if from_number not in session:
        session[from_number] = 0
        counter = session.get('counter', 0)
        counter += 1
        session['counter'] = counter
        message = "Shall we play a game? %s "  % questions(0)
    else:
        game_round = session['counter']

        if answers(game_round) == simplify_body:
            session[from_number] += 10
            score = session[from_number]
            message = "Correct Answer. You have %d points out of 30. %s" % (score, questions(game_round))
        else:
            score = session[from_number]
            message = "Wrong answer. We were looking for %s. Your score is %d out of 30. %s" % (answers(game_round), score, questions(game_round))

        session['counter'] += 1

    if session['counter'] > 3:
        session.pop(from_number, None)
        session['counter'] = 0

    response.sms(message)

    return Response(str(response))



    # message += u'🌟'.encode('utf-8') #gives ascii error - type string
    # message += u'\u1f31f'.encode('utf-8') #gives ascii error - type string
    # message += unichr(int('1F31F', 16)).encode('utf-8') # valueerror - unichar arg not in range - no type given
    # message += u'\u0001f31f'.encode('utf-8') #no error but no response - type string
    # message += u'\u1f31f'.decode('unicode_escape') # ascii error - no type
    # message += unicode('\u1f31f').decode('unicode_escape') # no error - response has weird content - unicode type
    # message +=  unicode('u0001f31f',"unicode_escape").encode('utf-8') # no response - no error 
    # message +=  unicode('u1f31f',"unicode_escape").encode('utf-8') # no error - type string - added the u value at the end 

    # trophy_piece = '\xF0\x9F\x8F\x86'
    # trophy_piece = u('\u1f31f').decode('unicode_escape')
    # trophy_piece = u'\u1f31f'.encode('utf-8') # changes to \x.. which is 
    
    # message += unicode('u1f31f','unicode_escape').encode('utf-8')
