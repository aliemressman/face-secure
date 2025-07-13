import os
import streamlit as st
from dotenv import load_dotenv
import bcrypt

load_dotenv()
print(bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode())

def check_admin_login():
    if st.session_state.get("admin_logged_in"):
        return True

    st.markdown("### 🔐 Admin Giriş")
    username = st.text_input("👤 Kullanıcı Adı")
    password = st.text_input("🔑 Parola", type="password")
    login_btn = st.button("🔓 Giriş Yap")

    real_username = os.getenv("ADMIN_USERNAME")
    real_password_hash = os.getenv("ADMIN_PASSWORD_HASH")

    if login_btn:
        if username == real_username and bcrypt.checkpw(password.encode(), real_password_hash.encode()):
            st.success("✅ Giriş başarılı")
            st.session_state["admin_logged_in"] = True
            st.rerun()
            return True
        else:
            st.error("❌ Kullanıcı adı veya parola hatalı")

    return False
