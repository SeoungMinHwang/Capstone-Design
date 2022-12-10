# Daum에서 지역을 지정해 검색한 날씨 정보를 추출하는 코드
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import schedule

# 날씨를 알고 싶은 지역 입력 
# ex) input: 광주 서구 금호동, 전남 무안군 청계면 
def get_weather_daum(location):
    
    search_query = location + " 날씨"
    search_url = "https://search.daum.net/search?w=tot&DA=YZR&t__nil_searchbox=btn&sug=&sugo=&sq=&o=&q="
    url = search_url + search_query
    html_weather = requests.get(url).text
    time.sleep(2)
    soup_weather = BeautifulSoup(html_weather, "lxml")
    
    txt_temp = soup_weather.select_one('strong.txt_temp').get_text()
    txt_weather = soup_weather.select_one('span.txt_weather').get_text()
    
    dl_weather_dds = soup_weather.select('dl.dl_weather dd')
    wind_speed, humidity, pm10 = [x.get_text() for x in dl_weather_dds]
    
    return (txt_temp, txt_weather, wind_speed, humidity, pm10)

# 날씨를 알고 싶은 지역 입력
def job(location):
    now = datetime.now()
    print("[작업 수행 시각] {:%H:%M:%S}".format(now))
    # location = "전남 무안군 청계면"
    
    (txt_temp, txt_weather, wind_speed, humidity, pm10) = get_weather_daum(location)

    print("-------[오늘의 날씨 정보] (Daum) ----------")
    print(f'- 설정 지역: {location}')
    print(f'- 기온: {txt_temp}')
    print(f'- 날씨 정보: {txt_weather}')
    print(f'- 현재 풍속: {wind_speed}, 현재 습도: {humidity}, 미세 먼저: {pm10}')


# Test 
if __name__ == "__main__":
    # 처음 한번은 먼저 가져와야함
    location = "전라남도 무안군 청계면"
    job(location)
    # 1시간 마다 Update
    schedule.every(1).hour.do(job, location)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except:
            print("작업 강제 종료")
            schedule.clear()
            break
