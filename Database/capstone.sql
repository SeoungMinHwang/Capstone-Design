DROP DATABASE IF EXISTS capstone;
create database capstone;

use capstone;

#cctv테이블
CREATE TABLE CCTV(
CCTVid			INTEGER PRIMARY KEY,
place			VARCHAR(20) NOT NULL,
ip				VARCHAR(20) NOT NULL,
subnetip		VARCHAR(20) NOT NULL
);

#이벤트테이블
CREATE TABLE Eventt(
eventid			INTEGER PRIMARY KEY,
CCTVid			INTEGER,
eventtime		datetime,

FOREIGN KEY (CCTVid) REFERENCES CCTV(CCTVid)
);
# str_to_date("2022-04-28 17:00",'%Y-%m-%d %H:%i')

#대응 상황 테이블
CREATE TABLE Response(
eventid			INTEGER,
state			VARCHAR(20),

PRIMARY KEY(eventid, state),
FOREIGN KEY (eventid) REFERENCES Eventt(eventid)
);

#드론 테이블
CREATE TABLE Drone(
droneid			INTEGER PRIMARY KEY,
dronestate		VARCHAR(20),
eventid			INTEGER,

FOREIGN KEY (eventid) REFERENCES Response(eventid)
);

#동영상 링킹 테이블
CREATE TABLE VideoLink(
videoid			INTEGER PRIMARY KEY,
cctvid			INTEGER,
videotime		datetime NOT NULL,

UNIQUE(cctvid, videotime),
FOREIGN KEY (cctvid) REFERENCES CCTV(cctvid)
); 

#시스템 이벤트 테이블
CREATE TABLE Systemevent(
seventid		INTEGER	PRIMARY KEY,
eventname		VARCHAR(20),
eventstate		VARCHAR(20)
);