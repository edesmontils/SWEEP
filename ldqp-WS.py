#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Application ...
"""
#    Copyright (C) 2017 by
#    Emmanuel Desmontils <emmanuel.desmontils@univ-nantes.fr>
#    Patricia Serrano-Alvarado <patricia.serrano-alvarado@univ-nantes.fr>
#    All rights reserved.
#    GPL v 2.0 license.

import sys
from threading import *

import multiprocessing as mp

import datetime as dt
import iso8601 # https://pypi.python.org/pypi/iso8601/     http://pyiso8601.readthedocs.io/en/latest/

import re
import argparse

from tools.tools import *

from lxml import etree  # http://lxml.de/index.html#documentation
from lib.bgp import *

from io import StringIO

from ldqp import *

from flask import Flask, render_template, request, jsonify
# http://flask.pocoo.org/docs/0.12/

#==================================================

def processResults(ldqp):
    i = 0
    try:
        res = ldqp.get()
        while res != None:
            i += 1
            res.print()
            res = ldqp.get()
    except KeyboardInterrupt:
        pass

#==================================================

#Function for handling connections. This will be used to create threads
def clientthread(conn, ldqp):
    #Sending message to connected client
    #conn.send('Welcome to the server. Type something and hit enter\n') #send only takes string
     
    #infinite loop so that function do not terminate and thread do not end.
    while True:
         
        #Receiving from client
        try:
            mess = conn.recv(2048)
            data = mess.decode("utf-8")
            # print('received:',data)

            if not data: 
                break
            else:
                try:
                    tree = etree.parse(StringIO('<msg>'+data+'</msg>'), parser)
                    root = tree.getroot()
                    for x in root: 
                        # print('xml:',x.tag ) 
                        ldqp.put(x)               
                except Exception as e:
                    print('Exception',e)
                    print('About:',data)
            #conn.sendall(reply)
        except KeyboardInterrupt:
            break
    #came out of loop
    conn.close()
    # print('end thread')

#==================================================

# Initialize the Flask application
app = Flask(__name__)
 
# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('index.html')
 
# Route that will process the AJAX request, sum up two
# integer numbers (defaulted to zero) and return the
# result as a proper JSON response (Content-Type, etc.)
@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)
 
# sur requete AJAX _get_message on renvoie le texte   
# je suis la réponse ajax du serveur à + le paramètre transmis  
@app.route('/_get_message')
def get_message():
    param = request.args.get('param', 'pas de param', type=str)
    return jsonify(result='je suis la réponse ajax du serveur à ' + param)

@app.route('/_add_query', methods=['post'])
def add_query():
    param = request.form['query']
    print(param)
    return jsonify(result='La requête : ' + param)

#==================================================
#==================================================
#==================================================
 
# launch : python3.6 ldqp-WS.py 
# example to request : curl -d 'query="select * where {?s :p1 ?o}"' http://127.0.0.1:8090/_add_query

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Linked Data Query Profiler (for a modified TPF server)')
    # parser.add_argument('files', metavar='file', nargs='+',help='files to analyse')
    parser.add_argument("-g", "--gap", type=float, default=60, dest="gap", help="Gap in minutes (60 by default)")
    parser.add_argument("--port", type=int, default=5002, dest="port", help="Port (5002 by default)")
    parser.add_argument("--host", default='127.0.0.1', dest="host", help="Host ('127.0.0.1' by default)")
    parser.add_argument("-to", "--timeout", type=float, default=0, dest="timeout",
                        help="TPF server Time Out in minutes (%d by default). If '-to 0', the timeout is the gap." % 0)
    parser.add_argument("-o","--optimistic", help="BGP time is the last TP added (False by default)",
                    action="store_true",dest="doOptimistic")

    args = parser.parse_args()

    ldqp = LDQP_XML(dt.timedelta(minutes= args.gap))
    if args.timeout > 0 : ldqp.setTimeout(dt.timedelta(minutes= args.timeout))
    if args.doOptimistic: ldqp.swapOptimistic()
    parser = etree.XMLParser(recover=True, strip_cdata=True)

    resProcess = mp.Process(target=processResults, args=(ldqp,))
    resProcess.start() 

    ldqp.startSession()

    try:
        app.run(
            host="0.0.0.0",
            port=int("8090"),
            debug=True
        )
    except KeyboardInterrupt: 
        pass
    finally:   
        ldqp.endSession() 
        ldqp.stop()
        resProcess.join()
    print('Fin')

