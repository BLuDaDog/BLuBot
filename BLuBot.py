#BLuBot v0.2 by BLuDaDoG (reddit)
#TODO:
#add !socials command to link social media/venmo/etc
#!help/!commands/!actions command to list user commands
#add an admin !silence command that toggles the bot updating the chat
#add a '!public' command to support toggling the bot to accepting non-host cmds

#TODO: next major version
#REFACTOR: CacheableCollection & CacheableCollectionItem classes type for parent of Requests/Users, serialize() cache() deserialize() and reverseReference prop
#externalize the command permission table
#get the damn praw.ini to work
#make the private properties prefixed: _
#add poll features

import praw
import pdb
import re
import os
import json
import datetime
import sys
import pytz
import time
from datetime import timedelta

STREAM_ID = "sy5wyu"
CACHE_DIR = "D:/Dev/Python/RequestBot/v0.2/"
CLIENT_ID = ""
CLIENT_SECRET = ""
PASSWORD = ""
USERNAME = ""
USER_AGENT = "BluzCruzMuze 0.1"
DEBUG = True



class Users:
    def __init__(self, bot, cacheDir = None):
        self.bot = bot
        self.users = []
        if cacheDir is not None:
            self.cachePath = os.path.join(cacheDir,"users.txt")
            try:
                with open(self.cachePath, "r") as f:
                    data = f.read()
                    self.deserialize(data)
            except:
                #no users added or file doesn't exist yet
                pass

        if len(self.users) == 0:
            self.add(self.bot.reddit.user.me().name)

    def __call__(self, username):
        for user in self.users:
            if user.username == username:
                return user
        return None

    def cache(self):
        if self.cachePath is not None:
            with open(self.cachePath, "w") as f:
                f.write(self.serialize())
            return True
        return False

    def serialize(self):
        data = ""
        for user in self.users:
            data += user.serialize() + "\n"
        return data.strip()

    def deserialize(self, data):
        for jsonUser in data.split("\n"):
            if jsonUser is not None and jsonUser != "":
                User.deserialize(jsonUser, self)
        return True

    def user(self, username):
        users.append(User(username, self))

    def containsUsername(self, username):
        return any(user.username == username for user in self.users)

    def add(self, username):
        return User(username, self)

class User:
    #only for new users
    def __init__(self, username, usersReference):
        self.username = username
        self.permLevel = 1
        self.reverseReference = usersReference #store reverse reference to container to refresh the cache everytime a user is changed
        self.reverseReference.users.append(self)
        if username is not None:
            self.cache()

    def cache(self):
        self.reverseReference.cache()

    def promote(self):
        if self.permLevel < len(Bot.BotCommand.ACTIONS):
            self.permLevel += 1
            self.cache()
        return self.permLevel

    def demote(self):
        if self.permLevel > 0:
            self.permLevel -= 1
            self.cache()
        return self.permLevel

    def serialize(self):
        tempDict = self.__dict__.copy()
        tempDict.pop('reverseReference') #remove collection reference before storing, this reference will change every time the script runs
        return json.dumps(tempDict).replace("\n", "")

    def getFriendlyPermLevel(self):
        match self.permLevel:
            case 0:
                friendlyPermLevel = "Banned User"
            case 1:
                friendlyPermLevel = "Basic User"
            case 2:
                friendlyPermLevel = "Super User"
            case 3:
                friendlyPermLevel = "Administrator"
            case _:
                friendlyPermLevel = "UNKNOWN"
        return friendlyPermLevel

    #only for existing users, existing users aren't stored with the collection, reference, needs to be added
    @staticmethod
    def deserialize(data, usersReference):
        user = User(None, usersReference)
        tempDict = json.loads(data)
        for key in tempDict:
            setattr(user, key, tempDict[key])
        user.cache()
        return user

