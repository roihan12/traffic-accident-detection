from ultralytics import YOLO
import cv2
import math
import os
from image_email import SendMail  # Uncomment for alert to email


def process_image(file_path):
    # Perform the detection
    yolo = YOLO("YOLO-Weights\yolov8m-5000-300.pt")
    detections = yolo.predict(file_path, save=True, imgsz=640, conf=0.25)
    return detections


def webcam_detection(frame):
    # Perform the detection
    model = YOLO("YOLO-Weights\yolov8m-5000-300.pt")
    classNames = ["Accident"]
    
    results = model(frame, stream=True)
    for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                print(x1, y1, x2, y2)
                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])
                class_name = classNames[cls]
                label = f"{class_name}{conf}"
                t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
                print(t_size)
                c2 = x1 + t_size[0], y1 - t_size[1] - 3
                if class_name == "Accident":
                    color = (0, 204, 255)

                if conf > 0.25:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                    cv2.rectangle(frame, (x1, y1), c2, color, -1, cv2.LINE_AA)  # filled
                    cv2.putText(
                        frame,
                        label,
                        (x1, y1 - 2),
                        0,
                        1,
                        [255, 255, 255],
                        thickness=1,
                        lineType=cv2.LINE_AA,
                    ) 
    yield frame                
  
 

def video_detection(path_x):
    video_capture = path_x
    print(path_x)
    # Create a Webcam Object
    cap = cv2.VideoCapture(video_capture)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    # out = cv2.VideoWriter(
    #     file_name + ".mp4",
    #     cv2.VideoWriter_fourcc("M", "J", "P", "G"),
    #     10,
    #     (frame_width, frame_height),
    # )

    global alert_var
    # Define the codec and create VideoWriter object

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter("output.mp4", fourcc, 10.0, (frame_width, frame_height))

    model = YOLO("YOLO-Weights\yolov8m-5000-300.pt")
    classNames = ["Accident"]
    while True:
        success, img = cap.read()
        if not success:
             exit()
        results = model(img, stream=True, save=True, conf=0.50)
        

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                print(x1, y1, x2, y2)
                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])
                class_name = classNames[cls]
                label = f"{class_name}{conf}"
                t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
                print(t_size)
                c2 = x1 + t_size[0], y1 - t_size[1] - 3
                if class_name == "Accident":
                    color = (0, 204, 255)

                if conf > 0.25:
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
                    cv2.rectangle(img, (x1, y1), c2, color, -1, cv2.LINE_AA)  # filled
                    cv2.putText(
                        img,
                        label,
                        (x1, y1 - 2),
                        0,
                        1,
                        [255, 255, 255],
                        thickness=1,
                        lineType=cv2.LINE_AA,
                    ) 
                    # while alert < 4:
                    #     cv2.imwrite("crash_alert.jpg", img)
                    #     SendMail("crash_alert.jpg")
                    #     print(alert)
                    #     alert += 1
                # if alert_var == 3:         # makes sure that alert is generated when there are atleast 3 frames which shows that a fall has been detected
                #     cv2.imwrite('crash_alert.jpg',img)
                #     SendMail('crash_alert.jpg')
                # alert_var += 1
                
        yield img
        # alert_var=0
        print(results)
        cv2.waitKey(1)
        cv2.imshow("result", img)
        out.write(img)

        if cv2.waitKey(1) & 0xFF == ord("1"):
            break
    out.release()
    print(":::Video Write Completed")

cv2.destroyAllWindows()

