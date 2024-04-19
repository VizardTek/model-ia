import cv2
from ultralytics import YOLO
import math
import requests

# Load your trained model
model = YOLO('best2.pt')

# Open a video file
  
cap = cv2.VideoCapture(0)  # Read the video file
# video_path = 'fire.mp4'
# cap = cv2.VideoCapture(video_path)

frame_rate = cap.get(cv2.CAP_PROP_FPS)
# counter = 0``
frame_skip = 30  # Number of frames to skip
frame_count = 30  # Frame counter

classNames = ['fire', 'other', 'smoke']

if not cap.isOpened():
    print("Error opening video file")
else:
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))

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
                # print("Confidence --->", confidence)

                # class name
                cls = int(box.cls[0])

                # print("Class name -->", classNames[cls])

                    # object details
                org = [x1, y1]
                font = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 1
                color = (255, 0, 0)
                thickness = 2

                frame_count += 1
                set_fire = False
                if classNames[cls] != 'other':
                    if classNames[cls] == 'fire':
                        set_fire = True

                        if set_fire:
                            print("je passe tout les 30")
                            cv2.putText(img, classNames[cls] + " " + str(confidence), org, font, fontScale, color, thickness)
                            print("feu detecté")

                            headers = {
                                'Content-Type': 'application/json',
                                "Authorization": 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uIjoiNjVmYWUzMGY0MDJmYjBiMGVkYTEyNWY1IiwiX2lkIjoiNjVmYWUzMGQ0MDJmYjBiMGVkYTEyNWVmIiwicm9sZSI6IkFETUlOIiwiaWF0IjoxNzEwOTQxMTI5LCJleHAiOjE3MTExMTM5Mjl9.vWV2PXix2t3MK5nf-RO7rHqbzyzI4fTI7szKJ3V99MY'
                            }

                            data = {
                                'id': frame_count, 
                                "alertData": { "title": "ALERTE FEU", "body": f"ALERTE FEU DETECTE AVEC UNE CONFIANCE DE {confidence}%"}
                            }


                            print(requests.post('http://192.168.137.1:4000/api/alerting/alert', json=data, headers=headers).json())
                              
                    pass
                    

                # cv2.putText(img, classNames[cls], org, font, fontScale, color, thickness)

            out.write(img)
            if cv2.waitKey(1) == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
