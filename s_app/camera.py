import datetime
import os
import cv2
import dlib
import imutils
import pickle
import face_recognition
from s_project.settings import MEDIA_ROOT
from .models import *
from datetime import datetime

facial_landmarks_file = os.path.join(MEDIA_ROOT, '68_facial_landmarks_file',
                                     'shape_predictor_68_face_landmarks.dat')
training_dir = os.path.join(MEDIA_ROOT, 'training_dataset')
classes_save_path = os.path.join(MEDIA_ROOT, 'classes', 'classes.npy')
svc_save_path = os.path.join(MEDIA_ROOT, "sav", "svc.sav")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(facial_landmarks_file)
attendance_names = list()


def encodings_for_training(data_list: list):
    faces_encodings, faces_names = list(), list()
    for data in data_list:
        globals()['image_{}'.format(data[1])] = face_recognition.load_image_file(data[1])
        try:
            globals()['image_encoding_{}'.format(data[1])] = \
                face_recognition.face_encodings(globals()['image_{}'.format(data[1])], model='large', num_jitters=100)[
                    0]
            faces_encodings.append(globals()['image_encoding_{}'.format(data[1])])
            # print(faces_encodings)
            # Create array of known names
            faces_names.append(data[0])
        except:
            pass

    print()
    data = {"encodings": faces_encodings, "names": faces_names}
    print("---------------------------")
    print(len(faces_encodings))
    print("---------------------------")
    # use pickle to save data into a file for later use
    f = open(os.path.join(MEDIA_ROOT, 'model', "face_enc"), "wb")
    f.write(pickle.dumps(data))  # to open file in write mode
    f.close()  # to close file

    # data = pickle.loads(open(os.path.join(MEDIA_ROOT, "face_enc"), "rb").read())
    # print("++++++++++++++++++++++++++++++")
    # print(len(data['encodings']))
    # print("++++++++++++++++++++++++++++++")


def most_common(lst):
    return max(set(lst), key=lst.count)


