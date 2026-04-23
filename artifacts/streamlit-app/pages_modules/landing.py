import streamlit as st

def render():

    # ---------- Custom CSS ----------
    st.markdown("""
    <style>

    /* Global */
    body {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        color: white;
    }

    .main {
        padding: 2rem 4rem;
    }

    /* Hero Section */
    .hero {
        text-align: center;
        padding: 80px 20px;
    }

    .hero h1 {
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero p {
        font-size: 1.2rem;
        color: #cbd5f5;
        margin-top: 10px;
    }

    /* Button */
    .stButton>button {
        background: linear-gradient(90deg, #6366f1, #3b82f6);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        transition: 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 8px 20px rgba(99,102,241,0.4);
    }

    /* Cards */
    .card {
        background: rgba(255,255,255,0.05);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        transition: 0.3s ease;
        height: 100%;
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 10px 25px rgba(0,0,0,0.3);
    }

    .card h3 {
        color: #60a5fa;
        margin-bottom: 10px;
    }

    .section-title {
        text-align: center;
        font-size: 2rem;
        margin: 60px 0 20px;
        font-weight: 600;
    }

    </style>
    """, unsafe_allow_html=True)

    # ---------- HERO ----------
    st.markdown("""
    <div class="hero">
        <h1>Analyze Your Data Intelligently</h1>
        <p>AI-powered research platform for cleaning, analysis, statistical testing, and visualization</p>
    </div>
    """, unsafe_allow_html=True)

    # CTA Button (UNCHANGED LOGIC)
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("🚀 Start Analysis", use_container_width=True):
            st.session_state.step = "login"
            st.rerun()

    # ---------- FEATURES ----------
    st.markdown('<div class="section-title">⚙️ Powerful Features</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="card">
            <h3>📂 Data Cleaning</h3>
            <p>Automatically preprocess and clean raw datasets efficiently.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <h3>🤖 AI Suggestions</h3>
            <p>Smart recommendations for statistical tests and workflows.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <h3>📊 Statistical Analysis</h3>
            <p>Perform accurate tests with automated execution.</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="card">
            <h3>📈 Visualization</h3>
            <p>Elegant charts, reports, and cross-tab analysis.</p>
        </div>
        """, unsafe_allow_html=True)

    # ---------- WORKFLOW ----------
    st.markdown('<div class="section-title">🔄 How It Works</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    steps = [
        ("Upload", "Import your dataset"),
        ("Clean", "Automated preprocessing"),
        ("Analyze", "Run statistical tests"),
        ("Visualize", "Get insights & reports")
    ]

    for i, col in enumerate([col1, col2, col3, col4]):
        with col:
            st.markdown(f"""
            <div class="card">
                <h3>Step {i+1}</h3>
                <p><b>{steps[i][0]}</b><br>{steps[i][1]}</p>
            </div>
            """, unsafe_allow_html=True)
