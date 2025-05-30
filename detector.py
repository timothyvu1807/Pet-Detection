import io
import os
import cv2
import telebot
import threading
import numpy as np
from PIL import Image
import pygame as pygame
import UI
from ultralytics import YOLO
from datetime import datetime, timedelta
import subprocess

# initiliaze the pet_ID with UI
pet_id = UI.run_ui()
# print(pet_id)

#starting detection alg
telegram_key = "" #insert your telegram key
chat_id = "" #insert your id chat key
bot = telebot.TeleBot(telegram_key)
shared_frame = None

def send_message(chat_id, message):
    bot.send_message(chat_id, message)

def send_photo(chat_id, frame):
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img_rgb)

    bio = io.BytesIO()
    bio.name = 'image.jpeg'
    img.save(bio, 'JPEG')
    bio.seek(0)

    bot.send_photo(chat_id, bio)

def telegram_listener():
    @bot.message_handler(func=lambda message: True)
    def echo_all(message):
        if message.text == "update":
            global shared_frame
            if shared_frame is not None:
                send_photo(chat_id, shared_frame)
    bot.polling()

telegram_thread = threading.Thread(target=telegram_listener)
telegram_thread.start()

last_sent_time = datetime.now() - timedelta(seconds=15)
model = YOLO("yolov8n.pt")
classes = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
    'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
    'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
    'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis',
    'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard',
    'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon',
    'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog',
    'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table',
    'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
    'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
    'teddy bear', 'hair drier', 'toothbrush'
]

pygame.init()
pygame.mixer.init()
alarm_played = False
pygame.mixer.music.load(os.path.abspath('alarm2.mp3'))

COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

cap = cv2.VideoCapture(0)
fps_camera = cap.get(cv2.CAP_PROP_FPS)
target_fps = 10
n = int(fps_camera / target_fps)
frame_counter, not_detected = 0, 0

while True:
    # Used to start the detection since it hangs after UI Selection.
    command = "\n"
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    ret, frame = cap.read()
    if not ret:
        break
    shared_frame = frame

    if frame_counter % n == 0:
        outs = model(frame, task='detect', iou=0.2, conf=0.3, show=True, save_conf=True, classes=[pet_id,57,59], boxes=True)

        pred_classes = [classes[int(i.item())] for i in outs[0].boxes.cls]
        pred_bbox = [i.tolist() for i in outs[0].boxes.xywh]

        length = len(pred_classes)
        dog_boxes = []
        couch_boxes = []
        dog_flag, couch_bed_flag = 0, 0

        for i in range(length):
            if pred_classes[i] in ['dog', 'cat']:
                dog_boxes.append((round(pred_bbox[i][0]), round(pred_bbox[i][1]), round(pred_bbox[i][0] + pred_bbox[i][2]), round(pred_bbox[i][1] + pred_bbox[i][3])))
                dog_flag = 1
            if pred_classes[i] in ['couch', 'bed']:
                couch_boxes.append((round(pred_bbox[i][0]), round(pred_bbox[i][1]), round(pred_bbox[i][0] + pred_bbox[i][2]), round(pred_bbox[i][1] + pred_bbox[i][3])))
                couch_bed_flag = 1

        if alarm_played and (not dog_flag or not couch_bed_flag):
            dog_boxes = [(0, 0, 0, 0)]
            couch_boxes = [(0, 0, 0, 0)]
        else:
            for dog_box in dog_boxes:
                for couch_box in couch_boxes:
                    if dog_box[3] < (couch_box[3] - ((couch_box[3] - couch_box[1]) * 0.3)) and ((couch_box[0] < dog_box[0] < couch_box[2]) or (couch_box[0] < dog_box[2] < couch_box[2])) and dog_flag and couch_bed_flag:
                    # if dog_flag and couch_bed_flag:
                    #     not_detected = 0
                        if not alarm_played:
                            if datetime.now() - last_sent_time >= timedelta(seconds=5):
                                send_message(chat_id, "Dog has detected on couch!")
                                last_sent_time = datetime.now()
                                send_photo(chat_id, frame)
                            pygame.mixer.music.play(1)  # play in a loop
                            alarm_played = True
                    else:
                        if alarm_played:
                            not_detected += 1
                            if not_detected > 10:
                                not_detected = 0
                                pygame.mixer.music.stop()
                                alarm_played = False

    couch_bed_flag = 0
    dog_flag = 0
    dog_boxes = [(0, 0, 0, 0)]
    couch_boxes = [(0, 0, 0, 0)]
    frame_counter += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
