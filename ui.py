import streamlit as st
import requests # Import requests for API calls

# --- Backend API Configuration ---
BACKEND_API_URL = "http://localhost:8000/api" # Replace with your actual backend API URL
FIXED_COMMUNITY_NAME = "未來街坊圈"
LOGO_URL = "https://via.placeholder.com/150x50?text=未來街坊圈" # 請替換為實際商標圖片

# --- Helper Functions for API Calls ---

def api_call(endpoint, method="GET", data=None):
    """Helper function to make API calls."""
    url = f"{BACKEND_API_URL}/{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=data)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url, json=data)
        else:
            return {"error": "Unsupported HTTP method"}

        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return {"error": str(e)}

# --- Page Rendering Functions ---

def render_album_detail_page():
    """相冊詳情頁"""
    if "selected_album_id" not in st.session_state:
        st.warning("請先選擇相冊。")
        return
    
    album_id = st.session_state.selected_album_id
    
    # 返回按鈕
    if st.button("← 返回首頁"):
        st.session_state.view = "home"
        del st.session_state.selected_album_id
        st.rerun()
    
    st.markdown("---")
    
    # 取得相冊資訊
    album = api_call(f"albums/{album_id}", method="GET")
    if album.get("error"):
        st.error("找不到相冊。")
        return
    
    st.title(album.get("title", "相冊"))
    st.caption(album.get("description", ""))
    st.markdown("---")
    
    # 取得相冊中的照片
    photos = api_call("photos", method="GET", data={"album_id": album_id}) or []
    
    if photos:
        # 以網格形式展示照片
        cols = st.columns(4)
        for idx, photo in enumerate(photos):
            with cols[idx % 4]:
                st.image(
                    photo.get("url", "https://via.placeholder.com/300x200"),
                    use_column_width=True,
                    caption=photo.get("caption", "")
                )
    else:
        st.info("這個相冊還沒有照片。")

