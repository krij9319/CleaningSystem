from flask import Flask, render_template, request, redirect, url_for, session
import db, string, random, mail

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
        return render_template('menu.html')   
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

@app.route('/room')
def room_management():
    return render_template('room_management.html')

@app.route('/sift')
def shift_management():
    return render_template('sift_management.html')

if __name__ == '__main__':
    app.run(debug=True)