class Requests:
    def __init__(self, cacheDir):
        self.requests = []
        if cacheDir is not None:
            self.cachePath = os.path.join(cacheDir,"requests.txt")
            try:
                with open(self.cachePath, "r") as f:
                    data = f.read()
                    self.deserialize(data)
            except:
                pass

    def add(self, requestor, request):
        return Request(requestor, request, self)

    def insert(self, request, index):
        if index >= 0:
            self.requests.insert(index, request)
            self.cache()
            return True
        return False

    def next(self):
        if len(self.requests) > 0:
            self.requests.pop(0)
            self.cache()
            if len(self.requests) > 0:
                return self.requests[0]
        return None

    def remove(self, index):
        index = int(index)
        if len(self.requests) > int(index):
            request = self.requests.pop(index)
            self.cache()
            return request
        return None

    def clear(self):
        if len(self.requests) > 0:
            self.requests.clear()
            self.cache()
            return True
        else:
            return False

    def requestsByRequestor(self, requestor):
        requestDict = {}
        for i in range(len(self.requests)):
            if self.requests[i].requestor == requestor:
                requestDict[i] = self.requests[i]
        return requestDict

    def move(self, index, newQueueSpot):
        try:
            return self.insert(self.remove(index),newQueueSpot)
        except:
            return False

    def toString(self):
        requestString = ""
        for i in range(len(self.requests)):
            requestString += "({}) {} [{}]\n".format(i,self.requests[i].request,self.requests[i].requestor)  #(SONGNUMBER) SONGREQUEST [REQUESTOR]
        return requestString.strip()

    def serialize(self):
        data = ""
        for request in self.requests:
            data += request.serialize() + "\n"
        return data.strip()

    def deserialize(self, data):
        for jsonRequest in data.split("\n"):
            if jsonRequest is not None and jsonRequest != "":
                Request.deserialize(jsonRequest, self)
        return True

    def cache(self):
        if self.cachePath is not None:
            with open(self.cachePath, "w") as f:
                f.write(self.serialize())
            return True
        return False

class Request:
    def __init__(self, requestor, request, requestsReference):
        self.requestor = requestor
        self.request = request
        self.reverseReference = requestsReference
        self.reverseReference.requests.append(self)
        if self.request is not None:
            self.cache()

    def serialize(self):
        tempDict = self.__dict__.copy()
        tempDict.pop('reverseReference') #remove collection reference before storing, this reference will change every time the script runs
        return json.dumps(tempDict).replace("\n", "")

    def cache(self):
        self.reverseReference.cache()

    @staticmethod
    def deserialize(data, requestsReference):
        request = Request(None, None, requestsReference)
        tempDict = json.loads(data)
        for key in tempDict:
            setattr(request, key, tempDict[key])
        request.cache()
        return request

#not implemented
class SongRequest(Request):
    def __init__(self, requestor, request):
        super().__init__(requestor, request)
        self.songName = "" #need ytube lookup to identify song name + band?
        self.bandName = "" #^
        self.songLength = "" #^
        self.songKey = "" #^
        self.ytURL = "" #^
        self.tabURL = "" #https://github.com/joncardasis/ultimate-api/

