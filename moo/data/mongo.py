"""
Mongo Storage interface
"""

#!/usr/bin/python
import time
import pymongo
import ast
import json
import sys
import uuid

from pymongo import Connection

#localtime = time.asctime( time.localtime(time.time()))
#print "Local current time :", localtime
class Storage(object):
    def __init__(self):
        # initialize our storage, data is a placeholder
        connection = Connection()
        db = connection.cmpe275
        self.uc = db.usercollection
        self.cc = db.coursecollection
        self.catc = db.categorycollection
        self.qc = db.quizcollection
        self.ac = db.announcementcollection
        self.dc = db.discussioncollection
        self.userid = self.uc.count() + 1
        self.rc = db.runCommand

    def insert(self,entity):
        print "---> insert:"
        try:
            self.uc.insert(entity)
            return "added"
        except:
            return "error: data not added"

    def remove(self,name):
        self.uc.remove({ "email" : "test@gmail.com"})
        print "---> remove:",name

    def names(self):
        print "---> names:"
        for user in self.uc.find():
            print user

    def find(self,name):
        print "---> storage.find:",name
        count = self.uc.find({"email":"test@gmail.com"}).count()
        if count > 0:
            return {"found" :"true"}
        else :
            return {"found" :"false"}

    #_________________________________________________________________________________________________
    #
    #  Sign In
    #
    def signIn(self, email, pwd):
        print "---> signIn in mongo.py storage ------> :",email,pwd
        try:
            result = self.uc.find_one({"email": email.strip("'")})

            if len(result) == 0:
                print "user not present"
                return {"status": 0}
            if result["pwd"] == pwd.strip("'"):
                print "user is present in the MongoDB"
                self.uc.update({"email": email.strip("'")}, {"$set": {"status": 1}})
                del result["_id"]
                print result
                return result
            else:
                print "user not present"
                return {"status": 0}
        except:
            print "error in sign in ",sys.exc_info()[0]
            return {"status": 0}

    #
    # SIGN OUT
    #
    def signOut(self, email):
        print "---> signIn:",email
        try:
            self.uc.update({"email": email.strip("'")}, {"$set": {"status": 0}})
            return {"status": 0}
        except:
            print "Error in sign out ", sys.exc_info()[0]
            return {"status": 1}

    #
    # SIGN UP
    #
    def signUp(self, email, pwd, fName, lName):
        print "----> signUp: ", email
        count = self.uc.find({"email":email.strip("'")}).count()
        if count > 0:
            print "user already exist with email ID: ", email
            return {"found":"true"}
        else:
            print "Signing up the user with Email ID: ", email
            try:
                userInfo = {"email" : email, "pwd": pwd , "fName" : fName , "lName" : lName,"status": 0}
                additionInfo = {"own": [],"enrolled": [],"quizzes": [{"quiz": "None","grade": 0,"submitDate": None},{"quiz": "None","grade": 0,"submitDate": None}]}
                result = dict(userInfo.items() + additionInfo.items())
                print result
                self.uc.insert(result)
                print "new user added"
                del result["_id"]
                return result
            except:
                print "error: user not added"
                return {"found": "false"}



    #
    # Get Details of the user
    #
    def getUser(self, email):
        print "Get Details of user with email id ", email
        try:
            userDetails = self.uc.find_one({"email": email.strip("'")})

            if len(userDetails) == 0:
                print "Failed to get details of the user"
                return {"found": "false"}
            else:
                print "Returning Json user details"
                del userDetails["_id"]
                del userDetails["pwd"]
                print userDetails
                return userDetails
        except:
            print "error to get user details", sys.exc_info()[0]
            return {"found": "false"}




    #
    # Delete User
    #
    def deleteUser(self,email):
        print "Deleting the user mongo.py", email
        try:
            count = self.uc.find({"email": email.strip("'")}).count()
            if count > 0:
                try:
                    print "Deleting User finally"
                    self.uc.remove({"email": email})
                    return {"userDeleted": "true"}
                except:
                    print "Failed in deleting user", sys.exc_info()
                    return {"userDeleted": "false"}
            else:
                print "user not found with email id", email
                return {"found": "false"}
        except:
            print "error: Invalid Email id", sys.exc_info()
            return {"found": "false"}



    #
    # Update User
    #

    def updateUser(self,email, password, firstName, lastName):
        print "Updating the user details -> mongo.py", email
        try:
            self.uc.update({"email": email.strip("'")}, {"$set": {"pwd" : password.strip("'"), "fName": firstName.strip("'"),"lName": lastName.strip("'")}})
            updateUserDetails = self.uc.find_one({"email": email.strip("'")})
            if updateUserDetails > 0:
                print "updated the entries of User", email
                del updateUserDetails['_id']
                return updateUserDetails
            else:
                print "Failed to fetch user details"
                return {"updateUserDetails": "false"}
        except:
            print "error: update user failed", sys.exc_info()
            return {"userUpdated": "false"}



    #
    # Enroll Courses
    #
    def enrollCourse(self, email, courseId):
        print "Enroll Course of person", email, courseId
        try:
            checkCourseCount = self.cc.find({"id": courseId}).count()
            if checkCourseCount > 0:
                checkDuplicateCourse = self.uc.find({"email": email.strip("'"), "enrolled": courseId}).count()
                if checkDuplicateCourse == 0:
                    try:
                        self.uc.update({"email": email.strip("'")}, {"$addToSet": {"enrolled": courseId}})
                        print "Updated the entry successfully"
                        userDetails = self.uc.find_one({"email": email.strip("'")})
                        del userDetails['_id']
                        print userDetails
                        return userDetails
                    except:
                        print "error: Failed updating course id", sys.exc_info()
                        return {"updatingCourseId": "failed"}
                else:
                    print "Error: User is enrolled in this course"
                    return {"courseId": "User Is Already Enrolled"}
            else:
                print "Error: Course is either deleted or not present"
                return {"courseId": "Course Not Present"}
        except:
               print "Error: Problem in user entry (INPUT)", sys.exc_info()

    #
    # Drop Course
    #
    def dropCourse(self, email, courseId):
        print "Drop course with course Id", courseId, "of the person with email ID", email
        checkUserCount = self.uc.find({"email": email.strip("'")}).count()
        if checkUserCount > 0:
            try:
                checkCourseEntry = self.uc.find({"enrolled": courseId}).count()
                if checkCourseEntry > 0:
                    self.uc.update({"email": email.strip("'")}, {"$pull": {"enrolled": courseId.strip("'")}})
                    print "Course Dropped Successfully"
                    userDetails = self.uc.find_one({"email": email.strip("'")})
                    del userDetails['_id']
                    print userDetails
                    return userDetails
                else:
                    print "User is not enrolled in this course -- Cannot Delete the course"
                    return {"dropCourse": "You are not enrolled in this course"}
            except:
                print "Error: Failed to Drop the course.. Try Again", sys.exc_info()
                return {"dropCourse": "Drop Course Failed"}
        else:
            print "user not present in the database"
            return {"status": 0}


    #
    # Add Course
    #

    def addCourse(self, jsonObj):
        print "Add course------- mongo.py"
        teamName = "Rangers:"
        try:
            objectId = uuid.uuid4()
            print objectId
            courseId = teamName + str(objectId)
            print courseId
            additionInfo = {"id": courseId}
            jsonObjFinal = dict(jsonObj.items() + additionInfo.items())
            self.cc.insert(jsonObjFinal)
            print "Course added successfully"
            #self.cc.update({"_id": jsonObj['_id']}, {"$set": {"id": courseId.strip("'")}})
            responseAddCourse = self.cc.find_one({"id": courseId.strip("'")})
            if len(responseAddCourse) > 0:
                del responseAddCourse['_id']
                return responseAddCourse
            else:
                print "error---- Invalid Id"
                return {"addCourse": "Invalid Course Id"}
        except:
            print "error in adding course: ", sys.exc_value
            return {"addCourse": "Add Course Failed"}


    #
    # List all courses
    #
    def listCourse(self):
        print "List all courses ---- Mongo.py"
        try:
            courseList = self.cc.find()
            courseListData = []
            for data in courseList:
                del data['_id']
                courseListData.append(data)
            #print "course list Array format", courseListData
            courseListFinal = json.dumps(courseListData)
            print "Final course list JSON format", courseListFinal
            return courseListFinal
        except:
            print "error to get list details", sys.exc_info()[0]
            return {"listCourses": "list retrieval failed"}


    #
    #Get Course
    #
    def getCourse(self, courseId):
        print "Get Course with course ID = " + courseId
        checkCourseEntry = self.cc.find({"id": courseId.strip("'")}).count()
        print "Course entry ", checkCourseEntry
        if checkCourseEntry > 0:
            print "Sending the Course Details"
            courseDetails = self.cc.find_one({"id": courseId})
            if len(courseDetails) > 0:
                print "send course details"
                del courseDetails['_id']
                return courseDetails
            else:
                return {"courseId": "Course not found"}
        else:
            print "Error in Getting course details ---> mongo.py"
            return {"courseId": "ID is invalid"}

    #
    # Update Course
    #
    #def updateCourse(self, ):

    #
    # Delete Course
    #
    def deleteCourse(self, id):
        print "Delete Course with ID = ", id
        responseHandler = 0
        try:
            deleteCount = self.cc.find({"id": id}).count()
            if deleteCount > 0:
                self.cc.remove({"id": id})
                print "Delete successful"
                return {"deleteCourse":"success"}
            else:
                print "error: Invalid ID - MONGO.py"
                responseHandler = 400
                return {"deleteCourse": responseHandler}

        except:
            print "error: course not found - MONGO.py", sys.exc_traceback

            return {"deleteCourse":"failed"}


    #_____________________________QUIZZES__________________________________________


    #
    # Add Quiz
    #
    def addQuiz(self, jsonObj):
        try:
            print "Add quiz ---> mongo.py"
            teamName = "RangersQuiz:"
            objectId = uuid.uuid4()
            print objectId
            quizId = teamName + str(objectId)
            print quizId
            additionInfo = {"id": quizId}
            jsonObjFinal = dict(jsonObj.items() + additionInfo.items())
            self.qc.insert(jsonObjFinal)
            print "Quiz added successfully"
            responseAddQuiz = self.qc.find_one({"id": quizId.strip("'")})
            if len(responseAddQuiz) > 0:
                del responseAddQuiz['_id']
                return responseAddQuiz
            else:
                print "error: Invalid ID"
                return {"quizId": "ID is invalid"}
        except:
            print "error in adding quiz: ", sys.exc_traceback
            return {"addQuiz": "quiz addition Failed"}


    #
    #Get Quiz
    #
    def getQuiz(self, quizId):
        print "Get quiz with quiz ID = " + quizId
        checkQuizEntry = self.qc.find({"id": quizId.strip("'")}).count()
        print "Quiz entry ", checkQuizEntry
        if checkQuizEntry > 0:
            print "Sending the Quiz Details"
            quizDetails = self.qc.find_one({"id": quizId})
            if len(quizDetails) > 0:
                print "send quiz details"
                del quizDetails['_id']
                return quizDetails
            else:
                return {"quizId": "Quiz not found"}
        else:
            print "Error in Getting quiz details ---> mongo.py"
            return {"quizId": "ID is invalid"}


    #
    # List all quizes
    #
    def listQuiz(self):
        print "List all quizzes ---- Mongo.py"
        try:
            quizList = self.qc.find()
            quizListData = []
            for data in quizList:
                del data['_id']
                quizListData.append(data)
            #print "course list Array format", courseListData
            quizListFinal = json.dumps(quizListData)
            print "Final quiz list JSON format", quizListFinal
            return quizListFinal
        except:
            print "error to get quiz list details", sys.exc_info()[0]
            return {"listQuizzes": "list retrieval failed"}

    #
    # Delete Quiz
    #
    def deleteQuiz(self, id):
        print "Delete Quiz with ID = ", id
        try:
            deleteCount = self.qc.find({"id": id}).count()
            if deleteCount > 0:
                self.qc.remove({"id": id})
                print "Delete successful"
                return {"deleteQuiz":"success"}
            else:
                print "error: Invalid ID - MONGO.py"
                responseHandler = 400
                return {"deleteQuiz": responseHandler}

        except:
            print "error: quiz not found - MONGO.py", sys.exc_traceback

            return {"deleteQuiz":"failed"}

    #_____________________________ANNOUNCEMENTS__________________________________________


    #
    # Add Announcement
    #
    def addAnnouncement(self, jsonObj):
        print "Add announcement ---> mongo.py"
        teamName = "RangersAnnouncement:"
        objectId = uuid.uuid4()
        localtime = time.asctime(time.localtime(time.time()))
        print objectId, localtime
        announcementId = teamName + str(objectId)
        print announcementId
        try:
            additionalInfo = {"id": announcementId.strip("'"), "postDate": localtime, "status": 1}
            finalJsonObj = dict(jsonObj.items() + additionalInfo.items())
            self.ac.insert(finalJsonObj)
            print "Announcement added successfully"
            responseAnnouncement = self.ac.find_one({"id": announcementId.strip("'")})
            if len(responseAnnouncement) > 0:
                del responseAnnouncement['_id']
                return responseAnnouncement
            else:
                print "error: Invalid ID"
                return {"responseAnnouncementId": "ID is invalid"}
        except:
            print "error in adding announcement: ", sys.exc_value
            return {"addAnnouncement": "announcement addition Failed"}


    #
    #Get Announcement
    #
    def getAnnouncement(self, announcementId):
        print "Get announcement with announcement ID = " + announcementId
        checkAnnouncementEntry = self.ac.find({"id": announcementId.strip("'")}).count()
        print "Announcement entry ", checkAnnouncementEntry
        if checkAnnouncementEntry > 0:
            print "Sending the Announcement Details"
            announcementDetails = self.ac.find_one({"id": announcementId})
            if len(announcementDetails) > 0:
                print "send announcement details"
                del announcementDetails['_id']
                return announcementDetails
            else:
                return {"announcementId": "Announcement not found"}
        else:
            print "Error in Getting announcement details ---> mongo.py"
            return {"announcementId": "ID is invalid"}


    #
    # List all announcements
    #
    def listAnnouncement(self):
        print "List all announcements ---- Mongo.py"
        try:
            announcementList = self.ac.find()
            announcementListData = []
            for data in announcementList:
                del data['_id']
                announcementListData.append(data)
            #print "course list Array format", courseListData
            announcementListFinal = json.dumps(announcementListData)
            print "Final announcement list JSON format", announcementListFinal
            return announcementListFinal
        except:
            print "error to get announcement list details", sys.exc_info()[0]
            return {"listAnnouncements": "list retrieval failed"}

    #
    # Delete Announcement
    #
    def deleteAnnouncement(self, id):
        print "Delete Announcement with ID = ", id
        responseHandler = 0
        try:
            deleteCount = self.ac.find({"id": id}).count()
            if deleteCount > 0:
                self.ac.remove({"id": id})
                print "Delete successful"
                return {"deleteAnnouncement":"success"}
            else:
                print "error: Invalid ID - MONGO.py"
                responseHandler = 400
                return {"deleteAnnouncement": responseHandler}

        except:
            print "error: announcement not found - MONGO.py", sys.exc_traceback

            return {"deleteAnnouncement":"failed"}

    #_____________________________DISCUSSIONS__________________________________________


    #
    # Add Discussion
    #
    def addDiscussion(self, jsonObj):
        print "Add discussion ---> mongo.py"
        teamName = "RangersDiscussion:"
        discussionEntriesCount = self.dc.count() + 1
        print "discussionEntriesCount + 1 = ", discussionEntriesCount
        discussionId = teamName + str(discussionEntriesCount)
        discussionIdDict = {"id": discussionId}
        try:
            print "I am in try of insert"
            jsonEntry = dict(discussionIdDict.items() + jsonObj.items())
            print "Json Entry is = ", jsonEntry
            self.dc.insert(jsonEntry)
            print "discussion added successfully"
            del jsonEntry["_id"]
            return jsonEntry
        except:
            print "error in adding discussion: ", sys.exc_info()[0]
            return {"addDiscussion": "discussion addition Failed"}


    #
    #Get Discussion
    #
    def getDiscussion(self, discussionId):
        print "Get discussion with discussion ID = " + discussionId
        checkDiscussionEntry = self.dc.find({"id": discussionId.strip("'")}).count()
        print "Discussion entry ", checkDiscussionEntry
        if checkDiscussionEntry > 0:
            print "Sending the Discussion Details"
            discussionDetails = self.dc.find_one({"id": discussionId})
            if len(discussionDetails) > 0:
                print "send discussion details"
                del discussionDetails['_id']
                return discussionDetails
            else:
                return {"discussionId": "Discussion not found"}
        else:
            print "Error in Getting discussion details ---> mongo.py"
            return {"discussionId": "ID is invalid"}


    #
    # List all Discussion
    #
    def listDiscussion(self):
        print "List all discussions ---- Mongo.py"
        try:
            discussionList = self.dc.find()
            discussionListData = []
            for data in discussionList:
                del data['_id']
                discussionListData.append(data)
            #print "course list Array format", courseListData
            discussionListFinal = json.dumps(discussionListData)
            print "Final discussion list JSON format", discussionListFinal
            return discussionListFinal
        except:
            print "error to get discussion list details", sys.exc_info()[0]
            return {"listDiscussions": "list retrieval failed"}

    #
    # Delete Discussion
    #
    def deleteDiscussion(self, id):
        print "Delete Discussion with ID = ", id
        responseHandler = 0
        try:
            deleteCount = self.dc.find({"id": id}).count()
            if deleteCount > 0:
                self.dc.remove({"id": id})
                print "Delete successful"
                return {"deleteDiscussion":"success"}
            else:
                print "error: Invalid ID - MONGO.py"
                responseHandler = 400
                return {"deleteDiscussion": responseHandler}
        except:
            print "error: discussion not found - MONGO.py", sys.exc_traceback

            return {"deleteDiscussion":"failed"}