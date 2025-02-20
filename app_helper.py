
import numpy as np
import cv2 as cv2
print("cv2 version:",cv2.__version__)
import os



def get_detected_image(image, filename):

	LABEL_FILE = "object_detection_classes_coco.txt"

	LABELS = open(LABEL_FILE).read().strip().split("\n")

	WEIGHTS="mask_rcnn_frozen_inference_graph.pb"
	MODEL_CONFIG="mask_rcnn_inception_v2_coco_2018_01_28.pbtxt"


	basepath = os.path.dirname(__file__)

	label_file = os.path.join(basepath, LABEL_FILE)
	weights = os.path.join(basepath, WEIGHTS)
	model_config = os.path.join(basepath, MODEL_CONFIG)
	OUTPUT_PATH = os.path.join(basepath,'static','detections')
		
	np.random.seed(42) 
	LABELS = open(label_file).read().strip().split("\n")

	COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),dtype="uint8")

	net = cv2.dnn.readNetFromTensorflow(weights, model_config)

	img = cv2.imread(image)

	blob = cv2.dnn.blobFromImage(img, swapRB=True, crop=False)

	net.setInput(blob)

	(boxes, masks) = net.forward(["detection_out_final", "detection_masks"])

	threshold=0.9

	detected_objects = []

	for i in range(0, boxes.shape[2]): 
	    classID = int(boxes[0, 0, i, 1]) 
	    confidence = boxes[0, 0, i, 2] 
	    if confidence > threshold:
	        (H, W) = img.shape[:2]
	        box = boxes[0, 0, i, 3:7] * np.array([W, H, W, H]) 
	        (startX, startY, endX, endY) = box.astype("int")
	        boxW = endX - startX
	        boxH = endY - startY      
	        mask = masks[i, classID]
	        mask = cv2.resize(mask, (boxW, boxH), interpolation=cv2.INTER_CUBIC)
	        mask = (mask > threshold)
	        roi = img[startY:endY, startX:endX][mask]

	        color = COLORS[classID]
	        blended = ((0.4 * color) + (0.6 * roi)).astype("uint8")

	        img[startY:endY, startX:endX][mask] = blended

	        color = COLORS[classID]
	        color = [int(c) for c in color]
	        detected_objects.append(LABELS[classID])
	        cv2.rectangle(img, (startX, startY), (endX, endY), color, 2)
	        text = "{}: {:.4f}".format(LABELS[classID], confidence)
	        cv2.putText(img, text, (startX, startY - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
	        
	cv2.imwrite(os.path.join(OUTPUT_PATH, filename), img)
	return ", ".join(detected_objects)
	