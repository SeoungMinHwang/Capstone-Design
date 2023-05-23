// OAuth.js 라는 컴포넌트를 따로 생성하여 관리하였음


const CLIENT_ID = "7257f938553965cf0ca3c2d561fd91d9";
const REDIRECT_URI =  "http://localhost:3000";

export const KAKAO_AUTH_URL = `https://kauth.kakao.com/oauth/authorize?client_id=7257f938553965cf0ca3c2d561fd91d9&redirect_uri=http://localhost:3000/oauth&response_type=code`;