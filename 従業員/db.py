import os, psycopg2, string, random, hashlib, mail

# postgresへの接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

# ソルトの生成
def get_salt():
    charset = string.ascii_letters + string.digits
    
    salt = ''.join(random.choices(charset, k=32))
    return salt

def get_hash(password, salt):
    b_pw = bytes(password, 'utf-8')
    b_salt = bytes(salt, 'utf-8')
    hashed_password = hashlib.pbkdf2_hmac('sha256', b_pw, b_salt, 1246).hex()
    return hashed_password

# ログイン
def login(email, password):
  sql = 'SELECT password, salt FROM employee WHERE mail = %s'
  flg = False
  try:
    connection=get_connection()
    cursor=connection.cursor()
    cursor.execute(sql, (email,))
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

def otp_login(email):
  sql = 'SELECT * FROM employee WHERE mail = %s'
  try:
    connection=get_connection()
    cursor=connection.cursor()
    cursor.execute(sql, (email,))
    one_time_pass=cursor.fetchone()
  finally:
    cursor.close()
    connection.close()
  return one_time_pass

# 新しい番号を生成する関数
def generate_new_number():
    while True:
        new_number = mail.generate_number()
        if not number_exists_in_database(new_number):
            return new_number

# 生成された番号が既にデータベースに存在するか確認する関数
def number_exists_in_database(number):
  sql = "SELECT COUNT(*) FROM employee WHERE one_time_pass = %s"
  connection = get_connection()
  cursor = connection.cursor()
  cursor.execute(sql, (number,))
  count = cursor.fetchone()[0]
  return count > 0

def update_number(number, email):
  sql = 'UPDATE employee SET one_time_pass = %s WHERE mail = %s'
  
  try :   # 例外処理
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(sql, (number, email))
    count = cursor.rowcount # 更新件数を取得
    connection.commit()

  except psycopg2.DatabaseError:    # Java でいう catch 失敗した時の処理をここに書く
    count = 0   # 例外が発生したら 0 を return する。

  finally:  # 成功しようが、失敗しようが、close する。
    cursor.close()
    connection.close()

  return count

def number_check(number):
  sql = 'SELECT * FROM employee WHERE one_time_pass = %s'
  try:
    connection=get_connection()
    cursor=connection.cursor()
    cursor.execute(sql, (number,))
    one_time_pass=cursor.fetchone()
  finally:
    cursor.close()
    connection.close()
    print(one_time_pass)
  return one_time_pass

def password_update(password, otp):
  sql = 'UPDATE employee SET salt = %s, password = %s, tp_flag = True WHERE one_time_pass = %s'
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

# 未清掃一覧
def noclean_2f_list():
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT room_id FROM guestroom WHERE status = 0 and floors = 2"
    
    cursor.execute(sql)
    rows = cursor.fetchall()
    
    cursor.close()
    connection.close()
    return rows
  
# 清掃開始
def request(room_number):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT room_id, request_nightwear, request_bathtowel, request_water, request_facetowel, request_tissue, request_tea, request_toiletpaper, request_slipperr, request_hairbrush, request_toothbrush,  content varchar FROM request WHERE room_id = %s"
    
    cursor.execute(sql, (room_number,))
    rows = cursor.fetchall()
    
    cursor.close()
    connection.close()
    return rows
  
# 客室状況
def room_status(room_number):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT status FROM guestroom WHERE room_id = %s"
    
    cursor.execute(sql, (room_number,))
    row = cursor.fetchone()
    
    print(row)
    
    cursor.close()
    connection.close()
    return row