import streamlit as st
import openai
import json
import hashlib
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ET Intelligence · BCCL",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── OpenAI client ─────────────────────────────────────────────────────────────
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main { background: #fafaf7; }
.block-container { padding: 0 !important; max-width: 100% !important; }

.auth-container {
    max-width: 900px; margin: 3rem auto; display: flex;
    border: 1px solid #e2e0d5; border-radius: 12px; overflow: hidden;
    background: white; min-height: 520px;
}
.auth-left {
    width: 38%; background: #1a3a2a; padding: 3rem 2rem;
    display: flex; flex-direction: column; justify-content: space-between;
}
.auth-logo { font-family: 'Playfair Display', serif; font-size: 24px; color: #e8dcc8; }
.auth-logo span { color: #c8a96e; }
.auth-tagline { font-size: 12px; color: #6a9a70; margin-top: 4px; }
.auth-quote { font-family: 'Playfair Display', serif; font-size: 14px;
    color: #c5d9c8; line-height: 1.6; font-style: italic; }
.auth-meta { font-size: 11px; color: #4a6a50; text-transform: uppercase; letter-spacing: 0.06em; }
.auth-right { flex: 1; padding: 3rem 2.5rem; }
.auth-title { font-family: 'Playfair Display', serif; font-size: 26px;
    color: #0f0f0f; margin-bottom: 4px; }
.auth-sub { font-size: 13px; color: #6b6b5e; margin-bottom: 1.5rem; }

.header-bar {
    background: #1a3a2a; padding: 14px 28px;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0;
}
.header-logo { font-family: 'Playfair Display', serif; font-size: 20px; color: #e8dcc8; }
.header-logo span { color: #c8a96e; }
.header-user { font-size: 13px; color: #8aaa90; }
.header-badge {
    background: rgba(200,169,110,0.2); color: #c8a96e;
    font-size: 11px; padding: 3px 10px; border-radius: 20px;
    border: 1px solid rgba(200,169,110,0.3); margin-left: 8px;
}

.stat-box {
    background: white; border: 1px solid #e2e0d5; border-radius: 8px;
    padding: 14px 16px; text-align: center;
}
.stat-num { font-family: 'Playfair Display', serif; font-size: 24px; color: #1a3a2a; }
.stat-lbl { font-size: 11px; color: #6b6b5e; margin-top: 2px; }

.answer-box {
    background: white; border: 1px solid #e2e0d5; border-radius: 10px;
    padding: 20px; margin-top: 1rem;
}
.answer-tag {
    font-size: 10px; font-weight: 500; color: #1a3a2a;
    text-transform: uppercase; letter-spacing: 0.06em;
    background: #e8f0ea; padding: 3px 10px; border-radius: 20px;
    display: inline-block; margin-bottom: 12px;
}
.source-pill {
    display: inline-block; font-size: 11px; padding: 3px 10px;
    border: 1px solid #e2e0d5; border-radius: 4px;
    background: #f3f2ec; color: #6b6b5e; margin: 2px;
}
.kb-item {
    font-size: 12px; color: #6b6b5e; padding: 5px 0;
    border-bottom: 1px solid #f0eeea;
}
.welcome-strip {
    background: #f3f2ec; border: 1px solid #e2e0d5; border-radius: 8px;
    padding: 14px 18px; margin-bottom: 1rem;
}

/* Hide streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# ── Sample knowledge base ─────────────────────────────────────────────────────
ARTICLES = [
    {
        "id": 1, "tag": "Monetary Policy",
        "title": "RBI holds repo rate at 6.5% for sixth consecutive time, flags sticky inflation",
        "date": "ET, Feb 2024", "pub": "Economic Times",
        "content": """The Reserve Bank of India's Monetary Policy Committee voted 5-1 to hold the repo rate 
        at 6.5% for the sixth consecutive meeting. Governor Shaktikanta Das cited sticky core inflation 
        and global uncertainty as key reasons. The MPC remains focused on withdrawal of accommodation 
        to ensure inflation aligns with the 4% target. GDP growth forecast for FY25 was retained at 7%. 
        Das signalled rate cuts are unlikely before Q2 FY25 given food inflation pressures from erratic 
        monsoon patterns. The RBI also raised concerns about rising household debt and unsecured lending."""
    },
    {
        "id": 2, "tag": "Banking",
        "title": "HDFC Bank Q3 net profit rises 34% to ₹16,373 crore, NIM under pressure",
        "date": "ET, Jan 2024", "pub": "Economic Times",
        "content": """HDFC Bank reported a 34% year-on-year rise in net profit to ₹16,373 crore for Q3 FY24. 
        Net interest margin contracted to 3.4% from 3.6% a year ago, reflecting the cost of integrating 
        HDFC Ltd deposits. Gross NPA ratio improved to 1.26%. The bank's loan book grew 55% YoY including 
        erstwhile HDFC Ltd loans. MD Sashidhar Jagdishan said the focus remains on improving deposit 
        mobilisation and normalising margins over 4-6 quarters. CASA ratio stood at 37.7%."""
    },
    {
        "id": 3, "tag": "Markets",
        "title": "Sensex crosses 75,000 for first time; FII flows, earnings optimism fuel rally",
        "date": "ET, Mar 2024", "pub": "Economic Times",
        "content": """The BSE Sensex crossed the historic 75,000 mark for the first time, driven by strong 
        FII inflows of over ₹35,000 crore in March alone. Analysts cited robust corporate earnings, 
        political stability expectations ahead of general elections, and a softening US dollar as key 
        drivers. The Nifty Bank index rose 4.2% in March. Mid and smallcap indices corrected 8-12% from 
        peaks as SEBI flagged froth in the segment. Fund managers advise rebalancing toward large caps."""
    },
    {
        "id": 4, "tag": "NBFCs",
        "title": "Bajaj Finance profit up 21%; RBI removes restrictions on two loan products",
        "date": "ET, Apr 2024", "pub": "Economic Times",
        "content": """Bajaj Finance posted a 21% rise in net profit to ₹3,825 crore for Q4 FY24. The RBI 
        lifted its restrictions on Bajaj Finance's eCOM and Insta EMI card loan products after the NBFC 
        demonstrated compliance with digital lending guidelines. AUM grew 35% YoY to ₹3.31 lakh crore. 
        Management guided for 25-27% AUM growth in FY25 with credit costs expected at 1.75-1.85%. 
        The stock rose 6% on the day of the RBI announcement."""
    },
    {
        "id": 5, "tag": "Macro",
        "title": "India GDP grows 8.4% in Q3 FY24, beats estimates; full year likely 7.6%",
        "date": "ET, Feb 2024", "pub": "Economic Times",
        "content": """India's GDP grew at 8.4% in Q3 FY24, sharply ahead of the 6.6% consensus estimate, 
        driven by strong government capital expenditure and manufacturing output. The National Statistical 
        Office raised the full-year FY24 growth estimate to 7.6%. Private consumption growth remained 
        moderate at 3.5%. Economists noted the gap between GDP and GVA growth reflects higher net indirect 
        taxes. The strong data reduced near-term RBI rate cut expectations and pushed 10-year bond yields 
        up 6 basis points."""
    }
]

DESIGNATIONS = [
    "Equity Analyst", "Fund Manager", "CIO / CXO", "Research Head",
    "Risk Manager", "Compliance Officer", "Portfolio Manager",
    "Investment Banker", "Credit Analyst", "Other"
]

# Simple in-memory user store (resets on redeploy — fine for PoC)
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "demo@hdfcbank.com": {
            "password": hashlib.md5("demo1234".encode()).hexdigest(),
            "name": "Demo User",
            "org": "HDFC Bank",
            "desig": "Equity Analyst"
        }
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = {}
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "signup"
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "last_answer" not in st.session_state:
    st.session_state.last_answer = None

# ── RAG query function ────────────────────────────────────────────────────────
def query_rag(question: str) -> dict:
    """Simple RAG: inject all articles as context, ask GPT-4o to answer with citations."""
    context = "\n\n".join([
        f"[Article {a['id']}] {a['tag'].upper()} | {a['title']} | {a['date']}\n{a['content']}"
        for a in ARTICLES
    ])

    system_prompt = """You are ET Intelligence, a financial news intelligence assistant powered by 
The Economic Times archive. Answer questions using ONLY the provided article context.
Always cite the specific article(s) you used by referencing their title and date.
Be concise, analytical, and appropriate for BFSI professionals (analysts, fund managers, CXOs).
Format: 2-3 paragraph answer followed by a line starting with 'SOURCES:' listing the article titles used."""

    user_prompt = f"""Context from ET archive:
{context}

Question from BFSI analyst: {question}

Answer using only the above context with citations."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=600,
        temperature=0.3
    )

    full_response = response.choices[0].message.content

    # Split answer and sources
    if "SOURCES:" in full_response:
        parts = full_response.split("SOURCES:")
        answer_text = parts[0].strip()
        sources_text = parts[1].strip() if len(parts) > 1 else ""
        sources = [s.strip("•-– ").strip() for s in sources_text.split("\n") if s.strip()]
    else:
        answer_text = full_response
        sources = ["Economic Times archive"]

    return {"answer": answer_text, "sources": sources}

# ── AUTH SCREENS ───────────────────────────────────────────────────────────────
def show_signup():
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 3])

    with col_left:
        st.markdown("""
        <div class="auth-left">
            <div>
                <div class="auth-logo">ET<span>Intelligence</span></div>
                <div class="auth-tagline">Powered by BCCL · Times Group</div>
            </div>
            <div class="auth-quote">"180 years of journalism, structured for the decisions you make today."</div>
            <div class="auth-meta">Enterprise Access · BFSI Edition</div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="auth-right">', unsafe_allow_html=True)
        st.markdown('<div class="auth-title">Create your account</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Get access to ET\'s news intelligence platform</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            fname = st.text_input("First name", placeholder="Rahul", key="su_fname")
        with c2:
            lname = st.text_input("Last name", placeholder="Sharma", key="su_lname")

        email = st.text_input("Work email", placeholder="rahul@hdfcbank.com", key="su_email")
        org = st.text_input("Organisation", placeholder="HDFC Bank", key="su_org")
        desig = st.selectbox("Your designation", DESIGNATIONS, key="su_desig")
        password = st.text_input("Password", type="password", placeholder="Min 8 characters", key="su_pass")

        if st.button("Create account & get access", use_container_width=True, type="primary"):
            if not all([fname, lname, email, org, password]) or len(password) < 8:
                st.error("Please fill all fields. Password must be at least 8 characters.")
            elif email in st.session_state.users_db:
                st.error("Email already registered. Please sign in.")
            else:
                st.session_state.users_db[email] = {
                    "password": hashlib.md5(password.encode()).hexdigest(),
                    "name": f"{fname} {lname}",
                    "org": org,
                    "desig": desig
                }
                st.session_state.current_user = {"name": f"{fname} {lname}", "org": org, "desig": desig, "email": email}
                st.session_state.logged_in = True
                st.rerun()

        st.markdown("---")
        st.markdown("Already have an account?")
        if st.button("Sign in instead", use_container_width=False):
            st.session_state.auth_mode = "login"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def show_login():
    col_left, col_right = st.columns([2, 3])

    with col_left:
        st.markdown("""
        <div class="auth-left" style="background:#1a3a2a;padding:3rem 2rem;border-radius:10px;height:100%;min-height:400px;display:flex;flex-direction:column;justify-content:space-between;">
            <div>
                <div class="auth-logo">ET<span>Intelligence</span></div>
                <div class="auth-tagline">Powered by BCCL · Times Group</div>
            </div>
            <div class="auth-quote">"The trusted intelligence layer for India's financial decision-makers."</div>
            <div class="auth-meta">Enterprise Access · BFSI Edition</div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="auth-title">Welcome back</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Sign in to your ET Intelligence account</div>', unsafe_allow_html=True)
        st.caption("Demo credentials: demo@hdfcbank.com / demo1234")

        email = st.text_input("Work email", placeholder="demo@hdfcbank.com", key="li_email")
        password = st.text_input("Password", type="password", key="li_pass")

        if st.button("Sign in", use_container_width=True, type="primary"):
            hashed = hashlib.md5(password.encode()).hexdigest()
            if email in st.session_state.users_db and st.session_state.users_db[email]["password"] == hashed:
                u = st.session_state.users_db[email]
                st.session_state.current_user = {"name": u["name"], "org": u["org"], "desig": u["desig"], "email": email}
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials. Try demo@hdfcbank.com / demo1234")

        st.markdown("---")
        st.markdown("New user?")
        if st.button("Create account", use_container_width=False):
            st.session_state.auth_mode = "signup"
            st.rerun()


# ── MAIN APP ──────────────────────────────────────────────────────────────────
def show_app():
    u = st.session_state.current_user

    # Header
    st.markdown(f"""
    <div class="header-bar">
        <div class="header-logo">ET<span>Intelligence</span>
            <span style="font-size:11px;color:#4a6a50;font-family:'DM Sans',sans-serif;margin-left:12px">
            by BCCL · Times Group</span>
        </div>
        <div class="header-user">
            {u['name']} · {u['org']}
            <span class="header-badge">{u['desig']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main layout
    sidebar_col, main_col = st.columns([1, 3.5])

    with sidebar_col:
        st.markdown("### Navigation")
        st.markdown("**📊 News Intelligence** ← you are here")
        st.markdown("📈 Market Signals")
        st.markdown("🏦 BFSI Coverage")
        st.markdown("📅 Policy Tracker")
        st.markdown("---")
        st.markdown("**Knowledge base loaded**")
        for a in ARTICLES:
            st.markdown(f"""<div class="kb-item">📄 {a['tag']}</div>""", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("Sign out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = {}
            st.session_state.last_answer = None
            st.session_state.query_count = 0
            st.session_state.auth_mode = "signup"
            st.rerun()

    with main_col:
        # Welcome strip
        st.markdown(f"""
        <div class="welcome-strip">
            <strong>Good morning, {u['name'].split()[0]}</strong> &nbsp;·&nbsp;
            ET Intelligence · BFSI Edition &nbsp;·&nbsp; {u['desig']} access
            <span style="float:right;font-size:11px;color:#6b6b5e;">
                Knowledge base updated: {datetime.now().strftime('%d %b %Y')}
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Stats
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""<div class="stat-box"><div class="stat-num">180+</div>
            <div class="stat-lbl">Years of ET archive</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="stat-box"><div class="stat-num">5</div>
            <div class="stat-lbl">Articles in demo KB</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="stat-box"><div class="stat-num">{st.session_state.query_count}</div>
            <div class="stat-lbl">Queries this session</div></div>""", unsafe_allow_html=True)

        st.markdown("---")

        # Suggested questions
        st.markdown("**Suggested queries for your role**")
        chips = st.columns(5)
        suggestions = [
            "RBI repo rate outlook",
            "HDFC Bank NIM pressure",
            "Sensex rally drivers",
            "NBFC sector update",
            "India GDP growth"
        ]
        for i, (chip_col, sugg) in enumerate(zip(chips, suggestions)):
            with chip_col:
                if st.button(sugg, key=f"chip_{i}", use_container_width=True):
                    st.session_state["prefill_q"] = sugg

        # Query input
        prefill = st.session_state.pop("prefill_q", "")
        question = st.text_input(
            "Ask ET Intelligence",
            value=prefill,
            placeholder="Ask any BFSI question against ET's archive...",
            key="main_q"
        )

        ask_col, _ = st.columns([1, 3])
        with ask_col:
            ask_clicked = st.button("Ask Intelligence →", type="primary", use_container_width=True)

        if ask_clicked and question:
            with st.spinner("Searching ET archive and generating cited response..."):
                try:
                    result = query_rag(question)
                    st.session_state.last_answer = result
                    st.session_state.query_count += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}. Please check your OpenAI API key in Streamlit secrets.")

        # Display answer
        if st.session_state.last_answer:
            ans = st.session_state.last_answer
            st.markdown("""<div class="answer-box">
                <div class="answer-tag">ET Intelligence · Cited response · Powered by GPT-4o + RAG</div>
            </div>""", unsafe_allow_html=True)

            st.markdown(ans["answer"])

            st.markdown("**Sources from ET archive:**")
            sources_html = " ".join([f'<span class="source-pill">📄 {s}</span>' for s in ans["sources"]])
            st.markdown(sources_html, unsafe_allow_html=True)

            st.markdown("---")
            st.caption(f"Response generated using Retrieval Augmented Generation (RAG) · "
                      f"Model: GPT-4o · Knowledge base: {len(ARTICLES)} ET articles · "
                      f"Session queries: {st.session_state.query_count}")


# ── ROUTER ────────────────────────────────────────────────────────────────────
if st.session_state.logged_in:
    show_app()
else:
    if st.session_state.auth_mode == "signup":
        show_signup()
    else:
        show_login()
