# Python example with Flask and a Webex Message oAuth Integration.
#    DJ Uittenbogaard (duittenb@cisco.com)
"""Webex Virtual Background Logo Insertion Script.
Allows you to insert an image (like a logo) in a specific space on a
virtual background of a Cisco Webex Desk Pro video device.
Copyright (c) 2019 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""
# ------------------------------------------------------------
# START: create integration with "people_read" as the scope and
#        populate the variables below
# TIP: use text editor with syntax highlighting to make it easier
#      to read like Atom (Mac) or Notepad++ (Win)
# more info: https://github.com/DJF3/Webex-Teams-Flask-oAuth/
# ------------------------------------------------------------
from flask import Flask, redirect, url_for, request
import requests
import json
import urllib.parse
import datetime
# --- update variables below ---
myClientID = "YOUR_CLIENT_ID_HERE"
myClientSecret = "YOUR_CLIENT_SECRET_HERE"
myScope = "spark:people_read"
myRedirectURI = "http://127.0.0.1:5000/gologin"
# --- update variables above ---

app = Flask(__name__)


# ------ MAIN PAGE ------------------------------------------------
# url: /
# This is the 'main page' that contains a login link.
@app.route('/')
def hello():
    html = "<br>Hello World!<br>Click <a href='http://127.0.0.1:5000/gologin'>here</a> to authenticate"
    return html


# ------ AUTHENTICATE ------------------------------------------------
# url: /gologin
# This does 2 things:
#   1. URL = /gologin
#          Redirect user to Webex to authenticate (when you clicked 'here' above)
#   2. URL = /gologin?code=SE293AJXKSE293AJXKSE293AJXK
#          This is Webex returning the Auth.code after succesfull login
#          With this code+clientId+clientSecret you can get the real user token
#          Then do an API call to /people/me to get my details
@app.route('/gologin')
def gologin():
    # read the URL that was called (like '127.0.0.1:5000/gologin')
    query = request.url

    # 1. URL = /gologin ('code' not in URL) in the URL: Redirect user to Webex to authenticate
    if 'code' not in query:
        # Create the redirect URL
        oauthRedirectUrl = get_oauthRedirectUrl(myClientID, myRedirectURI, myScope)
        # Redirect user to this URL
        return redirect(oauthRedirectUrl)

    # 2. URL = /gologin?code=SE293AJXKSE293AJXK..etc
    #       Webex returning the Auth.code after succesfull login
    if 'code' in query:
        # Extract the 'code' from the URL
        teamsAuthCode = query.split('=', 1)[-1]

        # With the 'code', now get your real accesss token.
        myAccessToken = get_token(myRedirectURI, teamsAuthCode, myClientID, myClientSecret)

        # Use token to get my details
        myInfo = get_myDetails(myAccessToken)

    # Return HTML that shows information from the /people/me API call
    return "<hr><strong>You are:</strong><br>Name: " + myInfo['displayName'] + "<br>Email: " + myInfo['emails'][0] + "<br><hr>"



# REDIRECT URL creation
def get_oauthRedirectUrl(myClientID, myRedirectURI, myScope):
	oauthRedirectUrl = "https://api.ciscospark.com/v1/authorize"
	oauthRedirectUrl += "?response_type=code"
	oauthRedirectUrl += "&client_id=" + myClientID
	oauthRedirectUrl += "&redirect_uri=" + str(urllib.parse.quote(myRedirectURI, safe='~@#$&()*!+=;,.?\''))
	oauthRedirectUrl += "&scope=" + str(urllib.parse.quote(myScope, safe='_'))
	return oauthRedirectUrl


# GET TOKEN - API call to get the user access token
def get_token(myRedirectURI, teamsAuthCode, myClientID, myClientSecret):
    data = {'grant_type': 'authorization_code', 'redirect_uri': myRedirectURI, 'code': teamsAuthCode, 'client_id': myClientID, 'client_secret': myClientSecret}
    header = {'content-type': 'application/x-www-form-urlencoded'}
    myAccessToken = ""
    try:
        req = requests.post('https://api.ciscospark.com/v1/access_token', headers=header, data=data)
        response = req.json()
        myAccessToken = response['access_token']
    except:
        myAccessToken = "error"
    return myAccessToken


# GET MY DETAILS - API call to get my account information
def get_myDetails(mytoken):
    header = {'Authorization': "Bearer " + mytoken,'content-type': 'application/json; charset=utf-8'}
    result = requests.get(url='https://api.ciscospark.com/v1/people/me', headers=header)
    return result.json()



if __name__ == '__main__':
    app.run()
