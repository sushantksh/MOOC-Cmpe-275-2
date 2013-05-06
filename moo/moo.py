"""
6, Apr 2013

Example bottle (python) RESTful web service.

This example provides a basic setup of a RESTful service

Notes
1. example should perform better content negotiation. A solution is
   to use minerender (https://github.com/martinblech/mimerender)
"""

import time
import sys
import socket
import bottle
import json

# bottle framework
from bottle import request, response, route, run, template

# moo
from classroom import Room

# virtual classroom implementation
room = None

def setup(base,conf_fn):
   print '\n**** service initialization ****\n'
   global room 
   room = Room(base,conf_fn)

#
# setup the configuration for our service
@route('/')
def root():
   print "--> root"
   return 'welcome'
   

#
#
@route('/moo/ping', method='GET')
def ping():
   return 'ping %s - %s' % (socket.gethostname(),time.ctime())

#
# Development only: echo the configuration of the virtual classroom.
#
# Testing using curl:
# curl -i -H "Accept: application/json" http://localhost:8080/moo/conf
#
# WARN: This method should be disabled or password protected - dev only!
#
@route('/moo/conf', method='GET')
def conf():
   fmt = __format(request)
   response.content_type = __response_format(fmt)
   return room.dump_conf(fmt)

#
# example of a RESTful method. This example is very basic, it does not 
# support much in the way of content negotiation.
#
@route('/moo/echo/:msg')
def echo(msg):
   fmt = __format(request)
   response.content_type = __response_format(fmt)
   if fmt == Room.html:
      return '<h1>%s</h1>' % msg
   elif fmt == Room.json:
      rsp = {}
      rsp["msg"] = msg
      return json.dumps(all)
   else:
      return msg


#
# example of a RESTful query
#
@route('/moo/data/:name', method='GET')
def find(name):
   print '---> moo.find:',name
   return room.find(name)

#
# example of a RESTful query
#
@route('/moo/data/:name', method='DELETE')
def remove(name):
   print '---> moo.remove:',name
   return room.remove(name)

#
# example adding data using forms
#
@route('/moo/data', method='POST')
def add():
   print '---> moo.add'

   # example list form values
   for k,v in request.forms.allitems():
      print "form:",k,"=",v
   data = request.body.readline()
   if not data:
       abort(400, 'No data received')
   entity = json.loads(data)
   if not entity.has_key('_id'):
       abort(400, 'No _id specified')
   #name = request.forms.get('name')
   #value = request.forms.get('value')
   return room.add(entity)

#____________________________________________________________________________________________________
# example sign in for user
#
# RANGERS
#
# Checks if the user is present or not, if not returns a error and if present display shows.html
@route('/user/auth', method='POST')
def login():
   print '---> Checking User is present or not!!'
   k = request.forms.allitems()
   print "I am in LogIn fucntion of moo.py"
   for key, value in k:
      data = json.loads(key)
      print str(data)

   # example list form values
   return room.signIn(data['email'], data['pwd'])

#
# example sign out for user
#
@route('/user/signout/:email', method='GET')
def logout(email):
   print '---> moo.logout', email
   return room.signOut(email)


#
# SignUp / Create User
#
@route('/user', method = 'POST')
def signUp():
   print 'sign UP ------> moo.signUp'
   k = request.forms.allitems()
   print "I am in Sign Up fucntion of moo.py"
   for key, value in k:
      data = json.loads(key)
      print str(data)

   # example list form values
   return room.signUp(data['email'], data['pwd'], data['fName'], data['lName'])


#
# Get User / View user / Details of User
#
@route('/user/:email', method = 'GET')
def getUser(email):
    print 'Get User details Mooc.py'
    return room.getUser(email)


#
# delete user
#
@route('/user/:email', method = 'DELETE')
def deleteUser(email):
    print 'Delete User Moo.py'
    return room.deleteUser(email)


#
# update user
#
@route('/user', method ='PUT')
def updateUser():
    print 'Update User Moo.py'
    k = request.forms.allitems()
    for key, value in k:
      data = json.loads(key)
    return room.updateUser(data['email'],data['pwd'],data['fName'],data['lName'],)

#_______________________________________________ COURSE COLLECTION ______________________________________#
#
# Enroll Course
#
@route('/course/enroll', method ='PUT')
def enrollCourse():
    print "Enroll Course moo.py"
    jsonArray = request.forms.allitems()

    for key,value in jsonArray:
        jsonData = json.loads(key)
        # loads is converting the data into JSON format
        print str(jsonData)

    return room.enrollCourse(jsonData['email'], jsonData['courseId'])

#
# Drop Course
#
@route('/course/drop', method ='PUT')
def dropCourse():
    print "Drop Course moo.py"
    jsonArray = request.forms.allitems()
    for key, value in jsonArray:
        jsonData = json.loads(key)
        print str(jsonData)
    return room.dropCourse(jsonData['email'], jsonData['courseId'])


