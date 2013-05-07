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
from bottle import abort

#localtime = time.asctime( time.localtime(time.time()))
#print "Local current time :", localtime
# Needs a Date Type like this  2013-04-18T08:56:20.583Z" // ISO format

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
        #self.userid = self.uc.count() + 1
        #self.rc = db.runCommand

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
    # Create User details in backend
    # {"email": "test@google.com","own": [],"enrolled": [],"quizzes": []}
    # Sqlite in Django at front end has Username, firstname, lastname, password
    #
    def createUser(self, jsonObj):
        print "----> create User: ", jsonObj['email']
        count = self.uc.find({"email": jsonObj['email'].strip("'")}).count()
        if count > 0:
            print "user already exist with email ID: ", jsonObj['email']
            #return {"found":"true"}
            abort(409, 'Duplicate Email ID')
        else:
            print "create user with Email ID: ", jsonObj['email']
            try:
                self.uc.insert(jsonObj)
                print "new user added"
                objectId = jsonObj['_id']
                objectIdStr = str(objectId)
                #print objectIdStr
                del jsonObj["_id"]
                id = {"_id": objectIdStr}
                finalJson = dict(jsonObj.items() + id.items())
                #jsonObj['_id'] = objectIdStr
                print finalJson
                return finalJson
            except:
                print "Failed to add user"
                abort(500, 'Other Errors')



    #
    # Get Details of the user
    #
    def getUser(self, email):
        print "Get Details of user with email id ", email
        try:
            userDetails = self.uc.find_one({"email": email.strip("'")})

            if len(userDetails) == 0:
                print "user not found in the database"
                abort(404, "User not found")
                #return {"found": "false"}
            else:
                print "Returning Json user details = ", userDetails
                del userDetails['_id']
                return userDetails
        except:
            print "error to get user details", sys.exc_info()[0]
            abort (400, "Email is Invalid")
            #return {"found": "false"}



    #
    # Delete User
    #
    def deleteUser(self, email):
        print "Deleting the user mongo.py", email
        #try:
        count = self.uc.find({"email": email.strip("'")}).count()
        if count > 0:
            try:
                print "Deleting User finally"
                self.uc.remove({"email": email})
                return {"success": True}
            except:
                print "Failed in deleting user", sys.exc_info()
                abort(400, "Email is invalid")
                #return {"userDeleted": "false"}
        else:
            print "user not found with email id", email
            abort(404, "User not found")
                #return {"found": "false"}
        #except:
         #   print "error: Invalid Email id", sys.exc_info()
         #   return {"found": "false"}



    #
    # Update User .................... This will be used to Enroll Course Id, Update Own Course Id or Quiz Details
    # It also handles requests to drop enrolled and added course and also delete quiz entries
    # need to test if the user is already enrolled or added the class.
    #
    # return JSON with success true or success false when user is already enrolled in the course
    # jsonObj has email and courseId

    def updateUser_CourseEntry(self, jsonObj, EntryType):
        print "Updating the user details -> mongo.py", jsonObj['email']
        #try:
        #
        # We need only the single values in own , enroll , quizzes (quizzes will have dictionary of quizId & grade)
        #

        # __________________________________ OWN COURSE ID _________________________________________________

        if EntryType == "own" and jsonObj.has_key('courseId') and len(jsonObj['courseId']) != 0:
            print "I am in Own"
            self.uc.update({"email": jsonObj['email'].strip("'")}, {"$addToSet": {"own": jsonObj['courseId'].strip("'")}})

        # __________________________________ Enrolled COURSE ID _____________________________________________

        elif EntryType == "enrolled" and jsonObj.has_key('courseId') and len(jsonObj['courseId']) != 0:
            print "I am in enrolled"
            self.uc.update({"email": jsonObj['email'].strip("'")}, {"$addToSet": {"enrolled": jsonObj['courseId'].strip("'")}})

        # __________________________________ Quiz Details ____________________________________________________

        elif EntryType == "quizzes" and jsonObj.has_key('quizzes') and len(jsonObj['quizzes']) != 0:
            print "I am in quizzes"

            localtime = time.asctime( time.localtime(time.time()))
            print "Local current time :", localtime
            quizId = jsonObj['quizzes']['quiz']
            print "quiz ID = ", quizId
            grade = jsonObj['quizzes']['grade']
            self.uc.update({"email": jsonObj['email'].strip("'")}, {"$addToSet": {"quizzes": {"quiz": quizId, "grade": grade, "submitDate": localtime}}})

        #
        # ___________________________________ Drop Enrolled Course______________________________________________
        #
        elif EntryType == "dropEnrolledCourse" and jsonObj.has_key('courseId') and len(jsonObj['courseId']) != 0:
            print "I am going to Drop the enrolled course"
            self.uc.update({"email": jsonObj['email'].strip("'")}, {"$pull": {"enrolled": jsonObj['courseId'].strip("'")}})

        else:
            print "Failed to update the User Entry details"
            print " Own Course Id / Enroll Course Id / Quiz Details / Dropping / Deleting the course failed"
            abort(400, "Email or Json is invalid")
        # __________________________________Sending Response to the function back ____________________________

        # Do we need to send success or whole Json to the user or both // Currently, we are sending both
        updatedUserDetails = self.uc.find_one({"email": jsonObj['email'].strip("'")})
        print "Details Updated:", updatedUserDetails
        if updatedUserDetails > 0:
            print "updated the entries of User", jsonObj['email']
            objectId = updatedUserDetails['_id']
            objectIdStr = str(objectId)
            print objectIdStr
            del updatedUserDetails["_id"]
            id = {"_id": objectIdStr, "success": True}
            finalUserUpdates = dict(updatedUserDetails.items() + id.items())
            return finalUserUpdates
        else:
            print "Failed to fetch user details"
            abort(500, "Other Errors - Update User Entry function")

    #
    # Enroll Courses
    #
    def enrollCourse(self, jsonData):
        # We need to append the team name with object ID in Django

        print "Enroll Course of person with email ID", jsonData['email'], "with Course ID", jsonData['courseId']

        # Check whether the user is already enrolled in the course or not
        checkDuplicate_CourseEntry = self.uc.find({"email": jsonData['email'].strip("'"), "enrolled": jsonData['courseId'].strip("'")}).count()
        if checkDuplicate_CourseEntry == 0:
                #
                # Calling updateUser_CourseEntry function
                #
            jsonResp = Storage.updateUser_CourseEntry(self, jsonData, "enrolled")
            print "Course has been enrolled successfully"
            return jsonResp
                #userDetails = self.uc.find_one({"email": jsonData['email'].strip("'")})
                #del userDetails['_id']
                #print userDetails
                #return userDetails
        else:
            print "User is already enrolled in the class"
            return {"success": False}

