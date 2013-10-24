# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, session, url_for, request, jsonify, g
from flask import Response
from app import app
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from twilio import twiml
from twilio.rest import TwilioRestClient
import re, random

# create an authenticated client that can make requests to Twilio for your
# account.
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


# @app.route('/')
# @app.route('/index')
# def index():
#     return render_template('index.html')

# # Clean up sent text
# def simplify_txt(submitted_txt):
#     response_letters = re.sub(r'\W+', '', submitted_txt)
#     return response_letters.lower()

@app.route('/')
def view():
  response = twiml.Response()
  response.sms(u'\uf31f'.encode('utf-8'))
  return Response([response])

 # Twiliocon challenge 4 - Create an sms quiz game
@app.route("/quiz_game")
def quiz_game():
    # We're using some chars that python doesn't know about (too recent a unicode version)
    # so we have to hack around a bit; we can't trust len(trophy_chars)
    num_trophies = 4
    trophy_chars = u'👍🏆🌟👿'
    type ('🌟')
    trophy_piece = ""

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

    # Stripped down answers to compare to text in case multiple word answer
    simplify_answers = { 
            1:"short", 
            2:"fire", 
            3:"palm",
            4:""
            }

    # Pretty print answers
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
        message = "Shall we play a game? %s "  % questions[0]
    else:
        game_round = session['counter']

        if simplify_answers[game_round] == simplify_body:
            session[from_number] += 10
            score = session[from_number]

            message = "Correct Answer. You have %d points out of 30. %s" % (score, questions[game_round])
            # if won give trophy:
            print 100, message
            #chosen_index = random.randint(0, num_trophies-1)
            # print 101, chosen_index
            #chosen_trophy = trophy_chars[chosen_index*2:(chosen_index+1)*2].encode('utf-8')
            #print 102, chosen_trophy

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

        else:
            score = session[from_number]
            message = "Wrong answer. We were looking for %s. Your score is %d out of 30. %s" % (print_answers[game_round], score, questions[game_round])

        session['counter'] += 1

    # message = unicode('U0001F31F').decode('unicode_escape')
    # print 103, type(message)

    if session['counter'] > 3:
        session.pop(from_number, None)
        session['counter'] = 0

    print 4, session

    response.sms(message)
    # response.sms(trophy_piece)


    # print 5, response.sms(trophy_piece)

    return Response(unicode(response))

