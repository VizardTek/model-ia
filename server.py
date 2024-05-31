from flask import Flask, request, Response
import cv2
import requests
import threading
import time
import uuid
import math

from ultralytics import YOLO

app = Flask(__name__)


cameras = []
threads = []

def fire_detection(camera):

    print("camera", camera)

    print("url", camera["url"])

    # print("device_id", device_id)
    # print("name", name)
    # print("url", url)
    # Load your trained model
    model = YOLO('best-fire-smoke-only.pt')

    # Open a video file

    cap = cv2.VideoCapture(int(camera["url"][-1]))  # Read the video file
    # video_path = 'fire.mp4'
    # cap = cv2.VideoCapture(video_path)

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
        out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))

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
                    cv2.putText(img, classNames[cls] + " " + str(confidence), org, font, fontScale, color, thickness)

                    if classNames[cls] == 'fire':
                        set_fire = True

                        if set_fire:
                            print('COUNTTTTTTTT ',count)
                            cv2.putText(img, classNames[cls] + " " + str(confidence), org, font, fontScale, color, thickness)
                            if confidence > 70 :
                                count = count + 1
                                print("feu detectÃ©")
                                if count == 10:
                                    print('SEND ALERTTTT')
                                    headers = {
                                        'Content-Type': 'application/json',
                                        "Authorization": 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uIjoiNjY1OWRiMzc2ZjcwMGIwOGFlZjBkZDNlIiwiX2lkIjoiNjY1OWQ3ZDc2ZjcwMGIwOGFlZjBkZDM3Iiwicm9sZSI6IkFETUlOIiwiaWF0IjoxNzE3MTY2Nzc3LCJleHAiOjE3MTczMzk1Nzd9.3-bUMc2y4LaPLZBZW6F8blhsTjzMVreuLiZ4SYRi-Js'
                                    }

                                    # data = {
                                    #     'id': frame_count, 
                                    #     "alertData": { "title": "ALERTE FEU", "body": f"ALERTE FEU DETECTE AVEC UNE CONFIANCE DE {confidence}% sur la pièce {name} avec l'id {device_id}"}
                                    # }


                                    # print(requests.post('http://192.168.137.1:4000/api/alerting/alert', json=data, headers=headers).json())

                                elif count > 10:
                                    count = 0
                    """ else:
                        countNoFire += 1
                        if(countNoFire == 10):
                            count = 0 """
                        
                    pass
                        

                    # cv2.putText(img, classNames[cls], org, font, fontScale, color, thickness)

                out.write(img)
                if cv2.waitKey(1) == ord('q'):
                    break

        cap.release()
        cv2.destroyAllWindows()


def find_available_cameras():

   
    max_attempts = 100
    newCams = []
    global cameras

    cameras = [{'device_id': '20ed4948-abfe-4819-b741-78d451711856', 'name': 'Cam0', 'url': '/camera/0'}, {'device_id': 'c99edacb-0903-4214-9594-d8818a09bb74', 'name': 'Cam1', 'url': '/camera/1'}]

    print("Trying to find cams")

    for i in range(max_attempts):
        print("Trying to find cams", i)
        cap = cv2.VideoCapture(i)
        if cap.isOpened():  # Check if the camera is available
            cap.release()
            # Generate a unique device_id
            device_id = str(uuid.uuid4())

            # Construct the name
            name = "Cam" + str(i)

            # Check if a camera with the same name already exists
           
            camObj = {
                "device_id": device_id,
                "name": name,
                "url": "/camera/"+str(i)
            }
            newCams.append(camObj)

            cameras = newCams

            print("caaaaaaaaaaaaaaaaa", cameras)
            print(f"Camera {i} is available.")

            for camera in cameras:

                print("camera", camera)

                # print(de)
                thread = threading.Thread(target=fire_detection, args=(camera,))
                threads.append(thread)
                thread.start()
                
            # fire_detection()
        else:
            # Indicate which camera is not available
            print(f"Camera {i} is not available.")
            
            break  # Stop the loop if no more cameras are available

    return cameras


def update_cameras_on_api():
    posturl = "http://192.168.137.1:4000/api/sensors/cameras"
    geturl = "http://192.168.137.1:4000/api/cameras"
    headers = {"Content-Type": "application/json"}
    
    try:
        # Fetch the current list of registered camera device_ids from the backend
        registeredCamerasResponse = requests.get(geturl, headers=headers)
        registeredCamerasResponse.raise_for_status()
        registeredCamerasData = registeredCamerasResponse.json()

        # Extract device_ids from the registered cameras
        registered_device_ids = [cam['_deviceId']
                                 for cam in registeredCamerasData['availableCameras']]

        # Find available cameras
        camerasAvailable = find_available_cameras()

        # Initialize a list to hold cameras to be updated
        camerasToUpdate = []
        
        # Check if there's a match between registered and available device_ids
        for cam in camerasAvailable:
            if cam['device_id'] in registered_device_ids:
                continue
            else:
                # Create a default camera object for not-found device_id
                defaultCam = {
                    "device_id": cam['device_id'],
                    "name": f"{cam['name']}",
                    "url": f"{cam['url']}"
                }
                camerasToUpdate.append(defaultCam)

        if camerasToUpdate:
            data = {
                "cameras": camerasToUpdate
            }

            response = requests.post(posturl, json=data, headers=headers)
            response.raise_for_status()  # Raises an exception if the response was unsuccessful
            camera_data = response.json()
            print(camera_data)
        else:
            # If there's a match, do nothing
            print("All cameras have matching device_ids. No update needed.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
       


@app.route('/camera/<int:camera_index>', methods=['GET'])
def video_feed(camera_index):
    # Check if the requested camera exists
    if camera_index >= len(cameras):
        return "Camera not found", 404

    cap = cv2.VideoCapture(camera_index)

    def generate_frames():
        while True:
            success, frame = cap.read()
            if not success:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    # update_cameras_on_api()
    find_available_cameras()
    app.run(host='0.0.0.0', port=8000)