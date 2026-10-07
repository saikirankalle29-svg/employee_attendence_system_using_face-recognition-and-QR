import os
from django.core.files.storage import FileSystemStorage
import pymysql
import datetime
import pyqrcode
import png
from pyqrcode import QRCode
from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
global username
from PIL import Image
try:
    import face_recognition
except (ImportError, SystemExit, Exception):
    face_recognition = None


import time
import cv2
import numpy as np
import base64
import random

global ids, name, phone, desg, sal, names, encodings, username
if hasattr(cv2, 'CascadeClassifier'):
    face_detection = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
else:
    face_detection = None


def loadModel():
    global names, encodings
    if os.path.exists("model/encoding.npy"):
        encodings = np.load("model/encoding.npy")
        names = np.load("model/names.npy")        
    else:
        encodings = []
        names = []
loadModel()        

def test(request):
    if request.method == 'GET':
       return render(request, 'test.html', {})

def AdminLoginAction(request):
    global username
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        if username == 'admin' and password == 'admin':
            context= {'data':'Hello! Administrator'}
            return render(request, 'AdminScreen.html', context)
        else:
            context= {'data':'login failed. Please retry'}
            return render(request, 'AdminLogin.html', context)  

def AdminLogin(request):
    if request.method == 'GET':
       return render(request, 'AdminLogin.html', {})

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})  

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def AddEmp(request):
    if request.method == 'GET':
       return render(request, 'AddEmp.html', {})

def ViewEmpAttendanceAction(request):
    if request.method == 'POST':
        empid = request.POST.get('t1', False)
        from_date = request.POST.get('t2', False)
        to_date = request.POST.get('t3', False)
        from_dd = str(datetime.datetime.strptime(from_date, "%d-%b-%Y").strftime("'%Y-%m-%d'"))
        to_dd = str(datetime.datetime.strptime(to_date, "%d-%b-%Y").strftime("'%Y-%m-%d'"))
        presence_days = 0
        salary = 0
        columns = ['Employee ID', 'Presence Date']
        output = '<div class="table-responsive"><table class="custom-table">'
        output += "<thead><tr>"
        for i in range(len(columns)):
            output += "<th>"+columns[i]+"</th>"            
        output += "</tr></thead><tbody>"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sai123', database = 'emp_attendance',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select emp_salary FROM employee_details where employeeID='"+empid+"'")
            rows = cur.fetchall()
            for row in rows:
                salary = row[0]
                break
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sai123', database = 'emp_attendance',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * from mark_attendance where employeeID='"+empid+"' and attended_date between "+from_dd+" and "+to_dd)
            rows = cur.fetchall()
            for row in rows:
                presence_days = presence_days + 1
                output += "<tr>"
                output += "<td><span class=\"badge badge-id\">"+str(row[0])+"</span></td>"
                output += "<td>"+str(row[1])+"</td></tr>"
        output += "</tbody></table></div>"
        calculated_salary = (salary/30) * presence_days if salary else 0
        output += '<div class="stats-summary"><div class="stat-card"><span class="label"><i class="fa-solid fa-calendar-check"></i> Attended Days</span><span class="value">'+str(presence_days)+' Days</span></div><div class="stat-card"><span class="label"><i class="fa-solid fa-wallet"></i> Current Salary</span><span class="value badge-salary">$'+f'{calculated_salary:.2f}'+'</span></div></div>'
        context= {'data': output}
        return render(request, 'AdminScreen.html', context)

def ViewEmpAttendance(request):
    if request.method == 'GET':
        output = '<select name="t1" class="form-control select-control">'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sai123', database = 'emp_attendance',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select employeeID FROM employee_details")
            rows = cur.fetchall()
            for row in rows:
                output += '<option value="'+row[0]+'">'+row[0]+'</option>'
        output += "</select>"
        context= {'data1': output}
        return render(request, 'ViewEmpAttendance.html', context)

def ViewAttendance(request):
    if request.method == 'GET':
        return render(request, 'ViewAttendance.html', {})

def FaceAttendance(request):
    if request.method == 'GET':
        return render(request, 'FaceAttendance.html', {})    

