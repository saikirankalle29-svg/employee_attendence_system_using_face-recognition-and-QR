import numpy as np
import os, cv2, pymysql, time

global employeeID, currentDate
employeeID = 0
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
    if isAttendanceTaken(employee_code) == False and isEmpExists(employee_code) == True:
        connect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'sai123', database = 'emp_attendance',charset='utf8')
        curs = connect.cursor()
        curs.execute("INSERT INTO mark_attendance(employeeID, attended_date) VALUES('"+employee_code+"','"+current_date+"')")
        connect.commit()
        error = "Attendance Accepted for Employee ID "+employee_code
    if isAttendanceTaken(employee_code) == True:
        error = "Attendance Accepted only one time for current day"
    if isEmpExists(employee_code) == False:
        error = "Waiting for scan"
    return error

def startWebcam():
    global employeeID
    status = "Waiting"
    webcam = cv2.VideoCapture(0)
    qr_reader = cv2.QRCodeDetector()
    while True:
        _, image = webcam.read()
        code, bounding, _ = qr_reader.detectAndDecode(image)
        if bounding is not None:
            for i in range(len(bounding)):
                cv2.line(image, tuple(bounding[i][0]), tuple(bounding[(i+1) % len(bounding)][0]), color=(255, 0, 0), thickness=2)
        if code != employeeID:
            status = "Last Scan Result: "+takeAttendance(code)
            employeeID = code
        cv2.putText(image, status, (10, 25),  cv2.FONT_HERSHEY_SIMPLEX,0.7, (255, 0, 0), 2)
        cv2.imshow("Employee Attendance System", image)
        if cv2.waitKey(1) == ord("q"):
            break    
    cap.release()
    cv2.destroyAllWindows()        
            
startWebcam()
