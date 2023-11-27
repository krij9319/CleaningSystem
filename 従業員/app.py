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
    email = request.form.get('mail')
    password = request.form.get('password')
    otp = db.otp_login(email)
    
    if email == '':
        error = "ログインに失敗しました。もう一度やり直してください。"
        return render_template('index.html', error=error)
    if password == '':
        error = "ログインに失敗しました。もう一度やり直してください。"
        return render_template('index.html', error=error)
    
    if otp and otp[5] == False:
        return redirect(url_for('otp_mail'))
    
    if db.login(email, password):
        session['user'] = True
        return redirect(url_for('menu'))
    
    else:
        error = 'ユーザ名またはパスワードが違います。'
        
        # dictで返すことでフォームの入力量が増えても可読性が下がらない。
        input_data={'admin_id':email, 'password':password}
        return render_template('index.html', error=error, data=input_data)

# OTP送信
@app.route('/OTP_mail', methods=['GET'])
def OTP_mail():
    return render_template('OTP_mail.html')

# メール送信
@app.route('/OTP_send', methods=['POST'])
def OTP_send():
    email = request.form.get('mail')
    authnumber = db.generate_new_number()
    
    db.update_number(authnumber, email)
    
    if email == '':
        return redirect(url_for('OTP_send_error'))
    
    to = email
    subject = '確認番号'
    body = f'確認番号は{authnumber}です。'

    mail.send_mail(to, subject, body)
    if email == '':
        error = 'このメールアドレスは登録されていません'
        return render_template('OTP_mail.html', error=error)
    else:
        return redirect(url_for('confirm_input'))

# メール送信エラー
@app.route('/OTP_send_error', methods=['GET'])
def OTP_send_error():
    return render_template('OTP_mail_error.html')

# 確認番号
@app.route('/confirm_input', methods=['GET'])
def confirm_input():
    return render_template('confirm_input.html')

# パスワード変更
@app.route('/otp_confirm', methods=['POST'])
def change_password():
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    number = request.form.get('otp')
    print(password1, password2, number)
    authnumber = db.number_check(number)
    
    if number == '':
        error = '確認番号が違います。もう一度やり直してください。'
        return render_template('confirm_input.html', error=error)
    if password1 == '' or password2 == '':
        error = 'パスワードが一致しません。もう一度やり直してください'
        return render_template('confirm_input.html', error=error)
    
    if (authnumber and authnumber[8] == number) and password1 == password2:
        db.password_update(password2, number)
        msg = 'パスワードを変更しました。'
        return render_template('index.html', msg=msg)   

# メニュー画面
@app.route('/menu', methods=['GET'])
def menu():
    return render_template('menu.html')

# 未清掃一覧
@app.route('/noclean_all', methods=['GET'])
def noclean_all():
    noclean_list = db.noclean_list()
    return render_template('noclean_all.html', room=noclean_list)

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

# シフト申請
@app.route('/shift', methods=['GET'])
def shift():
    return render_template('shift.html')

@app.route('/submit_shift', methods=['POST'])
def submit_shift():
    selected_days = request.form.getlist('selected_days[]')
    return render_template('shift_all.html', selected_days=selected_days)

if __name__ == '__main__':
    app.run(debug=True)

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

# ログアウト
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)