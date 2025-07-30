# browsing_history

Reusable Python module to store browsing history using SQLAlchemy and Pydantic.

## Usage

```python
from browsing_history import store_browsing_history, BrowsingHistoryInput

store_browsing_history(db, BrowsingHistoryInput(
    user_id=123,
    page_url="/profile",
    page_title="Profile Page",
    ip_address="192.168.1.1",
    device_info="Chrome on Windows"
))
