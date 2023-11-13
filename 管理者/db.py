import os, psycopg2, hashlib, string, random

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