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

    #def insert(self,entity):
    #    print "---> insert:"
    #    try:
    #        self.uc.insert(entity)
    #        return "added"
    #    except:
    #        return "error: data not added"

    #def remove(self,name):
    #    self.uc.remove({ "email" : "test@gmail.com"})
    #    print "---> remove:",name

    #def names(self):
    #    print "---> names:"
    #    for user in self.uc.find():
    #        print user

    #def find(self,name):
    #    print "---> storage.find:",name
    #    count = self.uc.find({"email":"test@gmail.com"}).count()
    #    if count > 0:
    #        return {"found" :"true"}
    #    else :
    #        return {"found" :"false"}

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
    # Update User
    #
    #def updateUser(self, jsonObj, email):
    #    print "update user functions ---- mongo.py"
    #    EntryType = "enrolled"
    #    if self.uc.find({"enrolled": jsonObj['courseId'].strip("'")}):
    #        # EntryType = "enrolled"
    #        print "enroll the user and go into updateUser_CourseEntry function"
    #        jsonResp = Storage.updateUser_CourseEntry(self, jsonObj, EntryType)
    #        return jsonResp
    #   elif EntryType == "dropEnrolledCourse":
    #       print "Drop the course"
    #       jsonResp = Storage.updateUser_CourseEntry(self, jsonObj, EntryType)
    #       return jsonResp



    #
    # Update User .................... This will be used to Enroll Course Id, Own Course Id or Quiz Details
    # It also handles requests to drop enrolled and added course
    #
    #
    # return JSON with success true or success false when user is already enrolled in the course
    # jsonObj has email and courseId
    # argument EntryType is passed from the function which calls this functions for services.

    def updateUser_CourseEntry(self, jsonObj, EntryType):
        print "Updating the user details -> mongo.py", jsonObj['email']
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


        updatedUserDetails = self.uc.find_one({"email": jsonObj['email'].strip("'")})
        #print "Details Updated:", updatedUserDetails
        if updatedUserDetails > 0:
            print "updated the entries of User", jsonObj['email']
            objectId = updatedUserDetails['_id']
            objectIdStr = str(objectId)
            print objectIdStr
            del updatedUserDetails["_id"]
            id = {"id": objectIdStr, "success": True}
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

        # splitting the course Id into Team Name and course id string format
        splitCourseId = jsonData['courseId'].split(":")
        Team = splitCourseId[0]
        courseStrId = splitCourseId[1]

        appendedCourseId = jsonData['courseId']
        print appendedCourseId

        try:
            from bson.objectid import ObjectId
            objectId = ObjectId(courseStrId)
        except:
            print "Error: Id is invalid", sys.exc_traceback
            respCode = 400
            abort(400, respCode)

        if self.cc.find({"_id": objectId}):
            if self.uc.find({"email": jsonData['email']}):
                print " You are same mooc user "
            # Check whether the user is already enrolled in the course or not
                checkDuplicate_CourseEntry = self.uc.find({"email": jsonData['email'].strip("'"), "enrolled": appendedCourseId}).count()
                if checkDuplicate_CourseEntry == 0:
                    #
                    # Calling updateUser_CourseEntry function
                    #
                    #
                    finalCourseId = {"courseId": appendedCourseId.strip("'")}
                    del jsonData['courseId']
                    jsonPacket = dict(jsonData.items() + finalCourseId.items())
                    jsonResp = Storage.updateUser_CourseEntry(self, jsonPacket, "enrolled")
                    print "Course has been enrolled successfully"
                    return jsonResp
                else:
                    print "User is already enrolled in the class"
                    respCode = 500
                    abort(500, respCode)
                #return {"success": False}
            else:
                print "You are different mooc user"
                return {"id": appendedCourseId, "success": True}
        else:
            print "Error: Course not found", sys.exc_traceback
            respCode = 404
            abort(404, respCode)



    #
    # Drop Course
    #

    def dropCourse(self, jsonData):
            print "Drop course with course Id", jsonData['courseId'], "of the person with email ID", jsonData['email']

            # splitting the course Id into Team Name and course id string format
            splitCourseId = jsonData['courseId'].split(":")
            Team = splitCourseId[0]
            courseStrId = splitCourseId[1]

            try:
                from bson.objectid import ObjectId
                objectId = ObjectId(courseStrId)
            except:
                print "Error: Id is invalid", sys.exc_traceback
                respCode = 400
                abort(400, respCode)

            checkUserCount = self.uc.find({"email": jsonData['email'].strip("'")}).count()
            if checkUserCount > 0:
                print "You are same Mooc user"
                isFoundUser = self.uc.find({"email": jsonData['email'].strip("'"), "enrolled": jsonData['courseId']}).count()
                if isFoundUser > 0:
                    jsonResp = Storage.updateUser_CourseEntry(self, jsonData, "dropEnrolledCourse")
                    print "Course Dropped Successfully"
                    return jsonResp
                else:
                    print "User is not enrolled in the course - cannot drop the course"
                    respCode = 500
                    abort(500, respCode)
            else:
                print "You are different mooc user"
                from bson.objectid import ObjectId
                objectid = ObjectId(jsonData['courseId'])

                checkCourseEntry = self.cc.find({"enrolled": objectid}).count()
                if checkCourseEntry > 0:
                    print "Course Dropped Successfully"
                    return {"id": jsonData['courseId'], "success": True}
                else:
                    print "User is not enrolled in this course -- Cannot Drop the course"
                    respCode = 500
                    abort(500, respCode)


    # ______________________________________CATEGORY COLLECTIONS________________________________________

    #
    # Add Category
    #

    def addCategory(self, jsonObj):
        print "Add Category------- mongo.py"
        name = jsonObj['name']
        Team = "RangersCategory:"
        localtime = time.asctime(time.localtime(time.time()))
        #print localtime
        duplicateCount = self.catc.find({"name": name.strip("'")}).count()
        if duplicateCount == 0:
            try:
                self.catc.insert(jsonObj)
                objectId = jsonObj['_id']
                obj_id = str(objectId)
                del jsonObj['_id']
                additionalInfo = {"createDate": localtime, "status": 1}
                categoryId = {"categoryId": obj_id.strip("'")}
                self.catc.update({"name": jsonObj['name'].strip("'")}, {"$addToSet": additionalInfo})
                finalJsonObj = dict(jsonObj.items() + additionalInfo.items() + categoryId.items())
                #self.catc.insert(finalJsonObj)
                print "category added successfully"
                #del finalJsonObj['_id']
                return finalJsonObj
            except:
                print "error in adding Category: ", sys.exc_value
                responseCategory = 500
                abort(500, responseCategory)
        else:
            print "Error: Duplicate Category found"
            responseCategory = 409
            abort(409, responseCategory)


    #
    # Get Category
    #

    def getCategory(self, categoryId):
        print "Get Category in mongo.py with category ID = ", categoryId

        # splitting the category Id into Team Name and course id string format

        splitCategoryId = categoryId.split(":")
        Team = splitCategoryId[0]
        categoryStrId = splitCategoryId[1]

        try:
            # Converting the String Type Category Id into Object Type Category Id
            from bson.objectid import ObjectId
            objectId = ObjectId(categoryStrId)
        except:
            print "Error: The ID is invalid", sys.exc_traceback
            responseCode = 400
            abort(400, responseCode)
        checkCategoryEntry = self.catc.find({"_id": objectId}).count()
        #print "Category entry ", checkCategoryEntry
        if checkCategoryEntry > 0:
            print "Sending the Category Details"
            categoryDetails = self.catc.find_one({"_id": objectId})
            if len(categoryDetails) > 0:
                print "send category details"
                del categoryDetails['_id']
                return categoryDetails
            else:
                print "Error: Category not found", sys.exc_traceback
                responseCode = 500
                abort(500, responseCode)
        else:
            print "Error: Category not found", sys.exc_traceback
            responseCode = 404
            abort(404, responseCode)

    #
    # List Category
    #

    def listCategory(self):
        print "List all category ---- Mongo.py"
        Team = "RangersCategory:"
        try:
            countCategory = self.catc.count()
            if countCategory > 0:
                categoryList = self.catc.find()
                categoryListData = []
                for data in categoryList:
                    objectId = data['_id']
                    objectIdStr = str(objectId)
                    categoryId = Team + objectIdStr
                    catId = {'categoryId': categoryId}
                    del data['_id']
                    data.update(catId)
                    #print data
                    categoryListData.append(data)
                courseListFinal = json.dumps(categoryListData)
                print "Final Category List ", courseListFinal
                return courseListFinal
            else:
                print "No courses are present on the MOOC"
                return {"success": False}
        except:
            print "error to get category list details", sys.exc_info()[0]
            respCode = 500
            abort(500, respCode)



    #_______________________________________ COURSE COLLECTION __________________________________________

    #
    # Update Course
    #
    def updateCourse(self, jsonData, courseId):
        print "Update Course with courseId"

        # splitting the course Id into Team Name and course id string format

        splitCourseId = courseId.split(":")
        Team = splitCourseId[0]
        courseStrId = splitCourseId[1]
        print "String Course Id = ", courseStrId + "Team Name", Team
        from bson.objectid import ObjectId
        try:
            obj_id = ObjectId(courseStrId)
        except:
            print "Error: Not a valid Object ID", sys.exc_traceback()
            respCode = 500
            abort(500, respCode)

        print "Converted object Id from string to object = ", obj_id
        checkCourseEntry = self.cc.find({"_id": obj_id}).count()
        print "course entry  = ", checkCourseEntry
        if checkCourseEntry > 0:
            try:
                self.cc.update({"_id": obj_id}, {"$set": {"category": jsonData['category'], "term": jsonData['term'],"Description": jsonData['Description'], "title": jsonData['title'], "section": jsonData['section'],"days": jsonData['days'], "hours": jsonData['hours'], "dept": jsonData['dept'], "instructor": jsonData['instructor'], "attachment": jsonData['attachment'], "year": jsonData['year']}})
                #"instructor": jsonData['instructor']
                print "Course details updated successfully"
                return jsonData
            except:
                print "error: course Id or Json is invalid", sys.exc_traceback
                respCode = 400
                abort(400, respCode)
        else:
            print "error: course not found"
            respCode = 404
            abort(404, respCode)


    #
    # Add Course - need to check at Django whether the user belongs to different Mooc or Default Mooc
    #
    # We need a Team/MOOC Name from sqlite to append it to the courseId

    def addCourse(self, jsonObj):
        print "Add course------- mongo.py", jsonObj
        Team = "Rangers:"
        userEntryType = jsonObj['instructor'][0]['email']
        print userEntryType
        checkUserEntry = self.uc.find({"email": userEntryType.strip("'")}).count()
        if checkUserEntry > 0:
            print "User is of the same mooc", userEntryType
            #del jsonObj['email']
            try:
                self.cc.insert(jsonObj)
            except:
                print "Error: Internal server error", sys.exc_traceback
                respcode = 500
                abort(500, respcode)
            objectId = jsonObj['_id']
            objectIdStr = str(objectId)
            finalCourseId = Team + objectIdStr
            #print objectIdStr
            jsonEntry = {"email": userEntryType, "courseId": finalCourseId}
            #jsonResp =
            Storage.updateUser_CourseEntry(self, jsonEntry, "own")
            return {"courseId": finalCourseId, "success": True}

        # user is from other MOOC
        else:
            print "user is from different mooc", userEntryType
            #del jsonObj['email']
            try:
                self.cc.insert(jsonObj)
            except:
                print "Error: Internal server error", sys.exc_traceback
                respcode = 500
                abort(500, respcode)
            objectId = jsonObj['_id']
            objectIdStr = str(objectId)
            finalCourseId = Team + objectIdStr
            return {"courseId": finalCourseId, "success": True}


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
                    id = {'courseId': courseId}
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

        # splitting the course Id into Team Name and course id string format
        splitCourseId = courseId.split(":")
        Team = splitCourseId[0]
        courseStrId = splitCourseId[1]
        try:
            from bson.objectid import ObjectId
            obj_id = ObjectId(courseStrId)
        except:
            print "Error: Id is invalid", sys.exc_traceback
            respcode = 400
            abort(400, respcode)
        print "Object ID", obj_id
        checkCourseEntry = self.cc.find({"_id": obj_id}).count()
        print "Course entry ", checkCourseEntry
        if checkCourseEntry > 0:
            courseDetails = self.cc.find_one({"_id": obj_id})
            print courseDetails
            if len(courseDetails) > 0:
                print "send course details"
                courseIdWithTeam = Team + ":" + courseId
                id = {'courseId': courseIdWithTeam}
                del courseDetails['_id']
                finalCourseDetails = dict(courseDetails.items() + id.items())
                return finalCourseDetails
            else:
                print "ERROR: course not found", sys.exc_traceback
                respcode = 500
                abort(500, respcode)
                #return {"courseId": "Course not found"}
        else:
            print "Error in Getting course details Id Is Invalid---> mongo.py"
            respcode = 404
            abort(404, respcode)
            #return {"courseId": "ID is invalid"}

    #
    # Get owned courses of the user to run the functionalities of quizzes and announcements
    # This functionality works for same mooc user


    def getOwnedCourses(self, email):
        print "Get owned courses with email - ", email
        from bson.objectid import ObjectId
        isUserPresent = self.uc.find({"email": email.strip("'")}).count()
        if isUserPresent > 0:
            ownCourseList = self.uc.find_one({"email": email})
            ownCourseId = ownCourseList['own']
            print ownCourseId
            totalOwnIdCount = len(ownCourseId)
            count = 0
            jsonData = []
            while count < totalOwnIdCount:
                # converting the arrays of owned Id into object iD
                try:
                    numberValueOfId = ownCourseId[count]
                    print numberValueOfId
                    # splitting the obtained course ID to get Team name and object Id in string format
                    splitCourseId = numberValueOfId.split(":")
                    print splitCourseId[1]
                    obj_id = ObjectId(splitCourseId[1])
                except:
                    print "Id from own user collection is invalid", sys.exc_traceback()
                    respcode = 400
                    abort(400, respcode)
                # fetching details of courses with own course ID obtaied from usercollection own field
                courseDetails = self.cc.find_one({"_id": obj_id})
                courseIdFromCC = str(courseDetails['_id'])
                Team = splitCourseId[0]
                ownCourseIdWithTeam = Team + ":" + courseIdFromCC
                # creating the course Id Json with Team name appended
                finalId = {'courseId': ownCourseIdWithTeam}
                del courseDetails['_id']
                finalCourseDetails = dict(finalId.items() + courseDetails.items())
                jsonData.append(finalCourseDetails)
                count = count + 1
            finalJsonData = json.dumps(jsonData)
            return finalJsonData
        else:
            print "error: user not found", sys.exc_traceback
            respcode = 404
            abort(404, respcode)

    #
    # Delete Course
    #

    def deleteCourse(self, courseId):
        print "Delete Course with ID = ", courseId
        # splitting the course Id into Team Name and course id string format
        splitCourseId = courseId.split(":")
        Team = splitCourseId[0]
        courseStrId = splitCourseId[1]
        try:
            from bson.objectid import ObjectId
            obj_id = ObjectId(courseStrId)
        except:
            print "Error: Id Is Invalid", sys.exc_traceback
            responseHandler = 400
            abort(400, responseHandler)
        try:
            deleteCount = self.cc.find({"_id": obj_id}).count()
            if deleteCount > 0:
                userDetails = self.uc.find_one({"own": courseId})
                print "User details = ", userDetails
                if userDetails > 0:
                    print "User with add course ID = ", userDetails['email']
                    self.uc.update({"own": userDetails['own']}, {"$pull": {"own": courseId}})
                else:
                    print "error: User is from different Mooc"

                ### Deleting course from course collection ###

                self.cc.remove({"_id": obj_id})
                print "Delete successful"
                return {"success": True}
            else:
                print "error: user not found - mongo.py"
                responseHandler = 404
                abort(404, responseHandler)
                #return {"deleteCourse": responseHandler}
        except:
            print "error: Invalid Id - MONGO.py", sys.exc_traceback
            responseHandler = 400
            abort(400, responseHandler)


    #_____________________________QUIZZES__________________________________________


    #
    # Add Quiz
    #

    def addQuiz(self, jsonObj):

        print "Add quiz ---> mongo.py"

        # splitting the obtained course Id from the front end to split into Team Name and
        splitCourseId = jsonObj['courseId'].split(":")

        # splitCourseId is a array that contains Team name at 0th position and courseId at 1th position
        Team = splitCourseId[0]

        from bson.objectid import ObjectId
        try:
            courseObjectId = ObjectId(splitCourseId[1])
            #print courseObjectId
        except:
            print "Invalid course Id "
            print sys.exc_traceback()
            respcode = 400
            abort(400, respcode)

        print "Is the course still available online"
        ifFoundCourse = self.cc.find({"_id": courseObjectId}).count()
        if ifFoundCourse > 0:
            findCourseInQuiz = self.qc.find_one({"courseId": jsonObj['courseId'].strip("'")})
            print "Quiz details - When quizzes are already present of a course", findCourseInQuiz
            if findCourseInQuiz != None:

                try:
                    print "Course entry with quiz details already present"
                    self.qc.update({"courseId": jsonObj['courseId'].strip("'")}, {"$addToSet": {"questions": jsonObj['questions'][0]}})
                    self.qc.update({"courseId": jsonObj['courseId'].strip("'")}, {"$addToSet": {"questions": jsonObj['questions'][1]}})
                    print "details updated in already present courseId and quiz"
                    quizDetails = self.qc.find_one({"courseId": jsonObj['courseId'].strip("'")})
                    objectId = quizDetails['_id']
                    objectIdStr = str(objectId)
                    Obj_id = Team + "quiz" + ":" + objectIdStr
                    del quizDetails["_id"]
                    additionInfo = {"quizId": Obj_id, "success": True}
                    finalResponseQuiz = dict(additionInfo.items() + quizDetails.items())
                    return finalResponseQuiz

                except:
                    print "Error: In adding quiz details", sys.exc_traceback
                    respcode = 500
                    abort(500, respcode)

            else:

                try:

                    print "This course never had a quiz added - Adding it for first time"
                    self.qc.insert(jsonObj)
                    objectId = jsonObj['_id']
                    objectIdStr = str(objectId)
                    Obj_id = Team + "quiz" + ":" + objectIdStr
                    del jsonObj["_id"]
                    additionInfo = {"quizId": Obj_id, "success": True}
                    finalResponseQuiz = dict(additionInfo.items() + jsonObj.items())
                    return finalResponseQuiz

                except:

                    print "Error: In adding quiz details", sys.exc_traceback
                    respcode = 500
                    abort(500, respcode)

        else:

            print "error: Course not found"
            respcode = 404
            abort(404, respcode)

    #
    #Get Quiz
    #

    def getQuiz(self, quizId):
        print "Get quiz with quiz ID = " + quizId

        # splitting the course Id into Team Name and course id string format

        splitQuizId = quizId.split(":")
        Team = splitQuizId[0]
        quizStrId = splitQuizId[1]

        from bson.objectid import ObjectId
        try:
            objectId = ObjectId(quizStrId)
        except:
            print "Error: ID is Invalid", sys.exc_traceback
            respcode = 400
            abort(400,respcode)
        checkQuizEntry = self.qc.find({"_id": objectId}).count()
        print "Quiz entry", checkQuizEntry
        if checkQuizEntry > 0:
            #print "Sending the Quiz Details"
            quizDetails = self.qc.find_one({"_id": objectId})
            if len(quizDetails) > 0:
                print "send quiz details"
                del quizDetails['_id']
                return quizDetails
            else:
                print "Error: 500 Internal Server --> mongo.py"
                respcode = 500
                abort(500, respcode)
        else:
            print "Error: Quiz Not Found"
            respcode = 404
            abort(404, respcode)


    #
    # List all quizes
    #

    def listQuiz(self):
        print "List all quizzes ---- Mongo.py"
        Team = "RangersQuizzes:"
        try:
            countQuizzes = self.qc.count()
            if countQuizzes > 0:
                quizList = self.qc.find()
                quizListData = []
                for data in quizList:
                    objectId = data['_id']
                    objectIdStr = str(objectId)
                    quizId = Team + objectIdStr
                    id = {'quizId': quizId}
                    del data['_id']
                    data.update(id)
                    print data
                    quizListData.append(data)
                quizListFinal = json.dumps(quizListData)
                return quizListFinal
            else:
                print "No courses are present on the MOOC"
                return {"success": False}
        except:
            #listCourses = "Other Errors"
            print "error to get list details", sys.exc_info()[0]
            abort(500, "Other Errors")
            #return {listCourses: 500}

    #
    # Delete Quiz
    #
    def deleteQuiz(self, quizId):

        print "Delete Quiz with ID = ", quizId

        # splitting the course Id into Team Name and course id string format

        splitQuizId = quizId.split(":")
        Team = splitQuizId[0]
        quizStrId = splitQuizId[1]
        from bson.objectid import ObjectId
        try:
            quizObjectId = ObjectId(quizStrId)
        except:
            print "Error: Quiz ID is Invalid", sys.exc_traceback
            respcode = 400
            abort(400, respcode)

        try:
            deleteCount = self.qc.find({"_id": quizObjectId}).count()
            if deleteCount > 0:
                self.qc.remove({"_id": quizObjectId})
                print "Delete successful"
                return {"success": True}
            else:
                print "error: quiz with quiz ID not found - MONGO.py"
                respcode = 404
                abort(404, respcode)

        except:
            print "error: Internal Server Error - MONGO.py", sys.exc_traceback
            respcode = 500
            abort(500, respcode)



    #_____________________________ANNOUNCEMENTS__________________________________________


    #
    # Add Announcement
    #
    #{
    # "courseId": "courseId",
    # "title": "Title",               JSON DATA - title, courseId, description ..
    # "description": "desc",
    # "postDate": "DATE",
    # "status": 0
    #}
    def addAnnouncement(self, jsonObj):

        print "Add announcement ---> mongo.py"
        localtime = time.asctime(time.localtime(time.time()))
        splitCourseId = jsonObj['courseId'].split(":")
        from bson.objectid import ObjectId
        courseId = ObjectId(splitCourseId[1])
        checkCourseEntry = self.cc.find({"_id": courseId}).count()
        if checkCourseEntry > 0:
            try:
                additionalInfo = {"postDate": localtime, "status": 1}
                finalJsonObj = dict(jsonObj.items() + additionalInfo.items())
                self.ac.insert(finalJsonObj)
                print "Announcement added successfully"
                objectIdStr = str(finalJsonObj['_id'])
                announcementId = splitCourseId[0] + "announcement" + ":" + objectIdStr
                announcementId = {"AnnouncementId": announcementId}
                responseAnnouncement = self.ac.find_one({"_id": finalJsonObj['_id']})
                if len(responseAnnouncement) > 0:
                    del responseAnnouncement['_id']
                    finalResponse = dict(announcementId.items() + responseAnnouncement.items())
                    return finalResponse
                else:
                    print "error: Announcement Entry _id invalid"
                    respCode = 400
                    abort(400, respCode)
            except:
                print "error in adding announcement: ", sys.exc_value
                respCode = 500
                abort(500, respCode)
        else:
            print "Error: course not offered anymore found"
            respCode = 404
            abort(404, respCode)


    #
    # Get Announcement
    #

    def getAnnouncement(self, announcementId):
        print "Get announcement with announcement ID = " + announcementId

        # splitting the announcement Id to get the Team name and announcement id in string format
        splitAnnId = announcementId.split(":")

        annObjId = splitAnnId[1]
        Team = splitAnnId[0]

        from bson.objectid import ObjectId
        try:
            objectId = ObjectId(annObjId)
        except:
            print "Error: Id is invalid",sys.exc_traceback
            respcode = 400
            abort(400, respcode)
        checkAnnouncementEntry = self.ac.find({"_id": objectId}).count()

        if checkAnnouncementEntry > 0:
            print "Sending the Announcement Details"
            announcementDetails = self.ac.find_one({"_id": objectId})
            if len(announcementDetails) > 0:
                print "send announcement details"
                del announcementDetails['_id']
                return announcementDetails
            else:
                print "Error: 500 Internal Server error ----> mongo.py"
                respcode = 500
                abort(500, respcode)
        else:
            print "Error: Aannouncement Id Not Found ---> mongo.py"
            respcode = 404
            abort(404, respcode)

    #
    # List all announcements
    #
    def listAnnouncement(self):
        print "List all Announcement ---- Mongo.py"
        Team = "Rangersannouncement:"
        try:
            countAnn = self.ac.count()
            if countAnn > 0:
                annList = self.ac.find()
                annListData = []
                for data in annList:
                    objectId = data['_id']
                    objectIdStr = str(objectId)
                    annId = Team + objectIdStr
                    Id = {'annId': annId}
                    del data['_id']
                    data.update(Id)
                    print data
                    annListData.append(data)
                annListFinal = json.dumps(annListData)
                return annListFinal
            else:
                print "No courses are present on the MOOC"
                return {"success": False}
        except:
            #listCourses = "Other Errors"
            print "error to get list details", sys.exc_info()[0]
            abort(500, "Other Errors")


    #
    # Delete Announcement
    #

    def deleteAnnouncement(self, annId):
        print "Delete Announcement with ID = ", annId
        # splitting the announcement Id to get the Team name and announcement id in string format
        splitAnnId = annId.split(":")

        annObjId = splitAnnId[1]
        Team = splitAnnId[0]

        from bson.objectid import ObjectId
        try:
            objectId = ObjectId(annObjId)
        except:
             print "error: announcement Id is Invalid - MONGO.py", sys.exc_traceback()
             respcode = 400
             abort(400, respcode)

        try:
            deleteCount = self.ac.find({"_id": objectId}).count()
            if deleteCount > 0:
                self.ac.remove({"_id": objectId})
                print "Delete successful"
                return {"success": True}
            else:
                print "error: Announcement not found - MONGO.py"
                respcode = 404
                abort(404, respcode)

        except:
            print "error: announcement Internal server error - MONGO.py", sys.exc_traceback()
            respcode = 500
            abort(500, respcode)

    #_____________________________DISCUSSIONS__________________________________________

    #
    # Add Discussion
    # JSon expected from front end is given below
    # {
    # "course_id": "Rangers:519057591d41c8248488584c",
    # "title": "When will be the final Exam?",
    # "created_by": "email"
    # }

    #
    #
    def addDiscussion(self, jsonObj):
        print "Add discussion ---> mongo.py"

        # This will update the postDate of the user discussion
        localtime = time.asctime(time.localtime(time.time()))

        # Splitting the course id to obtain the Team name and CourseId in string format
        splitCourseId = jsonObj['courseId'].split(":")
        courseObjId = splitCourseId[1]
        Team = splitCourseId[0]

        from bson.objectid import ObjectId
        try:
            objectId = ObjectId(courseObjId)
        except:
            print "Error: Course Id is invalid", sys.exc_traceback()
            respCode = 400
            abort(400, respCode)
        checkCourseEntry = self.cc.find({"_id": objectId}).count()
        if checkCourseEntry > 0:
            try:
                additionalInfo = {"created_at": localtime, "updated_at": localtime}
                print "Created at and updated at ", additionalInfo
                finalJsonObj = dict(jsonObj.items() + additionalInfo.items())
                self.dc.insert(finalJsonObj)
                print "Discussion added successfully"
                #objectIdStr = str(finalJsonObj['_id'])
                discussionId = Team + "discussion" + ":" + courseObjId
                Id = {"discussionId": discussionId}
                responsediscussion = self.dc.find_one({"_id": finalJsonObj['_id']})
                if len(responsediscussion) > 0:
                    del responsediscussion['_id']
                    finalResponse = dict(Id.items() + responsediscussion.items())
                    return finalResponse
                else:
                    print "error: Discussion Entry Id invalid"
                    respCode = 400
                    abort(400, respCode)
            except:
                print "error in adding discussion: ", sys.exc_value()
                respCode = 500
                abort(500, respCode)
        else:
            print "Error: Either course is not present or no more offered"
            respCode = 404
            abort(404, respCode)


    #
    #Get Discussion
    #
    def getDiscussion(self, courseId):
        print "List all Discussion based on course ID---- Mongo.py",courseId
        Team = "Rangersdiscussion:"
        try:
            countDis = self.dc.count()
            if countDis > 0:
                disList = self.dc.find({"courseId": courseId})
                disListData = []
                for data in disList:
                    objectId = data['_id']
                    objectIdStr = str(objectId)
                    disId = Team + objectIdStr
                    Id = {'disId': disId}
                    del data['_id']
                    data.update(Id)
                    print data
                    disListData.append(data)
                disListFinal = json.dumps(disListData)
                return disListFinal
            else:
                print "No discussion is present for course ID in the MOOC"
                return {"success": False}
        except:
            print "error to get list details", sys.exc_info()[0]
            abort(500, "Other Errors")


    #
    # Delete Discussion
    #
    def deleteDiscussion(self, discussionId):
        print "Delete Discussion with ID = ", discussionId

        # splitting the announcement Id to get the Team name and announcement id in string format
        splitDisId = discussionId.split(":")

        disObjId = splitDisId[1]
        Team = splitDisId[0]

        from bson.objectid import ObjectId
        try:
            objectId = ObjectId(disObjId)
        except:
             print "error: discussion Id is Invalid - MONGO.py", sys.exc_traceback()
             respcode = 400
             abort(400, respcode)

        try:
            disCount = self.dc.find({"_id": objectId})

            if disCount > 0:
                self.dc.remove({"_id": objectId})
                print "Delete discussion successful"
                return {"success": True}
            else:
                print "error: discussion not found - MONGO.py"
                respcode = 404
                abort(404, respcode)

        except:
            print "error: discussion Internal server error - MONGO.py", sys.exc_traceback()
            respcode = 500
            abort(500, respcode)