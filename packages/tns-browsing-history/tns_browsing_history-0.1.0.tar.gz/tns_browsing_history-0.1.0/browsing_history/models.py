from sqlalchemy import Column, BigInteger, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BrowsingHistory(Base):
    __tablename__ = "browsing_history"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    page_url = Column(Text, nullable=False)
    page_title = Column(String(255))
    ip_address = Column(String(50))
    device_info = Column(String(255))
    visited_at = Column(DateTime(timezone=True), server_default=func.now())
