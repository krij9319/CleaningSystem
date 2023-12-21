from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import db, string, random, mail, psycopg2, calendar


app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))

@app.route('/', methods=['GET'])
def index():
    msg = request.args.get('msg')   # Redirect された時のパラメータ受け取り

    if msg == None:
        # 通常のアクセスの場合
        return render_template('index.html')
    else :
        # register_exe() から redirect された場合
        return render_template('index.html', msg=msg)
@app.route('/otpmail')
def otp_mail():
    return render_template('OTP_mail.html')

@app.route('/', methods=['POST'])
def login():
    admin_id = request.form.get('adminid')
    password = request.form.get('password')
    otp = db.otp_login(admin_id)
    # ログイン判定
    
    if otp and otp[5] == False:
        return redirect(url_for('otp_mail'))
    
    if db.login(admin_id, password):
        session['user'] = True
        return redirect(url_for('admintop'))
    
    else:
        error = 'ユーザ名またはパスワードが違います。'
        
        # dictで返すことでフォームの入力量が増えても可読性が下がらない。
        input_data={'admin_id':admin_id, 'password':password}
        return render_template('index.html', error=error, data=input_data)
    
@app.route('/logout')
def logout():
    session.pop('user', None)   # sessionの破棄
    return redirect(url_for('index'))   # ログイン画面にリダイレクト    

@app.route('/admintop', methods=['GET'])
def admintop():
    if 'user' in session:
        return redirect(url_for('menu'))   
    else :
        return redirect(url_for('index'))   
    
@app.route('/register')
def register_form():
    return render_template('admin_register.html')

@app.route('/registermail', methods=['POST'])
def register_mail():
    admin_id = request.form.get('adminid')
    name = request.form.get('name')
    mail_address = request.form.get('mail')
    otp = mail.generate_otp()
    
    db.insert_admin(admin_id, name, mail_address, otp)
    
    to = mail_address
    subject = 'ワンタイムパスワード'
    body = f'あなたのワンタイムパスワードは{otp}です。'
    
    mail.send_mail(to, subject, body)
    return redirect(url_for('navigateSend'))

@app.route('/send', methods=['GET'])
def navigateSend():
    return render_template('admin_temporary.html')

@app.route('/numbermail', methods=['POST'])
def send_number():
    mail_address = request.form.get('mail')
    
    if mail_address == '':
        error = 'このメールアドレスは登録されていません'
        return render_template('OTP_mail.html', error=error)
    else:
        authnumber = db.generate_new_number()
    
        db.update_number(authnumber, mail_address)
        
        to = mail_address
        subject = '確認番号'
        body = f'確認番号は{authnumber}です。'
        mail.send_mail(to, subject, body)
        return redirect(url_for('navigateNumber'))

@app.route('/sendnumber', methods=['GET'])
def navigateNumber():
    return render_template('confirm_input.html')

@app.route('/confirmnumber', methods=['POST'])
def confirm_number():
    pass1 = request.form.get('password1')
    pass2 = request.form.get('password2')
    number = request.form.get('number')
    authnumber = db.number_check(number)
    
    if (authnumber and authnumber[6] == number) and pass1 == pass2:
        db.password_update(pass2, number)
        msg = 'パスワードを変更しました。'
        return render_template('index.html', msg=msg)
    else:
        error = '入力内容に誤りがあります'
        return render_template('confirm_input.html', error=error)
        

@app.route('/menu', methods=['GET'])
def menu():
    return render_template('menu.html')

@app.route('/emp', methods=['GET'])
def emp():
    return render_template('employee_register.html')

@app.route('/confirmemp' , methods=['POST'])
def con_regi():
    id = request.form.get('employee_id')
    name = request.form.get('name')
    email = request.form.get('mail')
    concat = request.form.get('concat')
    if concat == 'A':
        concat = '9:00~15:00'
    else:
        concat ='10:00~15:00'
    print(concat)
    
        
    return render_template('confirm_register.html', id=id, name=name, email=email, concat=concat)
    

