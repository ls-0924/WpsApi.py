import time  # 必须导入用于处理时间戳
import os
import requests
from flask import Flask, request, redirect, session
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))  # 生产环境应使用固定密钥

# ============ 配置信息 ============
CLIENT_ID = os.getenv("WPS_CLIENT_ID", "AK20250310BDSABY")        # 默认测试ID
CLIENT_SECRET = os.getenv("WPS_CLIENT_SECRET")                    # 必须从环境变量获取
REDIRECT_URI = "http://47.109.45.56:9527/callback"               # 需与WPS控制台配置一致
TOKEN_URL = "https://open.wps.cn/oauth2/v1/token"
USER_INFO_URL = "https://open.wps.cn/oauthapi/v1/user"

# ============ 模拟数据库 ============
tokens_db = {}  # 生产环境需替换为真实数据库

def save_tokens(user_id, access_token, refresh_token, expires_in):
    """存储令牌及过期时间"""
    tokens_db[user_id] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": time.time() + expires_in - 60  # 提前60秒过期
    }

def get_tokens(user_id):
    """获取用户令牌"""
    return tokens_db.get(user_id, None)

# ============ 路由定义 ============
@app.route('/')
def index():
    """首页重定向到登录"""
    return redirect('/login')

@app.route('/login')
def login():
    """模拟登录并跳转WPS授权"""
    # 实际应在此处实现用户认证逻辑
    session['user_id'] = "test_user_001"  # 模拟用户ID

    # 构造WPS授权地址
    auth_url = (
        f"https://open.wps.cn/oauth2/v1/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
    )
    return redirect(auth_url)

@app.route('/callback')
def oauth_callback():
    """处理OAuth回调"""
    # 错误处理
    if request.args.get('error'):
        return f"授权失败: {request.args.get('error_description')}", 400

    # 获取授权码
    auth_code = request.args.get('code')
    if not auth_code:
        return "缺少授权码参数", 400

    # 交换访问令牌
    try:
        response = requests.post(
            TOKEN_URL,
            data={
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': REDIRECT_URI
            },
            auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
            timeout=15
        )
        response.raise_for_status()
        token_data = response.json()
    except requests.exceptions.RequestException as e:
        return f"令牌获取失败: {str(e)}", 500

    # 存储令牌
    user_id = session.get('user_id')
    if not user_id:
        return "会话失效，请重新登录", 401

    save_tokens(
        user_id,
        token_data['access_token'],
        token_data['refresh_token'],
        token_data['expires_in']
    )
    return redirect('/user_info')

def refresh_access_token(user_id):
    """刷新访问令牌"""
    tokens = get_tokens(user_id)
    if not tokens or 'refresh_token' not in tokens:
        return None

    try:
        response = requests.post(
            TOKEN_URL,
            data={
                'grant_type': 'refresh_token',
                'refresh_token': tokens['refresh_token']
            },
            auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
            timeout=15
        )
        response.raise_for_status()
        new_tokens = response.json()

        # 更新令牌（注意可能返回新的refresh_token）
        save_tokens(
            user_id,
            new_tokens['access_token'],
            new_tokens.get('refresh_token', tokens['refresh_token']),  # 保留旧refresh_token如果未返回新的
            new_tokens['expires_in']
        )
        return new_tokens['access_token']
    except requests.exceptions.RequestException:
        return None

@app.route('/user_info')
def get_user_info():
    """获取用户信息（带自动令牌刷新）"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    tokens = get_tokens(user_id)
    if not tokens:
        return "未找到令牌信息", 401

    # 检查令牌是否过期
    if time.time() > tokens['expires_at']:
        new_token = refresh_access_token(user_id)
        if not new_token:
            return "令牌刷新失败", 401
        access_token = new_token
    else:
        access_token = tokens['access_token']

    # 请求用户信息
    try:
        response = requests.get(
            USER_INFO_URL,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"API请求失败: {str(e)}", 500

@app.route('/favicon.ico')
def handle_favicon():
    """避免浏览器请求favicon报错"""
    return '', 204

if __name__ == '__main__':
    # 生产环境应使用生产服务器（如gunicorn）
    app.run(host='0.0.0.0', port=9527, debug=True)