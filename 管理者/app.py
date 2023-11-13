from flask import Flask, render_template, request, redirect, url_for, session
import db, string, random

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    msg = request.args.get('msg')   # Redirect された時のパラメータ受け取り

    if msg == None:
        # 通常のアクセスの場合
        return render_template('index.html')
    else :
        # register_exe() から redirect された場合
        return render_template('index.html', msg=msg)

@app.route('/', methods=['POST'])
def login():
    admin_id = request.form.get('adminid')
    password = request.form.get('password')
    
    # ログイン判定
    if db.login(admin_id, password):
        session['user'] = True
        return redirect(url_for('menu'))
    
    else:
        error = 'ユーザ名またはパスワードが違います。'
        
        # dictで返すことでフォームの入力量が増えても可読性が下がらない。
        input_data={'admin_id':admin_id, 'password':password}
        return render_template('index.html', error=error, data=input_data)
    
@app.route('/logout')
def logout():
    session.pop('user', None)   # sessionの破棄
    return redirect(url_for('index'))   # ログイン画面にリダイレクト    

if __name__ == '__main__':
    app.run(debug=True)