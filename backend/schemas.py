"""Pydantic 資料驗證模型（Schema）"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── 會員註冊 ──────────────────────────────────────────────
class MemberRegister(BaseModel):
    """會員註冊時的請求資料結構"""
    email: EmailStr                                      # 登入帳號（Email 格式驗證）
    password: str = Field(min_length=8)                  # 密碼（至少 8 碼）
    display_name: str = Field(min_length=1, max_length=100)  # 顯示名稱
    gender: str = ""                                     # 性別
    age: str = ""                                        # 年齡
    zodiac: str = ""                                     # 星座
    occupation: str = ""                                 # 職業
    city: str = ""                                       # 居住縣市
    district: str = ""                                   # 居住區域
    interests: str = ""                                  # 興趣
    preferred_cuisine: str = ""                          # 偏好料理


# ── 登入 ────────────────────────────────────────────────
class LoginRequest(BaseModel):
    """登入時的請求資料結構"""
    email: EmailStr
    password: str


# ── 會員資料更新 ──────────────────────────────────────────
class MemberUpdate(BaseModel):
    """更新會員個人資料的請求資料結構"""
    display_name: str = Field(min_length=1, max_length=100)
    gender: str = ""
    age: str = ""
    zodiac: str = ""
    occupation: str = ""
    city: str = ""
    district: str = ""
    interests: str = ""
    preferred_cuisine: str = ""
    bio: str = ""                                        # 自我介紹


# ── 會員回應 ──────────────────────────────────────────────
class Member(BaseModel):
    """會員資料的 API 回應結構"""
    model_config = ConfigDict(from_attributes=True)     # 允許從 ORM 物件轉換
    id: int
    email: EmailStr
    display_name: str
    gender: str = ""
    age: str = ""
    zodiac: str = ""
    occupation: str = ""
    city: str
    district: str = ""
    interests: str
    preferred_cuisine: str = ""
    bio: str
    created_at: datetime


# ── 登入回應 ──────────────────────────────────────────────
class LoginResponse(BaseModel):
    """登入成功後的回應資料結構"""
    member_id: int
    display_name: str


# ── 活動建立 ──────────────────────────────────────────────
class ActivityCreate(BaseModel):
    """建立活動的請求資料結構"""
    organizer_id: int                                    # 發起人會員編號
    title: str = Field(min_length=1, max_length=200)     # 活動名稱
    description: str = ""                                # 活動說明
    category: str                                        # 活動分類
    city: str                                            # 活動城市
    location_name: str                                   # 活動地點
    activity_date: datetime                              # 活動時間
    deadline: datetime                                   # 報名截止時間
    max_participants: int = Field(gt=0)                  # 人數上限（必須 > 0）
    image_url: str = ""                                  # 封面圖片網址


class ActivityUpdate(ActivityCreate):
    """更新活動的請求資料結構（與建立相同）"""
    pass


# ── 活動回應 ──────────────────────────────────────────────
class Activity(BaseModel):
    """活動資料的 API 回應結構"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    organizer_id: int
    organizer_name: str = ""                             # 發起人顯示名稱
    title: str
    description: str
    category: str
    city: str
    location_name: str
    activity_date: datetime
    deadline: datetime
    max_participants: int
    approved_count: int = 0                              # 已核准人數
    image_url: str
    status: str
    created_at: datetime
    my_application_id: Optional[int] = None
    my_application_status: Optional[str] = None


# ── 申請建立 ──────────────────────────────────────────────
class ApplicationCreate(BaseModel):
    """申請參加活動的請求資料結構"""
    member_id: int                                       # 申請人會員編號
    message: str = ""                                    # 申請留言


# ── 申請回應 ──────────────────────────────────────────────
class Application(BaseModel):
    """申請資料的 API 回應結構"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    activity_id: int
    member_id: int
    member_name: str = ""                                # 申請人顯示名稱
    activity_title: str = ""                             # 活動名稱
    message: str
    status: str
    created_at: datetime


# ── 推薦回應 ──────────────────────────────────────────────
class Recommendation(Activity):
    """推薦活動的回應結構（繼承 Activity，加上評分與原因）"""
    score: int                                           # 推薦分數
    reasons: list[str]                                   # 推薦原因列表
