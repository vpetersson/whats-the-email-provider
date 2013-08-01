#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv
from socket import gethostname

from urlparse import urlparse

from bottle import get, post, request, template
from bottle import debug as bottle_debug
from bottle import run as bottle_run

import dns.resolver

try:
    port = argv[1]
except:
    port = '8080'

if gethostname() == 'hax0rbook3':
    listen = '127.0.0.1'
    bottle_debug(True)
else:
    listen = '0.0.0.0'

def is_running_google_apps(domain):
    result = False

    try:
        query = dns.resolver.query(domain, 'MX')
    except:
        return result

    for rdata in query:
        if ('google.com' or 'googlemail.com') in str(rdata).lower():
            result = True
            break

    return result


def guess_domain(input):
    guess_domain = input

    # If it's an email, just use the part after the @
    if '@' in input:
        guess_domain = input.split('@')[1]

    if len(guess_domain) == 0:
        return {'status': False, 'msg': 'Invalid domain name'}

    # Append http:// to satisfy urlparse if missing
    if not guess_domain.startswith('http://' or 'https://'):
        guess_domain = 'http://%s' %  guess_domain

    parse_domain = urlparse(guess_domain)

    # Extract the 'netloc' block from urlparse
    educated_guess = parse_domain[1]

    return {'status': True, 'domain': educated_guess}


@get('/')
def input_form():
    return '''<form method="POST" action="/result">
            <h1>Are they using Google Apps?</h1>
            <strong>Domain: </strong><input name="domain" type="text" /> (e.g. 'foobar.com' or 'user@foobar.com')<br />
            <input type="submit" />
            </form>'''


@post('/result')
def build_links():
    input = request.forms.get('domain')

    if not input:
        return "Invalid input"

    domain = guess_domain(input)
    if not domain['status']:
        result = domain['msg']
    else:
        query = is_running_google_apps(domain['domain'])

        if query:
            result = "Yes they are. :)"
        else:
            result = "No, they aren't :("


    return template('''
    <h1>{{result}}</h1>
    ''', result=result)

bottle_run(host=listen, port=port, reloader=True)
