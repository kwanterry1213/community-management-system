import streamlit as st
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from passlib.context import CryptContext
import shutil
import secrets
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from jose import JWTError, jwt
from datetime import datetime, timedelta

# --- Database Setup ---
DATABASE_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "community_app.db")

def get_db():
    db = sqlite3.connect(DATABASE_NAME)
    db.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
    return db

def init_db():
    db = get_db()
    cursor = db.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        phone TEXT UNIQUE,
        username TEXT UNIQUE NOT NULL,
        wechat_id TEXT UNIQUE,
        hashed_password TEXT NOT NULL,
        profile_picture TEXT,
        bio TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Communities Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS communities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        rules TEXT,
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(id)
    )
    """)

    # Community Members Table (for roles and membership)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS community_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        community_id INTEGER NOT NULL,
        role TEXT NOT NULL DEFAULT 'member', -- 'admin', 'moderator', 'member'
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (community_id) REFERENCES communities(id),
        UNIQUE (user_id, community_id)
    )
    """)

    # Posts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        community_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        image_url TEXT,
        video_url TEXT,
        document_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_pinned BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (community_id) REFERENCES communities(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # Comments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # Likes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE (post_id, user_id)
    )
    """)

    # Direct Messages Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_read BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    )
    """)

    # Announcements Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        community_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        is_pinned BOOLEAN DEFAULT FALSE,
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (community_id) REFERENCES communities(id),
        FOREIGN KEY (created_by) REFERENCES users(id)
    )
    """)

    # Events Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        community_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        start_at TIMESTAMP NOT NULL,
        end_at TIMESTAMP,
        location TEXT,
        image_url TEXT,
        capacity INTEGER,
        is_public BOOLEAN DEFAULT TRUE,
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (community_id) REFERENCES communities(id),
        FOREIGN KEY (created_by) REFERENCES users(id)
    )
    """)

    # Event Registrations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS event_registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'registered', -- registered/cancelled/checked_in
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES events(id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE (event_id, user_id)
    )
    """)

    # Albums Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS albums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        community_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        cover_url TEXT,
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (community_id) REFERENCES communities(id),
        FOREIGN KEY (created_by) REFERENCES users(id)
    )
    """)

    # Photos Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        album_id INTEGER NOT NULL,
        photo_url TEXT NOT NULL,
        caption TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (album_id) REFERENCES albums(id)
    )
    """)

    # Memberships Table (per community)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memberships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        community_id INTEGER NOT NULL,
        membership_no TEXT UNIQUE,
        level TEXT,
        status TEXT NOT NULL DEFAULT 'active', -- active/expired/suspended
        role TEXT NOT NULL DEFAULT 'visitor', -- visitor/member/staff
        expires_at TIMESTAMP,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (community_id) REFERENCES communities(id),
        UNIQUE (user_id, community_id)
    )
    """)

    # 為既有資料庫補上 payments 表（若不存在）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        community_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        method TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        related_type TEXT,
        related_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (community_id) REFERENCES communities(id)
    )
    """)

    # 為既有資料庫補上 wechat_id 欄位（若不存在）
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    if "wechat_id" not in existing_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN wechat_id TEXT")

    # 補上 memberships.role 欄位（若不存在）
    cursor.execute("PRAGMA table_info(memberships)")
    membership_columns = {row[1] for row in cursor.fetchall()}
    if "role" not in membership_columns:
        # Check if column exists before adding - Wait, if "role" is NOT in columns, we add it.
        # But wait, checking logic:
        # The existing code was:
        # cursor.execute("ALTER TABLE memberships ADD COLUMN role TEXT NOT NULL DEFAULT 'visitor'")
        # I should keep it.
        cursor.execute("ALTER TABLE memberships ADD COLUMN role TEXT NOT NULL DEFAULT 'visitor'")

    # --- New Migration: Add image_url to events ---
    cursor.execute("PRAGMA table_info(events)")
    event_columns = {row[1] for row in cursor.fetchall()}
    if "image_url" not in event_columns:
        cursor.execute("ALTER TABLE events ADD COLUMN image_url TEXT")
    
    # --- New Migration: Add early_bird columns to events (If missing from previous step) ---
    if "early_bird_price" not in event_columns:
         cursor.execute("ALTER TABLE events ADD COLUMN early_bird_price REAL")
    if "early_bird_deadline" not in event_columns:
         cursor.execute("ALTER TABLE events ADD COLUMN early_bird_deadline TIMESTAMP")
    if "joined_at" not in membership_columns:
        cursor.execute("ALTER TABLE memberships ADD COLUMN joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
    # 補上 events.price 欄位（若不存在）
    cursor.execute("PRAGMA table_info(events)")
    event_columns = {row[1] for row in cursor.fetchall()}
    if "price" not in event_columns:
        cursor.execute("ALTER TABLE events ADD COLUMN price REAL DEFAULT 0")
    if "early_bird_price" not in event_columns:
        cursor.execute("ALTER TABLE events ADD COLUMN early_bird_price REAL")
    if "early_bird_deadline" not in event_columns:
        cursor.execute("ALTER TABLE events ADD COLUMN early_bird_deadline TIMESTAMP")


    db.commit()
    db.close()

init_db()

# --- Password Hashing ---
# bcrypt 只支援 72 bytes，改用 pbkdf2_sha256 並保留舊 bcrypt 相容
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt_sha256", "bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- Pydantic Models ---
class UserCreate(BaseModel):
    email: str
    phone: Optional[str] = None
    username: str
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    identifier: str  # email or phone
    password: str

class ApiRegisterRequest(BaseModel):
    email: str
    phone_number: Optional[str] = None
    username: str
    password: str

class ApiLoginRequest(BaseModel):
    identifier: str  # email or phone
    password: str

class ApiWeChatSSORequest(BaseModel):
    wechat_id: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None

class ApiWeChatMockExchangeRequest(BaseModel):
    code: str

class User(BaseModel):
    id: int
    email: str
    phone: Optional[str] = None
    username: str
    profile_picture: Optional[str] = None
    bio: Optional[str] = None

    class Config:
        orm_mode = True

class CommunityCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rules: Optional[str] = None

class Community(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    rules: Optional[str] = None
    created_by: int

    class Config:
        orm_mode = True

class MembershipCreate(BaseModel):
    user_id: int
    community_id: int
    membership_no: Optional[str] = None
    level: Optional[str] = None
    status: Optional[str] = "active"
    role: Optional[str] = "visitor"
    role: Optional[str] = "visitor"
    expires_at: Optional[str] = None
    joined_at: Optional[str] = None

class MembershipUpdate(BaseModel):
    level: Optional[str] = None
    status: Optional[str] = None
    role: Optional[str] = None
    expires_at: Optional[str] = None
    joined_at: Optional[str] = None

class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    method: Optional[str] = None

class Membership(BaseModel):
    id: int
    user_id: int
    community_id: int
    membership_no: Optional[str] = None
    level: Optional[str] = None
    status: str
    role: str
    expires_at: Optional[str] = None
    joined_at: Optional[str] = None

    class Config:
        orm_mode = True

class AnnouncementCreate(BaseModel):
    community_id: int
    title: str
    content: str
    is_pinned: Optional[bool] = False

class Announcement(BaseModel):
    id: int
    community_id: int
    title: str
    content: str
    is_pinned: bool
    created_by: int
    created_at: str

    class Config:
        orm_mode = True

class EventCreate(BaseModel):
    community_id: int
    title: str
    description: Optional[str] = None
    start_at: str
    end_at: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    is_public: Optional[bool] = True
    price: Optional[float] = 0
    image_url: Optional[str] = None
    early_bird_price: Optional[float] = None
    early_bird_deadline: Optional[str] = None


class Event(BaseModel):
    id: int
    community_id: int
    title: str
    description: Optional[str] = None
    start_at: str
    end_at: Optional[str] = None
    location: Optional[str] = None
    image_url: Optional[str] = None
    capacity: Optional[int] = None
    is_public: bool
    price: float
    early_bird_price: Optional[float] = None
    early_bird_deadline: Optional[str] = None
    created_by: int

    created_at: str

    class Config:
        orm_mode = True

class EventRegistrationCreate(BaseModel):
    event_id: int
    user_id: int
    status: Optional[str] = "registered"

class EventRegistration(BaseModel):
    id: int
    event_id: int
    user_id: int
    status: str
    registered_at: str

    class Config:
        orm_mode = True

class AlbumCreate(BaseModel):
    community_id: int
    title: str
    description: Optional[str] = None
    cover_url: Optional[str] = None

class Album(BaseModel):
    id: int
    community_id: int
    title: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    created_by: int
    created_at: str

    class Config:
        orm_mode = True

class PhotoCreate(BaseModel):
    album_id: int
    photo_url: str
    caption: Optional[str] = None

class Photo(BaseModel):
    id: int
    album_id: int
    photo_url: str
    caption: Optional[str] = None
    created_at: str

    class Config:
        orm_mode = True

class PostCreate(BaseModel):
    content: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    document_url: Optional[str] = None

class Post(BaseModel):
    id: int
    community_id: int
    user_id: int
    content: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    document_url: Optional[str] = None
    created_at: str
    is_pinned: bool
    username: str # Added for display

    class Config:
        orm_mode = True

class CommentCreate(BaseModel):
    content: str

class Comment(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: str
    username: str # Added for display

    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class Message(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    sent_at: str
    is_read: bool
    sender_username: str # Added for display

    class Config:
        orm_mode = True

# --- FastAPI App ---
app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Authentication Dependencies ---
# --- Authentication Dependencies ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days for mobile app convenience

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    # 1. Try Streamlit session first (for monolithic app usage)
    # Note: accessing st.session_state from a different thread (Uvicorn worker) might not work as expected
    # but we keep it for the Streamlit runner.
    try:
        if "user_id" in st.session_state and st.session_state.user_id:
             db = get_db()
             cursor = db.cursor()
             cursor.execute("SELECT * FROM users WHERE id = ?", (st.session_state.user_id,))
             user_data = cursor.fetchone()
             db.close()
             if user_data:
                 return User(**dict(user_data))
    except Exception:
        pass # Ignore Streamlit session errors in API context

    # 2. Try JWT token (for Vue/API usage)
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (int(user_id_str),))
    user_data = cursor.fetchone()
    db.close()
    
    if user_data is None:
        raise credentials_exception
    if user_data is None:
        raise credentials_exception
    return User(**dict(user_data))


def generate_membership_no():
    # Format: M + YYYYMMDD + 4 random digits
    date_str = datetime.utcnow().strftime("%Y%m%d")
    random_digits = secrets.randbelow(10000)
    return f"M{date_str}{random_digits:04d}"


# --- Auth API Endpoints (for Streamlit UI) ---
@app.post("/api/auth/register")
def api_register(payload: ApiRegisterRequest):
    db = get_db()
    cursor = db.cursor()
    hashed_password = get_password_hash(payload.password)
    try:
        cursor.execute(
            "INSERT INTO users (email, phone, username, hashed_password) VALUES (?, ?, ?, ?)",
            (payload.email, payload.phone_number, payload.username, hashed_password),
        )
        db.commit()

        # Generate Membership
        user_id = cursor.lastrowid
        membership_no = generate_membership_no()
        try:
            cursor.execute(
                "INSERT INTO memberships (user_id, community_id, membership_no, level, status, role, joined_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, 1, membership_no, 'friend', 'active', 'member', datetime.utcnow()),
            )
            db.commit()
        except sqlite3.Error as e:
            # Log error but don't fail registration completely if membership fails? 
            # Ideally should rollback user creation too.
            print(f"Failed to create membership: {e}")
            # db.rollback() # Cannot rollback committed user?
            # Ideally we should do both in one transaction without intermediate commit.
            # But the code above commits user first.
            pass

    except sqlite3.IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"註冊失敗: {exc}") from exc
    finally:
        db.close()
    return {"message": "註冊成功"}


@app.post("/api/auth/login")
def api_login(payload: ApiLoginRequest):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email = ? OR phone = ?",
        (payload.identifier, payload.identifier),
    )
    user_data = cursor.fetchone()
    db.close()

    if not user_data or not verify_password(payload.password, user_data["hashed_password"]):
        raise HTTPException(status_code=401, detail="無效的電子郵件/手機號碼或密碼。")

    user_info = {
        "id": user_data["id"],
        "email": user_data["email"],
        "phone_number": user_data["phone"],
        "username": user_data["username"],
        "profile_picture_url": user_data["profile_picture"],
        "bio": user_data["bio"],
        "is_profile_public": True,
        "show_email_publicly": False,
    }
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_data["id"])}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_info": user_info}


@app.post("/api/auth/wechat_sso")
def api_wechat_sso(payload: ApiWeChatSSORequest):
    wechat_id = payload.wechat_id.strip()
    if not wechat_id:
        raise HTTPException(status_code=400, detail="wechat_id 不能為空")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE wechat_id = ?", (wechat_id,))
    user_data = cursor.fetchone()

    if not user_data:
        base_username = (payload.nickname or f"wechat_{wechat_id[:8]}").strip()
        username = base_username
        suffix = 1
        while True:
            cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            if not cursor.fetchone():
                break
            username = f"{base_username}_{suffix}"
            suffix += 1

        email = f"{wechat_id}@wechat.local"
        email_candidate = email
        email_suffix = 1
        while True:
            cursor.execute("SELECT 1 FROM users WHERE email = ?", (email_candidate,))
            if not cursor.fetchone():
                break
            email_candidate = f"{wechat_id}+{email_suffix}@wechat.local"
            email_suffix += 1

        random_password = secrets.token_urlsafe(32)
        hashed_password = get_password_hash(random_password)
        try:
            cursor.execute(
                "INSERT INTO users (email, phone, username, wechat_id, hashed_password, profile_picture) VALUES (?, ?, ?, ?, ?, ?)",
                (email_candidate, None, username, wechat_id, hashed_password, payload.avatar_url),
            )
            db.commit()
            
            # Generate Membership for WeChat User
            new_user_id = cursor.lastrowid
            membership_no = generate_membership_no()
            try:
                cursor.execute(
                    "INSERT INTO memberships (user_id, community_id, membership_no, level, status, role, joined_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (new_user_id, 1, membership_no, 'friend', 'active', 'member', datetime.utcnow()),
                )
                db.commit()
            except sqlite3.Error:
                pass

        except sqlite3.IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"微信註冊失敗: {exc}") from exc

        cursor.execute("SELECT * FROM users WHERE wechat_id = ?", (wechat_id,))
        user_data = cursor.fetchone()

    db.close()

    user_info = {
        "id": user_data["id"],
        "email": user_data["email"],
        "phone_number": user_data["phone"],
        "username": user_data["username"],
        "profile_picture_url": user_data["profile_picture"],
        "bio": user_data["bio"],
        "is_profile_public": True,
        "show_email_publicly": False,
    }
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_data["id"])}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_info": user_info}


# --- WeChat OAuth Mock (for testing without service account) ---
@app.post("/api/wechat/mock_exchange")
def api_wechat_mock_exchange(payload: ApiWeChatMockExchangeRequest):
    code = payload.code.strip()
    if not code:
        raise HTTPException(status_code=400, detail="code 不能為空")
    # 以 code 派生固定的 mock openid
    openid = f"mock_openid_{code}"
    return {"openid": openid, "unionid": None}


# --- Communities API ---
@app.get("/api/communities", response_model=List[Community])
def list_communities():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM communities ORDER BY created_at DESC")
    rows = cursor.fetchall()
    db.close()
    return [Community(**dict(row)) for row in rows]


@app.get("/api/communities/by-name", response_model=Community)
def get_community_by_name(name: str):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM communities WHERE name = ?", (name,))
    row = cursor.fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="社團不存在")
    return Community(**dict(row))


@app.get("/api/communities/{community_id}", response_model=Community)
def get_community(community_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM communities WHERE id = ?", (community_id,))
    row = cursor.fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="社團不存在")
    return Community(**dict(row))


@app.post("/api/communities", response_model=Community)
def create_community(payload: CommunityCreate, created_by: int):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO communities (name, description, rules, created_by)
            VALUES (?, ?, ?, ?)
            """,
            (payload.name, payload.description, payload.rules, created_by),
        )
        db.commit()
    except sqlite3.IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"建立社團失敗: {exc}") from exc
    cursor.execute("SELECT * FROM communities WHERE id = ?", (cursor.lastrowid,))
    row = cursor.fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="社團不存在")
    return Community(**dict(row))


