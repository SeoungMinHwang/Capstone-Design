테이블
1. CCTV : CCTV 테이블(cctvid(pk), place, ip, subnetip) = (cctvid, 장소, ip, 서브넷아이피)
2. Eventt : 이벤트 테이블(eventid(pk), cctvid(fk), eventtime) = (이벤트id, cctvid, 이벤트발생시간)
3. Response : 대응상황 테이블(eventid(pk), state(pk)) = (이벤트id, 상태)
4. Drone : 드론 테이블(droneid(pk), dronestate) = (드론id, 드론상태)
5. Videolink : 비디오 링킹 테이블(videoid(pk), cctvid(fk), videotime) = (비디오id, cctvid, 비디오시간)
6. Systemevent : 시스템 이벤트 테이블(Seventid(pk), eventname, eventstate) = (시스템이벤트id, 이벤트명, 이벤트상황)
7. DroneEvent : 드론 이벤트 테이블(droneid(fk), eventid(fk)) -> 모두가 기본키
