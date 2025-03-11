from urllib.parse import urlencode
import requests

# 定义授权所需的关键信息
CLIENT_ID = "AK20250310BDSABY"
CLIENT_SECRET = "4c80859ee0cf79b6699f6c246bd99259"
AUTH_URL = "https://open.wps.cn/oauth2/v1/authorize"
TOKEN_URL = "https://open.wps.cn/oauth2/v1/token"
REDIRECT_URI = "http://47.109.45.56:9527/callback"

# 构建授权请求的 URL
def get_authorization_url():
    auth_params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "user_info"
    }
    auth_request_url = f"{AUTH_URL}?{urlencode(auth_params)}"
    print(f"生成的授权 URL: {auth_request_url}")
    return auth_request_url

# 使用授权码换取访问令牌
def exchange_code_for_token(authorization_code):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(TOKEN_URL, data=data)
    token_info = response.json()
    return token_info

# 使用访问令牌访问受保护的资源
def access_protected_resource(access_token):
    RESOURCE_URL = "https://open.wps.cn/api/user_info"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    resource_response = requests.get(RESOURCE_URL, headers=headers)
    resource_data = resource_response.json()
    return resource_data

if __name__ == "__main__":
    # 第一步：获取授权 URL
    auth_url = get_authorization_url()
    print(f"请将用户重定向到以下 URL 进行授权：{auth_url}")

    # 第二步：从用户输入获取授权码
    authorization_code = input("请输入从回调 URL 中获取到的授权码：")

    # 第三步：用授权码换取访问令牌
    token_info = exchange_code_for_token(authorization_code)
    access_token = token_info.get("access_token")
    refresh_token = token_info.get("refresh_token")
    print(f"访问令牌：{access_token}")
    print(f"刷新令牌：{refresh_token}")

    # 第四步：使用访问令牌访问受保护的资源
    if access_token:
        resource_data = access_protected_resource(access_token)
        print(f"受保护的资源数据：{resource_data}")