# --- Membership API ---
@app.get("/api/memberships", response_model=List[Membership])
def api_list_memberships(
    user_id: Optional[int] = None, 
    community_id: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    cursor = db.cursor()
    query = "SELECT * FROM memberships WHERE 1=1"
    params = []
    if user_id is not None:
        query += " AND user_id = ?"
        params.append(user_id)
    if community_id is not None:
        query += " AND community_id = ?"
        params.append(community_id)
    query += " ORDER BY joined_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    return [Membership(**dict(row)) for row in rows]


@app.post("/api/memberships", response_model=Membership)
def api_create_membership(payload: MembershipCreate, current_user: User = Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO memberships (user_id, community_id, membership_no, level, status, role, expires_at, joined_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.user_id,
                payload.community_id,
                payload.membership_no,
                payload.level,
                payload.status,
                payload.role,
                payload.expires_at,
                payload.joined_at,
            ),
        )
        db.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="該用戶已是此社群會員")
    cursor.execute("SELECT * FROM memberships WHERE id = ?", (cursor.lastrowid,))
    row = cursor.fetchone()
    db.close()
    return Membership(**dict(row))


@app.patch("/api/memberships/{membership_id}", response_model=Membership)
def api_update_membership(membership_id: int, payload: MembershipUpdate, current_user: User = Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()
    updates = []
    params = []
    
    if payload.role:
        updates.append("role = ?")
        params.append(payload.role)
    if payload.level:
        updates.append("level = ?")
        params.append(payload.level)
    if payload.status:
        updates.append("status = ?")
        params.append(payload.status)
    if payload.expires_at:
        updates.append("expires_at = ?")
        params.append(payload.expires_at)
    if payload.joined_at:
        updates.append("joined_at = ?")
        params.append(payload.joined_at)
        
    if not updates:
        raise HTTPException(status_code=400, detail="沒有要更新的欄位")
        
    params.append(membership_id)
    cursor.execute(f"UPDATE memberships SET {', '.join(updates)} WHERE id = ?", params)
    db.commit()
    
    cursor.execute("SELECT * FROM memberships WHERE id = ?", (membership_id,))
    row = cursor.fetchone()
    db.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="會籍不存在")
    return Membership(**dict(row))


