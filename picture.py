import cv2
from ultralytics import YOLO
import math

# Load the trained model
model = YOLO('best.pt')

# Load an image
img = cv2.imread('test4.jpg')

# Check if image is loaded
if img is not None:
    # Perform inference
    results = model(img)
    print('results size', len(results))
    # Iterate through results
    for r in results:
        print('boxes', len(r.boxes))
        boxes = r.boxes  # Assuming this gives you access to detected bounding boxes

        for box in boxes:
            # Extract and convert bounding box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Draw the bounding box on the image
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cls = int(box.cls[0])
            print("Class name -->", cls)
            confidence = math.ceil((box.conf[0] * 100)) / 100
            print("Confidence --->", confidence)

            # Print coordinates of the box
            print(f"Coordinates: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

    # Display the image with detections
    cv2.imshow('Detected Image', img)
    cv2.waitKey(0)  # Wait for a key press to exit
    cv2.destroyAllWindows()
else:
    print("Failed to load image.")
