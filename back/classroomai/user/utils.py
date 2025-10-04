# user/utils.py
import json, time, requests, requests_cache, os
import jwt
from jwt import InvalidTokenError
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request  # ← 用这个
from google.auth.exceptions import RefreshError

# 用快取避免每次打 LINE 取 JWK
sess = requests_cache.CachedSession("line_jwks", expire_after=3600)


def verify_line_id_token(id_token: str) -> dict:
    """
    驗證 LINE LIFF 的 id_token：
    1. 取 header.kid -> 對應 JWK
    2. 依 kty = RSA / EC 轉換成公鑰
    3. jwt.decode 驗簽 + 驗 iss / aud / exp
    """
    try:
        header = jwt.get_unverified_header(id_token)
        jwks = sess.get("https://api.line.me/oauth2/v2.1/certs").json()["keys"]
        key_dict = next(k for k in jwks if k["kid"] == header["kid"])

        # --- 依金鑰類型轉換 ---
        if key_dict["kty"] == "RSA":
            pub_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_dict))
            allowed_algs = ["RS256"]
        elif key_dict["kty"] == "EC":
            pub_key = jwt.algorithms.ECAlgorithm.from_jwk(json.dumps(key_dict))
            allowed_algs = ["ES256"]
        else:
            raise ValidationError("Unsupported JWK key type")

        payload = jwt.decode(
            id_token,
            key=pub_key,
            algorithms=allowed_algs,
            issuer="https://access.line.me",
            audience=settings.LINE_CHANNEL_ID,
        )
        return payload  # payload["sub"] 即 LINE USER ID

    except (InvalidTokenError, StopIteration, KeyError) as e:
        raise ValidationError(f"LINE id_token 驗證失敗: {e}")
    

def get_valid_google_credentials(profile):
    """
    獲取有效的 Google 憑證，自動處理 token 刷新
    """
    try:
        # 檢查是否有必要的憑證
        if not profile.google_access_token or not profile.google_refresh_token:
            raise Exception("缺少 Google OAuth 憑證，需要重新授權")
        
        creds = Credentials(
            token=profile.google_access_token,
            refresh_token=profile.google_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        )

        # 如果還沒設定 expiry，或已過期／快過期，就自動刷新
        if creds.expiry is None or creds.expired or creds.expiry <= timezone.now() + timedelta(minutes=3):
            try:
                print(f"正在自動刷新 Google token (用戶: {profile.line_user_id})")
                creds.refresh(Request())
                
                # 確保 expiry 是時區感知的 datetime
                expiry = creds.expiry
                if expiry.tzinfo is None:
                    import pytz
                    expiry = timezone.make_aware(expiry, pytz.UTC)
                
                # 自動更新 profile 中的 tokens
                profile.google_access_token = creds.token
                profile.google_token_expiry = expiry
                profile.save(update_fields=["google_access_token", "google_token_expiry"])
                print(f"✅ 已自動刷新並保存 Google token (用戶: {profile.line_user_id})")
                
            except (RefreshError, Exception) as e:
                err_text = str(e)
                print(f"❌ 自動刷新失敗 (用戶: {profile.line_user_id}): {err_text}")
                # 若遭遇 invalid_grant 代表 refresh token 已失效/被撤銷，需要重新授權
                if "invalid_grant" in err_text or "invalid_client" in err_text:
                    # 清空憑證，避免之後持續嘗試
                    profile.google_access_token = None
                    profile.google_refresh_token = None
                    profile.google_token_expiry = None
                    profile.save(update_fields=[
                        "google_access_token",
                        "google_refresh_token",
                        "google_token_expiry",
                    ])
                    raise Exception("Google OAuth Token 已失效或被撤銷，請重新授權")
                
                # 其他暫時性錯誤不回退到舊 token（通常亦已過期），直接要求重新授權
                raise Exception(f"Google OAuth Token 刷新失敗，請稍後重試或重新授權。錯誤: {err_text}")

        return creds
        
    except Exception as e:
        # 記錄錯誤並重新拋出
        print(f"Google 憑證獲取失敗 (用戶: {profile.line_user_id}): {str(e)}")
        raise
