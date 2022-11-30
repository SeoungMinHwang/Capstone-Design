import json
import requests

# 친구 uuid 가져오기
def getuuidList(token):
    """
    친구 uuid 가져오기 함수
    메시지 보내는 함수에서 uuid가져오는데 사용
    """

    header = {"Authorization": 'Bearer ' + token}
    url = "https://kapi.kakao.com/v1/api/talk/friends" #친구 정보 요청

    result = json.loads(requests.get(url, headers=header).text)

    friends_list = result.get("elements")
    friends_id = []

    for friend in friends_list:
        friends_id.append(str(friend.get("uuid")))

    return friends_id

# 카카오톡 보내는 함수
def sendToMeMessage(token,text):
    """
    카카오톡 보내는 함수
    매개변수 : 토큰, 메시지
    출력 200나오면 전송 성공, 400 나오면 오류, 401 나오면 권한없음
    """
    def getuuidList(token):
        """
        친구 uuid 가져오기 함수
        메시지 보내는 함수에서 uuid가져오는데 사용
        """

        header = {"Authorization": 'Bearer ' + token}
        url = "https://kapi.kakao.com/v1/api/talk/friends" #친구 정보 요청

        result = json.loads(requests.get(url, headers=header).text)

        friends_list = result.get("elements")
        friends_id = []

        for friend in friends_list:
            friends_id.append(str(friend.get("uuid")))

        return friends_id
    
    header = {"Authorization": "Bearer " + token}
    url = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send" #api 주소
    uuid = getuuidList(token)
    uuidsData = {"receiver_uuids" : json.dumps(uuid)}    

    post = {
        "object_type": "text",
        "text" : text,
        "link" : {
        },
    }
    data = {"template_object": json.dumps(post)}
    uuidsData.update(data)

    return requests.post(url, headers=header, data=uuidsData).status_code