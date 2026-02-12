import sqlite3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_admin():
    conn = sqlite3.connect('community_app.db')
    cursor = conn.cursor()

    email = "admin@system.com"
    username = "系統管理員"
    password = "Admin123!@#"
    hashed_password = get_password_hash(password)

    # 1. 確保用戶存在
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if user:
        user_id = user[0]
        print(f"Update existing user {email} (ID: {user_id})")
        cursor.execute("UPDATE users SET hashed_password = ?, username = ? WHERE id = ?", (hashed_password, username, user_id))
    else:
        print(f"Create new user {email}")
        cursor.execute("INSERT INTO users (email, username, hashed_password) VALUES (?, ?, ?)", (email, username, hashed_password))
        user_id = cursor.lastrowid

    # 2. 確保社群存在
    cursor.execute("SELECT id FROM communities LIMIT 1")
    community = cursor.fetchone()
    
    if community:
        community_id = community[0]
        print(f"Using existing community ID: {community_id}")
    else:
        print("Create default community")
        cursor.execute("INSERT INTO communities (name, description, created_by) VALUES (?, ?, ?)", ("未來街坊", "默認社群", user_id))
        community_id = cursor.lastrowid

    # 3. 確保 Admin Membership 存在
    cursor.execute("SELECT id FROM memberships WHERE user_id = ? AND community_id = ?", (user_id, community_id))
    membership = cursor.fetchone()

    if membership:
        print(f"Update membership for user {user_id} in community {community_id}")
        cursor.execute("UPDATE memberships SET role = 'admin', status = 'active', level = 'admin' WHERE id = ?", (membership[0],))
    else:
        print(f"Create admin membership for user {user_id} in community {community_id}")
        cursor.execute("INSERT INTO memberships (user_id, community_id, role, status, level) VALUES (?, ?, 'admin', 'active', 'admin')", (user_id, community_id))

    conn.commit()
    conn.close()
    print("Admin setup completed successfully.")

if __name__ == "__main__":
    create_admin()
