import os, psycopg2

def get_connection():
    url = os.environ['DATABASE_URL']
    conneciton = psycopg2.connect(url)
    return conneciton

def insert_evaluation(evaluation,check_nightwear,check_slippers,check_garbage,check_towel,content):
    sql = "INSERT INTO questionnaire VALUES(default,,, %s, %s, %s, %s, %s,%s, current_timestamp)"
    try :
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql,(evaluation,check_nightwear,check_slippers,check_garbage,check_towel,content))
        count = cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()
    return count

def insert_request(request_nightwear,request_bathtowel,request_water,request_facetowel,request_tissue,request_tea,request_toiletpaper,request_slipperr,request_hairbrush,request_toothbrush,content):
    sql = "INSERT INTO request VALUES(default,,, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, current_timestamp)"
    try :
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql,(request_nightwear,request_bathtowel,request_water,request_facetowel,request_tissue,request_tea,request_toiletpaper,request_slipperr,request_hairbrush,request_toothbrush,content))
        count = cursor.rowcount
        connection.commit()
    except psycopg2.DatabaseError:
        count = 0
    finally:
        cursor.close()
        connection.close()
    return count