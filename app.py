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

    # Custom CSS για την οθόνη Login
    st.markdown("""
        <style>
        @import url('https://fonts.cdnfonts.com/css/pp-pangram-sans');

        /* Κεντράρισμα και Μπλε Φόντο/Περίγραμμα Login Form */
        div[data-testid="stForm"] {
            background-color: #0E1A1F !important;
            border: 2px solid #09A1A4 !important;
            border-radius: 15px !important;
            padding: 35px 30px !important;
            box-shadow: 0 0 20px rgba(9, 161, 164, 0.25) !important;
            max-width: 450px;
            margin: 0 auto;
        }

        .login-title {
            color: #09A1A4 !important;
            font-family: 'PP Pangram Sans', sans-serif !important;
            font-weight: 700 !important;
            font-size: 22px !important;
            text-transform: uppercase !important;
            text-align: center !important;
            letter-spacing: 3px !important;
            margin-top: 15px !important;
            margin-bottom: 5px !important;
        }

        .login-subtitle {
            color: #8A9BA8 !important;
            font-family: 'PP Pangram Sans', sans-serif !important;
            text-align: center !important;
            font-size: 13px !important;
            margin-bottom: 25px !important;
        }

        /* Styling Κουμπιού Connect σε Μπλε Τόνους */
        div[data-testid="stForm"] button[type="submit"] {
            background-color: #09A1A4 !important;
            color: #FFFFFF !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            border: none !important;
            width: 100% !important;
            padding: 10px !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="stForm"] button[type="submit"]:hover {
            background-color: #2FDDC0 !important;
            color: #112229 !important;
            box-shadow: 0 0 12px rgba(47, 221, 192, 0.4) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Στήλες για κεντράρισμα της φόρμας login στην οθόνη
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form"):
            # WEST LOGO (Χωρίς διπλό τίτλο West)
            try:
                st.image("WEST_logo.png", use_container_width=True)
            except Exception:
                pass

            st.markdown('<div class="login-title">Analytics Portal</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-subtitle">Please enter your credentials to access your dashboard</div>', unsafe_allow_html=True)

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
# 3. ΔΥΝΑΜΙΚΗ ΦOΡΤΩΣΗ ΤOΥ ΑΝΤΙΣΤOΙΧOΥ DASHBOARD CODE
# ---------------------------------------------------------
module_name = st.session_state.get("module_path")

try:
    # Φορτώνει δυναμικά το Python αρχείο που αντιστοιχεί στον χρήστη (π.χ. allwyn.py)
    dashboard_module = importlib.import_module(module_name)

    # Εκτελεί τη συνάρτηση run() από το συγκεκριμένο αρχείο (εκεί φορτώνονται τα φίλτρα)
    dashboard_module.run()

except Exception as e:
    st.error(f"⚠️ Αδυναμία φόρτωσης του Dashboard: {e}")

# ---------------------------------------------------------
# 4. SIDEBAR LOG OUT (ΜΠΑΙΝΕΙ ΚΑΤΩ ΑΠO ΤΑ ΦΙΛΤΡΑ)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("---")
    st.write(f"👤 **Connected as:** {st.session_state.get('current_user')}")
    if st.button("🚪 Log Out", type="secondary", use_container_width=True):
        # Καθαρισμός του session state
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None
        st.session_state["module_path"] = None
        st.session_state["sheet_id"] = None
        st.rerun()  # Επαναφορά στην οθόνη Login
