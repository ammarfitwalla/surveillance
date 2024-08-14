import os.path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.http import StreamingHttpResponse, HttpResponse
from .camera import *
from datetime import date
from s_project.settings import MEDIA_ROOT
from django.views.decorators.cache import cache_control

# File Uploader
from django.core.files.storage import FileSystemStorage

to_train = list()
source = None


def admin_check(user):
    if user.is_staff or user.is_superuser:
        return True
    return False


def detect_face(frame):
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_small_frame)
    if len(face_locations) == 1:
        return True
    else:
        return False


# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please log in to continue')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@user_passes_test(admin_check)
def home(request):
    global to_train

    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        mobile = request.POST.get('mobile')
        designation = request.POST.get('designation')
        shift = request.POST.get('shift')

        image = request.FILES.getlist('image')
        filesystem = FileSystemStorage()
        all_good = False
        for f in image:
            filename = filesystem.save(f.name, f)
            tmp_file = os.path.join(settings.MEDIA_ROOT, filename)
            image_array = cv2.imread(tmp_file)
            output = detect_face(image_array)
            if not output:
                all_good = False
                break
            else:
                all_good = True

        if all_good:
            insert_employee = Employee(emp_id=emp_id, name=name, age=age, gender=gender, mobile=mobile,
                                       designation=designation, shift=shift)
            insert_employee.save()
            get_employee_id = Employee.objects.last()

            for img in image:
                EmployeeImage.objects.create(model=get_employee_id, image=img)
        else:
            messages.error(request, f'Please upload proper image with one visible face.')

    train_emp = EmployeeImage.objects.all()

    for t in train_emp:
        if not t.model.train and t.model.id not in to_train:
            to_train.append(t)
            to_train.append(t.model.id)

    print('to_train', to_train)

    context = {
        'to_train': to_train,
    }

    return render(request, 'home.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@user_passes_test(admin_check)
def records(request):
    emp_records = []
    tmp_id = []
    all_attend = Attendance.objects.all()
    url_name = request.resolver_match.url_name

    for emp in EmployeeImage.objects.all():
        if emp.model.id not in tmp_id:
            tmp_id.append(emp.model.id)
            emp_records.append(emp)
        else:
            continue

    att_today = []
    today = str(date.today())
    for attend in Attendance.objects.all():
        if today == str(attend.enter).split()[0]:
            att_today.append(attend)

    context = {
        'all_attend': all_attend,
        'emp_records': emp_records,
        'url_name': url_name,
        'att_today': att_today
    }
    return render(request, 'records.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def main(request):
    global source
    ip_cam = None
    camera = request.POST.get('camera')
    ipValue = request.POST.get('ipValue')
    videoValue = request.FILES.get('video')
    print("CAMERA", source, camera, videoValue)
    print(request.POST)
    print("+==========================================================")
    print(request.GET)
    print("+==========================================================")
    print(request.FILES)
    if camera == 'ipcam':
        ip_cam = 'ipcam'
        source = str(ipValue)
        if ":" in source:
            if "https" in source:
                ip = source.split(":")[0]
                port = source.split(":")[1]
                source = f"https://{ip}:{port}/videofeed?username=&password="
                # http: // ip: port / videofeed?username = & password =
        else:
            source = int(source)

    elif camera == 'webcam':
        ip_cam = 'webcam'
        source = 0
    
    elif camera == 'video':
        ip_cam = 'video'
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'videos'))
        filename = fs.save(videoValue.name, videoValue)
        source = fs.path(filename)
        print("VIDEO", filename, type(filename))

    print('source ===', source)
    context = {
        'ip_cam': ip_cam,
    }
    return render(request, 'main.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@user_passes_test(admin_check)
def train(request):
    print("to train", to_train)
    if len(to_train) == 0:
        return redirect('home')
    else:
        all_emp_data = Employee.objects.all()
        data = list()
        for i in all_emp_data:
            all_emp_images = EmployeeImage.objects.filter(model=i.id)
            for j in all_emp_images:
                # frame = cv2.imread(os.path.join(MEDIA_ROOT, str(j.image)))
                data.append([i.emp_id + "_" + i.name, os.path.join(MEDIA_ROOT, str(j.image))])

        create_dir(os.path.join(MEDIA_ROOT, 'model'))
        create_dir(os.path.join(MEDIA_ROOT, 'employees'))
        create_dir(os.path.join(MEDIA_ROOT, 'unidentified'))

        if os.path.isfile(os.path.join(MEDIA_ROOT, 'model', 'face_enc')):
            os.remove(os.path.join(MEDIA_ROOT, 'model', 'face_enc'))

        encodings_for_training(data)

        for tr in to_train:
            if type(tr) != int:
                Employee.objects.filter(id=tr.model.id).update(train=True)

        messages.success(request, f'Training completed successfully!!!')
        to_train.clear()
        return redirect('home')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def unidentified_faces_records(request):
    all_unidentified_faces_records = UnidentifiedFaces.objects.all()
    context = {'all_records': all_unidentified_faces_records}
    return render(request, 'unidentified_faces_records.html', context)


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_feed(request):
    global source
    print("[INFO] Video Source", source)
    
    try:
        # Initialize the video generator
        video_generator = gen(VideoCamera(source))
        
        # Attempt to retrieve the first frame
        first_frame = next(video_generator, None)
        
        if first_frame is None:
            # If no frames are available, return an empty response or a message
            print("[INFO] No frames available in the video source.")
            return HttpResponse("No video frames available", content_type="text/plain", status=204)
        
        # If there are frames, return the StreamingHttpResponse
        return StreamingHttpResponse(video_generator, content_type='multipart/x-mixed-replace; boundary=frame')
    
    except Exception as e:
        # Handle any exceptions that might occur
        print(f"[ERROR] An error occurred: {e}")
        return HttpResponse("An error occurred while processing the video stream.", status=500)


def create_dir(path):
    if not os.path.isdir(path):
        os.mkdir(path)
