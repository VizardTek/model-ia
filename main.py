import cv2
from ultralytics import YOLO
import math
import requests

from dotenv import load_dotenv
import os

load_dotenv()

AUTHORIZATION = os.getenv('AUTHORIZATION')
SERVER_URL = os.getenv('SERVER_URL')

# Load your trained model
model = YOLO('best-fire-smoke-only.pt')

# Open a video file
  
cap = cv2.VideoCapture(0)  # Read the video file

frame_rate = cap.get(cv2.CAP_PROP_FPS)
# counter = 0``
frame_skip = 30  # Number of frames to skip
frame_count = 30  # Frame counter
count = 0
countNoFire = 0
classNames = ['Fire', 'clear', 'fire', 'nf', 'smoke']

if not cap.isOpened():
    print("Error opening video file")
else:
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    out = cv2.VideoWriter('zefuiyzeoafuzaife.mp4', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))

    while True:
        success, img = cap.read()
        if not success:
            break  # If no frame is read, end of video is reached

        results = model(img, stream=True)
        
         # coordinates
        for r in results:
            boxes = r.boxes

            for box in boxes:
                # bounding box
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # convert to int values

                # put box in cam
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

                # confidence
                confidence = math.ceil((box.conf[0] * 100))

                # class name
                cls = int(box.cls[0])
                    # object details
                org = [x1, y1]
                font = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 1
                color = (255, 0, 0)
                thickness = 2

                frame_count += 1
                set_fire = False
                cv2.putText(img, classNames[cls] + " " + str(confidence), org, font, fontScale, color, thickness)

                if classNames[cls] == 'fire':
                    set_fire = True

                    if set_fire:
                        print('COUNTTTTTTTT ',count)
                        cv2.putText(img, classNames[cls] + " " + str(confidence), org, font, fontScale, color, thickness)
                        if confidence > 70 :
                            count = count + 1
                            print("feu detecté")
                            if count == 10:
                                print('SEND ALERTTTT')
                                headers = {
                                    'Content-Type': 'application/json',
                                    "Authorization": AUTHORIZATION
                                }

                                data = {
                                    'id': frame_count, 
                                    "alertData": { "title": "ALERTE FEU", "body": f"ALERTE FEU DETECTE AVEC UNE CONFIANCE DE {confidence}%"}
                                }

                                print(requests.post(f'{SERVER_URL}/api/alerting/alert', json=data, headers=headers).json())

                            elif count > 10:
                                count = 0
                pass
            cv2.imshow("Image", img)
            if cv2.waitKey(1) == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()