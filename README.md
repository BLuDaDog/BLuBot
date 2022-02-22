# BLuBot
reddit queue/request bot


Dependencies:

1) Python 3.10 or greater

2) PRAW (Python Reddit API Wrapper)

3) Bot python script

4) Reddit Account with an API application


Installation/Setup:
1) Python 3.10 can be found here: https://www.python.org/downloads/

*During the install allow the Path directory to be added to your environmental variables, or you will have to manually add it after.

2) PRAW - https://praw.readthedocs.io/en/latest/getting_started/installation.html
From a command prompt, type: pip install praw

3) Download the script(s) from this git repository

4) Reddit account / API

a) Sign up for a reddit account, login, then go to: https://www.reddit.com/prefs/apps/

b) Click the button to create another application

c) Give your app a name

d) Choose the “script” option

e) Set the redirect uri to http://127.0.0.1

f) Click Create app

g) Save the key for “secret” and the key under “personal use script”, we’ll need those later

h) Go to https://www.reddit.com/wiki/api

i) Read the details and click the link at the bottom: “Read the full API terms and sign up for usage” - this is required to access the reddit API

j) Populate the fields and submit (OAUTH Client ID is the key from “personal use script”)

k) Open the bot script (.py) from step 3 in notepad

l) Near the top of the code, configure these values:

  STREAM_ID = "rbi13o" -last part of the URL, ie https://www.reddit.com/rpan/r/RedditSessions/rbi13o 
  
  CACHE_DIR = "D:/Dev/Python/RequestBot/v0.2/"  -local path to save the values 
  
  CLIENT_ID = "fjijsd_sjdijsw828skdjASKd" -client ID from step 4-G
  
  CLIENT_SECRET = "xxXxxXxxxxxxXxxxxxxxx" -client secret from step 4-G
  
  PASSWORD = "redditpassword" -reddit bot account password
  
  USERNAME = "redditusername" -reddit bot account username
  
  USER_AGENT = "android:com.example.myredditapp:v1.2.3 (by u/username)" -unique ID to help reddit route data - https://praw.readthedocs.io/en/stable/getting_started/quick_start.html
  
  DEBUG = True  -determines if the console will display debugging data
  
m) Save the script changes, and run it once the stream is online

*You will need to update the STREAM_ID when loading a new stream.  This can be parametized, but it will require another change to the code and manual invoking of the bot start.  I’ll do a writeup on this later.
