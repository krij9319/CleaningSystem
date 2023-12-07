from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os, random
import email.utils

def generate_otp():
    return ''.join(random.choice('0123456789ABCDEF') for i in range(16))

def generate_number():
    return str(random.randint(1000, 9999))

def send_mail(to, subject, body):
    ID = 'no.replay.cleaning.sys22@gmail.com'
    PASS = os.environ['Cleaning_PASS']
    HOST = 'smtp.gmail.com'
    PORT = 587
    
    msg = MIMEMultipart()
    
    msg.attach(MIMEText(body, 'html'))
    
    msg['Subject'] = subject
    msg['From'] = email.utils.formataddr(('システムメール', ID))
    msg['To'] = email.utils.formataddr(('ユーザ', to))
    
    server = SMTP(HOST, PORT)
    server.starttls()
    
    server.login(ID, PASS)
    
    server.send_message(msg)
    
    server.quit()    
    
