from pydantic import BaseModel
from typing import Optional

class BrowsingHistoryInput(BaseModel):
    user_id: int
    page_url: str
    page_title: Optional[str] = None
    ip_address: Optional[str] = None
    device_info: Optional[str] = None