def render_home_page():
    """首頁：最新活動與活動花絮"""
    # 頂部商標與橫幅
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_URL, use_column_width=True)
    
    st.markdown("<h1 style='text-align: center; color: #2c3e50;'>未來街坊圈</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>商務交流 · 活動精彩 · 人脈拓展</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # 取得社團 ID
    community = api_call("communities/by-name", method="GET", data={"name": FIXED_COMMUNITY_NAME})
    if community.get("error"):
        st.error("找不到社團，請聯繫管理員。")
        return
    
    community_id = community.get("id")
    
    # 最新活動區塊
    st.markdown("## 🎯 最新活動")
    events = api_call("events", method="GET", data={"community_id": community_id}) or []
    
    if events:
        # 顯示前 3 個最新活動
        for event in events[:3]:
            with st.container():
                st.markdown(
                    f"""
                    <div style='padding: 20px; background-color: #f8f9fa; border-radius: 10px; margin-bottom: 15px;'>
                        <h3 style='color: #2c3e50; margin: 0;'>{event.get('title', '')}</h3>
                        <p style='color: #7f8c8d; font-size: 14px;'>📅 {event.get('start_at', '')} | 📍 {event.get('location', '')}</p>
                        <p style='color: #34495e;'>{event.get('description', '')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                col1, col2, col3 = st.columns([2, 1, 1])
                with col2:
                    if st.button("查看詳情", key=f"home_event_detail_{event.get('id')}"):
                        st.info(f"活動：{event.get('title')}")
                with col3:
                    if st.button("立即報名", key=f"home_event_register_{event.get('id')}"):
                        if "user_info" in st.session_state and st.session_state.user_info:
                            user_id = st.session_state.user_info.get("id")
                            payload = {"event_id": event.get("id"), "user_id": user_id}
                            response = api_call(f"events/{event.get('id')}/register", method="POST", data=payload)
                            if "id" in response:
                                st.success("報名成功！")
                            else:
                                st.error(response.get("detail", "報名失敗。"))
                        else:
                            st.warning("請先登入再報名。")
    else:
        st.info("目前沒有活動。")
    
    st.markdown("---")
    
    # 活動花絮區塊
    st.markdown("## 📸 活動花絮")
    albums = api_call("albums", method="GET", data={"community_id": community_id}) or []
    
    if albums:
        # 顯示所有相冊封面
        cols = st.columns(3)
        for idx, album in enumerate(albums):
            with cols[idx % 3]:
                st.image(
                    album.get("cover_url", "https://via.placeholder.com/300x200"),
                    use_column_width=True
                )
                st.markdown(f"**{album.get('title', '')}**")
                st.caption(album.get("description", ""))
                if st.button("查看相冊", key=f"home_album_{album.get('id')}"):
                    st.session_state.selected_album_id = album.get("id")
                    st.session_state.view = "album_detail"
                    st.rerun()
    else:
        st.info("目前沒有相冊。")
    
    st.markdown("---")
    
    # 底部說明
    st.markdown(
        """
        <div style='text-align: center; color: #95a5a6; font-size: 12px; padding: 20px;'>
            未來街坊圈 © 2026 | 商務社團管理系統
        </div>
        """,
        unsafe_allow_html=True
    )

def render_login_page():
    # 商標與標題
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_URL, use_column_width=True)
    
    st.markdown("<h2 style='text-align: center; color: #2c3e50;'>會員登入</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>歡迎回來！</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("標準登入")
    login_identifier = st.text_input("📧 電子郵件或手機號碼", key="login_identifier")
    login_password = st.text_input("🔒 密碼", type="password", key="login_password")
    if st.button("登入"):
        user_data = {"identifier": login_identifier, "password": login_password}
        response = api_call("auth/login", method="POST", data=user_data)
        if "access_token" in response:
            st.session_state.user_logged_in = True
            st.session_state.access_token = response["access_token"]
            st.session_state.user_info = response.get("user_info", {})
            st.success("登入成功！")
            st.rerun()
        else:
            st.error(response.get("detail", "登入失敗，請檢查您的憑證。" ))

    st.markdown("---")
    st.subheader("微信 SSO 登入")
    wechat_id = st.text_input("微信ID / OpenID", key="wechat_id")
    wechat_nickname = st.text_input("微信暱稱 (選填)", key="wechat_nickname")
    if st.button("微信一鍵登入"):
        wechat_payload = {
            "wechat_id": wechat_id,
            "nickname": wechat_nickname or None,
        }
        response = api_call("auth/wechat_sso", method="POST", data=wechat_payload)
        if "access_token" in response:
            st.session_state.user_logged_in = True
            st.session_state.access_token = response["access_token"]
            st.session_state.user_info = response.get("user_info", {})
            st.success("微信登入成功！")
            st.rerun()
        else:
            st.error(response.get("detail", "微信登入失敗，請稍後再試。" ))

    st.markdown("---")
    st.subheader("模擬微信 OAuth 流程")
    mock_code = st.text_input("模擬 code (可任意填)", key="wechat_mock_code")
    if st.button("模擬 OAuth 登入"):
        if not mock_code.strip():
            st.error("請先輸入模擬 code")
        else:
            exchange = api_call("wechat/mock_exchange", method="POST", data={"code": mock_code})
            if "openid" in exchange:
                sso_payload = {
                    "wechat_id": exchange["openid"],
                    "nickname": wechat_nickname or "WeChat User",
                }
                response = api_call("auth/wechat_sso", method="POST", data=sso_payload)
                if "access_token" in response:
                    st.session_state.user_logged_in = True
                    st.session_state.access_token = response["access_token"]
                    st.session_state.user_info = response.get("user_info", {})
                    st.success("模擬 OAuth 登入成功！")
                    st.rerun()
                else:
                    st.error(response.get("detail", "模擬 OAuth 登入失敗。" ))
            else:
                st.error(exchange.get("detail", "模擬 exchange 失敗。"))

def render_registration_page():
    # 商標與標題
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_URL, use_column_width=True)
    
    st.markdown("<h2 style='text-align: center; color: #2c3e50;'>會員註冊</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>加入我們，開啟商務新篇章！</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    reg_email = st.text_input("📧 電子郵件", key="reg_email")
    reg_phone = st.text_input("📱 手機號碼", key="reg_phone")
    reg_username = st.text_input("👤 使用者名稱", key="reg_username")
    reg_password = st.text_input("🔒 密碼", type="password", key="reg_password")
    reg_confirm_password = st.text_input("🔒 確認密碼", type="password", key="reg_confirm_password")
    if st.button("註冊"):
        if reg_password != reg_confirm_password:
            st.error("密碼不一致，請重新輸入。" )
            return
        user_data = {
            "email": reg_email,
            "phone_number": reg_phone,
            "username": reg_username,
            "password": reg_password
        }
        response = api_call("auth/register", method="POST", data=user_data)
        if "message" in response:
            st.success(response["message"])
            st.info("請登入您的帳戶。" )
        else:
            st.error(response.get("detail", "註冊失敗，請稍後再試。" ))

def render_profile_page():
    st.title("我的個人資料")
    if "user_info" not in st.session_state or not st.session_state.user_info:
        st.warning("請先登入以查看您的個人資料。" )
        return

    user_info = st.session_state.user_info
    
    # Placeholder for profile picture upload
    profile_picture_url = user_info.get("profile_picture_url") or "https://via.placeholder.com/150"
    st.image(profile_picture_url, caption="個人頭像", use_column_width=True)
    uploaded_file = st.file_uploader("上傳新頭像", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        # In a real app, you'd upload this to a server and update the user_info
        st.success("頭像已上傳，請點擊儲存以更新。" )

    username = st.text_input("使用者名稱", value=user_info.get("username", ""), key="profile_username")
    bio = st.text_area("個人簡介", value=user_info.get("bio", ""), key="profile_bio")
    email = st.text_input("電子郵件", value=user_info.get("email", ""), key="profile_email", disabled=True)
    phone = st.text_input("手機號碼", value=user_info.get("phone_number", ""), key="profile_phone", disabled=True)

    st.subheader("隱私設定")
    privacy_public = st.checkbox("公開個人資料", value=user_info.get("is_profile_public", True), key="privacy_public")
    privacy_show_email = st.checkbox("顯示電子郵件", value=user_info.get("show_email_publicly", False), key="privacy_show_email")

    if st.button("儲存個人資料"):
        updated_info = {
            "username": username,
            "bio": bio,
            "is_profile_public": privacy_public,
            "show_email_publicly": privacy_show_email
        }
        # In a real app, you'd make an API call to update the profile
        # response = api_call(f"users/{user_info['id']}", method="PUT", data=updated_info)
        # if "message" in response:
        #     st.success(response["message"])
        #     st.session_state.user_info.update(updated_info) # Update local state
        # else:
        #     st.error(response.get("detail", "儲存個人資料失敗。" ))
        st.success("個人資料已儲存 (模擬)。" )
        st.session_state.user_info.update(updated_info) # Update local state for demo

def render_my_communities_page():
    st.title("社團資訊")
    st.markdown("---")

    if "user_info" not in st.session_state or not st.session_state.user_info:
        st.warning("以遊客身份瀏覽，可查看公告與活動。" )

    user_id = st.session_state.user_info.get("id")
    community = api_call("communities/by-name", method="GET", data={"name": FIXED_COMMUNITY_NAME})
    if community.get("error"):
        st.error(community.get("detail", "找不到固定社團，請先由後台建立。"))
        return

    st.session_state.current_community_id = community.get("id")
    st.session_state.current_community_name = community.get("name")

    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(community.get("cover_url", "https://via.placeholder.com/80"),
                 caption=community.get("name", "社團"),
                 use_column_width=True)
    with col2:
        st.subheader(community.get("name", "社團"))
        st.write(community.get("description", ""))

    if user_id:
        memberships = api_call("memberships", method="GET", data={"user_id": user_id, "community_id": community.get("id")})
        membership = memberships[0] if memberships else None
        if membership:
            st.session_state.user_role = membership.get("role", "visitor")
            st.caption(f"角色：{st.session_state.user_role}｜會籍：{membership.get('level', '一般')}｜狀態：{membership.get('status', 'active')}")
        else:
            st.session_state.user_role = "visitor"
            st.caption("角色：visitor")
    else:
        st.session_state.user_role = "visitor"
        st.caption("角色：visitor")

def render_discover_communities_page():
    st.title("發現社團")
    search_term = st.text_input("搜尋社團...", key="discover_search")
    
    categories = ["技術", "興趣", "學習", "遊戲", "藝術"]
    selected_category = st.selectbox("分類", ["所有分類"] + categories, key="discover_category")

    st.subheader("推薦社團")

    communities_to_display = api_call("communities", method="GET") or []
    if search_term:
        communities_to_display = [
            c for c in communities_to_display
            if search_term.lower() in (c.get("name", "").lower())
        ]

    cols = st.columns(3)
    for i, community in enumerate(communities_to_display):
        with cols[i % 3]:
            card(
                community.get("name", "社團"),
                community.get("description", ""),
                "推薦",
                "加入",
                key=f"discover_join_{community.get('id', i)}",
            )

    st.markdown("---")
    st.subheader("所有社團")
    # More community cards can be displayed here, fetched from backend

def render_messages_page():
    st.title("訊息")
    st.warning("訊息功能正在開發中。" )
    # This section would typically involve a list of conversations and a chat interface.
    # You would fetch conversations and messages from the backend API.

def render_settings_page():
    st.title("設定")
    st.subheader("通知設定")
    st.checkbox("接收新訊息通知", value=True, key="notif_messages")
    st.checkbox("接收社團動態通知", value=True, key="notif_community_updates")
    st.checkbox("接收提及通知", value=True, key="notif_mentions")
    
    st.subheader("帳戶設定")
    if st.button("變更密碼"):
        st.info("變更密碼功能正在開發中。" )
    if st.button("刪除帳戶"):
        st.warning("刪除帳戶功能正在開發中。請謹慎操作。" )

def render_admin_page():
    st.title("後台管理")
    communities = api_call("communities", method="GET") or []
    community_options = {f"{c.get('name', '社團')} (ID: {c.get('id')})": c.get("id") for c in communities}
    selected_community_id = None
    if community_options:
        selected_label = st.selectbox("選擇社團", list(community_options.keys()), key="admin_select_community")
        selected_community_id = community_options[selected_label]

    tabs = st.tabs(["會員管理", "公告管理", "活動管理", "相冊管理"])

    with tabs[0]:
        st.subheader("會員管理")
        users = api_call("users", method="GET") or []
        memberships = api_call("memberships", method="GET", data={"community_id": selected_community_id}) if selected_community_id else []
        if users:
            st.caption(f"目前會員數：{len(users)}")
            st.dataframe(users)

        if selected_community_id:
            st.caption("社團會籍")
            if memberships:
                st.dataframe(memberships)

            with st.expander("新增會籍"):
                user_ids = [u.get("id") for u in users]
                user_id = st.selectbox("選擇會員", user_ids, key="admin_membership_user")
                membership_no = st.text_input("會員編號", key="admin_membership_no")
                level = st.text_input("會籍等級", key="admin_membership_level")
                role = st.selectbox("角色", ["visitor", "member", "staff"], key="admin_membership_role")
                expires_at = st.text_input("到期日 (YYYY-MM-DD)", key="admin_membership_expires")
                if st.button("新增會籍"):
                    payload = {
                        "user_id": user_id,
                        "community_id": selected_community_id,
                        "membership_no": membership_no or None,
                        "level": level or None,
                        "role": role,
                        "expires_at": expires_at or None,
                    }
                    response = api_call("memberships", method="POST", data=payload)
                    if "id" in response:
                        st.success("會籍已新增")
                        st.rerun()
                    else:
                        st.error(response.get("detail", "新增會籍失敗。"))

    with tabs[1]:
        st.subheader("公告管理")
        if selected_community_id:
            announcements = api_call("announcements", method="GET", data={"community_id": selected_community_id}) or []
            if announcements:
                st.dataframe(announcements)
            with st.expander("新增公告"):
                title = st.text_input("標題", key="admin_announcement_title")
                content = st.text_area("內容", key="admin_announcement_content")
                is_pinned = st.checkbox("置頂", key="admin_announcement_pinned")
                if st.button("新增公告"):
                    payload = {"community_id": selected_community_id, "title": title, "content": content, "is_pinned": is_pinned}
                    response = api_call(f"announcements?created_by={st.session_state.user_info.get('id')}", method="POST", data=payload)
                    if "id" in response:
                        st.success("公告已新增")
                        st.rerun()
                    else:
                        st.error(response.get("detail", "新增公告失敗。"))

    with tabs[2]:
        st.subheader("活動管理")
        if selected_community_id:
            events = api_call("events", method="GET", data={"community_id": selected_community_id}) or []
            if events:
                st.dataframe(events)
            with st.expander("新增活動"):
                title = st.text_input("活動名稱", key="admin_event_title")
                description = st.text_area("活動描述", key="admin_event_description")
                start_at = st.text_input("開始時間", key="admin_event_start_at")
                end_at = st.text_input("結束時間", key="admin_event_end_at")
                location = st.text_input("地點", key="admin_event_location")
                capacity = st.number_input("名額", min_value=0, value=0, key="admin_event_capacity")
                if st.button("新增活動"):
                    payload = {
                        "community_id": selected_community_id,
                        "title": title,
                        "description": description,
                        "start_at": start_at,
                        "end_at": end_at or None,
                        "location": location,
                        "capacity": int(capacity) if capacity else None,
                        "is_public": True,
                    }
                    response = api_call(f"events?created_by={st.session_state.user_info.get('id')}", method="POST", data=payload)
                    if "id" in response:
                        st.success("活動已新增")
                        st.rerun()
                    else:
                        st.error(response.get("detail", "新增活動失敗。"))

    with tabs[3]:
        st.subheader("相冊管理")
        if selected_community_id:
            albums = api_call("albums", method="GET", data={"community_id": selected_community_id}) or []
            if albums:
                st.dataframe(albums)
            with st.expander("新增相冊"):
                title = st.text_input("相冊名稱", key="admin_album_title")
                description = st.text_area("相冊描述", key="admin_album_description")
                cover_url = st.text_input("封面 URL", key="admin_album_cover")
                if st.button("新增相冊"):
                    payload = {"community_id": selected_community_id, "title": title, "description": description, "cover_url": cover_url or None}
                    response = api_call(f"albums?created_by={st.session_state.user_info.get('id')}", method="POST", data=payload)
                    if "id" in response:
                        st.success("相冊已新增")
                        st.rerun()
                    else:
                        st.error(response.get("detail", "新增相冊失敗。"))

def render_community_announcements(community_id, user_role, user_id):
    st.subheader("活動公告")

    if user_role == "staff":
        with st.expander("發布公告"):
            title = st.text_input("公告標題", key="announcement_title")
            content = st.text_area("公告內容", key="announcement_content")
            is_pinned = st.checkbox("置頂公告", key="announcement_pinned")
            if st.button("發布公告"):
                payload = {
                    "community_id": community_id,
                    "title": title,
                    "content": content,
                    "is_pinned": is_pinned,
                }
                response = api_call(f"announcements?created_by={user_id}", method="POST", data=payload)
                if "id" in response:
                    st.success("公告已發布！")
                    st.rerun()
                else:
                    st.error(response.get("detail", "發布公告失敗。"))

    announcements = api_call("announcements", method="GET", data={"community_id": community_id}) or []
    
    if announcements:
        for item in announcements:
            pinned_style = "border-left: 5px solid #f39c12;" if item.get("is_pinned") else "border-left: 5px solid #3498db;"
            pinned_label = "📌 置頂" if item.get("is_pinned") else ""
            
            st.markdown(
                f"""
                <div style='padding: 20px; background-color: #f8f9fa; border-radius: 10px; 
                            {pinned_style} margin-bottom: 15px;'>
                    <h3 style='color: #2c3e50; margin: 0;'>{pinned_label} {item.get('title', '')}</h3>
                    <p style='color: #34495e; margin: 10px 0;'>{item.get('content', '')}</p>
                    <p style='color: #95a5a6; font-size: 12px; margin: 0;'>📅 {item.get('created_at', '')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("目前沒有公告。")

def render_community_events(community_id, user_role, user_id):
    st.subheader("活動")

    if user_role == "staff":
        with st.expander("新增活動"):
            title = st.text_input("活動名稱", key="event_title")
            description = st.text_area("活動描述", key="event_description")
            start_at = st.text_input("開始時間 (YYYY-MM-DD HH:MM)", key="event_start_at")
            end_at = st.text_input("結束時間 (YYYY-MM-DD HH:MM)", key="event_end_at")
            location = st.text_input("地點", key="event_location")
            capacity = st.number_input("名額", min_value=0, value=0, key="event_capacity")
            if st.button("建立活動"):
                payload = {
                    "community_id": community_id,
                    "title": title,
                    "description": description,
                    "start_at": start_at,
                    "end_at": end_at or None,
                    "location": location,
                    "capacity": int(capacity) if capacity else None,
                    "is_public": True,
                }
                response = api_call(f"events?created_by={user_id}", method="POST", data=payload)
                if "id" in response:
                    st.success("活動已建立！")
                    st.rerun()
                else:
                    st.error(response.get("detail", "建立活動失敗。"))

    events = api_call("events", method="GET", data={"community_id": community_id}) or []
    
    if events:
        for event in events:
            st.markdown(
                f"""
                <div style='padding: 20px; background-color: #fff3cd; border-radius: 10px; 
                            border-left: 5px solid #ffc107; margin-bottom: 15px;'>
                    <h3 style='color: #2c3e50; margin: 0;'>🎉 {event.get('title', '')}</h3>
                    <p style='color: #34495e; margin: 10px 0;'>{event.get('description', '')}</p>
                    <p style='color: #7f8c8d; font-size: 14px; margin: 5px 0;'>📅 {event.get('start_at', '')} ~ {event.get('end_at', '')}</p>
                    <p style='color: #7f8c8d; font-size: 14px; margin: 5px 0;'>📍 {event.get('location', '')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("報名活動", key=f"event_register_{event.get('id')}"):
                payload = {"event_id": event.get("id"), "user_id": user_id}
                response = api_call(f"events/{event.get('id')}/register", method="POST", data=payload)
                if "id" in response:
                    st.success("報名成功！")
                else:
                    st.error(response.get("detail", "報名失敗。"))
            st.markdown("---")
    else:
        st.info("目前沒有活動。")

def render_community_albums(community_id, user_role, user_id):
    st.subheader("活動相冊")

    if user_role == "staff":
        with st.expander("建立相冊"):
            title = st.text_input("相冊名稱", key="album_title")
            description = st.text_area("相冊描述", key="album_description")
            cover_url = st.text_input("封面圖片 URL", key="album_cover_url")
            if st.button("建立相冊"):
                payload = {
                    "community_id": community_id,
                    "title": title,
                    "description": description,
                    "cover_url": cover_url or None,
                }
                response = api_call(f"albums?created_by={user_id}", method="POST", data=payload)
                if "id" in response:
                    st.success("相冊已建立！")
                    st.rerun()
                else:
                    st.error(response.get("detail", "建立相冊失敗。"))

    albums = api_call("albums", method="GET", data={"community_id": community_id}) or []
    
    if albums:
        # 以卡片形式展示相冊
        cols = st.columns(3)
        for idx, album in enumerate(albums):
            with cols[idx % 3]:
                st.image(
                    album.get("cover_url", "https://via.placeholder.com/300x200"),
                    use_column_width=True
                )
                st.markdown(f"**{album.get('title', '')}**")
                st.caption(album.get("description", ""))
                if st.button("查看", key=f"album_view_{album.get('id')}"):
                    st.session_state.selected_album_id = album.get("id")
                    st.session_state.view = "album_detail"
                    st.rerun()
    else:
        st.info("目前沒有相冊。")

def render_community_view():
    community_name = st.session_state.get("current_community_name", "未選取社團")
    community_id = st.session_state.get("current_community_id")

    # 頂部橫幅
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_URL, use_column_width=True)
    
    # 社團標題卡片
    st.markdown(
        f"""
        <div style='padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; color: white; margin-bottom: 25px; text-align: center;'>
            <h1 style='color: white; margin: 0;'>{community_name}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")

    # Fetch community details and user role from backend
    # For now, using placeholder roles and data
    user_role = st.session_state.get("user_role", "member") # Example role

    if user_role in ["admin", "moderator"]:
        st.subheader("社團管理")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("管理成員"):
                st.info("管理成員功能正在開發中。" )
        with col2:
            if st.button("編輯社團資訊"):
                st.info("編輯社團資訊功能正在開發中。" )
        with col3:
            if st.button("設定社團規則"):
                st.info("設定社團規則功能正在開發中。" )
        st.markdown("---")

    user_info = st.session_state.user_info or {}
    user_id = user_info.get("id")

    if user_role == "visitor":
        tabs = st.tabs(["公告", "活動"])
        with tabs[0]:
            render_community_announcements(community_id, user_role, user_id)
        with tabs[1]:
            render_community_events(community_id, user_role, user_id)
    elif user_role == "member":
        tabs = st.tabs(["公告", "活動", "相冊"])
        with tabs[0]:
            render_community_announcements(community_id, user_role, user_id)
        with tabs[1]:
            render_community_events(community_id, user_role, user_id)
        with tabs[2]:
            render_community_albums(community_id, user_role, user_id)
    else:  # staff
        tabs = st.tabs(["公告", "活動", "相冊"])
        with tabs[0]:
            render_community_announcements(community_id, user_role, user_id)
        with tabs[1]:
            render_community_events(community_id, user_role, user_id)
        with tabs[2]:
            render_community_albums(community_id, user_role, user_id)

def render_post(post_data):
    with st.container():
        if post_data.get("pinned", False):
            st.warning("📌 置頂")
        st.markdown(f"**{post_data['author']}** - {post_data['timestamp']}")
        st.write(post_data['content'])
        # Example image, in a real app, this would be from the post data
        if "image_url" in post_data:
            st.image(post_data["image_url"], caption="範例圖片", use_column_width=True, output_format="PNG")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button(f"👍 讚 ({post_data['likes']})")
        with col2:
            st.button(f"💬 評論 ({post_data['comments']})")
        with col3:
            st.button("🔗 分享")
        
        with st.expander("查看評論"):
            st.text_area("留下您的評論...", key=f"comment_{post_data['timestamp']}") # Unique key for each comment input
            if st.button("發佈評論"):
                st.success("評論已發佈！" )
            
            st.markdown("---")
            # Example comments, fetch from backend
            st.markdown("**使用者C** - 2023-10-27 11:00 AM")
            st.write("很棒的分享！")

# --- Helper Functions for UI Elements ---
def card(title, description, tag, action_text, key=None):
    with st.container():
        st.subheader(title)
        st.write(description)
        st.markdown(f"**標籤:** {tag}")
        button_key = key or f"card_action_{title}_{tag}_{action_text}"
        if st.button(action_text, key=button_key):
            # In a real app, this would trigger a join/apply request to the backend
            st.success(f"您已點擊 '{action_text}' 按鈕於 '{title}'。" )

# --- Main App Logic ---
def app():
    st.set_page_config(layout="wide", page_title="未來街坊圈", page_icon="🏢")
    
    # 自定義 CSS 樣式
    st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ecf0f1;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3498db;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Sidebar for Navigation ---
    with st.sidebar:
        st.image(LOGO_URL, use_column_width=True)
        st.title("未來街坊圈")
        st.markdown("---")

        # User Authentication/Profile Section
        st.header("帳戶")
        if "user_logged_in" not in st.session_state or not st.session_state.user_logged_in:
            menu_options = ["首頁", "登入", "註冊"]
            selected_option = st.radio("導航", menu_options, key="sidebar_radio_auth")
        else:
            menu_options = ["首頁", "我的個人資料", "社團資訊", "訊息", "設定"]
            if st.session_state.get("user_role") == "staff":
                menu_options.append("後台管理")
            selected_option = st.radio("導航", menu_options, key="sidebar_radio_main")
        
        st.markdown("---")
        if "user_logged_in" in st.session_state and st.session_state.user_logged_in:
            if st.button("登出"):
                # Clear session state related to login
                st.session_state.user_logged_in = False
                st.session_state.access_token = None
                st.session_state.user_info = None
                st.session_state.current_community_id = None
                st.session_state.current_community_name = None
                st.rerun()

    # --- Main Content Area ---
    # 檢查是否需要顯示特殊視圖
    if "view" in st.session_state and st.session_state.view == "album_detail":
        render_album_detail_page()
    elif selected_option == "首頁":
        render_home_page()
    elif "user_logged_in" not in st.session_state or not st.session_state.user_logged_in:
        if selected_option == "登入":
            render_login_page()
        elif selected_option == "註冊":
            render_registration_page()
    else:
        if selected_option == "我的個人資料":
            render_profile_page()
        elif selected_option == "社團資訊":
            render_my_communities_page()
        elif selected_option == "訊息":
            render_messages_page()
        elif selected_option == "設定":
            render_settings_page()
        elif selected_option == "後台管理":
            render_admin_page()

# --- Initial State Setup ---
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "view" not in st.session_state:
    st.session_state.view = "login"
if "current_community_id" not in st.session_state:
    st.session_state.current_community_id = None
if "current_community_name" not in st.session_state:
    st.session_state.current_community_name = None
if "user_role" not in st.session_state: # Example role, would be fetched from backend
    st.session_state.user_role = "member"

# --- Main App Execution ---
if st.session_state.current_community_id:
    render_community_view()
else:
    app()
