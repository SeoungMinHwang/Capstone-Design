use capstone;

/*

*/
delimiter //
CREATE PROCEDURE EventInsert(
  myCCTVid INTEGER, 
  myEventTime datetime
  ) 
BEGIN
  INSERT INTO eventt values(null,myCCTVID,date_format(now(),'%Y-%m-%d %H:%i'));
END;
//
delimiter ;