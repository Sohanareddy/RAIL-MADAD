from flask import Flask, render_template, request, jsonify
import smtplib
import os
import speech_recognition as sr
from pydub import AudioSegment
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)

# Email credentials
SENDER_EMAIL = "sohanareddy26@gmail.com"
SENDER_PASSWORD = "tbfr uszv rktp fund"  # Use Google App Password

def convert_audio_to_text(audio_path):
    recognizer = sr.Recognizer()
    if not audio_path.endswith(".wav"):
        sound = AudioSegment.from_file(audio_path)
        audio_path = audio_path.replace(os.path.splitext(audio_path)[1], ".wav")
        sound.export(audio_path, format="wav")

    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except Exception as e:
        return f"Audio conversion failed: {e}"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/send_complaint', methods=['POST'])
def send_complaint():
    recipient_email = request.form['email']
    complaint_text = request.form['complaint']
    image = request.files.get('image')
    audio = request.files.get('audio')
    
    msg = MIMEMultipart()
    msg["Subject"] = "Railway Complaint"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    msg.attach(MIMEText(complaint_text, "plain"))
    
    if image:
        image_path = os.path.join("static/uploads", image.filename)
        image.save(image_path)
        with open(image_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={image.filename}")
        msg.attach(part)
    
    if audio:
        audio_path = os.path.join("static/uploads", audio.filename)
        audio.save(audio_path)
        audio_text = convert_audio_to_text(audio_path)
        msg.attach(MIMEText(f"\n[Audio Complaint Converted to Text]: {audio_text}", "plain"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        return jsonify({"status": "success", "message": "Complaint sent successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    os.makedirs("static/uploads", exist_ok=True)
    app.run(debug=True)