# --- Users API (admin) ---
@app.get("/api/users", response_model=List[User])
def api_list_users(current_user: User = Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    rows = cursor.fetchall()
    db.close()
    return [User(**dict(row)) for row in rows]


@app.get("/api/users/{user_id}", response_model=User)
def api_get_user(user_id: int, current_user: User = Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="使用者不存在")
    return User(**dict(row))


class UserUpdate(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None


@app.patch("/api/users/{user_id}", response_model=User)
def api_update_user(user_id: int, payload: UserUpdate, current_user: User = Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()
    updates = []
    params = []
    for field in ["username", "phone", "email", "bio", "profile_picture"]:
        value = getattr(payload, field, None)
        if value is not None:
            updates.append(f"{field} = ?")
            params.append(value)
    if not updates:
        raise HTTPException(status_code=400, detail="沒有要更新的欄位")
    params.append(user_id)
    cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)
    db.commit()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="使用者不存在")
    return User(**dict(row))


# --- Payments API ---
@app.get("/api/payments")
def list_payments(user_id: Optional[int] = None, community_id: Optional[int] = None):
    db = get_db()
    cursor = db.cursor()
    query = """
        SELECT p.*, u.username, u.profile_picture 
        FROM payments p
        LEFT JOIN users u ON p.user_id = u.id
        WHERE 1=1
    """
    params = []
    if user_id is not None:
        query += " AND p.user_id = ?"
        params.append(user_id)
    if community_id is not None:
        query += " AND p.community_id = ?"
        params.append(community_id)
    query += " ORDER BY p.created_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    db.close()
    return [dict(row) for row in rows]


@app.post("/api/payments")
def create_payment(payload: dict):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO payments (user_id, community_id, description, amount, method, status, related_type, related_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            payload.get("user_id"),
            payload.get("community_id", 1),
            payload.get("description", ""),
            payload.get("amount", 0),
            payload.get("method"),
            payload.get("status", "pending"),
            payload.get("related_type"),
            payload.get("related_id"),
        ),
    )
    db.commit()
    cursor.execute("SELECT * FROM payments WHERE id = ?", (cursor.lastrowid,))
    row = cursor.fetchone()
    db.close()
    return dict(row)


