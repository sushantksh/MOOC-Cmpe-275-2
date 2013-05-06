"""
6, Apr 2013

Example domain logic for the RESTful web service example.

This class provides basic configuration, storage, and logging.
"""

import sys
import os
import socket
import StringIO
import json

# moo 
from data.mongo import Storage

#
# Room (virtual classroom -> Domain) functionality - note this is separated 
# from the RESTful implementation (bottle)
#
# TODO: only return objects/data and let moo.py handle formatting through 
# templates
#
class Room(object):
    # very limited content negotiation support - our format choices
    # for output. This also shows _a way_ of representing enums in python
    json, xml, html, text = range(1,5)

    #
    # setup the configuration for our service
    #
    def __init__(self,base,conf_fn):
        self.host = socket.gethostname()
        self.base = base
        self.conf = {}

        # should emit a failure (file not found) message
        if os.path.exists(conf_fn):
            with open(conf_fn) as cf:
                for line in cf:
                    name, var = line.partition("=")[::2] #returns 1st and 3rd param of list.
                    self.conf[name.strip()] = var.strip()
        else:
            raise Exception("configuration file not found.")

        # create storage
        self.__store = Storage()


    #
    # example: find data
    #
    def find(self,name):
        print '---> classroom.find:',name
        return self.__store.find(name)

    #
    # example: remove data
    #
    def remove(self,name):
        print '---> classroom.remove:',name
        return self.__store.remove(name)

    #
    # example: add data
    #
    def add(self,entity):
        try:
            self.__store.insert(entity)
            self.__store.names();
            return 'success'
        except:
            return 'failed'

            # TODO success|failure

    #_________________________________________________________________________________
    # example: sign in
    #
    def signIn(self,email,pwd):
        try:
            print "I am going from room to storage -----------> SIGN IN"
            return self.__store.signIn(email,pwd)
        except:
            return { "signIn": "false"}

    #
    # example: sign out
    #
    def signOut(self,email):
        print "Sign out function of room"
        return self.__store.signOut(email)

    #
    # example: signUp
    #
    def signUp(self,email,pwd,fName,lName):
        try:
            print "I am going from room to stroge  -----------> Sign UP"
            return self.__store.signUp(email,pwd,fName,lName)
        except:
            return { "signUp": "false"}

    #
    # Get Details of the user
    #
    def getUser(self, email):
        try:
            print "Classroom.py -------> Get user"
            return self.__store.getUser(email)
        except:
            print "Error", sys.exc_info()[0]
            return {"found": "false"}
    #
    # delete user
    #
    def deleteUser(self,email):
        try:
            print "Classroom.py -----> delete user"
            return self.__store.deleteUser(email)
        except:
            print "Error", sys.exc_info()[0]
            return {"found": "false"}
    #
    # update user
    #
    def updateUser(self, email, password, firstName, lastName):
        try:
            print "Classroom.py -----> update user"
            return self.__store.updateUser(email, password, firstName, lastName)
        except:
            print "Error", sys.exc_info()[0]
            return {"updateUser": "false"}

    # _________________________________ COURSE COLLECTION _______________________________ #
    #
    # Enroll Course
    #
    def enrollCourse(self, email, courseId):
        try:
            print "Room to storage -----> enroll course"
            return self.__store.enrollCourse(email,courseId)
        except:
            print "Error in enroll course of Classroom.py",sys.exc_info()[0]
            return {"errorInQuery": "enrollCourse"}

    #
    # Drop Course
    #
    def dropCourse(self, email, courseId):
        try:
            print "Room to storage -------> Drop Course"
            return self.__store.dropCourse(email, courseId)
        except:
            print "Error in drop course -----> Classroom.py", sys.exc_info()
            return {"errorInQuery": "dropCourse"}

    #
    # Add Course
    #
    def addCourse(self, jsonObj):
        try:
            print "Room to storage -----> Add Course"
            return self.__store.addCourse(jsonObj)
        except:
             print "Error in Add course -------> Classroom.py", sys.exc_traceback
             return {"errorInQuery": "AddCourse"}



    #
    #List Course
    #
    def listCourse(self):
        try:
            print "room to storage ------> List Course"
            return self.__store.listCourse()
        except:
            print "Error in Getting listing details ---> classroom.py"
            return {"errorInQuery": "listCourse"}



    #
    #Get Course
    #
    def getCourse(self, courseId):
        try:
            print "room to stroage ------> Get Course"
            return self.__store.getCourse(courseId)
        except:
            print "Error in Getting course details ---> classroom.py"
            return {"errorInQuery": "getCourse"}

    #
    # Delete Course
    #
    def deleteCourse(self, id):
        print "delete Course moo.py"
        return self.__store.deleteCourse(id)

    # ___________________________________________ QUIZZES ___________________________________________
    #
    # Add Quiz
    #
    def addQuiz(self, jsonObj):
        print "Room to storage ------> add quiz"
        return self.__store.addQuiz(jsonObj)
    #
    #Get Quiz
    #
    def getQuiz(self, quizId):
        try:
            print "room to stroage ------> Get Quiz"
            return self.__store.getQuiz(quizId)
        except:
            print "Error in Getting Quiz details ---> classroom.py"
            return {"errorInQuery": "getQuiz"}

    #
    #List Quiz
    #
    def listQuiz(self):
        try:
            print "room to storage ------> List Quiz"
            return self.__store.listQuiz()
        except:
            print "Error in  listing Quiz details ---> classroom.py"
            return {"errorInQuery": "listQuiz"}

    #
    # Delete Quiz
    #
    def deleteQuiz(self, id):
        print "delete Quiz moo.py"
        return self.__store.deleteQuiz(id)


    # ___________________________________________ ANNOUNCEMENTS ___________________________________________
    #
    # Add Announcement
    #
    def addAnnouncement(self, jsonObj):
        print "Room to storage ------> add announcement"
        return self.__store.addAnnouncement(jsonObj)
    #
    #Get Announcement
    #
    def getAnnouncement(self, announcementId):
        try:
            print "room to stroage ------> Get Announcement"
            return self.__store.getAnnouncement(announcementId)
        except:
            print "Error in Getting Announcement details ---> classroom.py"
            return {"errorInQuery": "getAnnouncement"}

    #
    #List Announcement
    #
    def listAnnouncement(self):
        try:
            print "room to storage ------> List Announcement"
            return self.__store.listAnnouncement()
        except:
            print "Error in  listing Announcement details ---> classroom.py"
            return {"errorInQuery": "listAnnouncement"}

    #
    # Delete Announcement
    #
    def deleteAnnouncement(self, id):
        print "delete Announcement moo.py"
        return self.__store.deleteAnnouncement(id)



    # ___________________________________________ DISCUSSIONS ___________________________________________
    #
    # Add Discussion
    #
    def addDiscussion(self, jsonObj):
        print "Room to storage ------> add Discussion"
        return self.__store.addDiscussion(jsonObj)
    #
    #Get Discussion
    #
    def getDiscussion(self, discussionId):
        try:
            print "room to stroage ------> Get Discussion"
            return self.__store.getDiscussion(discussionId)
        except:
            print "Error in Getting Discussion details ---> classroom.py"
            return {"errorInQuery": "getDiscussion"}

    #
    #List Discussion
    #
    def listDiscussion(self):
        try:
            print "room to storage ------> List Discussion"
            return self.__store.listDiscussion()
        except:
            print "Error in  listing Discussion details ---> classroom.py"
            return {"errorInQuery": "listDiscussion"}

    #
    # Delete Discussion
    #
    def deleteDiscussion(self, id):
        print "delete Discussion moo.py"
        return self.__store.deleteDiscussion(id)




    #_________________________________________________________________________________________
    # TODO success|failure

    #
    # dump the configuration in the requested format. Note placing format logic
    # in the functional code is not really a good idea. However, it is here to
    # provide an example.
    #
    #
    def dump_conf(self,format):
        if format == Room.json:
            return self.__conf_as_json()
        elif format == Room.html:
            return self.__conf_as_html()
        elif format == Room.xml:
            return self.__conf_as_xml()
        elif format == Room.text:
            return self.__conf_as_text()
        else:
            return self.__conf_as_text()

    #
    # output as xml is supported through other packages. If
    # you want to add xml support look at gnosis or lxml.
    #
    def __conf_as_json(self):
        return "xml is hard"

    #
    #
    #
    def __conf_as_json(self):
        try:
            all = {}
            all["base.dir"] = self.base
            all["conf"] = self.conf
            return json.dumps(all)
        except:
            return "error: unable to return configuration"

    #
    #
    #
    def __conf_as_text(self):
        try:
            sb = StringIO.StringIO()
            sb.write("Room Configuration\n")
            sb.write("base directory = ")
            sb.write(self.base)
            sb.write("\n\n")
            sb.write("configuration:\n")

            for key in sorted(self.conf.iterkeys()):
                print >>sb, "%s=%s" % (key, self.conf[key])

            str = sb.getvalue()
            return str
        finally:
            sb.close()

        #
        return "text"

    #
    #
    #
    def __conf_as_html(self):
        try:
            sb = StringIO.StringIO()
            sb.write("<html><body>")
            sb.write("<h1>")
            sb.write("Room Configuration")
            sb.write("</h1>")
            sb.write("<h2>Base Directory</h2>\n")
            sb.write(self.base)
            sb.write("\n\n")
            sb.write("<h2>Configuration</h2>\n")

            sb.write("<pre>")
            for key in sorted(self.conf.iterkeys()):
                print >>sb, "%s=%s" % (key, self.conf[key])
            sb.write("</pre>")

            sb.write("</body></html>")

            str = sb.getvalue()
            return str
        finally:
            sb.close()

#
# test and demonstrate the setup
#
if __name__ == "__main__":
    if len(sys.argv) > 2:
        base = sys.argv[1]
        conf_fn = sys.argv[2]
        svc = Room(base,conf_fn)
        svc.dump_conf()
    else:
        print "usage:", sys.argv[0],"[base_dir] [conf file]"