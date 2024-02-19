from pydantic import BaseModel
from datetime import datetime

class ItemResponse(BaseModel):
    id: str

class DateRangeInput(BaseModel):
    dt_from: datetime
    dt_to: datetime

class CategoryInput(BaseModel):
    category: str