@app.route('/empregi', methods=['POST'])
def emp_regi():
    id = request.form.get('employee_id')
    name = request.form.get('name')
    mail_address = request.form.get('mail')
    concat = request.form.get('concat')
    otp = mail.generate_otp()
    
    if concat == '9:00~15:00':
        concat = 'A'
    else:
        concat = 'B'

    db.insert_emp(id, name, mail_address, concat, otp)

    to = mail_address
    subject = 'ワンタイムパスワード'
    body = f'あなたのワンタイムパスワードは{otp}です。'
    
    mail.send_mail(to, subject, body)    
    return redirect(url_for('employee_all'))

@app.route('/room')
def room_management():
    room = db.select_two_room()
    troom = db.select_three_room()
    foroom = db.select_four_room()
    firoom = db.select_five_room()
    siroom = db.select_six_room()
    seroom = db.select_seven_room()
    eiroom = db.select_eight_room()
    niroom = db.select_nine_room()
    teroom = db.select_ten_room()
    elroom = db.select_eleven_room()
    return render_template('room_management.html', room=room, troom=troom, foroom=foroom, firoom=firoom, siroom=siroom,
                           seroom=seroom, eiroom=eiroom, niroom=niroom, teroom=teroom, elroom=elroom)

@app.route('/shift')
def shift_management():
    management = db.employee()
    shift = db.shift()
    name = []
    type = []
    shift_day= []
    volume = len(management)

    shift_vol = len(shift_day)
    for i in range(volume):
        name.append(management[i][1])
        type.append(management[i][6])
    current_month = datetime.now().month
    current_year = datetime.now().year
    if current_month == 12:
        current_year += 1
        current_month = 1
    else:
        current_month = current_month + 1
    month = calendar.monthrange(current_year,current_month)
    day_list = []
    sample_cw_list = ['月', '火', '水', '木', '金', '土', '日']
    cw_list = []
    for i in range(month[1]):
        day_list.append(i+1)
        for j in range(len(sample_cw_list)):
            cw_list.append(sample_cw_list[j])
    value = len(day_list)
    for i in range(value):
        if len(shift) < i:
            if shift[1] == i:
                shift_day.append(shift[i][1])
            else:
                shift_day.append(0)
        else:
                shift_day.append(1)
    print(shift_day)
    return render_template('shift_management.html', shifts = management, request=shift, current_month=current_month, current_year=current_year, day_list=day_list, cw_list=cw_list, value=value, name=name, type=type, volume=volume, shift_day=shift_day, shift_vol=shift_vol)  

@app.route('/employee')
def employee_all():
    employee = db.all_employee()
    return render_template('employee_all.html', employees = employee)  

@app.route('/detail')
def employee_detail():
    user_name = request.args.get('emp_name')
    print(user_name)
    user_detail = db.get_user_details(user_name)
    return render_template('employee_detail.html', user_details=user_detail)

@app.route('/emped' , methods=['POST'])
def employee_edit():
    id = request.form.get('employee_id')
    name = request.form.get('name')
    email = request.form.get('mail')
    concat = request.form.get('concat')
    
    if name == '':
        error = '名前が未入力です'
        return render_template('employee_edit.html', error=error)
    if email == '':
        error = 'メールアドレスが未入力です'
        return render_template('employee_edit.html', error=error)
    if concat == '':
        error = '業務時間が未選択です'
        return render_template('employee_edit.html', error=error)
    
    return render_template('confirm_edit.html',id=id, name=name, mail=email, concat=concat)

 
@app.route('/delete', methods=['POST'])
def emp_delete():
    id = request.form.get('id')
    print(id)
    name = request.form.get('name')
    mail_address = request.form.get('mail')
    
    return render_template('employee_delete.html', id=id, name=name, mail_address=mail_address) 

@app.route('/complete_delete', methods=['POST'])
def complete_delete():
    id = request.form.get('emp_id')
    # print(id)
    db.employee_delete(id)
    
    return redirect(url_for('employee_all')) 

  
if __name__ == '__main__':
    app.run(debug=True)