# self.uc.update({"email": jsonData['email'].strip("'")}, {"$addToSet": {"enrolled": jsonData['courseId'].strip("'")}})


    #
    # Drop Course
    #
    def dropCourse(self, jsonData):
        print "Drop course with course Id", jsonData['courseId'], "of the person with email ID", jsonData['email']
        #checkUserCount = self.uc.find({"email": email.strip("'")}).count()
        #if checkUserCount > 0:

        checkCourseEntry = self.uc.find({"enrolled": jsonData['courseId']}).count()
        if checkCourseEntry > 0:
            #
            # Calling updateUser_CourseEntry function
            #
            jsonResp = Storage.updateUser_CourseEntry(self, jsonData, "enrolled")
            print "Course Dropped Successfully"
            return jsonResp
            #userDetails = self.uc.find_one({"email": email.strip("'")})
            #del userDetails['_id']
            #return userDetails
        else:
            print "User is not enrolled in this course -- Cannot Drop the course"
            return {"success": False}

# self.uc.update({"email": email.strip("'")}, {"$pull": {"enrolled": courseId.strip("'")}})


    # ______________________________________CATEGORY COLLECTIONS________________________________________

    #
    # Add Category
    #

    def addCategory(self, jsonObj):
        print "Add Category------- mongo.py"
        name = jsonObj['name']
        teamName = "RangersCategory:"
        objectId = uuid.uuid4()
        localtime = time.asctime(time.localtime(time.time()))
        print objectId, localtime
        categoryId = teamName + str(objectId)
        print categoryId
        duplicateCount = self.catc.find({"name": name.strip("'")}).count()
        print "category present count = ", duplicateCount
        if duplicateCount == 0:
            try:
                additionalInfo = {"id": categoryId.strip("'"), "createDate": localtime, "status": 1}
                finalJsonObj = dict(jsonObj.items() + additionalInfo.items())
                self.catc.insert(finalJsonObj)
                print "category added successfully"
                responseCategory = self.catc.find_one({"id": categoryId.strip("'")})
                if len(responseCategory) > 0:
                    del responseCategory['_id']
                    return responseCategory
                else:
                    print "error: Invalid ID"
                    return {"responseCategoryId": "ID is invalid"}
            except:
                responseCategory = "Other Errors"
                print "error in adding Category: ", sys.exc_value
                return {responseCategory: 500}
        else:
            print "Error: Duplicate Category found"
            responseCategory = "Name is Duplicated"
            return {responseCategory: 409}


    #
    # Get Category
    #


    def getCategory(self,categoryId):
        print "Get Category with category ID ",categoryId
        checkCategoryEntry = self.catc.find({"id": categoryId.strip("'")}).count()
        print "Category entry ", checkCategoryEntry
        if checkCategoryEntry > 0:
            print "Sending the Category Details"
            categoryDetails = self.catc.find_one({"id": categoryId})
            if len(categoryDetails) > 0:
                print "send category details"
                del categoryDetails['_id']
                return categoryDetails
            else:
                return {"404": "Category not found"}
        else:
            print "Error in Getting category details ---> classroom.py"
            return {"400": "ID is invalid"}

    #
    # List Category
    #

    def listCategory(self):
         print "List all category ---- Mongo.py"
         try:
             categoryList = self.catc.find()
             categoryListData = []
             for data in categoryList:
                 del data['_id']
                 categoryListData.append(data)
             categoryListFinal = json.dumps(categoryListData)
             return categoryListFinal
         except:
             responseListCategory = "Other Errors"
             print "error to get list details", sys.exc_info()[0]
             return {responseListCategory: 500}



    #_______________________________________ COURSE COLLECTION __________________________________________

    #
    # Update Course
    #
    def updateCourse(self, jsonData, email):
        print "Update Course with email ", email



    #
    # Add Course - need to check at Django whether the user belongs to different Mooc or Default Mooc
    # If user is of same mooc append the email id to the Json else send {"email" : "NotMyMooc"}
    # We need a Team/MOOC Name from sqlite to append it to the courseId
    # need to append the
    # TEST WITH TWO THINGS WITH JSON "email": "NotMyMooc" & "email": Valid EmailId of Same Mooc

    def addCourse(self, jsonObj):
        print "Add course------- mongo.py", jsonObj
        userEntryType = jsonObj['email']
        print userEntryType

        # user is from other MOOC
        if userEntryType == "NotMyMooc":
            print "user is from different mooc", userEntryType
            del jsonObj['email']
            self.cc.insert(jsonObj)
            objectId = jsonObj['_id']
            objectIdStr = str(objectId)
            print objectIdStr
            del jsonObj["_id"]
            responseJson = {"_id": objectIdStr, "success": True}
            return responseJson

        # True if user is in the list
        elif self.uc.find({ "email": {"$in": [userEntryType]}}):
            print "User is of the same mooc", userEntryType
            del jsonObj['email']
            self.cc.insert(jsonObj)
            objectId = jsonObj['_id']
            objectIdStr = str(objectId)
            print objectIdStr
            jsonEntry = {"email": userEntryType, "courseId": objectIdStr}
            jsonResp = Storage.updateUser_CourseEntry(self, jsonEntry, "own")
            return {"_id": jsonResp['_id'], "success": True}
        else:
            print "Error: In adding the course"
            abort(500, "Other Errors")

    #objectId = uuid.uuid4()
    #courseId = teamName + str(objectId)
    #additionInfo = {"id": courseId}

    #
    # List all courses
    #
    def listCourse(self):
        print "List all courses ---- Mongo.py"
        Team = "Rangers:"
        try:
            countCourses = self.cc.count()
            if countCourses > 0:
                courseList = self.cc.find()
                courseListData = []
                for data in courseList:
                    objectId = data['_id']
                    objectIdStr = str(objectId)
                    courseId = Team + objectIdStr
                    id = {'_id': courseId}
                    del data['_id']
                    data.update(id)
                    print data
                    courseListData.append(data)
                courseListFinal = json.dumps(courseListData)
                #print "Final course list JSON format", courseListFinal
                return courseListFinal
            else:
                print "No courses are present on the MOOC"
                return {"success": False}
        except:
            #listCourses = "Other Errors"
            print "error to get list details", sys.exc_info()[0]
            abort(500, "Other Errors")
            #return {listCourses: 500}


    #
    # Get Course
    #

    def getCourse(self, courseId):
        print "Get Course with course ID = ", courseId
        obj_id = object(courseId)
        checkCourseEntry = self.cc.find({"_id": obj_id.strip("'")}).count()
        print "Course entry ", checkCourseEntry
        if checkCourseEntry > 0:
            print "Sending the Course Details"
            courseDetails = self.cc.find_one({"id": courseId})
            if len(courseDetails) > 0:
                print "send course details"
                del courseDetails['_id']
                return courseDetails
            else:
                abort(400, "Id is invalid")
                #return {"courseId": "Course not found"}
        else:
            print "Error in Getting course details Id Is Invalid---> mongo.py"
            abort(404, "Course not found")
            #return {"courseId": "ID is invalid"}


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