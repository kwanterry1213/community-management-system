from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    email: str
    phone: Optional[str] = None
    username: str
    profile_picture: Optional[str] = None
    bio: Optional[str] = None

    class Config:
        from_attributes = True
        extra = 'ignore' # Verify if this is default or needed

try:
    data = {
        "id": 1,
        "email": "test@test.com",
        "username": "test",
        "hashed_password": "secret_hash", # Extra field
        "created_at": "2023-01-01" # Extra field
    }
    user = User(**data)
    print("Validation Success:", user)
except Exception as e:
    print("Validation Failed:", e)

# Now test without explicit class Config extra='ignore' (simulating current app.py)
class UserDefault(BaseModel):
    id: int
    email: str
    username: str

    class Config:
        orm_mode = True

try:
    user_def = UserDefault(**data)
    print("Default Validation Success:", user_def)
except Exception as e:
    print("Default Validation Failed:", e)
