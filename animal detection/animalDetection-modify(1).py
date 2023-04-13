from imutils.video import VideoStream
from flask import Response
from flask import Flask, request
from flask import render_template
from time import sleep
import numpy as np
import socket
import threading
import argparse
import datetime
import imutils
import time
import cv2
import RPi.GPIO as GPIO
from twilio.rest import Client
import socket

GET_IP_CMD ="hostname -I"
LED = 23
BUZZER = 25
PIR = 24
GPIO.setmode(GPIO.BCM)
number = 0
capture = 0
detection = 0
detected = 1
GPIO.setup(BUZZER,GPIO.OUT)
GPIO.setup(LED,GPIO.OUT)
GPIO.setup(PIR,GPIO.IN)
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--probability", type = float, default = 0.2, help = "minimum probability to filter weak detections")
args = vars(ap.parse_args())
outputFrame = None
motionoutput = ""
lock = threading.Lock()
app = Flask(__name__)
vs = VideoStream(src=0).start()#enable the camera to start capturing
time.sleep(2.0)
@app.route("/",methods = ['GET', 'POST'])

def index():
        global capture
        global detection
        global motionoutput
        global number
        global detected
        if request.method == "POST":
                if request.form.get("capture") == "capture":
                        print("Capturing")
                        capture = 1
                if request.form.get("backward") == "backward":
                        detection = 1
                if request.form.get("buzzeroff") == "buzzeroff":
                        GPIO.output(BUZZER,GPIO.LOW)
                if request.form.get("buzzeron") == "buzzeron":
                        GPIO.output(BUZZER,GPIO.HIGH)
                if request.form.get("stop") == "stop":
                        capture = 0
                        print("Capturing Stopped")
        return render_template("index-modify.html",name = motionoutput)

