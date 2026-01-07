import cv2
import os
import time
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta

class CCTV:
    def __init__(self, frame_rate=3, video_duration=5):
        self.frame_rate = frame_rate
        self.video_duration = video_duration
        self.images_folder = 'images'
        self.videos_folder = 'videos'
        self.create_folders()
        self.cap = cv2.VideoCapture(0)
        self.yolo_model = self.load_yolo_model()
        self.detection = False
        self.detection_start_time = None

    def create_folders(self):
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)
        if not os.path.exists(self.videos_folder):
            os.makedirs(self.videos_folder)

    def load_yolo_model(self):
        # Load YOLO model here
        net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        return net, output_layers

    def capture_images(self):
        prev = 0
        while True:
            time_elapsed = time.time() - prev
            ret, frame = self.cap.read()
            if time_elapsed > 1./self.frame_rate:
                prev = time.time()
                timestamp = int(time.time())
                filename = f'{self.images_folder}/frame_{timestamp}.jpg'
                cv2.imwrite(filename, frame)
                threading.Thread(target=self.detect_person, args=(frame, timestamp)).start()
                cv2.imshow('frame', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def detect_person(self, frame, timestamp):
        net, output_layers = self.yolo_model
        height, width, channels = frame.shape
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5 and class_id == 0:  # Class ID 0 is for person
                    self.detection = True
                    self.detection_start_time = timestamp
                    threading.Thread(target=self.create_video_clip, args=(timestamp,)).start()
                    return

    def create_video_clip(self, detection_time):
        start_time = detection_time - self.video_duration
        end_time = detection_time + self.video_duration
        video_filename = f'{self.videos_folder}/clip_{detection_time}.avi'
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(video_filename, fourcc, self.frame_rate, (640, 480))

        for timestamp in range(start_time, end_time + 1):
            image_filename = f'{self.images_folder}/frame_{timestamp}.jpg'
            if os.path.exists(image_filename):
                frame = cv2.imread(image_filename)
                out.write(frame)

        out.release()
        threading.Thread(target=self.send_email, args=(video_filename,)).start()

    def send_email(self, video_filename):
        fromaddr = "your_email@example.com"
        toaddr = "recipient_email@example.com"
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "CCTV Alert: Person Detected"
        body = "A person was detected. Please find the attached video clip."
        msg.attach(MIMEText(body, 'plain'))
        attachment = open(video_filename, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % video_filename)
        msg.attach(part)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(fromaddr, "your_password")
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()

if __name__ == "__main__":
    cctv = CCTV()
    cctv.capture_images()