#
# Add Course
#
@route('/course', method = 'POST')
def addCourse():
    print "Add Course moo.py"
    jsonData = json.loads(request.body.read())
    return room.addCourse(jsonData)


#
# Update Course ---------------------------------------
#
@route('/course' , method = "PUT")
def updateCourse(email):
    json = request.query.get(email)
    print "JSON = ",json
    jsonData = json.loads(request.body.read())
    print "Update course --- > mOO.py"
    return room.updateCourse(jsonData)



#
# List Courses
#
@route('/course/list', method = 'GET')
def listCourse():
    print 'List all courses moo.py'
    return room.listCourse()


#
# Get Course
#
@route('/course/:id', method = 'GET')
def getCourse(id):
    print "Get Course moo.py"
    return room.getCourse(id)

#
# Delete Course
#
@route('/course/:id', method = 'DELETE')
def deleteCourse(id):
    print "Get Course moo.py"
    return room.deleteCourse(id)

# _____________________________________________________________ QUIZZES __________________________

#
# Add Quiz
#
@route('/quizzes' , method = 'POST')
def addQuiz():
    print "Add Quiz----> Moo.py"
    jsonData = json.loads(request.body.read())
    print "JSON VALUE MOO.PY = ", jsonData
    return room.addQuiz(jsonData)

#
# Get Quiz
#
@route('/quiz/:id' , method = 'GET')
def getQuiz(id):
    print "Get  Quiz----> Moo.py"
    return room.getQuiz(id)


#
# List Quiz
#
@route('/quiz', method = 'GET')
def listQuiz():
    print 'List all quizes moo.py'
    return room.listQuiz()

#
# Delete Quiz
#
@route('/quiz/:id', method = 'DELETE')
def deleteQuiz(id):
    print "Get Quiz moo.py"
    return room.deleteQuiz(id)

# _____________________________________________________________ ANNOUNCEMENTS __________________________

#
# Add Announcement
#
@route('/announcements' , method = 'POST')
def addAnnouncement():
    print "Add Announcement----> Moo.py"
    jsonData = json.loads(request.body.read())
    return room.addAnnouncement(jsonData)

#
# Get Announcement
#
@route('/announcement/:id' , method = 'GET')
def getAnnouncement(id):
    print "Get  Announcement----> Moo.py"
    return room.getAnnouncement(id)


#
# List Announcement
#
@route('/announcement/list', method = 'GET')
def listAnnouncement():
    print 'List all announcements moo.py'
    return room.listAnnouncement()

#
# Delete Announcement
#
@route('/announcement/:id', method = 'DELETE')
def deleteAnnouncement(id):
    print "Get Announcement moo.py"
    return room.deleteAnnouncement(id)

# _____________________________________________________________ DISCUSSIONS __________________________

#
# Add Discussion
#
@route('/discussion' , method = 'POST')
def addDiscussion():
    print "Add Discussion----> Moo.py"
    jsonData = json.loads(request.body.read())
    print "JSON VALUE MOO.PY = ", jsonData
    return room.addDiscussion(jsonData)

#
# Get Discussion
#
@route('/discussion/:id' , method = 'GET')
def getDiscussion(id):
    print "Get  Discussion----> Moo.py"
    return room.getDiscussion(id)


#
# List Discussion
#
@route('/discussion/list', method = 'GET')
def listDiscussion():
    print 'List all discussions moo.py'
    return room.listDiscussion()

#
# Delete Discussion
#
@route('/discussion/:id', method = 'DELETE')
def deleteDiscussion(id):
    print "Get Discussion moo.py"
    return room.deleteDiscussion(id)


#_______________________________________________________________________________________
# Determine the format to return data (does not support images)
#
# TODO method for Accept-Charset, Accept-Language, Accept-Encoding, 
# Accept-Datetime, etc should also exist
#
def __format(request):
   #for key in sorted(request.headers.iterkeys()):
   #   print "%s=%s" % (key, request.headers[key])

   types = request.headers.get("Accept",'')
   subtypes = types.split(",")
   for st in subtypes:
      sst = st.split(';')
      if sst[0] == "text/html":
         return Room.html
      elif sst[0] == "text/plain":
         return Room.text
      elif sst[0] == "application/json":
         return Room.json
      elif sst[0] == "*/*":
         return Room.json

      # TODO
      # xml: application/xhtml+xml, application/xml
      # image types: image/jpeg, etc

   # default
   return Room.html

#
# The content type on the reply
#
def __response_format(reqfmt):
      if reqfmt == Room.html:
         return "text/html"
      elif reqfmt == Room.text:
         return "text/plain"
      elif reqfmt == Room.json:
         return "application/json"
      else:
         return "*/*"
         
      # TODO
      # xml: application/xhtml+xml, application/xml
      # image types: image/jpeg, etc