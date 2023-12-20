import os, psycopg2, hashlib, string, random, mail

def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

# ランダムなソルトを生成
def get_salt():
  # 文字列の候補(英大小文字 + 数字)
  charset = string.ascii_letters + string.digits

  # charset からランダムに30文字取り出して結合
  salt = ''.join(random.choices(charset, k=30))
  return salt

# ソルトとPWからハッシュ値を生成
def get_hash(password, salt):
  b_pw = bytes(password, "utf-8")
  b_salt = bytes(salt, "utf-8")
  hashed_password = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 1000).hex()
  return hashed_password

def login(admin_id, password):
  sql = 'SELECT password, salt FROM admin WHERE id = %s'
  flg = False
  try:
    connection=get_connection()
    cursor=connection.cursor()
    cursor.execute(sql, (admin_id,))
    user=cursor.fetchone()
    if user != None:
      # SQLの結果からソルトを取得
      salt=user[1]
      
      # DBから取得したソルト + 入力したパスワード からハッシュ値を取得
      hashed_password=get_hash(password, salt)
      
      # 生成したハッシュ値とDBから取得したハッシュ値を比較する
      if hashed_password == user[0]:
        flg = True
  except psycopg2.DatabaseError:
    flg = False
  finally:
    cursor.close()
    connection.close()
  return flg

def otp_login(admin_id):
  sql = 'SELECT * FROM admin WHERE id = %s'
  try:
    connection=get_connection()
    cursor=connection.cursor()
    cursor.execute(sql, (admin_id,))
    one_time_pass=cursor.fetchone()
  finally:
    cursor.close()
    connection.close()
  return one_time_pass

def number_check(number):
  sql = 'SELECT * FROM admin WHERE one_time_pass = %s'
  try:
    connection=get_connection()
    cursor=connection.cursor()
    cursor.execute(sql, (number,))
    one_time_pass=cursor.fetchone()
  finally:
    cursor.close()
    connection.close()
  return one_time_pass

def update_number(number, mail):
  sql = 'UPDATE admin SET one_time_pass = %s WHERE mail = %s'
  
  try :   # 例外処理
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(sql, (number, mail))
    count = cursor.rowcount # 更新件数を取得
    connection.commit()

  except psycopg2.DatabaseError:    # Java でいう catch 失敗した時の処理をここに書く
    count = 0   # 例外が発生したら 0 を return する。

  finally:  # 成功しようが、失敗しようが、close する。
    cursor.close()
    connection.close()

  return count

def password_update(password, otp):
  sql = 'UPDATE admin SET salt = %s, password = %s, tp_flag = True WHERE one_time_pass = %s'
  salt = get_salt() # ソルトの生成
  hashed_password = get_hash(password, salt) # 生成したソルトでハッシュ
  
  try :   # 例外処理
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(sql, (salt, hashed_password, otp))
    count = cursor.rowcount # 更新件数を取得
    connection.commit()

  except psycopg2.DatabaseError:    # Java でいう catch 失敗した時の処理をここに書く
    count = 0   # 例外が発生したら 0 を return する。

  finally:  # 成功しようが、失敗しようが、close する。
    cursor.close()
    connection.close()

  return count

def insert_admin(admin_id, name, mail, otp):
  sql = 'INSERT INTO admin VALUES (%s, %s, %s, null, null, False, %s)'
  
  try :   # 例外処理
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(sql, (admin_id, name, mail, otp))
    count = cursor.rowcount # 更新件数を取得
    connection.commit()

  except psycopg2.DatabaseError:    # Java でいう catch 失敗した時の処理をここに書く
    count = 0   # 例外が発生したら 0 を return する。

  finally:  # 成功しようが、失敗しようが、close する。
    cursor.close()
    connection.close()

  return count

# 生成された番号が既にデータベースに存在するか確認する関数
def number_exists_in_database(number):
  sql = "SELECT COUNT(*) FROM admin WHERE one_time_pass = %s"
  connection = get_connection()
  cursor = connection.cursor()
  cursor.execute(sql, (number,))
  count = cursor.fetchone()[0]
  return count > 0

# 新しい番号を生成する関数
def generate_new_number():
    while True:
        new_number = mail.generate_number()
        if not number_exists_in_database(new_number):
            return new_number
          
def insert_emp(id, name, email, concat, otp):
  sql = 'INSERT INTO employee VALUES (%s, %s, %s, null, null, False, %s, False, %s)'
  
  try :   # 例外処理
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(sql, (id, name, email, concat, otp))
    count = cursor.rowcount # 更新件数を取得
    connection.commit()

  except psycopg2.DatabaseError:    # Java でいう catch 失敗した時の処理をここに書く
    count = 0   # 例外が発生したら 0 を return する。

  finally:  # 成功しようが、失敗しようが、close する。
    cursor.close()
    connection.close()

  return count

def all_employee():
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT * FROM employee"
    cursor.execute(sql,)
    rows = cursor.fetchall()
    return rows

def get_user_details(user_name):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT employee_id, name, mail FROM employee WHERE name = %s"
    cursor.execute(sql, (user_name,))
    user_details = cursor.fetchall()
    cursor.close()
    connection.close()
    return user_details
  

def employee_update(name, mail, concat, employee_id):
  sql = 'UPDATE employee SET name = %s, mail = %s, concat = %s, WHERE employee_id = %s'

def employee_delete(id):
  sql = 'UPDATE employee SET delete_flag = True WHERE employee_id = %s'
  
  try :   # 例外処理
    connection = get_connection()
    cursor = connection.cursor()


    cursor.execute(sql, (id))

    cursor.execute(sql, (id,))

    count = cursor.rowcount # 更新件数を取得
    connection.commit()

  except psycopg2.DatabaseError:    # Java でいう catch 失敗した時の処理をここに書く
    count = 0   # 例外が発生したら 0 を return する。

  finally:  # 成功しようが、失敗しようが、close する。
    cursor.close()
    connection.close()


  return count


def select_two_room():
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT room_id, floors, status FROM guestroom WHERE floors = 2"
    
    cursor.execute(sql)
    rows = cursor.fetchall()
    
    cursor.close()
    connection.close()
    return rows

