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
# Using Git to collaborate

# bottle framework
from bottle import request, response, route, abort, run, template


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
      rsp["msg"] = msg
      return json.dumps(all)
   else:
      return msg


#
# example of a RESTful query
#
#@route('/moo/data/:name', method='GET')
#def find(name):
#   print '---> moo.find:',name
#   return room.find(name)

#
# example of a RESTful query
#
#@route('/moo/data/:name', method='DELETE')
#def remove(name):
#  print '---> moo.remove:',name
#  return room.remove(name)

#
# example adding data using forms
#
#@route('/moo/data', method='POST')
#def add():
#   print '---> moo.add'

   # example list form values
#   for k,v in request.forms.allitems():
#      print "form:",k,"=",v
#   data = request.body.readline()
#   if not data:
#       abort(400, 'No data received')
#   entity = json.loads(data)
#   if not entity.has_key('_id'):
#       abort(400, 'No _id specified')
   #name = request.forms.get('name')
   #value = request.forms.get('value')
#   return room.add(entity)

#____________________________________________________________________________________________________
# example sign in for user
#
# RANGERS
#
# Checks if the user is present or not, if not returns a error and if present display shows.html

#@route('/user/auth', method='POST')
#def login():
#   print '---> Checking User is present or not!!'
#   k = request.forms.allitems()
#   print "I am in LogIn function of moo.py"
#   for key, value in k:
#      data = json.loads(key)
#      print str(data)

   # example list form values
#   return room.signIn(data['email'], data['pwd'])


#########################################################################################################
#########################################################################################################
#########################################################################################################
#-------------------------------------------- TEAM RANGERS CODE-----------------------------------------#

#_____________________________________________User collection ___________________________________________

#
# Create User
#
@route('/user', method = 'POST')
def createUser():
   print 'create User ------> moo.signUp'
   jsonData = json.loads(request.body.read())
   if not jsonData:
       abort(400, 'No data received')
   print jsonData
   return room.createUser(jsonData)


#
# Get User / View user / Details of User
#
@route('/user/:email', method = 'GET')
def getUser(email):
    print 'Get User details Mooc.py'
    if not email:
        abort(400, 'No Email Id specified')
    return room.getUser(email)


#
# Update User - It updates the course entries of user like Enrolled courses, Own courses and Quizzes & Grades
#
@route('/user/update:email', method ='PUT')
def updateUser(email):
    print 'Update User Moo.py'
    jsonData = json.loads(request.body.read())
    if not jsonData:
       abort(400, 'No data received')
    return room.updateUser(jsonData, email)


#
# delete user
#
@route('/user/:email', method = 'DELETE')
def deleteUser(email):
    print 'Delete User Moo.py'
    return room.deleteUser(email)



#
# Enroll Course
#

@route('/course/enroll', method ='PUT')
def enrollCourse():
    print "Enroll Course moo.py"
    jsonData = json.loads(request.body.read())
    if not jsonData:
       abort(400, 'No data received')
    return room.enrollCourse(jsonData)



#
# Drop Course
#

@route('/course/drop', method ='PUT')
def dropCourse():
    print "Drop Course moo.py"
    jsonData = json.loads(request.body.read())
    if not jsonData:
       abort(400, 'No data received')
    return room.dropCourse(jsonData)




#________________________________________________CATEGORY COLLECTION ________________________________________

#
# Add Catergory
#
@route('/category', method='POST')
def addCategory():
    print "add category ---> moo.py"
    jsonData = json.loads(request.body.read())
    if not jsonData:
       abort(400, 'No data received')
    return room.addCategory(jsonData)



#
# Get Category
#
@route('/category/:categoryId', method='GET')
def getCategory(categoryId):
    print "Get Category moo.py", categoryId
    if not categoryId:
       abort(400, 'No data received')
    return room.getCategory(categoryId)



#
# List Category
#
@route('/category/list', method='GET')
def listCategory():
    print "List category moo.py"
    return room.listCategory()


# _______________________________________________ COURSE COLLECTION _________________________________________________#

#
# Add Course
#

@route('/course', method = 'POST')
def addCourse():
    print "Add Course moo.py"
    jsonData = json.loads(request.body.read())
    if not jsonData:
        abort(400, "No Json Data Received")
    return room.addCourse(jsonData)


#
# Update Course ---------------------------------------
#

@route('/course/update/:courseId', method = "PUT")
def updateCourse(courseId):
    print "I am in update course", courseId
    jsonData = json.loads(request.body.read())
    if not jsonData:
        abort(400, "No Json Data Received")
    return room.updateCourse(jsonData, courseId)



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
@route('/course/:courseId', method='GET')
def getCourse(courseId):
    print "Get Course moo.py"
    if not courseId:
        abort(400, 'No course Id specified')
    return room.getCourse(courseId)

#
# Get owned courses of the user to run the functionalities of quizzes and announcements
#
@route('/course/own/:email', method='GET')
def getOwnedCourses(email):
    print "Get owned courses moo.py"
    if not email:
        abort(400, 'No email Id specified')
    return room.getOwnedCourses(email)

#
# Delete Course
#

@route('/course/:courseId', method = 'DELETE')
def deleteCourse(courseId):
    print "Delete Course moo.py"
    if not courseId:
        abort(400, 'No course Id specified')
    return room.deleteCourse(courseId)

# _____________________________________________________________ QUIZZES __________________________

#
# Add Quiz
#
@route('/quizzes', method = 'POST')
def addQuiz():
    print "Add Quiz----> Moo.py"
    jsonData = json.loads(request.body.read())
    if not jsonData:
        abort(400, 'No jsonData specified')
    return room.addQuiz(jsonData)

#
# Get Quiz
#
@route('/quiz/:id', method = 'GET')
def getQuiz(id):
    print "Get  Quiz----> Moo.py"
    if not id:
        abort(400, 'No id specified')
    return room.getQuiz(id)


#
# List Quiz
#
@route('/quiz/list', method = 'GET')
def listQuiz():
    print 'List all quizes moo.py'
    return room.listQuiz()

#
# Delete Quiz
#
@route('/quiz/:id', method = 'DELETE')
def deleteQuiz(id):
    print "Get Quiz moo.py"
    if not id:
        abort(400, 'No id specified')
    return room.deleteQuiz(id)

# ___________________________________ANNOUNCEMENTS _______________________________________________

#
# Add Announcement
#
@route('/announcements' , method = 'POST')
def addAnnouncement():
    print "Add Announcement----> Moo.py"
    jsonData = json.loads(request.body.read())
    if not jsonData:
        abort(400, 'No jsonData specified')
    return room.addAnnouncement(jsonData)

#
# Get Announcement
#
@route('/announcement/:announcementId', method = 'GET')
def getAnnouncement(announcementId):
    print "Get  Announcement----> Moo.py"
    return room.getAnnouncement(announcementId)


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
@route('/announcement/delete/:annId', method = 'DELETE')
def deleteAnnouncement(annId):
    print "Get Announcement moo.py"
    return room.deleteAnnouncement(annId)

# _____________________________________________________________ DISCUSSIONS __________________________

#
# Add Discussion
#
@route('/discussions', method = 'POST')
def addDiscussion():
    print "Add Discussion----> Moo.py"
    jsonData = json.loads(request.body.read())
    #print "JSON VALUE MOO.PY = ", jsonData
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

#____________________________________________________MESSAGES COLLECTION____________________________________

#
#
#


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
