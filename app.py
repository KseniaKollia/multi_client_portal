import streamlit as st
import importlib

# ---------------------------------------------------------
# 1. ΒΑΣΙΚΗ ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ
# ---------------------------------------------------------
st.set_page_config(
    page_title="West Analytics",
    layout="wide",
    page_icon="📈"
)

# ---------------------------------------------------------
# 2. ΕΛΕΓΧΟΣ ΣΥΝΔΕΣΗΣ (LOGIN SYSTEM)
# ---------------------------------------------------------
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None

    if st.session_state["authenticated"]:
        return True

    st.title("🔒 Client Access")
    st.write("Please enter your credentials to access your dashboard.")
    
    with st.form("login_form"):
        username_input = st.text_input("Username:").strip()
        password_input = st.text_input("Password:", type="password").strip()
        submit_button = st.form_submit_button("Connect")
        
        if submit_button:
            users_db = st.secrets.get("users", {})
            
            # Case-insensitive έλεγχος για το Username
            matched_user_key = None
            for key in users_db:
                if key.upper() == username_input.upper():
                    matched_user_key = key
                    break

            if matched_user_key:
                user_info = users_db[matched_user_key]
                if password_input == user_info.get("password"):
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"] = matched_user_key
                    st.session_state["module_path"] = user_info.get("module")
                    st.session_state["sheet_id"] = user_info.get("sheet_id")
                    st.session_state["display_title"] = user_info.get("display_name", "DECLUTTERING DASHBOARD")
                    st.rerun()
                else:
                    st.error("🚨 Wrong password.")
            else:
                st.error("🚨 Invalid username or password.")
    return False

if not check_password():
    st.stop()

# ---------------------------------------------------------
# 3. SIDEBAR (LOG OUT & ΣΤΟΙΧΕΙΑ ΧΡΗΣΤΗ)
# ---------------------------------------------------------
with st.sidebar:
    st.write(f"👤 **Connected as:** {st.session_state.get('current_user')}")
    if st.button("🚪 Log Out", type="secondary"):
        # Καθαρισμός του session state
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None
        st.session_state["module_path"] = None
        st.session_state["sheet_id"] = None
        st.rerun()  # Επαναφορά στην οθόνη Login

st.sidebar.divider()

# ---------------------------------------------------------
# 4. ΔΥΝΑΜΙΚΗ ΦΟΡΤΩΣΗ ΤΟΥ ΑΝΤΙΣΤΟΙΧΟΥ DASHBOARD CODE
# ---------------------------------------------------------
module_name = st.session_state.get("module_path")

try:
    # Φορτώνει δυναμικά το Python αρχείο που αντιστοιχεί στον χρήστη
    dashboard_module = importlib.import_module(module_name)
    
    # Εκτελεί τη συνάρτηση run() από το συγκεκριμένο αρχείο
    dashboard_module.run()
    
except Exception as e:
    st.error(f"⚠️ Αδυναμία φόρτωσης του Dashboard: {e}")