class Bot():
    def __init__(self, streamID, cacheDir, start = True, minResponseSeconds = 3, postToChat = False, fetchOldComments = False):

        self.running = start
        self.streamID = streamID
        self.postToChat = postToChat
        self.reddit = praw.Reddit(
            user_agent = USER_AGENT,
            client_id = CLIENT_ID,
            client_secret = CLIENT_SECRET,
            username = USERNAME,
            password = PASSWORD
        )
        self.commands = []
        self.cacheDir = os.path.normpath(cacheDir)

        self.users = Users(self, self.cacheDir)
        self.requests = Requests(self.cacheDir)

        #limit=0 will read remove items not in original response, limit=None will read all comments (takes longer to query)
        if fetchOldComments:
            self.replaceMoreCount = None
        else:
            self.replaceMoreCount = 0

       # self.submission = self.reddit.submission(self.streamID)
       # if self.submission is not None:
        self.startTimestamp = datetime.datetime.now(datetime.timezone.utc)

        while self.running:
            self.submission = self.reddit.submission(self.streamID)
            if self.submission is not None:
                self.comments = self.submission.comments
                self.comments.replace_more(limit=self.replaceMoreCount)
                self.comments = self.comments.list()
                # self.comments.sort(key=lambda comment: comment.created) #this will sort the comments by time, but that means every pulse, the last command will be processed first, may screw up queue order
                for topLevelComment in self.comments:
                    if topLevelComment is not None:
                        if topLevelComment.author is not None:
                            cmd = self.command(topLevelComment)
                            if DEBUG:
                                print(cmd.consoleResult())
                            if cmd.isProcessed and self.postToChat:
                                self.submission.reply(cmd.userResult())
                time.sleep(minResponseSeconds) #additional pause to slow things down a bit and not slam the API
            else:
                self.running = False

    def command(self, prawComment):
        return Bot.BotCommand(self, prawComment)

    class BotCommand:

        ACTIONS = {
            #1-BASIC USER
            1 : [
            "!me",
            "!queue",
            "!list",
            "!songlist",
            "!cancel",
            "!request"
            ],
            #2-SUPER USER
            2: [],
            #3-ADMIN/HOST
            3: [
            "!remove",
            "!next",
            "!bumpup",
            "!bumpdown",
            "!clear",
            "!promote",
            "!demote",
            "!shutdown"
            ]
        }


        def __init__(self, bot, prawComment):
            self.permLevel = None
            self.status = "VALIDATING"
            self.result = None
            self.isProcessed = False
            self.isEdited = prawComment.edited
            self.id = prawComment.id
            self.requestor = prawComment.author.name
            self.rawCommand = prawComment.body
            self.bot = bot
            self.timestamp = pytz.UTC.localize(datetime.datetime.utcfromtimestamp(prawComment.created_utc))
            tmpSplit = self.rawCommand.split()
            self.action = tmpSplit[0]
            if len(tmpSplit) > 1:
                self.actionArgs = tmpSplit[1:]
            if self.isValid():
                if self.isAuthorized():
                    if self.process():
                        self.status = "PROCESSED"
                        self.isProcessed = True

        def userResult(self):
            return self.result

        def consoleResult(self):
            return "{} - {}".format(self.status, self.result)

        def isValid(self):
            #is command submitted after the bot started?
            if  self.bot.startTimestamp >= self.timestamp:
                self.status = "STALE_CMD"
                self.result = "BotTimestamp({}) >= CmdTimestamp({}) : [{}] - {}".format(self.bot.startTimestamp, self.timestamp, self.requestor, self.rawCommand)
                return False

            #don't process edited comments, original comment must be accurate
            if self.isEdited:
                self.status = "EDITED_CMD"
                return False

            #is this message tagged as a command / starts with '!'
            #technically redundant since we check the action list, but this can trim out some items faster
            if self.action[0:1] != '!':
                self.status = "NON_CMD"
                return False

            #is the command a registered command? (cmdPermission returns None if not found in action list)
            if self.cmdPermission() is None:
                self.status = "INVALID_CMD"
                return False

            #is command already processed?
            if any(cmd.id == self.id for cmd in self.bot.commands):
                self.status = "DUPLICATE_CMD"
                return False
            self.bot.commands.append(self)

            self.status = "VALID_CMD"
            return True

        def isAuthorized(self):
            user = self.bot.users(self.requestor)
            if user is not None:
                self.userPermLevel = user.permLevel
            else:
                self.userPermLevel = 1
            if self.userPermLevel >= self.permLevel:
                self.status = "AUTHORIZED"
                return True
            else:
                self.status = "UNAUTHORIZED"
                return False

        def cmdPermission(self):
            #short out to make it run a bit faster if we've already fetched this, mostly to support updates so I don't have to track if this has been executed yet
            if self.permLevel is not None:
                return self.permLevel
            for permLevel in self.ACTIONS.keys():
                if self.action in self.ACTIONS[permLevel]:
                    self.permLevel = permLevel
                    return self.permLevel
            return None

        def process(self):
            self.status = "PROCESSING"
            match self.rawCommand.split():
                case ["!me"]:
                    #get my requested requests and display
                    userReqs = self.bot.requests.requestsByRequestor(self.requestor)
                    self.result = "{}, here's your requests: ".format(self.requestor)
                    for requestIndex in userReqs.keys():
                        self.result += "({}) - {}".format(requestIndex, userReqs[requestIndex].request)
                    if len(userReqs.keys()) > 0:
                        return True
                    else:
                        self.result = "{} - you have no requests in the queue.".format(self.requestor)
                        return False
                case ["!queue"] | ["!songlist"] | ["!list"]:
                    #display song queue
                    self.result = self.bot.requests.toString()
                    return True
                case ["!cancel"]:
                    #didn't provide a song #, cancel all user requests
                    userReqs = self.bot.requests.requestsByRequestor(self.requestor)
                    self.result = "Canceled: "
                    for requestIndex in reversed(list(userReqs.keys())):
                        self.bot.requests.remove(requestIndex)
                        self.result += "({}) - {}".format(requestIndex, userReqs[requestIndex].request)
                    if self.result != "Canceled: ":
                        return True
                    else:
                        self.result = "{} - you have no requests in the queue.".format(self.requestor)
                        return False
                case ["!cancel", requestIndex] | ["!remove", requestIndex]:
                    #cancel song request (optional song # if superuser/admin)
                    if int(requestIndex) < 0:
                        self.result = "Invalid request index: {}".format(requestIndex)
                        return False

                    match (self.userPermLevel):
                        case 0 | 1:
                            self.result = "{} - insufficient permission to cancel a request by number.  If you're trying to cancel your single request, just use '!cancel'.".format(self.requestor)
                            return False
                        case 2:
                            if requestIndex in self.bot.requests.requestsByRequestor(self.requestor).keys():
                                removedRequest = self.bot.requests.remove(requestIndex)
                                self.result = "Canceled: ({}) - {}".format(requestIndex, removedRequest.request)
                                return True
                            else:
                                self.result = "{} - insufficient permission to cancel a song requested by another user!".format(self.requestor)
                                return False
                        case 3:
                            if int(requestIndex) < len(self.bot.requests.requests):
                                removedRequest = self.bot.requests.remove(requestIndex)
                                self.result = "Canceled: ({}) - {}".format(requestIndex, removedRequest.request)
                                return True
                            else:
                                self.result = "{} not found in the request queue.".format(requestIndex)
                                return False
                        case _:
                            self.result = "UNKNOWN PERMISSION LEVEL"
                            return False
                case ["!request", *request]:
                    #request an item
                    if len(self.bot.requests.requestsByRequestor(self.requestor)) > 0:
                        if self.userPermLevel > 1:
                            #must have permission grp 2 or 3 to request multiple songs
                            self.bot.requests.add(self.requestor, " ".join(request))
                            self.result = "{} - I've added your request ({}) to the queue.  It's at #{} in the queue.".format(self.requestor, " ".join(request), len(self.bot.requests.requests)-1)
                            return True
                        else:
                            self.result = "{} - you already have a request in the queue.".format(self.requestor)
                            return False
                    else:
                        self.bot.requests.add(self.requestor, " ".join(request))
                        self.result = "{} - I've added your request ({}) to the queue.  It's at #{} in the queue.".format(self.requestor, " ".join(request), len(self.bot.requests.requests)-1)
                        return True

                case ["!next"] | ["!bumpup", "1"]:
                    #remove song #1 and bump everything up
                    oldReq = self.bot.requests.requests[0]
                    newReq = self.bot.requests.next()
                    self.result = "That was {} requested by {}.  Next up is {} requested by {}!".format(oldReq.request, oldReq.requestor, newReq.request, newReq.requestor)
                    return True
                case ["!clear"]:
                    #remove all songs from queue
                    if(self.bot.requests.clear()):
                        self.result = "Request queue cleared."
                        return True
                    else:
                        self.result = "No requests to clear."
                        return False
                case ["!bumpup", requestIndex]:
                    #bump song #X up one
                    if int(requestIndex) < len(self.bot.requests.requests) and int(requestIndex) >= 0:
                        self.bot.requests.move(int(requestIndex), int(requestIndex)-1)
                        self.result = "Bumped {} to spot {}.".format(self.bot.requests.requests[int(requestIndex)-1].request, int(requestIndex)-1)
                        return True
                    else:
                        self.result = "Invalid song number: {}".format(requestIndex)
                        return False
                case ["!bumpdown", requestIndex]:
                    #bump song #X down one
                    if int(requestIndex) < len(self.bot.requests.requests) and int(requestIndex) >= 0:
                        self.bot.requests.move(int(requestIndex), int(requestIndex)+1)
                        self.result = "Bumped {} to spot {}.".format(self.bot.requests.requests[int(requestIndex)+1].request, int(requestIndex)+1)
                        return True
                    else:
                        self.result = "Invalid song number: {}".format(requestIndex)
                        return False
                case ["!promote", promoteeName]:
                    #increase user permission by 1
                    promotee = self.bot.users(promoteeName)
                    if promotee is None:
                        promtee = self.bot.users.add(promoteeName)
                    if promotee.permLevel < self.userPermLevel:
                        promotee.promote()
                        self.result = "Promoted user ({}) to permission level {}.".format(promoteeName,promotee.permLevel)
                        return True
                    else:
                        self.result = "Promotee ({}={}) is equal or greater permission level than promoter ({}={}).".format(promoteeName,promotee.permLevel,self.userPermLevel)
                        return False
                case ["!demote", demoteeName]:
                    #decrease user permission by 1
                    #increase user permission by 1
                    demotee = self.bot.users(demoteeName)
                    if demotee is None:
                        demotee = self.bot.users.add(demoteeName)
                    #demoter must have higher permission
                    if demotee.permLevel < self.userPermLevel:
                        demotee.demote()
                        self.result = "Demoted user ({}) to permission level {}.".format(demoteeName,demotee.permLevel)
                        return True
                    else:
                        self.result = "Demotee ({}={}) is equal or greater to the permission level of the demoter ({}={}) and the demoter is not the host.".format(demoteeName,demotee.permLevel,self.requestor,self.userPermLevel)
                        return False
                case ["!shutdown"]:
                    #shutdown bot
                    self.bot.running = False
                    self.result = "BotRunning=False..."
                    return True




if __name__ == '__main__':
    myBot = Bot(STREAM_ID,CACHE_DIR)

    #test section, since
    #myBot.submission = myBot.reddit.submission(STREAM_ID)
    #myBot.comments = myBot.submission.comments
    #myBot.comments.replace_more(limit=None) #limit=0 will read portion?, limit=None will read replies
    #myBot.comments = myBot.comments.list()
    #myBot.comments.sort(key=lambda comment: comment.created)
    #myBot.startTimestamp = myBot.startTimestamp - timedelta(days=1)
    #cmd = myBot.command(myBot.comments[len(myBot.comments)-13])
    #print(cmd.consoleResult())