def create_folder(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def get_count(name):
    global attendance_names
    try:
        d = dict()
        for i in attendance_names:
            if i not in d:
                d[i] = 1
            else:
                d[i] += 1
        return d[name]
    except:
        return 0


def mark_employee_attendance(name, morning_shift_start_time, morning_shift_end_time,
                             night_shift_start_time, night_shift_end_time, base_folder, frame):
    global attendance_names
    user_id = name.split("_")[0]
    user_name = name.split("_")[1]
    user_record = Employee.objects.filter(emp_id=user_id)
    user_shift = user_record[0].shift
    current_time = datetime.now().strftime("%H:%M:%S")
    if (user_shift == 'Morning' and morning_shift_end_time > current_time > morning_shift_start_time) or \
            (user_shift == 'Night' and night_shift_end_time > current_time > night_shift_start_time):
        get_name_occurrence = get_count(name)
        if get_name_occurrence != 0 or get_name_occurrence % 2 != 0:
            Attendance.objects.filter(name=user_name).update(exit=datetime.now())
        else:
            user_designation = user_record[0].designation
            folder_name = os.path.join(base_folder, name)
            create_folder(folder_name)
            att_obj = Attendance(name=user_name,
                                 # image=folder_name + os.sep + name + '.jpg',
                                 image=name + '.jpg',  # TODO : fix image path issue
                                 emp_id=user_id,
                                 designation=user_designation,
                                 shift=user_shift, enter=datetime.now())
            att_obj.save()
            to_save_frame = cv2.resize(frame, (300, 300))
            cv2.imwrite(f'{folder_name}{os.sep}{name}.jpg', to_save_frame)

        attendance_names.append(name)
        return True
    else:
        return False


def mark_unidentified_face(folder_name, frame):
    enter_time = datetime.now()
    file_name = f'{str(enter_time.strftime("%Y%m%d%H%M%S"))}.jpg'
    u_obj = UnidentifiedFaces(enter=enter_time, image=file_name)
    u_obj.save()
    cv2.imwrite(f'{folder_name}{os.sep}{file_name}', frame)


class VideoCamera(object):
    def __init__(self, source):
        self.video = cv2.VideoCapture(source)
        self.data = pickle.loads(open(os.path.join(MEDIA_ROOT, 'model', "face_enc"), "rb").read())
        self.decider = list()
        self.marker = False
        self.text = None
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.counter = 150
        self.night_shift_start_time = "00:00:00"
        self.night_shift_end_time = "11:59:59"
        self.morning_shift_start_time = "12:00:00"
        self.morning_shift_end_time = "23:59:59"
        self.employee_base_folder = os.path.join(MEDIA_ROOT, 'employees')
        self.unidentified_folder = os.path.join(MEDIA_ROOT, 'unidentified')
        create_folder(self.employee_base_folder)
        create_folder(self.unidentified_folder)

    def __del__(self):
        self.video.release()

    def recognise_face(self, frame, border):
        if self.marker:
            if self.counter != 0:
                if 'marked!' in self.text:
                    cv2.putText(frame, self.text, (10, 30), self.font, 0.8, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, self.text, (10, 30), self.font, 0.8, (0, 0, 255), 2)
                self.counter -= 1
            else:
                self.marker = False
                self.counter = 150
        else:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]
            all_face_locations = face_recognition.face_locations(rgb_small_frame)
            face_locations = []
            if all_face_locations:
                for fl in all_face_locations:
                    if fl[0] * 4 < border[0] or fl[1] * 4 > border[1] or fl[2] * 4 > border[2] or fl[3] * 4 < border[3]:
                        pass
                    else:
                        face_locations.append(fl)
            if not face_locations:
                return frame
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(self.data['encodings'], face_encoding)
                name = "unknown"
                if True in matches:
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    count = {}
                    for i in matchedIdxs:
                        name = self.data["names"][i]
                        count[name] = count.get(name, 0) + 1
                        name = max(count, key=count.get)
                        face_names.append(name)
                else:
                    face_names.append(name)

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                if len(self.decider) <= 100:
                    self.decider.append(name)
                else:
                    name = most_common(self.decider)
                    if name != 'unknown':
                        print_name = name.split("_")[1]
                        if len(attendance_names) == 0 or name != attendance_names[-1]:
                            if mark_employee_attendance(name,
                                                        self.morning_shift_start_time,
                                                        self.morning_shift_end_time,
                                                        self.night_shift_start_time,
                                                        self.night_shift_end_time, self.employee_base_folder, frame):
                                self.text = f"{print_name.upper()}, attendance is marked!"
                            else:
                                self.text = f"{print_name.upper()}, WRONG SHIFT!"
                        else:
                            self.text = f"{print_name.upper()}, attendance is already marked!"
                        # cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        # cv2.putText(frame, text, (left + 6, bottom - 6),self.font, 1, (255, 255, 255), 1)
                        # cv2.putText(frame, self.text, (30, 30), self.font, 1, (255, 255, 255), 1)
                    else:
                        mark_unidentified_face(self.unidentified_folder, frame)
                        self.text = "UNIDENTIFIED PERSON!!!"
                        # cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                        # cv2.putText(frame, name, (30, 30), self.font, 2, (255, 255, 255), 2)
                    self.marker = True
                    self.decider = list()
        return frame

    def get_frame(self):
        success, frame = self.video.read()
        frame = imutils.resize(frame, width=800)
        h, w = frame.shape[:2]
        print("h, w")
        print(h, w)
        print("------------")

        bottom = int(h - (h * 15 / 100))
        top = int(h - (h * 85 / 100))

        right = int(w - (w * 25 / 100))
        left = int(w - (w * 75 / 100))

        border = (top, right, bottom, left)
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        # resize = cv2.resize(image, (640, 480), interpolation=cv2.INTER_LINEAR)
        frame = self.recognise_face(frame, border)
        # frame = cv2.flip(frame, 1)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
