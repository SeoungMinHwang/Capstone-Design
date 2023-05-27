import json
import requests

# # 친구 uuid 가져오기
# def getuuidList(token):
#     """
#     친구 uuid 가져오기 함수
#     메시지 보내는 함수에서 uuid가져오는데 사용
#     """
def f_auth():
    url = 'https://kauth.kakao.com/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': "7257f938553965cf0ca3c2d561fd91d9",
        'redirect_uri': "http://localhost:3000/oauth",
        'code': "mHm2BwvHAi_ABGZzWuoxvT_l7v4exyXzWsjSkXIcdBkdP6yLOM4CFqFewabsRiM2SMH9uwo9dZoAAAGIR59D2w",
    }

    response = requests.post(url, data=data)
    tokens = response.json()

    with open("kakao_code.json", "w") as fp:
        json.dump(tokens, fp)
    with open("kakao_code.json", "r") as fp:
        ts = json.load(fp)
    r_token = ts["refresh_token"]
    return r_token

def f_auth_refresh(r_token):
    url = 'https://kauth.kakao.com/oauth/token'
    with open("kakao_code.json", "r") as fp:
        ts = json.load(fp)
    data = {
        "grant_type": "refresh_token",
        "client_id": "7257f938553965cf0ca3c2d561fd91d9",
        "refresh_token": r_token
    }
    response = requests.post(url, data=data)
    tokens = response.json()

    with open("kakao_code.json", "w") as fp:
        json.dump(tokens, fp)
    with open("kakao_code.json", "r") as fp:
        ts = json.load(fp)
    token = ts["access_token"]
    return token

# 카카오톡 보내는 함수
def sendToMeMessage(text):
    """
    카카오톡 보내는 함수
    매개변수 : 토큰, 메시지
    출력 200나오면 전송 성공, 400 나오면 오류, 401 나오면 권한없음
    """
    r_token = 'L7q-oPZvg0jGjMgPY54x0g5C0CIF_zW183gs6KcsCj10mQAAAYhHn9wV'
    token = f_auth_refresh(r_token) 
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


sendToMeMessage("시발 이거 왜 안돼")