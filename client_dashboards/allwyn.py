import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse
import unicodedata
import hashlib
from streamlit_autorefresh import st_autorefresh

# ---------------------------------------------------------
# 1. CSS DESIGN & STYLES (ΧΩΡΙΣ st.set_page_config)
# ---------------------------------------------------------
def apply_custom_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.cdnfonts.com/css/pp-pangram-sans');

        /* 1. ΕΞΑΦΑΝΙΣΗ ΜOΝO ΤΩΝ ΚOΥΜΠΙΩΝ GITHUB / FORK / SHARE / MENU */
        [data-testid="stHeaderActionElements"],
        div[data-testid="stToolbar"] > div:nth-child(2),
        button[title="View source code on GitHub"],
        #MainMenu {
            display: none !important;
            visibility: hidden !important;
        }

        /* 2. ΚΡΑΤΑΜΕ ΤO HEADER ΔΙΑΦΑΝΕΣ ΚΑΙ ΤO ΚOΥΜΠΙ ΤOΥ SIDEBAR ΕΝΕΡΓO */
        header[data-testid="stHeader"] {
            background: transparent !important;
        }
        
        [data-testid="stSidebarCollapsedControl"] {
            display: block !important;
            visibility: visible !important;
            color: #2FDDC0 !important;
            background-color: #1A333D !important;
            border-radius: 5px !important;
            border: 1px solid #2FDDC0 !important;
            z-index: 999999 !important;
        }

        footer { visibility: hidden !important; }

        .stApp { background-color: #112229; color: #FFFFFF; }

        .main .block-container {
            border: 2px solid #2FDDC0 !important;
            border-radius: 15px !important;
            padding: 30px !important;
            margin-top: 15px !important;
            background-color: #112229 !important;
            box-shadow: 0 0 15px rgba(47, 221, 192, 0.2) !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.header-text-style) {
            background-color: #1A333D !important;
            padding: 15px 20px !important;
            align-items: center !important;
            border-radius: 10px !important;
            border: 1px solid #2FDDC0 !important;
        }
        .header-text-style {
            color: #2FDDC0 !important;
            font-family: 'PP Pangram Sans', 'Pangram', sans-serif !important;
            font-weight: 600 !important;
            font-size: 26px !important;
            text-transform: uppercase !important;
            text-align: center !important;
            letter-spacing: 2px !important;
            margin: 0 !important;
            padding: 0 !important;
            display: block !important;
            width: 100% !important;
        }
        [data-testid="stSidebar"] { background-color: #0E1A1F !important; }
        [data-testid="stSidebar"] *, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] label p,
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {
            color: #09A1A4 !important;
            font-weight: bold !important;
        }
        [data-testid="stSidebar"] div[data-baseweb="select"] > div { 
            background-color: #1A333D !important; 
            border: 1px solid #09A1A4 !important;
        }
        [data-testid="stSidebar"] div[data-baseweb="select"] span { color: #FFFFFF !important; }
        [data-testid="stMetric"] { 
            background-color: #1A333D !important; 
            padding: 15px !important; 
            border-radius: 8px !important; 
            border: 2px solid #2FDDC0 !important;
        }
        [data-testid="stMetricLabel"] p { color: #2FDDC0 !important; font-weight: bold; }
        [data-testid="stMetricValue"] div { color: #FFFFFF !important; }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, 
        .stApp label, .stApp p, .stApp span { color: #FFFFFF; }
        </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS ΓΙΑ DATA FETCHING
# ---------------------------------------------------------
def fetch_raw_csv(sheet_id, worksheet_name):
    encoded_sheet_name = urllib.parse.quote(worksheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    return pd.read_csv(url)

@st.cache_data(ttl=5, show_spinner=False)
def get_sheet_data_smart(sheet_id, worksheet_name):
    df = fetch_raw_csv(sheet_id, worksheet_name)
    df.columns = [str(c).strip() for c in df.columns]
    data_hash = hashlib.md5(pd.util.hash_pandas_object(df, index=True).values).hexdigest()
    return df, data_hash

@st.fragment
def background_sheet_checker(sheet_id):
    st_autorefresh(interval=10000, key="background_refresh_timer")
    try:
        _, hash_opap = get_sheet_data_smart(sheet_id, "OPAP ΕΡΩΤΗΣΗ 2000")
        _, hash_stores = get_sheet_data_smart(sheet_id, "STORE STATUS (WEEKLY)")
        current_combined_hash = f"{hash_opap}_{hash_stores}"

        if "last_data_hash" in st.session_state:
            if st.session_state["last_data_hash"] != current_combined_hash:
                st.session_state["last_data_hash"] = current_combined_hash
                st.cache_data.clear()
                st.rerun()
        else:
            st.session_state["last_data_hash"] = current_combined_hash
    except Exception:
        pass

def normalize_string(val):
    if pd.isna(val):
        return ""
    val = str(val).upper().strip().replace("O", "Ο")
    nfkd = unicodedata.normalize('NFKD', val)
    val = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return " ".join(val.split())

# ---------------------------------------------------------
# 3. ΚΥΡΙΑ ΣΥΝΑΡΤΗΣΗ ΕΚΤΕΛΕΣΗΣ (RUN)
# ---------------------------------------------------------
def run():
    apply_custom_styles()

    # Διαβάζουμε το SHEET_ID και τον Τίτλο που ορίστηκαν στο app.py
    sheet_id = st.session_state.get("sheet_id", "1Aw83hnkXT8yaXkKbpVAiCTx7AXT0Z-GXgAwS6r1itNs")
    display_title = st.session_state.get("display_title", "ALLWYN / OPAP DECLUTTERING DASHBOARD")

    background_sheet_checker(sheet_id)

    try:
        df_opap, _ = get_sheet_data_smart(sheet_id, "OPAP ΕΡΩΤΗΣΗ 2000")
        df_stores, _ = get_sheet_data_smart(sheet_id, "STORE STATUS (WEEKLY)")
    except Exception as e:
        st.error(f"Error loading Google Sheet: {e}")
        st.stop()

    if "DATE" in df_opap.columns:
        df_opap["DATE_DT"] = pd.to_datetime(df_opap["DATE"], format="%d/%m/%Y", errors='coerce')
        df_opap["DATE_DT"] = df_opap["DATE_DT"].fillna(pd.to_datetime(df_opap["DATE"], dayfirst=True, errors='coerce'))
        df_opap["MONTH"] = df_opap["DATE_DT"].dt.strftime('%B %Y')

    if "WEEK" in df_opap.columns:
        df_opap["WEEK_NUM"] = pd.to_numeric(df_opap["WEEK"].astype(str).str.extract(r'(\d+)')[0], errors='coerce')

    if "ID" in df_opap.columns:
        df_opap["ID"] = df_opap["ID"].astype(str).str.strip()

    if "ID" in df_stores.columns:
        df_stores["ID"] = df_stores["ID"].astype(str).str.strip()

    # ---------------------------------------------------------
    # 4. LOGOS & HEADER BANNER
    # ---------------------------------------------------------
    header_col1, header_col2, header_col3 = st.columns([1, 4, 1], vertical_alignment="center")

    with header_col1:
        try:
            st.image("WEST_logo.png", use_container_width=True)
        except Exception:
            pass

    with header_col2:
        st.markdown(f'<div class="header-text-style">{display_title}</div>', unsafe_allow_html=True)

    with header_col3:
        try:
            st.image("ALLWYN_logo.png", use_container_width=True)
        except Exception:
            pass

    st.markdown("---")

    # ---------------------------------------------------------
    # 5. SIDEBAR - ΦΙΛΤΡΑ & EXPORT DATA
    # ---------------------------------------------------------
    st.sidebar.header("⚙️ Dashboard Filters")

    months_order = [m for m in df_opap["MONTH"].unique() if pd.notna(m)] if "MONTH" in df_opap.columns else []

    selected_months = st.sidebar.multiselect(
        "MONTH (Μήνας)", 
        options=months_order, 
        default=[],
        placeholder="Select one or more"
    )

    df_filtered = df_opap.copy()
    if selected_months:
        df_filtered = df_filtered[df_filtered["MONTH"].isin(selected_months)]

    if "WEEK_NUM" in df_filtered.columns:
        available_weeks = sorted([int(x) for x in df_filtered["WEEK_NUM"].dropna().unique()])
    else:
        available_weeks = []

    selected_weeks = st.sidebar.multiselect(
        "WEEK (Εβδομάδα)", 
        options=available_weeks, 
        default=[],
        placeholder="Select one or more"
    )

    if selected_weeks:
        df_filtered = df_filtered[df_filtered["WEEK_NUM"].isin(selected_weeks)]

    # --- ΦΙΛΤΡO STORE ID ΣΤΗ SIDEBAR ---
    if "ID" in df_filtered.columns and not df_filtered.empty:
        store_counts = df_filtered.groupby("ID")["WEEK_NUM"].nunique()
        store_options = sorted([f"{sid} — ({count} weeks)" for sid, count in store_counts.items() if str(sid) != "nan"])
    else:
        store_options = []

    selected_store_option = st.sidebar.selectbox("STORE ID (Αναζήτηση)", options=["All Store IDs"] + store_options, index=0)

    if selected_store_option != "All Store IDs":
        selected_id = selected_store_option.split(" — ")[0].strip()
        df_filtered = df_filtered[df_filtered["ID"] == selected_id]

    st.sidebar.markdown("---")
    st.sidebar.header("📥 Export Data")

    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8-sig')

    csv_data = convert_df_to_csv(df_filtered)
    st.sidebar.download_button(
        label="Download Data (CSV)",
        data=csv_data,
        file_name="allwyn_decluttering_data_export.csv",
        mime="text/csv"
    )

    # ---------------------------------------------------------
    # 6. ΔΙΑΓΡΑΜΜΑΤΑ COVERAGE: ACTIVE & INACTIVE STORES
    # ---------------------------------------------------------
    if not df_filtered.empty:
        
        # 1. Καθαρισμός IDs
        df_opap_clean = df_filtered.dropna(subset=["ID"]).copy()
        df_opap_clean["ID_CLEAN"] = df_opap_clean["ID"].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

        # 2. Κρατάμε ΜOΝO την πιο πρόσφατη εγγραφή για κάθε κατάστημα (Last Response)
        sort_cols = [c for c in ["WEEK_NUM", "DATE_DT"] if c in df_opap_clean.columns]
        df_sorted = df_opap_clean.sort_values(by=sort_cols, ascending=True) if sort_cols else df_opap_clean.copy()
        df_last_responses = df_sorted.drop_duplicates(subset=["ID_CLEAN"], keep="last")

        # 3. Σύνδεση με το STORE STATUS / ACTIVITY
        status_col = "STATUS" if "STATUS" in df_last_responses.columns else ("STORE STATUS" if "STORE STATUS" in df_last_responses.columns else None)
        
        if status_col:
            df_last_responses["STATUS_CLEAN"] = df_last_responses[status_col].astype(str).str.strip().str.upper()
        elif "ACTIVITY" in df_stores.columns and "ID" in df_stores.columns:
            df_stores_clean = df_stores.dropna(subset=["ID"]).copy()
            df_stores_clean["ID_CLEAN"] = df_stores_clean["ID"].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df_last_status = df_stores_clean.drop_duplicates(subset=["ID_CLEAN"], keep="last")
            df_last_responses = pd.merge(df_last_responses, df_last_status[["ID_CLEAN", "ACTIVITY"]], on="ID_CLEAN", how="left")
            df_last_responses["STATUS_CLEAN"] = df_last_responses["ACTIVITY"].astype(str).str.strip().str.upper()
        else:
            df_last_responses["STATUS_CLEAN"] = "ACTIVE"

        valid_answers = ["ΝΑΙ", "ΔΕΝ ΥΠΗΡΧΕ ΠΑΛΑΙΟ-ΜΗ ΕΓΚΕΚΡΙΜΕΝΟ ΥΛΙΚΟ", "ΔΕΝ ΥΠΗΡΧΕ ΠΑΛΑΙO-ΜΗ ΕΓΚΕΚΡΙΜEΝO ΥΛΙΚO"]

        # =========================================================
        # ΔΙΑΓΡΑΜΜΑ 1: ACTIVE NETWORK COVERAGE
        # =========================================================
        st.subheader("ACTIVE NETWORK COVERAGE")

        df_active = df_last_responses[df_last_responses["STATUS_CLEAN"] == "ACTIVE"]
        total_active = len(df_active)
        decluttered_active = len(df_active[df_active["ANSWER"].isin(valid_answers)])
        remaining_active = max(0, total_active - decluttered_active)
        cov_active_pct = (decluttered_active / total_active * 100) if total_active > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Active IDs", f"{total_active:,}")
        c2.metric("Decluttered", f"{decluttered_active:,}")
        c3.metric("Coverage %", f"{cov_active_pct:.1f}%")

        fig_active = go.Figure()
        fig_active.add_trace(go.Bar(
            y=["Active Stores"], x=[decluttered_active], name="Decluttered",
            orientation='h', marker=dict(color='#2FDDC0'), text=f"{decluttered_active:,}" if decluttered_active > 0 else "",
            textposition='inside', insidetextfont=dict(color='white', size=13), cliponaxis=False
        ))
        fig_active.add_trace(go.Bar(
            y=["Active Stores"], x=[remaining_active], name="Remaining",
            orientation='h', marker=dict(color='#115566'), text=f"{remaining_active:,}" if remaining_active > 0 else "",
            textposition='inside', insidetextfont=dict(color='white', size=13), cliponaxis=False
        ))
        fig_active.update_layout(
            barmode='stack', height=160, margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
            xaxis=dict(showgrid=False, color='white'), yaxis=dict(color='white'), showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, 
                font=dict(color='white'),
                traceorder='normal'
            )
        )
        st.plotly_chart(fig_active, use_container_width=True)

        st.markdown("---")

        # =========================================================
        # ΔΙΑΓΡΑΜΜΑ 2: INACTIVE / CLOSED STORES COVERAGE
        # =========================================================
        st.subheader("INACTIVE / CLOSED STORES COVERAGE")

        df_inactive = df_last_responses[df_last_responses["STATUS_CLEAN"].isin(["INACTIVE", "CLOSED"])]
        total_inactive = len(df_inactive)
        decluttered_inactive = len(df_inactive[df_inactive["ANSWER"].isin(valid_answers)])
        remaining_inactive = max(0, total_inactive - decluttered_inactive)
        cov_inactive_pct = (decluttered_inactive / total_inactive * 100) if total_inactive > 0 else 0

        i1, i2, i3 = st.columns(3)
        i1.metric("Total Inactive/Closed IDs", f"{total_inactive:,}")
        i2.metric("Decluttered (Inactive)", f"{decluttered_inactive:,}")
        i3.metric("Coverage %", f"{cov_inactive_pct:.1f}%")

        fig_inactive = go.Figure()
        fig_inactive.add_trace(go.Bar(
            y=["Inactive Stores"], x=[decluttered_inactive], name="Decluttered (Inactive)",
            orientation='h', marker=dict(color='#FF9F43'), text=f"{decluttered_inactive:,}" if decluttered_inactive > 0 else "",
            textposition='inside', insidetextfont=dict(color='white', size=13), cliponaxis=False
        ))
        fig_inactive.add_trace(go.Bar(
            y=["Inactive Stores"], x=[remaining_inactive], name="Closed",
            orientation='h', marker=dict(color='#EA5455'), text=f"{remaining_inactive:,}" if remaining_inactive > 0 else "",
            textposition='inside', insidetextfont=dict(color='white', size=13), cliponaxis=False
        ))
        fig_inactive.update_layout(
            barmode='stack', height=160, margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
            xaxis=dict(showgrid=False, color='white'), yaxis=dict(color='white'), showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, 
                font=dict(color='white'),
                traceorder='normal'
            )
        )
        st.plotly_chart(fig_inactive, use_container_width=True)

    else:
        st.info("Δεν υπάρχουν δεδομένα για τα επιλεγμένα φίλτρα.")

    # ---------------------------------------------------------
    # 7. WEEKLY STACKED BAR CHART
    # ---------------------------------------------------------
    st.markdown("---")
    st.subheader("ΑΦΑΙΡΕΘΗΚΕ ΤΥΧOΝ ΤOΠOΘΕΤΗΜΕΝO ΠΑΛΑΙO Η ΜΗ ΕΓΚΕΚΡΙΜΕΝO ΥΛΙΚO (ΑΦΙΣΕΣ) ΑΠO ΤO ΚΑΤΑΣΤΗΜΑ ?")

    if "WEEK_NUM" in df_filtered.columns and "ANSWER" in df_filtered.columns and not df_filtered.empty:
        df_chart = df_filtered.groupby(["WEEK_NUM", "ANSWER"]).size().reset_index(name="Count")
        df_chart = df_chart.sort_values(by="WEEK_NUM", ascending=True)
        df_chart["WEEK_LABEL"] = "Week " + df_chart["WEEK_NUM"].astype(int).astype(str)

        sorted_weeks_labels = ["Week " + str(int(w)) for w in sorted(df_chart["WEEK_NUM"].unique())]
        totals = df_chart.groupby("WEEK_LABEL")["Count"].sum().reset_index(name="Total")

        color_map = {
            "ΝΑΙ": "#2FDDC0",
            "ΔΕΝ ΥΠΗΡΧΕ ΠΑΛΑΙΟ-ΜΗ ΕΓΚΕΚΡΙΜΕΝΟ ΥΛΙΚΟ": "#09A1A4",
            "ΔΕΝ ΥΠΗΡΧΕ ΠΑΛΑΙO-ΜΗ ΕΓΚΕΚΡΙΜEΝO ΥΛΙΚO": "#09A1A4",
            "ΟΧΙ": "#115566"
        }

        fig_weekly = px.bar(
            df_chart, x="WEEK_LABEL", y="Count", color="ANSWER",
            color_discrete_map=color_map, category_orders={"WEEK_LABEL": sorted_weeks_labels}
        )
        fig_weekly.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}: <b>%{y:,}</b><extra></extra>")

        for _, row in totals.iterrows():
            fig_weekly.add_annotation(
                x=row["WEEK_LABEL"], y=row["Total"], text=f"{row['Total']:,}",
                showarrow=False, yshift=10, font=dict(color="white", size=13, family="Arial Black")
            )

        max_y = totals["Total"].max() * 1.15 if not totals.empty else 10
        fig_weekly.update_layout(
            barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'), xaxis_title="Week", yaxis_title="Total Answers", legend_title_text="",
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, font=dict(color='white')),
            height=540,
            xaxis=dict(showgrid=False, type='category', color='white', categoryorder='array', categoryarray=sorted_weeks_labels),
            yaxis=dict(showgrid=False, color='white', range=[0, max_y])
        )
        st.plotly_chart(fig_weekly, use_container_width=True)
    else:
        st.info("Δεν υπάρχουν δεδομένα για το επιλεγμένο Store ID.")

    # ---------------------------------------------------------
    # 8. ΧΑΡΤΗΣ ΚΑΛΥΨΗΣ ΑΝΑ REGION
    # ---------------------------------------------------------
    if "REGION" in df_filtered.columns and not df_filtered.empty:
        st.markdown("---")
        st.subheader("🗺️ COVERAGE MAP BY REGION")

        REGION_COORDINATES_RAW = {
            "ΑΤΤΙΚΗΣ - ΑΤΤΙΚΗΣ": (37.9838, 23.7275),
            "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ - ΣΕΡΡΩΝ": (41.0849, 23.5476),
            "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ - ΘΕΣΣΑΛOΝΙΚΗΣ": (40.6401, 22.9444),
            "ΗΠΕΙΡOΥ - ΙΩΑΝΝΙΝΩΝ": (39.6650, 20.8537),
            "ΘΕΣΣΑΛΙΑΣ - ΛΑΡΙΣΗΣ": (39.6390, 22.4191),
            "ΘΕΣΣΑΛΙΑΣ - ΜΑΓΝΗΣΙΑΣ": (39.3621, 22.9422),
            "ΠΕΛOΠOΝΝΗΣOΥ - ΑΡΓOΛΙΔOΣ": (37.5672, 22.8014),
            "ΚΡΗΤΗΣ - ΗΡΑΚΛΕΙOΥ": (35.3387, 25.1442),
            "ΗΠΕΙΡOΥ - ΑΡΤΗΣ": (39.1606, 20.9853),
            "ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ - ΦΘΙΩΤΙΔOΣ": (38.8986, 22.4331),
            "ΑΝΑΤOΛΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ - ΚΑΒΑΛΑΣ": (40.9396, 24.4069),
            "ΗΠΕΙΡOΥ - ΘΕΣΠΡΩΤΙΑΣ": (39.5039, 20.2656),
            "ΠΕΛOΠOΝΝΗΣOΥ - ΚOΡΙΝΘΙΑΣ": (37.9386, 22.9322),
            "ΑΝΑΤOΛΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ - ΞΑΝΘΗΣ": (41.1349, 24.8880),
            "ΘΕΣΣΑΛΙΑΣ - ΤΡΙΚΑΛΩΝ": (39.5549, 21.7684),
            "ΠΕΛOΠOΝΝΗΣOΥ - ΑΡΚΑΔΙΑΣ": (37.5103, 22.3726),
            "ΙOΝΙΩΝ ΝΗΣΩΝ - ΚΕΡΚΥΡΑΣ": (39.6243, 19.9217),
            "ΑΝΑΤOΛΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ - ΔΡΑΜΑΣ": (41.1511, 24.1403),
            "ΔΥΤΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ - ΚOΖΑΝΗΣ": (40.3006, 21.7889),
            "ΠΕΛOΠOΝΝΗΣOΥ - ΜΕΣΣΗΝΙΑΣ": (37.0389, 22.1142),
            "ΘΕΣΣΑΛΙΑΣ - ΚΑΡΔΙΤΣΗΣ": (39.3644, 21.9214),
            "ΔΥΤΙΚΗΣ ΕΛΛΑΔΑΣ - ΑΧΑΪΑΣ": (38.2466, 21.7345),
            "ΑΝΑΤOΛΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ - ΕΒΡOΥ": (40.8457, 25.8739),
            "ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ - ΒOΙΩΤΙΑΣ": (38.4378, 22.8756),
            "ΠΕΛOΠOΝΝΗΣOΥ - ΛΑΚΩΝΙΑΣ": (37.0733, 22.4297),
            "ΗΠΕΙΡOΥ - ΠΡΕΒΕΖΗΣ": (38.9569, 20.7506),
            "ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ - ΕΥΒOΙΑΣ": (38.4636, 23.5991),
            "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ - ΗΜΑΘΙΑΣ": (40.5244, 22.2022),
            "ΔΥΤΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ - ΦΛΩΡΙΝΗΣ": (40.7819, 21.4098),
            "ΚΡΗΤΗΣ - ΧΑΝΙΩΝ": (35.5138, 24.0180),
            "ΑΝΑΤOΛΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ ΚΑΙ ΘΡΑΚΗΣ - ΡOΔOΠΗΣ": (41.1186, 25.4042),
            "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ - ΚΙΛΚΙΣ": (40.9930, 22.8753),
            "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ - ΠΕΛΛΗΣ": (40.8017, 22.0439),
            "ΒOΡΕΙOΥ ΑΙΓΑΙOΥ - ΛΕΣΒOΥ": (39.1042, 26.5550),
            "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ - ΠΙΕΡΙΑΣ": (40.2696, 22.5061),
            "ΚΕΝΤΡΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ - ΧΑΛΚΙΔΙΚΗΣ": (40.3783, 23.4428),
            "ΚΡΗΤΗΣ - ΡΕΘΥΜΝΗΣ": (35.3672, 24.4739),
            "ΔΥΤΙΚΗΣ ΕΛΛΑΔΑΣ - ΗΛΕΙΑΣ": (37.6726, 21.4402),
            "ΔΥΤΙΚΗΣ ΕΛΛΑΔΑΣ - ΑΙΤΩΛΙΑΣ ΚΑΙ ΑΚΑΡΝΑΝΙΑΣ": (38.6247, 21.4089),
            "ΙOΝΙΩΝ ΝΗΣΩΝ - ΛΕΥΚΑΔOΣ": (38.8304, 20.7044),
            "ΒOΡΕΙOΥ ΑΙΓΑΙOΥ - ΧΙOΥ": (38.3678, 26.1358),
            "ΝOΤΙOΥ ΑΙΓΑΙOΥ - ΚΥΚΛΑΔΩΝ": (37.4437, 24.9422),
            "ΔΥΤΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ - ΓΡΕΒΕΝΩΝ": (40.0839, 21.4275),
            "ΔΥΤΙΚΗΣ ΜΑΚΕΔOΝΙΑΣ - ΚΑΣΤOΡΙΑΣ": (40.5216, 21.2634),
            "ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ - ΦΩΚΙΔOΣ": (38.5286, 22.3769),
            "ΝOΤΙOΥ ΑΙΓΑΙOΥ - ΔΩΔΕΚΑΝΗΣOΥ": (36.4349, 28.2175),
            "ΙOΝΙΩΝ ΝΗΣΩΝ - ΚΕΦΑΛΛΗΝΙΑΣ": (38.1772, 20.4883),
            "ΒOΡΕΙOΥ ΑΙΓΑΙOΥ - ΣΑΜOΥ": (37.7548, 26.9778),
            "ΚΡΗΤΗΣ - ΛΑΣΙΘΙOΥ": (35.1653, 25.7153),
            "ΙOΝΙΩΝ ΝΗΣΩΝ - ΖΑΚΥΝΘOΥ": (37.7870, 20.8979),
            "ΣΤΕΡΕΑΣ ΕΛΛΑΔΑΣ - ΕΥΡΥΤΑΝΙΑΣ": (38.9122, 21.7981)
        }

        REGION_COORDINATES = {normalize_string(k): v for k, v in REGION_COORDINATES_RAW.items()}
        valid_answers = ["ΝΑΙ", "ΔΕΝ ΥΠΗΡΧΕ ΠΑΛΑΙΟ-ΜΗ ΕΓΚΕΚΡΙΜΕΝΟ ΥΛΙΚΟ", "ΔΕΝ ΥΠΗΡΧΕ ΠΑΛΑΙO-ΜΗ ΕΓΚΕΚΡΙΜEΝO ΥΛΙΚO"]
        
        df_active_map = df_filtered.dropna(subset=["ID"]).copy()
        df_active_map["REGION_NORM"] = df_active_map["REGION"].apply(normalize_string)
        
        df_map_total = df_active_map.groupby(["REGION", "REGION_NORM"])["ID"].nunique().reset_index(name="Total_Stores")
        df_decluttered_stores = df_active_map[df_active_map["ANSWER"].isin(valid_answers)]
        df_map_decluttered = df_decluttered_stores.groupby("REGION_NORM")["ID"].nunique().reset_index(name="Decluttered_Stores")

        df_map = pd.merge(df_map_total, df_map_decluttered, on="REGION_NORM", how="left")
        df_map["Decluttered_Stores"] = df_map["Decluttered_Stores"].fillna(0).astype(int)
        df_map["Coverage %"] = (df_map["Decluttered_Stores"] / df_map["Total_Stores"] * 100).round(1)

        df_map["lat"] = df_map["REGION_NORM"].map(lambda x: REGION_COORDINATES.get(x, (None, None))[0])
        df_map["lon"] = df_map["REGION_NORM"].map(lambda x: REGION_COORDINATES.get(x, (None, None))[1])
        df_map_clean = df_map.dropna(subset=["lat", "lon"]).copy()

        if not df_map_clean.empty:
            if hasattr(px, "scatter_map"):
                fig_map = px.scatter_map(
                    df_map_clean, lat="lat", lon="lon", size="Total_Stores", color="Coverage %",
                    color_continuous_scale=["#115566", "#09A1A4", "#2FDDC0"], range_color=[0, 100],
                    size_max=38, zoom=5.7, center={"lat": 38.5, "lon": 23.7}, hover_name="REGION",
                    hover_data={"Total_Stores": True, "Decluttered_Stores": True, "Coverage %": ":.1f%", "lat": False, "lon": False},
                    map_style="carto-darkmatter"
                )
            else:
                fig_map = px.scatter_mapbox(
                    df_map_clean, lat="lat", lon="lon", size="Total_Stores", color="Coverage %",
                    color_continuous_scale=["#115566", "#09A1A4", "#2FDDC0"], range_color=[0, 100],
                    size_max=38, zoom=5.7, center={"lat": 38.5, "lon": 23.7}, hover_name="REGION",
                    hover_data={"Total_Stores": True, "Decluttered_Stores": True, "Coverage %": ":.1f%", "lat": False, "lon": False},
                    mapbox_style="carto-darkmatter"
                )

            fig_map.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'), height=550, margin=dict(l=10, r=10, t=20, b=10)
            )
            st.plotly_chart(fig_map, use_container_width=True, config={'scrollZoom': True})
        else:
            st.info("Δεν υπάρχουν δεδομένα με έγκυρη περιοχή για τα επιλεγμένα φίλτρα.")

    st.markdown("---")