@app.patch("/api/payments/{payment_id}")
def update_payment(payment_id: int, payload: PaymentUpdate):
    db = get_db()
    cursor = db.cursor()
    updates = []
    params = []
    
    if payload.status:
        updates.append("status = ?")
        params.append(payload.status)
    if payload.method:
        updates.append("method = ?")
        params.append(payload.method)
        
    if not updates:
        raise HTTPException(status_code=400, detail="沒有要更新的欄位")
        
    params.append(payment_id)
    cursor.execute(f"UPDATE payments SET {', '.join(updates)} WHERE id = ?", params)
    db.commit()
    
    cursor.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
    row = cursor.fetchone()
    db.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="繳費記錄不存在")
        
    return dict(row)


# --- Dashboard Stats API ---
@app.get("/api/stats/dashboard")
def get_dashboard_stats(community_id: Optional[int] = None):
    db = get_db()
    cursor = db.cursor()
    cond = "WHERE community_id = ?" if community_id else ""
    params = [community_id] if community_id else []

    cursor.execute(f"SELECT COUNT(*) as cnt FROM memberships {cond}", params)
    total_members = cursor.fetchone()["cnt"]

    # Calculate conditions for active and expired members
    active_cond = cond.replace('WHERE', "WHERE status = 'active' AND") if cond else "WHERE status = 'active'"
    cursor.execute(f"SELECT COUNT(*) as cnt FROM memberships {active_cond}", params)
    active_members = cursor.fetchone()["cnt"]

    expired_cond = cond.replace('WHERE', "WHERE status = 'expired' AND") if cond else "WHERE status = 'expired'"
    cursor.execute(f"SELECT COUNT(*) as cnt FROM memberships {expired_cond}", params)
    expired_members = cursor.fetchone()["cnt"]

    pending_members = total_members - active_members - expired_members

    cursor.execute(f"SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE status = 'paid'" + (" AND community_id = ?" if community_id else ""), params)
    total_revenue = cursor.fetchone()["total"]

    cursor.execute(f"SELECT COUNT(*) as cnt FROM events {cond}", params)
    total_events = cursor.fetchone()["cnt"]

    db.close()
    return {
        "totalMembers": total_members,
        "activeMembers": active_members,
        "pendingMembers": pending_members,
        "expiredMembers": expired_members,
        "totalRevenue": total_revenue,
        "totalEvents": total_events,
    }


# --- Announcements API ---
@app.get("/api/announcements", response_model=List[Announcement])
def list_announcements(community_id: Optional[int] = None):
    db = get_db()
    cursor = db.cursor()
    query = "SELECT * FROM announcements WHERE 1=1"
    params = []
    if community_id is not None:
        query += " AND community_id = ?"
        params.append(community_id)
    query += " ORDER BY is_pinned DESC, created_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    db.close()
    return [Announcement(**dict(row)) for row in rows]


@app.get("/api/announcements/{announcement_id}", response_model=Announcement)
def get_announcement(announcement_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM announcements WHERE id = ?", (announcement_id,))
    row = cursor.fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="公告不存在")
    return Announcement(**dict(row))


@app.post("/api/announcements", response_model=Announcement)
def create_announcement(payload: AnnouncementCreate, created_by: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO announcements (community_id, title, content, is_pinned, created_by)
        VALUES (?, ?, ?, ?, ?)
        """,
        (payload.community_id, payload.title, payload.content, payload.is_pinned or False, created_by),
    )
    db.commit()
    cursor.execute("SELECT * FROM announcements WHERE id = ?", (cursor.lastrowid,))
    row = cursor.fetchone()
    db.close()
    return Announcement(**dict(row))


@app.put("/api/announcements/{announcement_id}", response_model=Announcement)
def update_announcement(announcement_id: int, payload: AnnouncementCreate):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE announcements
        SET title = ?, content = ?, is_pinned = ?
        WHERE id = ?
        """,
        (payload.title, payload.content, payload.is_pinned or False, announcement_id),
    )
    db.commit()
    cursor.execute("SELECT * FROM announcements WHERE id = ?", (announcement_id,))
    row = cursor.fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="公告不存在")
    return Announcement(**dict(row))


