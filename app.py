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

    # Compact Custom CSS για να χωράει η φόρμα χωρίς scroll
    st.markdown("""
        <style>
        @import url('https://fonts.cdnfonts.com/css/pp-pangram-sans');

        /* Μείωση περιθωρίων κύριας σελίδας */
        .main .block-container {
            padding-top: 2rem !important;
            padding-bottom: 1rem !important;
        }

        /* Compact Φόντο/Περίγραμμα Login Form */
        div[data-testid="stForm"] {
            background-color: #0E1A1F !important;
            border: 2px solid #09A1A4 !important;
            border-radius: 12px !important;
            padding: 20px 25px !important;
            box-shadow: 0 0 15px rgba(9, 161, 164, 0.2) !important;
            max-width: 400px;
            margin: 0 auto;
        }

        /* Περιορισμός μεγέθους Logo */
        div[data-testid="stForm"] img {
            max-height: 55px !important;
            width: auto !important;
            display: block;
            margin: 0 auto;
        }

        .login-title {
            color: #09A1A4 !important;
            font-family: 'PP Pangram Sans', sans-serif !important;
            font-weight: 700 !important;
            font-size: 18px !important;
            text-transform: uppercase !important;
            text-align: center !important;
            letter-spacing: 2px !important;
            margin-top: 10px !important;
            margin-bottom: 2px !important;
        }

        .login-subtitle {
            color: #8A9BA8 !important;
            font-family: 'PP Pangram Sans', sans-serif !important;
            text-align: center !important;
            font-size: 12px !important;
            margin-bottom: 15px !important;
        }

        /* Styling Κουμπιού Connect */
        div[data-testid="stForm"] button[type="submit"] {
            background-color: #09A1A4 !important;
            color: #FFFFFF !important;
            font-weight: bold !important;
            border-radius: 6px !important;
            border: none !important;
            width: 100% !important;
            padding: 8px !important;
            margin-top: 5px !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="stForm"] button[type="submit"]:hover {
            background-color: #2FDDC0 !important;
            color: #112229 !important;
            box-shadow: 0 0 10px rgba(47, 221, 192, 0.4) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form"):
            try:
                st.image("WEST_logo.png")
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
# 3. ΔΥΝΑΜΙΚΗ ΦΟΡΤΩΣΗ ΤΟΥ ΑΝΤΙΣΤΟΙΧΟΥ DASHBOARD CODE
# ---------------------------------------------------------
module_name = st.session_state.get("module_path")

try:
    dashboard_module = importlib.import_module(module_name)
    dashboard_module.run()
except Exception as e:
    st.error(f"⚠️ Αδυναμία φόρτωσης του Dashboard: {e}")

# ---------------------------------------------------------
# 4. SIDEBAR LOG OUT (ΚΑΤΩ ΑΠΟ ΤΑ ΦΙΛΤΡΑ)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("---")
    st.write(f"👤 **Connected as:** {st.session_state.get('current_user')}")
    if st.button("🚪 Log Out", type="secondary", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None
        st.session_state["module_path"] = None
        st.session_state["sheet_id"] = None
        st.rerun()