def ViewAttendanceAction(request):
    if request.method == 'POST':
        global username
        empid = username
        from_date = request.POST.get('t1', False)
        to_date = request.POST.get('t2', False)
        from_dd = str(datetime.datetime.strptime(from_date, "%d-%b-%Y").strftime("'%Y-%m-%d'"))
        to_dd = str(datetime.datetime.strptime(to_date, "%d-%b-%Y").strftime("'%Y-%m-%d'"))
        presence_days = 0
        salary = 0
        columns = ['Emp ID', 'Attended Date']
        output = '<div class="table-responsive"><table class="custom-table">'
        output += "<thead><tr>"
        for i in range(len(columns)):
            output += "<th>"+columns[i]+"</th>"            
        output += "</tr></thead><tbody>"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sai123', database = 'emp_attendance',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select emp_salary FROM employee_details where employeeID='"+empid+"'")
            rows = cur.fetchall()
            for row in rows:
                salary = row[0]
                break
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sai123', database = 'emp_attendance',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * from mark_attendance where employeeID='"+empid+"' and attended_date between "+from_dd+" and "+to_dd)
            rows = cur.fetchall()
            for row in rows:
                presence_days = presence_days + 1
                output += "<tr>"
                output += "<td><span class=\"badge badge-id\">"+str(row[0])+"</span></td>"
                output += "<td>"+str(row[1])+"</td></tr>"
        output += "</tbody></table></div>"
        calculated_salary = (salary/30) * presence_days if salary else 0
        output += '<div class="stats-summary"><div class="stat-card"><span class="label"><i class="fa-solid fa-calendar-check"></i> Attended Days</span><span class="value">'+str(presence_days)+' Days</span></div><div class="stat-card"><span class="label"><i class="fa-solid fa-wallet"></i> Current Salary</span><span class="value badge-salary">$'+f'{calculated_salary:.2f}'+'</span></div></div>'
        context= {'data': output}
        return render(request, 'UserScreen.html', context)    

def ViewEmp(request):
    if request.method == 'GET':
        columns = ['Emp ID', 'Name', 'Phone No', 'Designation', 'Salary']
        output = '<div class="table-responsive"><table class="custom-table">'
        output += "<thead><tr>"
        for i in range(len(columns)):
            output += "<th>"+columns[i]+"</th>"            
        output += "</tr></thead><tbody>"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sai123', database = 'emp_attendance',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM employee_details")
            rows = cur.fetchall()
            for row in rows:
                output += "<tr>"
                output += "<td><span class=\"badge badge-id\">"+str(row[0])+"</span></td>"
                output += "<td>"+str(row[1])+"</td>"
                output += "<td>"+str(row[2])+"</td>"
                output += "<td>"+str(row[3])+"</td>"
                output += "<td><span class=\"badge badge-salary\">$"+str(row[4])+"</span></td></tr>"
        output += "</tbody></table></div>"
        context= {'data': output}
        return render(request, 'AdminScreen.html', context)


def UserLoginAction(request):
    global username
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        index = 0
        emp_name = None
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sai123', database = 'emp_attendance',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select employeeID, empployeeName FROM employee_details")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    emp_name = row[1]
                    index = 1
                    break		
        if index == 1:
            context= {'data':'welcome '+emp_name}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'login failed. Please retry'}
            return render(request, 'UserLogin.html', context)        