@app.delete("/api/announcements/{announcement_id}")
def delete_announcement(announcement_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM announcements WHERE id = ?", (announcement_id,))
    db.commit()
    db.close()
    return {"message": "已刪除"}


# --- Events API ---
@app.get("/api/events", response_model=List[Event])
def list_events(community_id: Optional[int] = None):
    db = get_db()
    cursor = db.cursor()
    query = "SELECT * FROM events WHERE 1=1"
    params = []
    if community_id is not None:
        query += " AND community_id = ?"
        params.append(community_id)
    query += " ORDER BY start_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    db.close()
    return [Event(**dict(row)) for row in rows]


@app.get("/api/events/{event_id}", response_model=Event)
def get_event(event_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    row = cursor.fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="活動不存在")
    return Event(**dict(row))


@app.post("/api/events", response_model=Event)
def create_event(payload: EventCreate, current_user: User = Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO events (community_id, title, description, start_at, end_at, location, image_url, capacity, is_public, price, early_bird_price, early_bird_deadline, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.community_id,
            payload.title,
            payload.description,
            payload.start_at,
            payload.end_at,
            payload.location,
            payload.image_url,
            payload.capacity,
            True if payload.is_public is None else payload.is_public,
            payload.price or 0,
            payload.early_bird_price,
            payload.early_bird_deadline,
            current_user.id,
        ),
    )

    db.commit()
    cursor.execute("SELECT * FROM events WHERE id = ?", (cursor.lastrowid,))
    row = cursor.fetchone()
    db.close()
    return Event(**dict(row))


@app.put("/api/events/{event_id}", response_model=Event)
def update_event(event_id: int, payload: EventCreate, current_user: User = Depends(get_current_user)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE events
        SET title = ?, description = ?, start_at = ?, end_at = ?, location = ?, image_url = ?, capacity = ?, is_public = ?, price = ?, early_bird_price = ?, early_bird_deadline = ?
        WHERE id = ?
        """,

        (
            payload.title,
            payload.description,
            payload.start_at,
            payload.end_at,
            payload.location,
            payload.image_url,
            payload.capacity,
            True if payload.is_public is None else payload.is_public,
            payload.price or 0,
            payload.early_bird_price,
            payload.early_bird_deadline,
            event_id,
        ),
    )

    db.commit()
    cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    row = cursor.fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="活動不存在")
    return Event(**dict(row))


@app.delete("/api/events/{event_id}")
def delete_event(event_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    db.commit()
    db.close()
    return {"message": "已刪除"}


@app.post("/api/events/{event_id}/register", response_model=EventRegistration)
def register_event(event_id: int, payload: EventRegistrationCreate):
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if event has a price
        cursor.execute("SELECT title, price, community_id FROM events WHERE id = ?", (event_id,))
        event_info = cursor.fetchone()
        if not event_info:
            db.close()
            raise HTTPException(status_code=404, detail="活動不存在")
            
        cursor.execute(
            """
            INSERT INTO event_registrations (event_id, user_id, status)
            VALUES (?, ?, ?)
            """,
            (event_id, payload.user_id, payload.status or "registered"),
        )
        
        # Create payment if price > 0
        price = event_info["price"]
        if price and price > 0:
            cursor.execute(
                """
                INSERT INTO payments (user_id, community_id, description, amount, method, status, related_type, related_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.user_id,
                    event_info["community_id"],
                    f"活動費: {event_info['title']}",
                    price,
                    "cash", # Default to cash/transfer, can be updated later
                    "pending",
                    "event",
                    event_id
                )
            )
            
        db.commit()
    except sqlite3.IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"報名失敗: {exc}") from exc
    cursor.execute("SELECT * FROM event_registrations WHERE id = ?", (cursor.lastrowid,))
    row = cursor.fetchone()
    db.close()
    return EventRegistration(**dict(row))


# --- Albums & Photos API ---
@app.get("/api/albums", response_model=List[Album])
def list_albums(community_id: Optional[int] = None):
    db = get_db()
    cursor = db.cursor()
    query = "SELECT * FROM albums WHERE 1=1"
    params = []
    if community_id is not None:
        query += " AND community_id = ?"
        params.append(community_id)
    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    db.close()
    return [Album(**dict(row)) for row in rows]


@app.get("/api/albums/{album_id}", response_model=Album)
def get_album(album_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM albums WHERE id = ?", (album_id,))
    row = cursor.fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="相冊不存在")
    return Album(**dict(row))


@app.post("/api/albums", response_model=Album)
def create_album(payload: AlbumCreate, created_by: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO albums (community_id, title, description, cover_url, created_by)
        VALUES (?, ?, ?, ?, ?)
        """,
        (payload.community_id, payload.title, payload.description, payload.cover_url, created_by),
    )
    db.commit()
    cursor.execute("SELECT * FROM albums WHERE id = ?", (cursor.lastrowid,))
    row = cursor.fetchone()
    db.close()
    return Album(**dict(row))


@app.put("/api/albums/{album_id}", response_model=Album)
def update_album(album_id: int, payload: AlbumCreate):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE albums
        SET title = ?, description = ?, cover_url = ?
        WHERE id = ?
        """,
        (payload.title, payload.description, payload.cover_url, album_id),
    )
    db.commit()
    cursor.execute("SELECT * FROM albums WHERE id = ?", (album_id,))
    row = cursor.fetchone()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="相冊不存在")
    return Album(**dict(row))