def detect_motion(frameCount):
        global vs, outputFrame, lock
        CLASSES = ["background", "aeroplane", "bicycle", "bird", "mouse", "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]
        COLORS = np.random.uniform(0, 255, size = (len(CLASSES), 3))
# load our serialized model from disk
        print("[INFO] loading model...")
        net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt.txt", "MobileNetSSD_deploy.caffemodel")
        # loop over frames from the video stream
        global capture
        global detection
        global motionoutput
        global detected
        while True:
                if detected == 1:
                        print("Found")
                        print(CLASSES[idx])
                        account_sid = "AC429bddc63d3cf1f18dda84d5961442aa"
                        auth_token = "e5aa1df609ae1dc0b0b243c59afb1a9e"
                        client = Client(account_sid, auth_token)
                        message = client.api.account.messages.create(
                        body='Animal Found - ' + CLASSES[idx] ,
                        from_='+16515043978',
                        to='+918217877573'
                        )
                        # print("Found")
                        # print(CLASSES[idx])
                        # # account_sid = 'AC429bddc63d3cf1f18dda84d5961442aa' 
                        # # auth_token = 'e5aa1df609ae1dc0b0b243c59afb1a9e' 
                        # # client = Client(account_sid, auth_token) 
                        # # message = client.api.messages.create( 
                        # # from_='whatsapp:+14155238886',  
                        # # body='Animal Found - ' + CLASSES[idx],      
                        # # to='whatsapp:+918217877573' 
                        # # ) 
                        # account_sid = 'AC429bddc63d3cf1f18dda84d5961442aa' 
                        # auth_token = 'e5aa1df609ae1dc0b0b243c59afb1a9e' 
                        # client = Client(account_sid, auth_token) 
                        # message = client.api.messages.create(  
                        # messaging_service_sid='MG21f4fd475e7ac56194836599d4d67094', 
                        # body='Animal Detected -' + CLASSES[idx],      
                        # to='+918217877573' 
                        # ) 
 
# print(message.sid)
 
                        # print(message.sid)
                                                #print(message.sid)
                        GPIO.output(BUZZER,GPIO.HIGH)
                        GPIO.output(LED,GPIO.HIGH)
                        time.sleep(5)
                        GPIO.output(BUZZER,GPIO.LOW)
                        GPIO.output(LED,GPIO.LOW)
                        # if detected == 1:
                        # time.sleep(5)
                        # GPIO.cleanup()
                        
                # read the next frame from the video stream, resize it,
                frame = None
                # convert the frame to grayscale, and blur it
                if GPIO.input(PIR):
                        capture = 1
                        motionoutput = "MOTION DETECTED"
                else:
                        motionoutput = "MOTION NOT DETECTED"
                # else:
                        # motionoutput = "Motion Not Detected"
                if capture == 1:
                        # count = 0
                        frame = vs.read()
                        frame = imutils.resize(frame, width=1200)
        # grab the frame dimensions and convert it to a blob
        # Binary Large Object = BLOB
                        (h, w) = frame.shape[:2]
                        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
                        # pass the blob through the network and get the detections
                        net.setInput(blob)
                        detections = net.forward()
                        # loop over the detections
                        for i in np.arange(0, detections.shape[2]):
                                # extract the probability of the prediction
                                probability = detections[0, 0, i, 2]
                                # filter out weak detections by ensuring that probability is
                                # greater than the min probability
                                if probability > 0.5:
                                        # extract the index of the class label from the
                                        # 'detections', then compute the (x, y)-coordinates of
                                        # the bounding box for the object
                                        idx = int(detections[0, 0, i, 1])
                                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                                        (startX, startY, endX, endY) = box.astype("int")
                                        if (CLASSES[idx] == "horse" or CLASSES[idx] == "cow" or CLASSES[idx] == "sheep" or CLASSES[idx] == "dog" or CLASSES[idx] == "cat" or CLASSES[idx] == "sheep" or CLASSES[idx] == "person" or CLASSES[idx]  == "rat" or CLASSES[idx] == "bird"):
                                                label = "{}: {:.2f}%".format(CLASSES[idx], probability * 100)
                                                cv2.rectangle(frame, (startX, startY), (endX, endY), COLORS[idx], 2)
                                                y = startY - 15 if startY - 15 > 15 else startY + 15
                                                cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
                                                detected = 1
                                        else:
                                                detected = 0
                        # grab the current timestamp and draw it on the frame
                        timestamp = datetime.datetime.now()
                        cv2.putText(frame, timestamp.strftime(
                               "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 1)
                        # cv2.putText(frame, "Its Working Dude", (10, frame.shape[0] - 25), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 1)
                        # if the total number of frames has reached a sufficient
                        # number to constuct a reasonable background model, then
                        # continue to process the frame
                        # update the background model and increment the total number
                        # of frames read thus far
                        # print(detected)
                        # acquire the lock, set te output frame, and release the
                        # lock
                        with lock: #context managment 
                                if capture == 0:
                                        outputFrame = None
                                else:
                                        outputFrame = frame.copy()
                        #print(detected)
                # print(motionoutput)
                
def generate():
        # grab global references to the output frame and lock variables
        global outputFrame, lock
        global detected 
        # loop over frames from the output stream
        while True:
                # wait until the lock is acquired
                with lock:
                        # check if the output frame is available, otherwise skip
                        # the iteration of the loop
                        if outputFrame is None:
                                continue
                        # encode the frame in JPEG format
                        (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
                        # ensure the frame was successfully encoded
                        if not flag:
                                continue
                # yield the output frame in the byte format
                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                        bytearray(encodedImage) + b'\r\n')
@app.route("/video_feed")


def video_feed():
        
        # return the response generated along with the specific media
        # type (mime type)
        # print(detected)
        return Response(generate(),
                mimetype = "multipart/x-mixed-replace; boundary=frame")
# check to see if this is the main threasd of execution

        
if __name__ == '__main__':
        # construct the argument parser and parse command line arguments
        ap = argparse.ArgumentParser()
        #ap.add_argument("-i", "--ip", type=str, required=True,
                #help="ip address of the device")
        #ap.add_argument("-o", "--port", type=int, required=True,
        #       help="ephemeral port number of the server (1024 to 65535)")
        ap.add_argument("-f", "--frame-count", type=int, default=32,
                help="# of frames used to construct the background model")
        args = vars(ap.parse_args())

        # start a thread that will perform motion detection
        t = threading.Thread(target=detect_motion, args=(args["frame_count"],))
        t.daemon = True
        t.start()
        # start the flask app
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]     
        app.run(host=ip, port=8916, debug=True,
                threaded=True, use_reloader=False)
        s.close() 

if __name__=='__main__':
   app.run()
# release the video stream pointer
vs.stop()
GPIO.cleanup()
