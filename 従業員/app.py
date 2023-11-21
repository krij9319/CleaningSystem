from flask import Flask, render_template, request, redirect,url_for,session
import db,string,random,os,mail
from datetime import timedelta
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))

# ログイン画面
@app.route('/', methods=['GET'])
def index():
    msg = request.args.get('msg')
    
    if msg == None:
        return render_template('index.html')
    else:
        return render_template('index.html', msg=msg)

# ログイン
@app.route('/', methods=['POST'])
def login():
    mail = request.form.get('mail')
    password = request.form.get('password')
    
    if mail == '':
        error = "ログインに失敗しました。もう一度やり直してください。"
        return render_template('index.html', error=error)
    if password == '':
        error = "ログインに失敗しました。もう一度やり直してください。"
        return render_template('index.html', error=error)
    
    if db.login(mail, password):
        session['user'] = True
        from datetime import timedelta
        return redirect(url_for('menu'))
    else:
        error = "ログインに失敗しました。もう一度やり直してください。"
        
        input_data = {'mail':mail, 'password':password}
        return render_template('index.html', error=error, data=input_data)

# OTP送信
@app.route('/OTP_mail', methods=['GET'])
def OTP_mail():
    return render_template('OTP_mail.html')

# メール送信
@app.route('/OTP_send', methods=['POST'])
def OTP_send():
    email = request.form.get('mail')
    otp = mail.generate_otp()
    
    db.update_otp(otp, email)
    
    to = email
    subject = 'ワンタイムパスワード'
    body = f'あなたのワンタイムパスワードは{otp}です。'
    
    mail.send_mail(to, subject, body)
    return redirect(url_for('confirm_input'))
    
# 確認番号
@app.route('/confirm_input', methods=['GET'])
def confirm_input():
    return render_template('confirm_input.html')

# パスワード変更
@app.route('/otp_confirm', methods=['POST'])
def change_password(otp, password1, password2):
    otp = request.form.get('otp')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    
    if otp == '':
        error = '確認番号が違います。もう一度やり直してください。'
        return render_template('confirm_input.html', error=error)
    if password1 == '' or password2 == '':
        error = 'パスワードが一致しません。もう一度やり直してください'
        return render_template('confirm_input.html', error=error)
    

# メニュー画面
@app.route('/menu', methods=['GET'])
def menu():
    return render_template('menu.html')

# 未清掃一覧
@app.route('/noclean_all', methods=['GET'])
def noclean_all():
    return render_template('noclean_all.html')

# 清掃開始
@app.route('/start_clean', methods=['GET'])
def start_clean():
    return render_template('start_clean.html')

# 清掃開始エラー
@app.route('/start_clean_error', methods=['GET'])
def start_clean_error():
    return render_template('start_clean_error.html')

# 清掃画面
@app.route('/clean', methods=['GET'])
def clean():
    return render_template('clean.html')

# 清掃エラー
@app.route('/clean_error', methods=['GET'])
def clean_error():
    return render_template('clean_error.html')

# シフト登録
@app.route('/shift', methods=['GET'])
def shift():
    return render_template('shift.html')

# シフト閲覧
@app.route('/shift_all', methods=['GET'])
def shift_all():
    return render_template('shift_all.html')

# インセンティブ閲覧
@app.route('/insentive_view', methods=['GET'])
def insentive_view():
    return render_template('insentive_view.html')

# インセンティブ統計
@app.route('/insentive_statictics', methods=['GET'])
def insentive_statictics():
    return render_template('insentive_statictics.html')
    
if __name__ == '__main__':
    app.run(debug=True)