@app.delete("/api/albums/{album_id}")
def delete_album(album_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM albums WHERE id = ?", (album_id,))
    db.commit()
    db.close()
    return {"message": "已刪除"}


@app.get("/api/albums/{album_id}/photos", response_model=List[Photo])
def list_photos(album_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM photos WHERE album_id = ? ORDER BY created_at DESC", (album_id,))
    rows = cursor.fetchall()
    db.close()
    return [Photo(**dict(row)) for row in rows]


@app.post("/api/photos", response_model=Photo)
def create_photo(payload: PhotoCreate):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO photos (album_id, photo_url, caption) VALUES (?, ?, ?)",
        (payload.album_id, payload.photo_url, payload.caption),
    )
    db.commit()
    cursor.execute("SELECT * FROM photos WHERE id = ?", (cursor.lastrowid,))
    row = cursor.fetchone()
    db.close()
    return Photo(**dict(row))


@app.delete("/api/photos/{photo_id}")
def delete_photo(photo_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM photos WHERE id = ?", (photo_id,))
    db.commit()
    db.close()
    return {"message": "已刪除"}

# --- Streamlit App ---

def render_login_page():
    st.title("登入")
    login_identifier = st.text_input("電子郵件或手機號碼", key="login_identifier")
    login_password = st.text_input("密碼", type="password", key="login_password")
    if st.button("登入"):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? OR phone = ?", (login_identifier, login_identifier))
        user_data = cursor.fetchone()
        db.close()

        if user_data and verify_password(login_password, user_data["hashed_password"]):
            st.session_state.user_logged_in = True
            st.session_state.user_id = user_data["id"]
            st.session_state.username = user_data["username"]
            st.success("登入成功！")
            st.rerun()
        else:
            st.error("無效的電子郵件/手機號碼或密碼。")

def render_registration_page():
    st.title("註冊")
    reg_email = st.text_input("電子郵件", key="reg_email")
    reg_phone = st.text_input("手機號碼", key="reg_phone")
    reg_username = st.text_input("使用者名稱", key="reg_username")
    reg_password = st.text_input("密碼", type="password", key="reg_password")
    reg_confirm_password = st.text_input("確認密碼", type="password", key="reg_confirm_password")

    if st.button("註冊"):
        if reg_password != reg_confirm_password:
            st.error("密碼不匹配。" )
            return

        hashed_password = get_password_hash(reg_password)
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (email, phone, username, hashed_password) VALUES (?, ?, ?, ?)",
                (reg_email, reg_phone, reg_username, hashed_password)
            )
            db.commit()
            st.success("註冊成功！請登入。" )
        except sqlite3.IntegrityError as e:
            st.error(f"註冊失敗: {e}")
        finally:
            db.close()

def render_profile_page():
    st.title("我的個人資料")
    user_id = st.session_state.user_id

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    db.close()

    if not user_data:
        st.error("找不到使用者資料。" )
        return

    username = st.text_input("使用者名稱", value=user_data["username"], key="profile_username")
    bio = st.text_area("個人簡介", value=user_data["bio"] or "", key="profile_bio")
    profile_picture = st.text_input("個人頭像 URL", value=user_data["profile_picture"] or "https://via.placeholder.com/150", key="profile_picture_url")
    st.image(profile_picture, caption="個人頭像", use_column_width=True)

    st.text_input("電子郵件", value=user_data["email"], key="profile_email", disabled=True)
    st.text_input("手機號碼", value=user_data["phone"] or "未提供", key="profile_phone", disabled=True)

    st.subheader("隱私設定")
    # Placeholder for privacy settings, as they are not fully implemented in DB
    privacy_public = st.checkbox("公開個人資料", value=True, key="privacy_public")
    privacy_show_email = st.checkbox("顯示電子郵件", value=False, key="privacy_show_email")

    if st.button("儲存個人資料"):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE users SET username = ?, bio = ?, profile_picture = ? WHERE id = ?",
            (username, bio, profile_picture, user_id)
        )
        db.commit()
        db.close()
        st.success("個人資料已儲存。" )
        st.session_state.username = username # Update session state if username changed
        st.rerun()

