"""資料庫模型定義（SQLAlchemy ORM）"""

from datetime import datetime, timezone, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base

# 台北時區（UTC+8）
tz_taipei = timezone(timedelta(hours=8), "Asia/Taipei")

# 取得當前台北時間（忽略時區資訊，存入 naive datetime）
_naive_now = lambda: datetime.now(tz_taipei).replace(tzinfo=None)


class Member(Base):
    """會員資料表"""
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)             # 會員編號（主鍵）
    email = Column(String(255), unique=True, nullable=False, index=True)  # 登入帳號（Email，唯一）
    password_hash = Column(String(255), nullable=False)            # 密碼雜湊值
    display_name = Column(String(100), nullable=False)             # 顯示名稱
    gender = Column(String(10), default="")                        # 性別
    age = Column(String(10), default="")                           # 年齡
    zodiac = Column(String(10), default="")                        # 星座
    occupation = Column(String(100), default="")                   # 職業
    city = Column(String(100), default="")                         # 居住縣市
    district = Column(String(100), default="")                     # 居住區域
    interests = Column(String(500), default="")                    # 興趣（逗號分隔）
    preferred_cuisine = Column(String(500), default="")            # 偏好料理（逗號分隔）
    bio = Column(Text, default="")                                 # 自我介紹
    created_at = Column(DateTime, default=_naive_now)              # 註冊時間

    # 一對多關聯：會員 → 建立的活動
    activities = relationship("Activity", back_populates="organizer")
    # 一對多關聯：會員 → 提出的申請
    applications = relationship("Application", back_populates="member")


class Activity(Base):
    """活動資料表"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)             # 活動編號（主鍵）
    organizer_id = Column(Integer, ForeignKey("members.id"), nullable=False)  # 發起人（外鍵）
    title = Column(String(200), nullable=False)                    # 活動名稱
    description = Column(Text, default="")                         # 活動說明
    category = Column(String(50), nullable=False)                  # 活動分類
    city = Column(String(100), nullable=False)                     # 活動城市
    location_name = Column(String(200), nullable=False)            # 活動地點
    activity_date = Column(DateTime, nullable=False)               # 活動時間
    deadline = Column(DateTime, nullable=False)                    # 報名截止時間
    max_participants = Column(Integer, nullable=False)             # 人數上限
    image_url = Column(String(500), default="")                    # 封面圖片網址
    status = Column(String(20), default="open")                    # 活動狀態（open/closed）
    created_at = Column(DateTime, default=_naive_now)              # 建立時間

    # 多對一關聯：活動 → 發起人
    organizer = relationship("Member", back_populates="activities")
    # 一對多關聯：活動 → 申請（連帶刪除）
    applications = relationship("Application", back_populates="activity", cascade="all, delete-orphan")
class Application(Base):
    """活動申請資料表"""
    __tablename__ = "applications"
    # 唯一限制：同一會員不可重複申請同一活動
    __table_args__ = (UniqueConstraint("activity_id", "member_id", name="uq_activity_member"),)

    id = Column(Integer, primary_key=True, index=True)             # 申請編號（主鍵）
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)  # 活動（外鍵）
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)       # 申請人（外鍵）
    message = Column(Text, default="")                             # 申請留言
    status = Column(String(20), default="pending")                 # 狀態（pending/approved/rejected/cancelled）
    created_at = Column(DateTime, default=_naive_now)              # 申請時間

    # 多對一關聯：申請 → 活動
    activity = relationship("Activity", back_populates="applications")
    # 多對一關聯：申請 → 會員
    member = relationship("Member", back_populates="applications")



