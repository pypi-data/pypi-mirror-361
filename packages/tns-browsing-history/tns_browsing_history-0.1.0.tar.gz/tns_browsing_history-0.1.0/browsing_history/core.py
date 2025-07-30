from .models import BrowsingHistory
from .schemas import BrowsingHistoryInput
from sqlalchemy.orm import Session

def store_browsing_history(db: Session, data: BrowsingHistoryInput):
    entry = BrowsingHistory(**data.dict())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