def render_my_communities_page():
    st.title("我的社團")
    user_id = st.session_state.user_id

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.description
        FROM communities c
        JOIN community_members cm ON c.id = cm.community_id
        WHERE cm.user_id = ?
    """, (user_id,))
    my_communities = cursor.fetchall()
    db.close()

    if not my_communities:
        st.info("您尚未加入任何社團。" )
    else:
        for community in my_communities:
            col1, col2 = st.columns([1, 3])
            with col1:
                # Placeholder for community image
                st.image("https://via.placeholder.com/80", caption=community["name"], use_column_width=True)
            with col2:
                st.subheader(community["name"])
                st.write(community["description"] or "無描述")
                if st.button("進入社團", key=f"enter_community_{community['id']}"):
                    st.session_state.current_community_id = community["id"]
                    st.session_state.current_community_name = community["name"]
                    st.rerun()

    st.markdown("---")
    if st.button("建立新社團"):
        st.session_state.view = "create_community"
        st.rerun()

def render_create_community_page():
    st.title("建立新社團")
    community_name = st.text_input("社團名稱", key="create_community_name")
    community_description = st.text_area("社團描述", key="create_community_description")
    community_rules = st.text_area("社團規則", key="create_community_rules")

    if st.button("建立社團"):
        user_id = st.session_state.user_id
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO communities (name, description, rules, created_by) VALUES (?, ?, ?, ?)",
                (community_name, community_description, community_rules, user_id)
            )
            community_id = cursor.lastrowid
            # Add the creator as an admin
            cursor.execute(
                "INSERT INTO community_members (user_id, community_id, role) VALUES (?, ?, ?)",
                (user_id, community_id, 'admin')
            )
            db.commit()
            st.success(f"社團 '{community_name}' 已成功建立！")
            st.session_state.view = "my_communities"
            st.rerun()
        except sqlite3.IntegrityError:
            st.error("社團名稱已存在。" )
        finally:
            db.close()

def render_discover_communities_page():
    st.title("發現社團")
    search_term = st.text_input("搜尋社團...", key="discover_search")

    categories = ["技術", "興趣", "學習", "遊戲", "藝術"] # Example categories
    selected_category = st.selectbox("分類", ["所有分類"] + categories, key="discover_category")

    st.subheader("推薦社團")

    db = get_db()
    cursor = db.cursor()
    # Fetch some communities for display
    cursor.execute("SELECT * FROM communities LIMIT 3")
    recommended_communities = cursor.fetchall()
    db.close()

    if recommended_communities:
        cols = st.columns(3)
        for i, community in enumerate(recommended_communities):
            with cols[i % 3]:
                card(
                    title=community["name"],
                    description=community["description"] or "無描述",
                    tag=selected_category if selected_category != "所有分類" else "推薦", # Placeholder tag
                    action_text="查看詳情"
                )
                # In a real app, clicking "查看詳情" would navigate to community details or join flow

    st.markdown("---")
    st.subheader("所有社團")
    # More community cards can be displayed here, potentially with pagination and search filtering
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM communities")
    all_communities = cursor.fetchall()
    db.close()

    for community in all_communities:
        st.markdown(f"**{community['name']}** - {community['description'] or '無描述'}")
        if st.button("加入", key=f"join_community_{community['id']}"):
            # Logic to handle joining a community (e.g., sending a request or direct join)
            st.success(f"已發送加入 '{community['name']}' 的請求。" )

def render_messages_page():
    st.title("訊息")
    st.warning("訊息功能正在開發中。" )
    # This section would typically involve a list of conversations and a chat interface.
    # For now, we'll just show a placeholder.

def render_settings_page():
    st.title("設定")
    st.subheader("通知設定")
    st.checkbox("接收新訊息通知", value=True, key="notif_messages")
    st.checkbox("接收社團動態通知", value=True, key="notif_community_updates")
    st.checkbox("接收提及通知", value=True, key="notif_mentions")

    st.subheader("帳戶設定")
    if st.button("變更密碼"):
        st.warning("變更密碼功能正在開發中。" )
    if st.button("刪除帳戶"):
        st.warning("刪除帳戶功能正在開發中。" )

def render_community_view():
    community_id = st.session_state.get("current_community_id")
    community_name = st.session_state.get("current_community_name", "未選取社團")

    if not community_id:
        st.error("未選取社團。" )
        return

    st.title(f"社團: {community_name}")
    st.markdown("---")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT role FROM community_members WHERE user_id = ? AND community_id = ?", (st.session_state.user_id, community_id))
    member_role_data = cursor.fetchone()
    user_role = member_role_data["role"] if member_role_data else 'member'
    db.close()

    # Community Management Options (for admins/moderators)
    if user_role in ["admin", "moderator"]:
        st.subheader("社團管理")
        if st.button("管理成員"):
            st.session_state.view = "manage_members"
            st.session_state.current_community_id = community_id
            st.rerun()
        if st.button("編輯社團資訊"):
            st.session_state.view = "edit_community"
            st.session_state.current_community_id = community_id
            st.rerun()
        if st.button("設定社團規則"):
            st.session_state.view = "edit_community_rules"
            st.session_state.current_community_id = community_id
            st.rerun()
        st.markdown("---")

    st.subheader("社團動態")

    # Post creation
    with st.expander("發佈新動態"):
        new_post_content = st.text_area("您的訊息...", key="new_post_content")
        # Placeholder for file uploads, actual implementation would involve storage
        uploaded_files = st.file_uploader("上傳圖片/影片/文件", accept_multiple_files=True, key="post_files")
        if st.button("發佈"):
            if new_post_content or uploaded_files:
                # For simplicity, we'll just store content and a placeholder for file URLs
                image_url, video_url, document_url = None, None, None
                if uploaded_files:
                    # In a real app, you'd upload these to a storage service and get URLs
                    image_url = "https://via.placeholder.com/300x150" # Example URL

                db = get_db()
                cursor = db.cursor()
                cursor.execute(
                    "INSERT INTO posts (community_id, user_id, content, image_url, video_url, document_url) VALUES (?, ?, ?, ?, ?, ?)",
                    (community_id, st.session_state.user_id, new_post_content, image_url, video_url, document_url)
                )
                db.commit()
                db.close()
                st.success("動態已發佈！")
                st.rerun() # Rerun to show the new post
            else:
                st.warning("請輸入內容或上傳檔案。" )

    # Display posts
    st.markdown("---")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.*, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.community_id = ?
        ORDER BY p.is_pinned DESC, p.created_at DESC
    """, (community_id,))
    posts = cursor.fetchall()
    db.close()

    if not posts:
        st.info("此社團目前沒有任何動態。" )
    else:
        for post in posts:
            render_post(
                post_id=post["id"],
                author=post["username"],
                content=post["content"],
                timestamp=post["created_at"],
                pinned=post["is_pinned"],
                image_url=post["image_url"],
                community_id=community_id,
                user_role=user_role
            )

def render_post(post_id: int, author: str, content: str, timestamp: str, pinned: bool, image_url: Optional[str], community_id: int, user_role: str):
    with st.container():
        if pinned:
            st.warning("📌 置頂")
        st.markdown(f"**{author}** - {timestamp}")
        st.write(content)
        if image_url:
            st.image(image_url, caption="範例圖片", use_column_width=True, output_format="PNG") # Example image

        # Like count (placeholder)
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM likes WHERE post_id = ?", (post_id,))
        like_count = cursor.fetchone()[0]
        db.close()

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👍 讚", key=f"like_{post_id}"):
                # Logic for liking a post
                db = get_db()
                cursor = db.cursor()
                try:
                    cursor.execute("INSERT INTO likes (post_id, user_id) VALUES (?, ?)", (post_id, st.session_state.user_id))
                    db.commit()
                    st.success("您已按讚！")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.warning("您已按讚。" )
                finally:
                    db.close()
            st.write(f"{like_count} 個讚")
        with col2:
            if st.button("💬 評論", key=f"comment_btn_{post_id}"):
                # This button could toggle a comment section or navigate to a dedicated comment view
                st.session_state[f"show_comments_{post_id}"] = not st.session_state.get(f"show_comments_{post_id}", False)
                st.rerun()
        with col3:
            if st.button("🔗 分享", key=f"share_{post_id}"):
                st.warning("分享功能正在開發中。" )

        if st.session_state.get(f"show_comments_{post_id}", False):
            with st.expander("查看評論", expanded=True):
                comment_content = st.text_area("留下您的評論...", key=f"comment_input_{post_id}")
                if st.button("發佈評論", key=f"publish_comment_{post_id}"):
                    if comment_content:
                        db = get_db()
                        cursor = db.cursor()
                        cursor.execute(
                            "INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)",
                            (post_id, st.session_state.user_id, comment_content)
                        )
                        db.commit()
                        db.close()
                        st.success("評論已發佈！")
                        st.rerun()
                    else:
                        st.warning("請輸入評論內容。" )

                # Display existing comments
                db = get_db()
                cursor = db.cursor()
                cursor.execute("""
                    SELECT c.*, u.username
                    FROM comments c
                    JOIN users u ON c.user_id = u.id
                    WHERE c.post_id = ?
                    ORDER BY c.created_at ASC
                """, (post_id,))
                comments = cursor.fetchall()
                db.close()

                if not comments:
                    st.info("尚無評論。" )
                else:
                    for comment in comments:
                        st.markdown(f"**{comment['username']}** - {comment['created_at']}")
                        st.write(comment['content'])
                        st.markdown("---")

        # Admin/Moderator actions
        if user_role in ["admin", "moderator"]:
            st.markdown("---")
            st.subheader("管理操作")
            if st.button("編輯動態", key=f"edit_post_{post_id}"):
                st.warning("編輯動態功能正在開發中。" )
            if st.button("刪除動態", key=f"delete_post_{post_id}"):
                db = get_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
                db.commit()
                db.close()
                st.success("動態已刪除。" )
                st.rerun()
            if st.button("置頂/取消置頂", key=f"pin_post_{post_id}"):
                db = get_db()
                cursor = db.cursor()
                new_pin_status = not pinned
                cursor.execute("UPDATE posts SET is_pinned = ? WHERE id = ?", (new_pin_status, post_id))
                db.commit()
                db.close()
                st.success(f"動態已{'置頂' if new_pin_status else '取消置頂'}。" )
                st.rerun()

