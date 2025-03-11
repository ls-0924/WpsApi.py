import requests

TOKEN_URL = "https://open.wps.cn/oauth2/v1/token"

data = {
    "client_id": "AK20250310BDSABY",
    "client_secret": "4c80859ee0cf79b6699f6c246bd99259",
    "grant_type": "authorization_code",
    "code": "AUTHORIZATION_CODE_FROM_CALLBACK",
    "redirect_uri": "http://47.109.45.56:9527/callback"  # 需与授权请求一致
}

response = requests.post(TOKEN_URL, data=data)
token_info = response.json()

# 提取 access_token 和 refresh_token
access_token = token_info.get("access_token")
refresh_token = token_info.get("refresh_token")