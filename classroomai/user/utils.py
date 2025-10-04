# user/utils.py
import json, time, requests, requests_cache, os
import jwt
from jwt import InvalidTokenError
try:
    # PyJWT >= 2.x
    from jwt import PyJWKClient
except Exception:
    PyJWKClient = None
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
    - 以 PyJWKClient 自動解析 JWK，支援 RS256/ES256，避免 ECAlgorithm 缺失。
    - 驗證 iss/aud/exp，返回 payload。
    """
    try:
        # 優先使用 PyJWKClient（PyJWT 2.x），自動依 kid 拿到簽名金鑰
        signing_key = None
        if PyJWKClient is not None:
            jwk_client = PyJWKClient("https://api.line.me/oauth2/v2.1/certs")
            signing_key = jwk_client.get_signing_key_from_jwt(id_token).key
        else:
            # 兼容舊版 PyJWT：手動解析 JWK，僅保證 RSA；EC 需升級 PyJWT/cryptography
            header = jwt.get_unverified_header(id_token)
            jwks = sess.get("https://api.line.me/oauth2/v2.1/certs").json()["keys"]
            key_dict = next(k for k in jwks if k["kid"] == header["kid"])
            if key_dict.get("kty") == "RSA":
                signing_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_dict))
            else:
                raise ValidationError("LINE id_token 需要 PyJWT>=2.x 以支援 ES256，請升級依賴")

        # 先驗證簽名與 issuer，暫時關閉 aud 驗證，改為手動檢查以提供更清楚訊息
        payload = jwt.decode(
            id_token,
            key=signing_key,
            algorithms=["RS256", "ES256"],
            issuer="https://access.line.me",
            options={"verify_aud": False},
        )

        expected_aud = settings.LINE_CHANNEL_ID
        actual_aud = payload.get("aud")
        # aud 可能是字串或陣列
        def aud_matches(expected, actual):
            if actual is None:
                return False
            if isinstance(actual, str):
                return actual == expected
            if isinstance(actual, (list, tuple)):
                return expected in actual
            return False

        if not expected_aud:
            raise ValidationError("LINE_CHANNEL_ID 未設定，請在環境變數設定正確的 Channel ID")
        if not aud_matches(expected_aud, actual_aud):
            raise ValidationError(f"LINE id_token aud 不匹配：token={actual_aud}，backend={expected_aud}")

        return payload

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
