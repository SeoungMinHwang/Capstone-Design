import functools
import pymysql
import locale


# 데코레이터 정의 부분 
def auto_conn_disconn(original_func):
    @functools.wraps(original_func)
    def wrapper(*args, **kwargs):
        
        #이 곳에 쿼리 날리기전 커넥트 
        conn = pymysql.connect(host='orion.mokpo.ac.kr',port = 8391, user='remote', password='1234', db='capstone', charset='utf8')
        cursor = conn.cursor()
        
        
        #선언한 함수 실행 부분 
        query_result = original_func(cursor, *args, **kwargs)
        
        
        # 쿼리 날렸으니 커밋 후 디스 커넥트 
        conn.commit()
        conn.close()
        
        # 쿼리 결과 반환
        return query_result
        
    return wrapper    
    


@auto_conn_disconn
def show_drone(cursor):
    cursor.execute(f"""SELECT * FROM Drone""")
    
    print(cursor.fetchall())
    return cursor.fetchall()

@auto_conn_disconn
def cctv_list(cursor):
    cursor.execute(f"""select place from CCTV""")
    
    output = []
    for i in cursor.fetchall():
        output.append(i[0])
    
    return output

@auto_conn_disconn
def show_users(cursor):
    cursor.execute(f"""SELECT * FROM USERS""")
    
    print(cursor.fetchall())
    return cursor.fetchall()

# 이벤트번호, 장소, 발생시간 나오는 쿼리문
@auto_conn_disconn
def show_event(cursor):
    cursor.execute(f"""select A.eventid as 이벤트번호, B.place as 장소, A.eventtime as 발생시간 from Eventt A natural join CCTV B""")
    return cursor.fetchall()

# 로그인
@auto_conn_disconn
def get_password(cursor,id):
    cursor.execute(f"""select passwords from USERS where id = "{id}" """)
    password = cursor.fetchall()[0][0]
    return password

# select DAYOFWEEK(eventtime) as "요일",count(*) as "개수" from eventt group by DAYOFWEEK(eventtime);


# print(can_login("admin"))