// 확인 사이트 https://makemonument.tistory.com/119

var express = require("express");

var request = require('request');

var app = express();
var port = 5000;

var optionsSmartLamp = {
   uri : "http://PC서버ip주소:포트번호/smartLamp",
   method : "GET",
   headers : { "Content-Type" : "application/x-www-form-urlencoded"}
};

app.get('/', function(req,res) {
   console.log('smart void lamp');
   res.send('Smart Voice Lamp');
});

app.listen(port,function() {
   console.log("create Server");

   //1초마다 smartLamp 함수 호출
   setInterval(smartLamp,1000);
});

function smartLamp() {
   //GET 요청 전송
   request(optionsSmartLamp, function(error, response, body) {
      if(body == "empty" ) {
         console.log("no data");
      }
      else {
         console.log(body);
      }
   });
}