from sqlalchemy import Column, String, Integer, LargeBinary, Boolean, DateTime, func
from app.core.config import Base

# ---------------- Participant Model ----------------
class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(120), unique=False)
    meeting_id = Column(String(50), index=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

# ---------------- Meeting Model ----------------
class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(255))
    speaker = Column(String(100))  # The user who initiated the meeting
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

# ---------------- Meeting Audio Model ----------------
class MeetingAudio(Base):
    __tablename__ = "meeting_audio"
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(String(50), index=True)
    audio_format = Column(String(10), default="webm")  # Format hint for processing
    audio_data = Column(LargeBinary)  # Raw binary data (BLOB)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
