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

# dashboard 맵 쿼리
@auto_conn_disconn
def event_per_placeday(cursor):
    result = []
    cctv = cctv_list()
    for i in cctv:
        cursor.execute(f"""select latitude, longitude, count(*)
                        from FALLEVENT natural join CCTV
                        where (DATE_FORMAT(eventtime, "%Y-%m-%d") = CURDATE()) AND (placename = "{i}") """)
        tmp = cursor.fetchall()[0]
        result.append([i, tmp[0], tmp[1], tmp[2]])
    for i in range(len(result)):
        if result[i][1] == None:
            cursor.execute(f"""select latitude, longitude
                            from CCTV
                            where placename = "{result[i][0]}" """)
            tmp = cursor.fetchall()[0]
            result[i][1] = tmp[0]
            result[i][2] = tmp[1]
    return result

@auto_conn_disconn
def map_list(cursor):
    result = []
    cursor.execute(f"""select placename, latitude, longitude, place, placegruop, ip, working from CCTV """)
    for i in cursor.fetchall():
        result.append([i[0],float(i[1]), float(i[2]), i[3], i[4], i[5], i[6]])
    return result

# 이벤트로그 쿼리문
@auto_conn_disconn
def event_log(cursor):
    result = []
    cursor.execute(f"""select A.placename, B.eventtime, C.response, B.responsestate, C.droneid, B.sns
                   from (CCTV A natural join FALLEVENT B) left join RESPONSE C on B.eventid = C.eventid""")
    for i in cursor.fetchall():
        result.append([i[0], i[1].strftime('%Y-%m-%d %H:%M:%S'), i[2], i[3], i[4], i[5]])
    return result

@auto_conn_disconn
def last_event(cursor):
    cursor.execute(f"""select placename from FALLEVENT natural join CCTV order by eventtime DESC LIMIT 1""")
    return cursor.fetchall()[0][0]
                      

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
            WHERE droneid = 1 
            group by droneid, dronestate desc 
            limit 1;'''
    cursor.execute(sql)
    status_result = json.dumps(cursor.fetchall(), ensure_ascii=False)
    return status_result

@auto_conn_disconn
def update_drone_state(cursor):
    sql = '''UPDATE DRONE SET dronestate= '출동중' WHERE droneid = 1;'''
    cursor.execute(sql)
    return

@auto_conn_disconn
def droneStatus_log(cursor):
    sql = '''select droneid, dronestate, droneplace, working
            from DRONE
            WHERE droneplace = '목포대학교';'''
    cursor.execute(sql)
    statuslog_result = json.dumps(cursor.fetchall(), ensure_ascii=False)
    return statuslog_result


# detail화면 테이블을 위한 쿼리문
@auto_conn_disconn
def detail_list(cursor, placename):
    result = []
    cursor.execute(f"""select eventtime, responsestate, sns from (FALLEVENT natural join CCTV) WHERE placename="{placename}" ORDER BY eventtime DESC;
 """)
    for i in cursor.fetchall():
        result.append([i[0].strftime('%Y-%m-%d %H:%M:%S'),i[1],i[2]])
    return result

# detail 화면 지도를 위한 쿼리문
@auto_conn_disconn
def detail_place(cursor, placename):
    cursor.execute(f"""select latitude, longitude from CCTV where placename="{placename}" """)
    return cursor.fetchall()[0]

# 프로필을 위한 쿼리문
@auto_conn_disconn
def user_info(cursor, id):
    cursor.execute(f"""select id, fame, phonenumber, email from USERS where id = "{id}" """)
    return cursor.fetchall()[0]

@auto_conn_disconn
def user_access(cursor, id):
    cursor.execute(f"""select access from USERS where id = "{id}" """)
    return cursor.fetchall()[0]

@auto_conn_disconn
def cctv_insert(cursor, lat, lng, address, placename, placegruop, ip, working):
    cursor.execute(f"""insert into CCTV values(null, "{lat}", "{lng}","{address}", "{placename}","{placegruop}","{ip}","{working}") """)
    return

@auto_conn_disconn
def cctv_delete(cursor,placename):
    cursor.execute(f"""delete from CCTV where placename="{placename}" """)
    return

# print(last_event())