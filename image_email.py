import os
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


def SendMail(ImgFileName):
    img_data = open(ImgFileName, "rb").read()
    msg = MIMEMultipart()
    msg["Subject"] = "Crash Alert"
    msg["From"] = "roihansori34@gmail.com.cc"
    msg["To"] = "roihansori12@gmail.com.cc"

    text = MIMEText("Vehicle Crash Detected. Send HELP")
    msg.attach(text)
    image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
    msg.attach(image)

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("roihansori34@gmail.com", "password")
    s.sendmail("roihansori34@gmail.com", "roihansori12@gmail.com", msg.as_string())
    s.quit()
