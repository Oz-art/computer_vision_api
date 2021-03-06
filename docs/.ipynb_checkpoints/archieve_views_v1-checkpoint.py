from django.shortcuts import render
from PIL import Image
import numpy as np
import io
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Import Library Object Detection ------------------------------------
import os
import cv2

import json
from uuid import uuid4
import time
# Create your views here.


@csrf_exempt
def object_detection_api(request):
    
    output = {}
    
    if request.method == 'POST':
        try:
            image_request = request.FILES['input_image']

            # Preprocess
            image_bytes = image_request.read()
            image = Image.open(io.BytesIO(image_bytes))
            image = np.array(image)
            image = image[:, :, ::-1].copy()

            tic = time.time()
            image_result, boxes, names = detect_object(image)
            execution_time = time.time() - tic

            list_object = []
            for name, box in zip(names, boxes):
                data_object = {}
                data_object["name"] = name
                data_object["coordinate"] = str(box)
                list_object.append(data_object)

            output["list_object"] = list_object
            
            rand_token = uuid4()
            file_image = "media/" + str(rand_token) + ".png"
            cv2.imwrite(file_image, image_result)
            
            host = "http://127.0.0.1:8000/"
            
            output["url_image"] = host + file_image
            output["execution_time"] = execution_time
            output["status"] = "success"
        
        except:
            output["status"] = "no image attached"
            pass
        
    else:
        output["status"] = "not post request"
        

    with open('result.json', 'w') as f:
        jsonResult = JsonResponse(output, safe=False)
        
    return jsonResult

# Define Method plot_box ------------------------------------
def plot_box(frame, box, text):
    overlay = frame.copy()
    (H, W) = frame.shape[:2]
    box_border = int(W / 400)
    font_size = 0.6

    (startX, startY, endX, endY) = box

    y = startY - 10 if startY - 10 > 10 else startY + 10
    yBox = y + 5

    cv2.rectangle(overlay, (startX, startY), (endX, endY),
      (255, 255, 255), box_border+4)

    cv2.rectangle(overlay, (startX, startY), (endX, endY),
      (147, 0, 0), box_border+2)


    cv2.putText(overlay, text, (startX, y),
    cv2.FONT_HERSHEY_SIMPLEX, (0.5*box_border), (0, 0, 0), int(box_border*1))

    alpha = 0.6  # Transparency factor.

    # Following line overlays transparent rectangle over the image
    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    return frame


def detect_object(image):

    # Loading Model ------------------------------------
    protoPath = "app_object_detection/MobileNetSSD_deploy.prototxt"
    modelPath = "app_object_detection/MobileNetSSD_deploy.caffemodel"

    detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)



    # Setting Parameter ------------------------------------
    conf_treshold = 0.2
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]


    # Read Input Image ------------------------------------
    #frame = cv2.imread('tes.jpg')
    frame = image
    print(type(image))



    # Detection Process ------------------------------------
    (h, w) = frame.shape[:2]

    # numpy array to blob 
    blobPerson = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)

    detector.setInput(blobPerson)
    detectedPersons = detector.forward()

    boxes = []
    names = []

    for i in np.arange(0, detectedPersons.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the prediction
        confidence = detectedPersons[0, 0, i, 2]

        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence > conf_treshold:
            # extract the index of the class label from the
            # `detections`, then compute the (x, y)-coordinates of
            # the bounding box for the object
            idx = int(detectedPersons[0, 0, i, 1])
            box = detectedPersons[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # draw the prediction on the frame
            boxes.append((startX, startY, endX, endY))
            names.append(CLASSES[idx])


    # Draw Boxes ------------------------------------
    frame_output = frame.copy()
    for box, name in zip(boxes, names):
        frame_output = plot_box(frame_output, box, name)


    # Save Result ------------------------------------
    cv2.imwrite('result.jpg', frame_output)
    
    return frame_output, boxes, names
        
        
        
