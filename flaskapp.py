from flask import Flask,flash, render_template, Response, jsonify, request, session
from flask_wtf import FlaskForm
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_file,
    url_for,
    Response,
)
from werkzeug.utils import secure_filename, send_from_directory
from wtforms import (
    FileField,
    SubmitField,
    StringField,
    DecimalRangeField,
    IntegerRangeField,
)
from wtforms.validators import InputRequired, NumberRange
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import cv2
from YOLO_Video import video_detection
from YOLO_Video import process_image


app = Flask(__name__)

app.config["SECRET_KEY"] = "roihansori"
app.config["UPLOAD_FOLDER"] = "static/files"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/image_upload")
def image():
    session.clear()
    return render_template("image.html")

@app.route("/image_upload", methods=["GET", "POST"])
def predict_img():
    if request.method == "POST":
        
         if "file" in request.files:
            file = request.files["file"]
            
            basepath = os.path.dirname(__file__)
            filename = secure_filename(file.filename)
            filepath = os.path.join(basepath, app.config["UPLOAD_FOLDER"], filename)
            print("upload folder is ", filepath)
            file.save(filepath)
            global imgpath

            predict_img.imgpath = file.filename
            print("printing predict_img ::::::::::::", predict_img)

            file_extension = file.filename.rsplit(".", 1)[1].lower()

            if file_extension not in ALLOWED_EXTENSIONS:
                return render_template("invalid.html")
                
            if file and allowed_file(file.filename):
                detections = process_image(filepath)
                return display(file.filename)

            folder_path = "runs/detect"
            subfolders = [ f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
            latest_subfolder = max( subfolders, key=lambda x: os.path.getctime(os.path.join(folder_path, x)))
            image_path = folder_path + "/" + latest_subfolder + "/" + file.filename
            return render_template("image.html", image_path=image_path)
    # return "done"


@app.route("/<path:filename>")
def display(filename):
    folder_path = "runs/detect"
    subfolders = [
        f
        for f in os.listdir(folder_path)
        if os.path.isdir(os.path.join(folder_path, f))
    ]
    latest_subfolder = max(
        subfolders, key=lambda x: os.path.getctime(os.path.join(folder_path, x))
    )
    directory = folder_path + "/" + latest_subfolder
    print("printing directory: ", directory)
    files = os.listdir(directory)
    latest_file = files[0]

    print(latest_file)
    filename = os.path.join(folder_path, latest_subfolder, latest_file)

    file_extension = filename.rsplit(".", 1)[1].lower()

    environ = request.environ
    if file_extension == "jpg":
        return send_from_directory(
            directory, latest_file, environ
        )  # shows the result in separate tab
    else:
        return "Invalid file format"


@app.route("/download_image")
def download_image():
    folder_path = "runs/detect"
    subfolders = [
        f
        for f in os.listdir(folder_path)
        if os.path.isdir(os.path.join(folder_path, f))
    ]
    latest_subfolder = max(
        subfolders, key=lambda x: os.path.getctime(os.path.join(folder_path, x))
    )
    directory = folder_path + "/" + latest_subfolder
    print("printing directory: ", directory)
    files = os.listdir(directory)
    latest_file = files[0]

    print(latest_file)
    filename = os.path.join(folder_path, latest_subfolder, latest_file)

    file_extension = filename.rsplit(".", 1)[1].lower()

    environ = request.environ
    if file_extension == "jpg":
        return send_file(
            filename, as_attachment=True
        )  # shows the result in separate tab
    else:
        return "Invalid file format"
    
    

# Use FlaskForm to get input video file  from user
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Run")


def generate_frames(path_x=""):
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        ref, buffer = cv2.imencode(".jpg", detection_)
        if not ref:
            break
        frame = buffer.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")


def generate_frames_web(path_x):
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        ref, buffer = cv2.imencode(".jpg", detection_)

        frame = buffer.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    session.clear()
    return render_template("index.html")


@app.route("/webcam_detection", methods=["GET", "POST"])
def webcam():
    session.clear()
    return render_template("webcam.html")


@app.route("/video_detection", methods=["GET", "POST"])
def front():
    # Upload File Form: Create an instance for the Upload File Form
    form = UploadFileForm()
    if form.validate_on_submit():
        # Our uploaded video file path is saved here
        file = form.file.data
        file.save(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                app.config["UPLOAD_FOLDER"],
                secure_filename(file.filename),
            )
        )  # Then save the file
        # Use session storage to save video file path
        session["video_path"] = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            app.config["UPLOAD_FOLDER"],
            secure_filename(file.filename),
        )

    return render_template("video.html", form=form)

@app.route("/download_video")
def download_video():
     filename = 'output.mp4'

     return send_file(filename, as_attachment=True)
 
@app.route("/video")
def video():
    print("function called")
    # return Response(generate_frames(path_x='static/files/bikes.mp4'), mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(
        generate_frames(path_x=session.get("video_path", None)),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


# To display the Output Video on Webcam page
@app.route("/webapp")
def webapp():
    # return Response(generate_frames(path_x = session.get('video_path', None),conf_=round(float(session.get('conf_', None))/100,2)),mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(
        generate_frames_web(path_x=0),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


if __name__ == "__main__":
    app.run(debug=True)
