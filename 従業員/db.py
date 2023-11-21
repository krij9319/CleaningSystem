import os, psycopg2, string, random, hashlib

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
def login(mail, password):
    sql = "SELECT salt, password FROM employee WHERE mail = %s"
    flg = False
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(sql, (mail))
        emp = cursor.fetchone()
        
        if emp != None:
            salt = emp[1]
            
            hashed_password = get_hash(password, salt)
            
            if hashed_password == emp[0]:
                flg = True
    
    except psycopg2.DatabaseError:
        flg = False
    
    finally:
        cursor.close()
        connection.close()
    
    return flg

# otp更新
def update_otp(otp, email):
    sql = 'UPDATE employee SET otp = %s WHERE mail = %s'
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(sql, (otp, email))
        count = cursor.rowcount
        connection.commit()
    
    except psycopg2.DatabaseError:
        count = 0
    
    finally:
        cursor.close()
        connection.close()
    
    return count