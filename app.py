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
        st.session_state["is_admin"] = False

    if st.session_state["authenticated"]:
        return True

    # Custom CSS για την οθόνη Login
    st.markdown("""
        <style>
        @import url('https://fonts.cdnfonts.com/css/pp-pangram-sans');

        .main .block-container {
            padding-top: 2rem !important;
            padding-bottom: 1rem !important;
        }

        div[data-testid="stForm"] {
            background-color: #0A1318 !important;
            border: 2px solid #10385C !important;
            border-radius: 12px !important;
            padding: 20px 25px !important;
            box-shadow: 0 0 20px rgba(16, 56, 92, 0.4) !important;
            max-width: 400px;
            margin: 0 auto;
        }

        div[data-testid="stForm"] img {
            max-height: 55px !important;
            width: auto !important;
            display: block;
            margin: 0 auto !important;
        }

        .login-title {
            color: #21619A !important;
            font-family: 'PP Pangram Sans', sans-serif !important;
            font-weight: 700 !important;
            font-size: 19px !important;
            text-transform: uppercase !important;
            text-align: center !important;
            letter-spacing: 2px !important;
            margin-top: 8px !important;
            margin-bottom: 2px !important;
        }

        .login-subtitle {
            color: #6C8294 !important;
            font-family: 'PP Pangram Sans', sans-serif !important;
            text-align: center !important;
            font-size: 12px !important;
            margin-bottom: 15px !important;
        }

        div[data-testid="stForm"] button[type="submit"] {
            background-color: #10385C !important;
            color: #FFFFFF !important;
            font-weight: bold !important;
            border-radius: 6px !important;
            border: 1px solid #1B4D7E !important;
            width: 100% !important;
            padding: 8px !important;
            margin-top: 5px !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="stForm"] button[type="submit"]:hover {
            background-color: #1B4D7E !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 12px rgba(27, 77, 126, 0.6) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    login_placeholder = st.empty()

    with login_placeholder.container():
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            with st.form("login_form"):
                logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])
                with logo_col2:
                    try:
                        st.image("WEST_logo.png", use_container_width=True)
                    except Exception:
                        pass

                st.markdown('<div class="login-title">Analytics</div>', unsafe_allow_html=True)
                st.markdown('<div class="login-subtitle">Please enter your credentials to access your dashboard</div>', unsafe_allow_html=True)

                username_input = st.text_input("Username:").strip()
                password_input = st.text_input("Password:", type="password").strip()
                submit_button = st.form_submit_button("Connect")

                if submit_button:
                    users_db = st.secrets.get("users", {})

                    matched_user_key = None
                    for key in users_db:
                        if key.upper() == username_input.upper():
                            matched_user_key = key
                            break

                    if matched_user_key:
                        user_info = users_db[matched_user_key]
                        if password_input == user_info.get("password"):
                            login_placeholder.empty()

                            st.session_state["authenticated"] = True
                            st.session_state["current_user"] = matched_user_key
                            
                            # Έλεγχος αν ο χρήστης είναι Admin
                            is_admin = user_info.get("role") == "admin" or matched_user_key.lower() == "admin"
                            st.session_state["is_admin"] = is_admin

                            if not is_admin:
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
# 3. ADMIN SWITCHER (DROPDOWN ΓΙΑ ADMIN)
# ---------------------------------------------------------
users_db = st.secrets.get("users", {})

if st.session_state.get("is_admin"):
    # Φιλτράρισμα μόνο των κανονικών πελατών (εξαιρείται ο admin)
    client_keys = [k for k, v in users_db.items() if v.get("role") != "admin" and k.lower() != "admin"]
    
    if client_keys:
        selected_client = st.sidebar.selectbox(
            "👑 Select Client (Admin View):",
            options=client_keys,
            index=0
        )
        # Ενημέρωση των στοιχείων για τον επιλεγμένο πελάτη
        client_info = users_db[selected_client]
        st.session_state["module_path"] = client_info.get("module")
        st.session_state["sheet_id"] = client_info.get("sheet_id")
        st.session_state["display_title"] = client_info.get("display_name", "DECLUTTERING DASHBOARD")
        st.sidebar.divider()
    else:
        st.sidebar.warning("⚠️ Δεν βρέθηκαν διαθέσιμοι πελάτες στα Secrets.")

# ---------------------------------------------------------
# 4. ΔΥΝΑΜΙΚΗ ΦΟΡΤΩΣΗ ΤΟΥ ΑΝΤΙΣΤΟΙΧΟΥ DASHBOARD CODE
# ---------------------------------------------------------
module_name = st.session_state.get("module_path")

if module_name:
    try:
        with st.spinner("⏳ Loading Dashboard... Please wait."):
            dashboard_module = importlib.import_module(module_name)
            dashboard_module.run()
    except Exception as e:
        st.error(f"⚠️ Αδυναμία φόρτωσης του Dashboard: {e}")
else:
    st.warning("⚠️ Δεν έχει οριστεί Dashboard module για αυτόν τον χρήστη.")

# ---------------------------------------------------------
# 5. SIDEBAR LOG OUT (ΚΑΤΩ ΑΠΟ ΤΑ ΦΙΛΤΡΑ)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("---")
    st.write(f"👤 **Connected as:** {st.session_state.get('current_user')}")
    if st.button("🚪 Log Out", type="secondary", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None
        st.session_state["is_admin"] = False
        st.session_state["module_path"] = None
        st.session_state["sheet_id"] = None
        st.rerun()