# --- Helper Functions for UI Elements ---
def card(title, description, tag, action_text):
    with st.container():
        st.subheader(title)
        st.write(description)
        st.markdown(f"**標籤:** {tag}")
        if st.button(action_text, key=f"card_action_{title}"):
            # In a real app, this would trigger navigation or a specific action
            st.success(f"您已點擊 '{action_text}' 按鈕於 '{title}'。" )

def run_streamlit_ui():
    # --- Main App Logic ---
    st.set_page_config(layout="wide", page_title="社團會員App")

    # --- Sidebar for Navigation ---
    with st.sidebar:
        st.title("社團會員App")
        st.markdown("---")

        # User Authentication/Profile Section
        st.header("帳戶")
        if "user_logged_in" not in st.session_state or not st.session_state.user_logged_in:
            menu_options = ["登入", "註冊"]
            selected_option = st.radio("導航", menu_options, key="sidebar_menu_guest")
        else:
            menu_options = ["我的個人資料", "我的社團", "發現社團", "訊息", "設定"]
            selected_option = st.radio("導航", menu_options, key="sidebar_menu_user")
            st.write(f"歡迎, {st.session_state.username}!")

        st.markdown("---")
        if "user_logged_in" in st.session_state and st.session_state.user_logged_in:
            if st.button("登出"):
                st.session_state.user_logged_in = False
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.current_community_id = None
                st.session_state.current_community_name = None
                st.session_state.view = "login"
                st.rerun()

    # --- Main Content Area ---
    if "user_logged_in" not in st.session_state or not st.session_state.user_logged_in:
        if selected_option == "登入":
            render_login_page()
        elif selected_option == "註冊":
            render_registration_page()
    else:
        # Check if we are currently viewing a community
        if st.session_state.get("current_community_id"):
            render_community_view()
        elif st.session_state.get("view") == "create_community":
            render_create_community_page()
        # Default views for logged-in users
        elif selected_option == "我的個人資料":
            render_profile_page()
        elif selected_option == "我的社團":
            render_my_communities_page()
        elif selected_option == "發現社團":
            render_discover_communities_page()
        elif selected_option == "訊息":
            render_messages_page()
        elif selected_option == "設定":
            render_settings_page()

    # --- Initial State Setup ---
    if "user_logged_in" not in st.session_state:
        st.session_state.user_logged_in = False
    if "view" not in st.session_state:
        st.session_state.view = "login"
    if "current_community_id" not in st.session_state:
        st.session_state.current_community_id = None
    if "current_community_name" not in st.session_state:
        st.session_state.current_community_name = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None

    # --- To run this app ---
    # 1. Save the code as `app.py`
    # 2. Install necessary libraries: `pip install streamlit fastapi uvicorn python-multipart passlib bcrypt`
    # 3. Run the Streamlit app: `streamlit run app.py`
    #
    # Note: This is a monolithic Streamlit app that simulates backend interactions with SQLite.
    # For a true FastAPI backend, you would separate the FastAPI routes and models into
    # different files and run FastAPI separately, with Streamlit acting as the frontend.


# --- Uploads Handling ---
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Generate safe filename
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"{secrets.token_hex(8)}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"url": f"/uploads/{filename}"}
    except Exception as e:
        print(f"Upload error: {e}") # Debug print
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/debug-upload")
async def debug_upload():
    return {
        "upload_dir": UPLOAD_DIR,
        "exists": os.path.exists(UPLOAD_DIR),
        "writable": os.access(UPLOAD_DIR, os.W_OK),
        "files_count": len(os.listdir(UPLOAD_DIR)) if os.path.exists(UPLOAD_DIR) else 0
    }

# --- Debug/Backup Endpoints ---
ADMIN_SECRET = "mvp_admin_secret_123"  # 簡單的保護機制，正式環境請改用更安全的驗證

@app.get("/api/debug/db")
def download_db(secret: str):
    """下載資料庫備份"""
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized")
    if os.path.exists(DATABASE_NAME):
        return FileResponse(DATABASE_NAME, filename="community_app.db", media_type="application/x-sqlite3")
    raise HTTPException(status_code=404, detail="Database not found")

@app.post("/api/debug/db")
async def upload_db(secret: str, file: UploadFile = File(...)):
    """上傳並覆蓋資料庫 (還原備份)"""
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        # 寫入新檔案
        with open(DATABASE_NAME, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"message": "Database restored successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Frontend Static Files (SPA) ---
dist_dir = os.path.join(os.path.dirname(__file__), "h5-app", "dist")

if os.path.exists(dist_dir):
    # Mount assets folder
    assets_dir = os.path.join(dist_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Serve index.html for root
    @app.get("/")
    async def read_index():
        return FileResponse(os.path.join(dist_dir, "index.html"))

    # Serve other static files or fallback to index.html (SPA History Mode)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Skip API routes (handled by definition order, but good to be safe if moved)
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
            
        file_path = os.path.join(dist_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Fallback to index.html for Vue Router paths
        return FileResponse(os.path.join(dist_dir, "index.html"))

else:
    @app.get("/")
    async def read_index_fallback():
        return HTMLResponse(content="""
        <html>
            <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
                <h1 style="color: #e53e3e;">⚠️ 前端檔案未找到 (Frontend Not Found)</h1>
                <p>系統找不到 <code>h5-app/dist</code> 資料夾。</p>
                <p>請確認您在遷移時，是否遺漏了複製這個資料夾？</p>
                <hr>
                <p style="color: gray;">System could not find 'h5-app/dist'. Please ensure it is copied from the source.</p>
            </body>
        </html>
        """)

if __name__ == "__main__":
    run_streamlit_ui()
