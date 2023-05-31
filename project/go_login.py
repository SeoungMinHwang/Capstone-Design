import hashlib

def hash_password(s):
    """
    Password를 sha-256을 통해 해시함수를 만드는 함수
    패스워드를 파라미터로 넘겨주면 sha-256값으로 넘어옴
    """
    hash_object = hashlib.sha256()
    hash_object.update(s.encode())
    result = hash_object.hexdigest()
    
    return result