def DownloadAction(request):
    if request.method == 'POST':
        global username
        infile = open("EmployeeAttendance/static/qrcodes/"+username+".png", 'rb')
        data = infile.read()
        infile.close()       

        response = HttpResponse(data, content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename=%s' % username+".png"
        return response

def WebCam(request):
    if request.method == 'GET':
        data = str(request)
        formats, imgstr = data.split(';base64,')
        imgstr = imgstr[0:(len(imgstr)-2)]
        data = base64.b64decode(imgstr)
        if os.path.exists("EmployeeAttendance/static/photo/test.png"):
            os.remove("EmployeeAttendance/static/photo/test.png")
        with open('EmployeeAttendance/static/photo/test.png', 'wb') as f:
            f.write(data)
        f.close()
        context= {'data':"done"}
        return HttpResponse("Image saved")            

def AddEmpAction(request):
    if request.method == 'POST':
        global username
        global ids, name, phone, desg, sal
        ids = request.POST.get('t1', False)
        name = request.POST.get('t2', False)
        phone = request.POST.get('t3', False)
        desg = request.POST.get('t4', False)
        sal = request.POST.get('t5', False)
        output = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sai123', database = 'emp_attendance',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select employeeID FROM employee_details")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == ids:
                    output = ids+" employee already exists"
                    break
        if output == 'none':
            username = ids
            context= {'data':'Capture Your face'}
            return render(request, 'CaptureFace.html', context)
        else:
            context= {'data':username+' employee name already exists'}
            return render(request, 'AddEmp.html', context)
      
def saveFace():
    global names, encodings
    encodings = np.asarray(encodings)
    names = np.asarray(names)
    np.save("model/encoding", encodings)
    np.save("model/names", names)

def saveUser(request):
    if request.method == 'POST':
        global ids, name, phone, desg, sal
        global encodings, names
        img = cv2.imread('EmployeeAttendance/static/photo/test.png')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_component = None
        faces = face_detection.detectMultiScale(gray, 1.3,5) if face_detection is not None else []
        page = "CaptureFace.html"
        status = 'Unable to detect face. Please retry'
        for (x, y, w, h) in faces:
            face_component = img[y:y+h, x:x+w]
        if face_component is not None:
            img = cv2.resize(img, (600, 600))
            if os.path.exists("EmployeeAttendance/static/photo/test.png"):
                os.remove("EmployeeAttendance/static/photo/test.png")
            cv2.imwrite("EmployeeAttendance/static/photo/test.png", img)
            if face_recognition is not None:
                image = face_recognition.load_image_file("EmployeeAttendance/static/photo/test.png")
                encoding = face_recognition.face_encodings(image)
            else:
                encoding = [np.mean(img, axis=(0,1))]
            print("encoding "+str(encoding))
            if len(encoding) > 0 and ids not in names:
                encoding = encoding[0]
                if len(encodings) == 0:
                    encodings.append(encoding)
                    names.append(ids)
                else:
                    encodings = encodings.tolist()
                    names = names.tolist()
                    encodings.append(encoding)
                    names.append(ids)
                saveFace()
                page = "Download.html"
                status = 'User with Face Details added to Database & Download QR Code<br/><br/>'
                db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sai123', database = 'emp_attendance',charset='utf8')
                db_cursor = db_connection.cursor()
                student_sql_query = "INSERT INTO employee_details VALUES('"+ids+"','"+name+"','"+phone+"','"+desg+"','"+sal+"')"
                db_cursor.execute(student_sql_query)
                db_connection.commit()
                url = pyqrcode.create(ids)
                url.png('EmployeeAttendance/static/qrcodes/'+ids+'.png', scale = 6)                
        context= {'data': status}
        return render(request, page, context)

def isEmpExists(code):
    flag = False
    connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sai123', database = 'emp_attendance',charset='utf8')
    with connect:
        curs = connect.cursor()
        curs.execute("select * FROM employee_details where employeeID='"+code+"'")
        rows = curs.fetchall()
        for row in rows:
            flag = True
            break
    return flag

def isAttendanceTaken(code):
    flag = False
    current_date = str(time.strftime('%Y-%m-%d'))
    connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sai123', database = 'emp_attendance',charset='utf8')
    with connect:
        curs = connect.cursor()
        curs.execute("select * FROM mark_attendance where employeeID='"+code+"' and attended_date='"+current_date+"'")
        rows = curs.fetchall()
        for row in rows:
            flag = True
            break
    return flag

def takeAttendance(employee_code):
    error = "Internal error occured"
    current_date = str(time.strftime('%Y-%m-%d'))
    attended_date = isAttendanceTaken(employee_code)
    if attended_date == False and isEmpExists(employee_code) == True:
        connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sai123', database = 'emp_attendance',charset='utf8')
        curs = connect.cursor()
        curs.execute("INSERT INTO mark_attendance(employeeID, attended_date) VALUES('"+employee_code+"','"+current_date+"')")
        connect.commit()
        error = "Attendance Accepted for Employee ID "+employee_code
    if attended_date == True:
        error = "Attendance Accepted only one time for current day"    
    return error

def ValidateUser(request):
    if request.method == 'POST':
        global username, encodings, names
        predict = "none"
        page = "UserScreen.html"
        status = "unable to predict user"
        img = cv2.imread('EmployeeAttendance/static/photo/test.png')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_component = None
        faces = face_detection.detectMultiScale(img,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE) if face_detection is not None else []

        status = "Unable to predict.Please retry"
        if len(faces) > 0:
            faces = sorted(faces, reverse=True,key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
            (fX, fY, fW, fH) = faces
            face_component = gray[fY:fY + fH, fX:fX + fW]
            if face_component is not None:
                img = cv2.resize(img, (600, 600))
                if face_recognition is not None:
                    rgb_small_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert the frame to RGB color space
                    face_locations = face_recognition.face_locations(rgb_small_frame)  # Locate faces in the frame
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)  # Encode faces in the frame
                    for face_encoding in face_encodings:
                        matches = face_recognition.compare_faces(encodings, face_encoding)  # Compare face encodings
                        face_distance = face_recognition.face_distance(encodings, face_encoding)  # Calculate face distance
                        best_match_index = np.argmin(face_distance)  # Get the index of the best match
                        print(best_match_index)
                        if matches[best_match_index]:  # If the face is a match
                            name = names[best_match_index]  # Get the corresponding name
                            predict = name
                            break
            if predict == username:            
                status = takeAttendance(predict)
        else:
            status = "unable to detect face"
        context= {'data':status}
        return render(request, page, context)



    
