import functools
import pymysql
import locale
import time
import json



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
def cctv_list(cursor):
    cursor.execute(f"""select placename from CCTV""")
    
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
    cursor.execute(f"""select A.eventid as 이벤트번호, B.placename as 장소, A.eventtime as 발생시간 from FALLEVENT A natural join CCTV B""")
    return cursor.fetchall()

# 로그인
@auto_conn_disconn
def get_password(cursor,id):
    cursor.execute(f"""select passwords from USERS where id = "{id}" """)
    password = cursor.fetchall()[0][0]
    return password

@auto_conn_disconn
def get_idlist(cursor):
    result = []
    cursor.execute(f"""select id from USERS""")
    for i in cursor.fetchall():
        result.append(i[0])
    return result

# 요일별 이벤트 갯수 출력 형식 : [요일,갯수]
@auto_conn_disconn
def event_per_day(cursor):
    result = [0,0,0,0,0,0,0]
    cursor.execute(f"""select DAYOFWEEK(eventtime), count(*) 
                   from FALLEVENT 
                   where eventtime between DATE_ADD(Now(), INTERVAL -1 WEEK) AND NOW()
                   group by DAYOFWEEK(eventtime)
                   order by DAYOFWEEK(eventtime) """)
    for i in cursor.fetchall():
        result[i[0]-1] = i[1]
    return result

# 월별 이벤트 개수
@auto_conn_disconn
def event_per_month(cursor):
    result = [0,0,0,0,0,0,0,0,0,0,0,0]
    cursor.execute(f"""select MONTH(eventtime), count(*)
                   from FALLEVENT
                   where eventtime between DATE_ADD(Now(), INTERVAL -1 YEAR) AND NOW()
                   group by MONTH(eventtime)
                   order by MONTH(eventtime) """)
    for i in cursor.fetchall():
        result[i[0] - 1] = i[1]
    return result

# 장소별 이벤트 비율
@auto_conn_disconn
def event_per_place(cursor):
    result = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    cursor.execute(f"""select CCTVid, count(*)
                   from FALLEVENT
                   group by CCTVid
                   order by CCTVid""")
    for i in cursor.fetchall():
        result[i[0]-1] = i[1]
    return result

@auto_conn_disconn
def map_list(cursor):
    result = []
    cursor.execute(f"""select placename, latitude, longitude from CCTV """)
    for i in cursor.fetchall():
        result.append([i[0],float(i[1]), float(i[2])])
    return result

# 이벤트로그 쿼리문
@auto_conn_disconn
def event_log(cursor):
    result = []
    cursor.execute(f"""select A.placename, B.eventtime, C.response, C.responsestate, C.droneid, B.sns
                   from (CCTV A natural join FALLEVENT B) left join RESPONSE C on B.eventid = C.eventid""")
    for i in cursor.fetchall():
        result.append([i[0], i[1].strftime('%Y-%m-%d %H:%M:%S'), i[2], i[3], i[4], i[5]])
    return result
                      

@auto_conn_disconn
def event_list(cursor, placename):
    result = []
    cursor.execute(f"""select eventtime, eventtype
                   from FALLEVENT
                   where cctvid in (select cctvid from CCTV where placename = "{placename}")
                   ORDER BY eventtime DESC
                   LIMIT 3 """)
    for i in cursor.fetchall():
        result.append([i[0].strftime('%Y-%m-%d %H:%M:%S'), i[1]])
    return result

@auto_conn_disconn
def drone_list(cursor):
    result = []
    cursor.execute(f"""select droneid, working, dronestate from DRONE """)
    for i in cursor.fetchall():
        result.append([i[0],i[1],i[2]])
    return result

@auto_conn_disconn
def drone_state(cursor):
    sql = '''select droneid, dronestate 
            from DRONE 
            WHERE droneid = 2 
            group by droneid, dronestate desc 
            limit 1;'''
    cursor.execute(sql)
    status_result = json.dumps(cursor.fetchall(), ensure_ascii=False)
    return status_result

@auto_conn_disconn
def droneStatus_log(cursor):
    sql = '''select dronestate, droneplace, working
            from DRONE;'''
    cursor.execute(sql)
    statuslog_result = json.dumps(cursor.fetchall(), ensure_ascii=False)
    return statuslog_result


# print(get_idlist())
