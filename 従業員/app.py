from click import DateTime
from flask import Flask, render_template, request, redirect,url_for,session
import db,string,random,os,mail,datetime
import matplotlib.pyplot as plt
from datetime import datetime as dt
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
        return redirect(url_for('OTP_mail'))
    
    if db.login(email, password):
        employee_id = db.employee_id(email)
        app.permanent_session_lifetime = timedelta(hours=5)
        session['emp'] = employee_id
        print(employee_id)
        return render_template('menu.html', session=session)
    
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
@app.route('/menu', methods=['GET', 'POST'])
def menu():
    emp = session.get('emp')
    print(emp)
    return render_template('menu.html', session=session)

# 未清掃一覧
@app.route('/noclean_2f_all', methods=['GET', 'POST'])
def noclean_2f_all():
    emp = session.get('emp')
    print(emp)
    noclean_list = db.noclean_2f_list()
    return render_template('noclean_all.html', room=noclean_list, session=session)

@app.route('/noclean_all', methods=['GET', 'POST'])
def noclean_all():
    floor = request.args.get('floor')
    emp = session.get('emp')
    print(emp)
    noclean_list = db.noclean_list(floor)
    return render_template('noclean_all.html', room=noclean_list, session=session)

@app.route('/noclean_all_list', methods=['GET', 'POST'])
def noclean_all_list():
    noclean_list = db.noclean_all()
    emp = session.get('emp')
    print(emp)
    return render_template('noclean_all.html', room=noclean_list, session=session)

# 清掃開始
@app.route('/start_clean', methods=['GET', 'POST'])
def start_clean():
    room_number = request.form.get('room_number')
    emp = session.get('emp')
    request_room = db.request(room_number)
    print(room_number)
    print(emp)
    print(request_room)
    
    if request_room == []:
        no_request = db.no_request(room_number)
        return render_template('start_clean_norequest.html', request=no_request, session=session)
    else:
        return render_template('start_clean.html', request=request_room, session=session)
        

# 清掃開始エラー
@app.route('/start_clean_error', methods=['GET', 'POST'])
def start_clean_error():
    emp = session.get('emp')
    print(emp)
    return render_template('start_clean_error.html', session=session)

# 清掃画面
@app.route('/clean', methods=['GET', 'POST'])
def clean():
    room_number = request.form.get('room_number')
    emp = session.get('emp')
    status = db.room_status(room_number)
    print(room_number)
    print(emp)
    print(status)
    
    if status[0] != 0:
        request_room = db.request(room_number)
        print(request_room)
        if request_room != []:
            return render_template('start_clean_error.html', error=request_room, session=session)
        else:
            norequest_room = db.no_request(room_number)
            return render_template('clean_norequest_error.html', error=norequest_room, session=session)
    else:
        request_room = db.request(room_number)
        
        if request_room == []:
            clean_no_request = db.no_request(room_number)
            db.cleaning(room_number)
            return render_template('clean_norequest.html', clean=clean_no_request, session=session)
        else:
            db.cleaning(room_number)
            return render_template('clean.html', clean=request_room, session=session)

# 清掃エラー
@app.route('/clean_error', methods=['GET', 'POST'])
def clean_error():
    emp = session.get('emp')
    print(emp)
    return render_template('clean_error.html', session=session)

# 要望なし清掃エラー
@app.route('/clean_norequest_error', methods=['GET', 'POST'])
def clean_norequest_error():
    emp = session.get('emp')
    print(emp)
    return render_template('clean_norequest_error.html', session=session)

# 清掃完了
@app.route('/clean_completion', methods=['GET', 'POST'])
def clean_completion():
    room_number = request.form.get('room_number')
    emp = session.get('emp')
    incentive = db.select_incentive(room_number)
    print(room_number)
    print(emp)
    print(incentive)
    db.clean_completion(room_number)
    cleaning_history = db.insert_cleaning_history(emp, room_number, incentive)
    print(cleaning_history)
    noclean_list = db.noclean_2f_list()
    return render_template('noclean_all.html', room=noclean_list, session=session)

# シフト申請
@app.route('/shift', methods=['GET', 'POST'])
def shift():
    emp = session.get('emp')
    print(emp)
    return render_template('shift.html', session=session)

@app.route('/submit_shift', methods=['POST'])
def shift_request():
    holiday_request = request.form.get('holiday_request')
    emp = session.get('emp')
    print(emp)
    print(holiday_request.split(','))
    holiday = []
    for holi in holiday_request.split(','):
        print(holi)
        if holi == '':
            break
        holiday.append(datetime.datetime.strptime(holi, '%Y/%m/%d'))
        print(holiday)
    print(holiday)
    print(emp)
    for holi in holiday:
        print(type(holi))
        db.shift_request(emp, holi)
    message = "シフト申請が完了しました"
    return render_template('menu.html', msg=message, session=session)

# シフト閲覧
@app.route('/shift_all', methods=['GET', 'POST'])
def shift_all():
    emp = session.get('emp')
    work_day = db.shift_all(emp)
    work_type = db.work_type(emp)
    print(emp)
    print(work_day)
    print(work_type)
    return render_template('shift_all.html', session=session, shift=work_day, worktype=work_type)

# インセンティブ閲覧
@app.route('/insentive_view', methods=['GET', 'POST'])
def insentive_view():
    emp = session.get('emp')
    incentive_today = db.incentive_today(emp)
    incentive_month = db.incentive_month(emp)
    print(emp[0])
    print(incentive_today)
    print(incentive_month)
    return render_template('insentive_view.html', session=session, money1=incentive_today, money2=incentive_month)

# インセンティブ統計
@app.route('/insentive_statictics', methods=['GET', 'POST'])
def insentive_statictics():
    emp = session.get('emp')
    print(emp)
    categories = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
    incentive_list = db.incentive_statictics(emp)
    values = []
    
    values.extend(incentive_list)
    
    plt.bar(categories, values)
    plt.xlabel('日数')
    
    statictics = plt.show()
    
    return render_template('insentive_statictics.html', session=session, incentive=statictics)

# ログアウト
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)