import streamlit as st
import streamlit as st

# Initialize the search query variable if it doesn't exist yet
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
from sentence_transformers import SentenceTransformer, util
import urllib.parse

@st.fragment
def search_area():
    # We use st.session_state.search_query as the 'value' 
    # so the box fills up automatically when an example is clicked
    query = st.text_input("SEARCH THE MATRIX", value=st.session_state.search_query)
    
    st.markdown("### QUICK LINKS")
    cols = st.columns(4)
    
    # Example buttons
    examples = ["Neural", "Cyber", "Bio", "Grid"]
    
    for i, ex in enumerate(examples):
        if cols[i].button(ex):
            # Update the state and rerun ONLY this fragment
            st.session_state.search_query = ex
            st.rerun(scope="fragment")
            
    return query
# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG (Must be the first Streamlit command)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="SilentVoice", page_icon="🌌", layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────────────────
phrases_dict = {
    ("Open","Open"):"I am completely open to that.",("Open","Fist"):"Goodbye, have a great day!",
    ("Open","Index"):"Hello my friend, how are you?",("Open","Two"):"It is really nice to meet you.",
    ("Open","Three"):"Where are we going today?",("Open","Four"):"Let's bring everyone together.",
    ("Open","Pinky"):"Thank you so much!",("Open","Rock"):"Congratulations!",
    ("Open","Thumb"):"That is a great job.",("Open","Call"):"Please call me later.",
    ("Open","Gun"):"I need to point something out.",
    ("Fist","Open"):"Please wait a moment, I am thinking.",("Fist","Fist"):"System cleared.",
    ("Fist","Index"):"I need some help right now.",("Fist","Two"):"I am feeling very stressed.",
    ("Fist","Three"):"Could you repeat that?",("Fist","Four"):"Stop what you are doing.",
    ("Fist","Pinky"):"I am sorry, my mistake.",("Fist","Rock"):"Be careful, that is dangerous.",
    ("Fist","Thumb"):"I will hold on to this.",("Fist","Call"):"Emergency, I need assistance.",
    ("Fist","Gun"):"Do not do that again.",
    ("Index","Open"):"I am doing great, thank you.",("Index","Fist"):"I did not catch that.",
    ("Index","Index"):"I have a very important point.",("Index","Two"):"That sounds like a good idea.",
    ("Index","Three"):"I have a quick question.",("Index","Four"):"Let me count the ways.",
    ("Index","Pinky"):"Excuse me for a second.",("Index","Rock"):"I am so excited!",
    ("Index","Thumb"):"I agree with your point.",("Index","Call"):"Who was that on the phone?",
    ("Index","Gun"):"Look exactly right there.",
    ("Two","Open"):"Yes, I completely agree.",("Two","Fist"):"Let us take a short break.",
    ("Two","Index"):"What are we going to do now?",("Two","Two"):"We are in this together.",
    ("Two","Three"):"Let's work as a team.",("Two","Four"):"There are too many options.",
    ("Two","Pinky"):"I am sorry about the mix up.",("Two","Rock"):"See you tomorrow.",
    ("Two","Thumb"):"Two thumbs up from me.",("Two","Call"):"Let's do a group call.",
    ("Two","Gun"):"We need to choose one direction.",
    ("Three","Open"):"That is fantastic news!",("Three","Fist"):"I do not understand at all.",
    ("Three","Index"):"Look at this over here.",("Three","Two"):"Give me a few minutes.",
    ("Three","Three"):"Third time is the charm.",("Three","Four"):"We are almost finished.",
    ("Three","Pinky"):"No problem at all.",("Three","Rock"):"Have a safe trip.",
    ("Three","Thumb"):"I highly recommend this.",("Three","Call"):"Conference call in five minutes.",
    ("Three","Gun"):"Let's move to the next item.",
    ("Four","Open"):"Everything is perfectly fine.",("Four","Fist"):"Close the door, please.",
    ("Four","Index"):"First of all, listen to me.",("Four","Two"):"I have a couple of thoughts.",
    ("Four","Three"):"Just a few more things.",("Four","Four"):"Keep it absolutely square.",
    ("Four","Pinky"):"I promise I will do it.",("Four","Rock"):"This is a solid plan.",
    ("Four","Thumb"):"Everything is under control.",("Four","Call"):"I will notify everyone.",
    ("Four","Gun"):"Take a look at the details.",
    ("Pinky","Open"):"I need to use the restroom.",("Pinky","Fist"):"I am feeling very tired.",
    ("Pinky","Index"):"I am thirsty, I need water.",("Pinky","Two"):"I am hungry, let's eat.",
    ("Pinky","Three"):"What time is it right now?",("Pinky","Four"):"I need some personal space.",
    ("Pinky","Pinky"):"Little by little we get there.",("Pinky","Rock"):"That is a tiny detail.",
    ("Pinky","Thumb"):"Just a little bit better.",("Pinky","Call"):"I will call you specifically.",
    ("Pinky","Gun"):"That is exactly the small issue.",
    ("Rock","Open"):"This is awesome!",("Rock","Fist"):"Stop doing that right now.",
    ("Rock","Index"):"Turn up the volume.",("Rock","Two"):"Turn down the volume.",
    ("Rock","Three"):"Play some music.",("Rock","Four"):"Change the song.",
    ("Rock","Pinky"):"That is totally wild.",("Rock","Rock"):"Keep rocking on.",
    ("Rock","Thumb"):"I am feeling very confident.",("Rock","Call"):"Let's throw a party.",
    ("Rock","Gun"):"Let's hit the road.",
    ("Thumb","Open"):"Good morning everyone.",("Thumb","Fist"):"I strongly disagree.",
    ("Thumb","Index"):"I have one positive thought.",("Thumb","Two"):"That is twice as good.",
    ("Thumb","Three"):"Excellent work.",("Thumb","Four"):"Four stars out of five.",
    ("Thumb","Pinky"):"It is okay, don't worry.",("Thumb","Rock"):"You absolutely nailed it.",
    ("Thumb","Thumb"):"Perfect, I love it.",("Thumb","Call"):"Sounds like a plan, call me.",
    ("Thumb","Gun"):"You are right on target.",
    ("Call","Open"):"Let's open communication.",("Call","Fist"):"Hang up the phone.",
    ("Call","Index"):"I am waiting for a message.",("Call","Two"):"Send me a text instead.",
    ("Call","Three"):"Check your email.",("Call","Four"):"Broadcast the message to the team.",
    ("Call","Pinky"):"Just a quick chat.",("Call","Rock"):"Loud and clear.",
    ("Call","Thumb"):"Good talking to you.",("Call","Call"):"Stay in touch.",
    ("Call","Gun"):"Shoot me an email.",
    ("Gun","Open"):"Expand on that idea.",("Gun","Fist"):"Target locked, let's go.",
    ("Gun","Index"):"That is exactly the point.",("Gun","Two"):"Aim for the middle.",
    ("Gun","Three"):"Triangulate the problem.",("Gun","Four"):"Look at the big picture.",
    ("Gun","Pinky"):"Focus on the small stuff.",("Gun","Rock"):"We hit a roadblock.",
    ("Gun","Thumb"):"Nailed the objective.",("Gun","Call"):"Direct line, no waiting.",
    ("Gun","Gun"):"Right on the money.",
}

GESTURES = ["Open","Fist","Index","Two","Three","Four","Pinky","Rock","Thumb","Call","Gun"]
sentences = list(phrases_dict.values())
combos    = list(phrases_dict.keys())

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "chip_query" not in st.session_state:
    st.session_state.chip_query = ""

# ─────────────────────────────────────────────────────────────────────────────
# CHIP CLICK HANDLER (Reads natively from URL)
# ─────────────────────────────────────────────────────────────────────────────
chip_clicked = st.query_params.get("chip", "")
if chip_clicked:
    st.session_state.chip_query = chip_clicked
    st.query_params.clear()

# ─────────────────────────────────────────────────────────────────────────────
# MODEL
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_data
def get_embeddings():
    return load_model().encode(sentences, convert_to_tensor=True)

model               = load_model()
sentence_embeddings = get_embeddings()

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}

/* ── THE COLOR BREATHING LOGIC ── */
@keyframes colorCycle {
    0% { filter: hue-rotate(0deg); }
    100% { filter: hue-rotate(360deg); }
}

[data-testid="stAppViewContainer"] {
    font-family: 'Space Grotesk', sans-serif;
    
    /* 1. Base Colors: Set a vibrant primary gradient */
    background: linear-gradient(
        125deg, 
        #6d28d9, /* Vibrant Purple */
        #047857, /* Emerald */
        #1e40af  /* Blue */
    ) !important;
    background-size: 400% 400% !important;

    /* 2. Layer the Grid */
    background-image: 
        radial-gradient(circle at center, rgba(0,0,0,0) 0%, #000 100%),
        linear-gradient(rgba(0, 255, 204, 0.1) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 204, 0.1) 1px, transparent 1px) !important;
    background-size: 100% 100%, 60px 60px, 60px 60px !important;

    /* 3. The Magic: This cycles the colors AND moves the grid */
    /* 15s is the speed - make it 5s if you want it faster/wilder */
    animation: 
        colorCycle 15s linear infinite, 
        gridMove 10s linear infinite !important;
}

/* Keep your gridMove keyframe as is */
@keyframes gridMove {
    0% { background-position: 0 0; }
    100% { background-position: 60px 60px; }
}
                                   
/* ── CYBERPUNK GRID CORE BACKGROUND ── */
@keyframes neonShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes gridMove {
    0% { background-position: 0 0; }
    100% { background-position: 50px 50px; }
}

[data-testid="stAppViewContainer"]{
    font-family:'Space Grotesk',sans-serif;
    overflow:hidden;
    
    /* layer 1: Shifting Neon Core Gradient Base */
    background: linear-gradient(120deg, #0a0015, #1a0033, #001f4d, #33001a) !important;
    background-size: 300% 300% !important;
    
    /* layer 2: Overlay Moving Cyan Digital Grid (Hacker Squares) */
    background-image: 
        radial-gradient(circle at center, rgba(10, 25, 48, 0.4) 0%, #000000 100%),
        linear-gradient(rgba(0, 255, 204, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 204, 0.05) 1px, transparent 1px) !important;
    background-size: 100% 100%, 50px 50px, 50px 50px !important;
    
    background-blend-mode: normal, overlay, lighten !important;
    animation: neonShift 8s ease infinite, gridMove 6s linear infinite !important;
    color: #ffffff;
}

[data-testid="block-container"]{padding:0!important;max-width:100%!important;position:relative;z-index:2;}
[data-testid="stVerticalBlock"]{gap:0!important;}

/* ── NATIVE STREAMLIT SIDEBAR OVERRIDES ── */
[data-testid="stSidebar"] {
    background: rgba(10,4,26,0.92) !important;
    border-right: 1px solid rgba(140,80,255,0.18) !important;
    backdrop-filter: blur(24px) !important;
}
.sv-sb-title {
    text-align:center; padding: 0.5rem 0 0.5rem;
    font-size:16px; font-weight:700; color:#c4b5fd; letter-spacing:1px; text-transform:uppercase;
}
.sv-sb-hr { border:none; border-top:1px solid rgba(140,80,255,0.15); margin:0.5rem 0 1rem; }

/* This defines HOW the colors change */
@keyframes neonShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ── THE COLOR BREATHING LOGIC ── */
@keyframes colorCycle {
    0% { filter: hue-rotate(0deg); }
    100% { filter: hue-rotate(360deg); }
}

[data-testid="stAppViewContainer"] {
    font-family: 'Space Grotesk', sans-serif;
    
    /* 1. Base Colors: Set a vibrant primary gradient */
    background: linear-gradient(
        125deg, 
        #6d28d9, /* Vibrant Purple */
        #047857, /* Emerald */
        #1e40af  /* Blue */
    ) !important;
    background-size: 400% 400% !important;

    /* 2. Layer the Grid */
    background-image: 
        radial-gradient(circle at center, rgba(0,0,0,0) 0%, #000 100%),
        linear-gradient(rgba(0, 255, 204, 0.1) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 204, 0.1) 1px, transparent 1px) !important;
    background-size: 100% 100%, 60px 60px, 60px 60px !important;

    /* 3. The Magic: This cycles the colors AND moves the grid */
    /* 15s is the speed - make it 5s if you want it faster/wilder */
    animation: 
        colorCycle 15s linear infinite, 
        gridMove 10s linear infinite !important;
}

/* Keep your gridMove keyframe as is */
@keyframes gridMove {
    0% { background-position: 0 0; }
    100% { background-position: 60px 60px; }
}
/* ── MAIN CONTENT ── */
.sv-wrap{
    position:relative;z-index:2;
    padding:0 2.5rem 5rem;
    max-width:860px;margin:0 auto;
}

/* ── HERO ── */
.sv-hero{text-align:center;padding:4.5rem 1rem 2rem;}
.sv-logo-stack{position:relative;width:96px;height:96px;margin:0 auto 2rem;}
.sv-ring{
    position:absolute;inset:0;border-radius:50%;
    border:1px solid rgba(140,80,255,0.5);
    animation:ringOut 3s ease-out infinite;
}
.sv-ring:nth-child(2){animation-delay:1s;}
.sv-ring:nth-child(3){animation-delay:2s;}
@keyframes ringOut{
    0%{transform:scale(0.65);opacity:0.9;}
    100%{transform:scale(2.1);opacity:0;}
}
.sv-core{
    position:absolute;inset:14px;border-radius:50%;
    background:linear-gradient(135deg,#7c3aed,#059669);
    display:flex;align-items:center;justify-content:center;font-size:32px;
    box-shadow:0 0 50px rgba(124,58,237,0.7),0 0 100px rgba(5,150,105,0.3);
    animation:coreBreath 4s ease-in-out infinite;
}
@keyframes coreBreath{
    0%,100%{box-shadow:0 0 50px rgba(124,58,237,0.7),0 0 100px rgba(5,150,105,0.3);}
    50%{box-shadow:0 0 80px rgba(124,58,237,1),0 0 160px rgba(5,150,105,0.55);}
}

.sv-title{
    font-size:3.8rem;font-weight:700;letter-spacing:-2px;
    background:linear-gradient(135deg,#fff 0%,#c4b5fd 35%,#6ee7b7 70%,#fff 100%);
    background-size:300% 300%;
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
    animation:shimmer 6s ease infinite;margin-bottom:0.6rem;
}
@keyframes shimmer{0%{background-position:0% 50%;}50%{background-position:100% 50%;}100%{background-position:0% 50%;}}

.sv-tagline{font-size:0.9rem;color:rgba(196,181,253,0.6);letter-spacing:3px;text-transform:uppercase;}
.sv-dot{
    display:inline-block;width:7px;height:7px;background:#34d399;border-radius:50%;
    margin-right:8px;box-shadow:0 0 10px #34d399;animation:dp 2s ease infinite;vertical-align:middle;
}
@keyframes dp{0%,100%{opacity:1;box-shadow:0 0 10px #34d399;}50%{opacity:0.2;box-shadow:none;}}

/* ── SEARCH ── */
.stTextInput input{
    width:100%!important;padding:18px 24px!important;
    background:rgba(255,255,255,0.05)!important;
    border:1px solid rgba(140,80,255,0.3)!important;
    border-radius:18px!important;color:#fff!important;
    font-size:1rem!important;font-family:'Space Grotesk',sans-serif!important;
    transition:all 0.3s!important;outline:none!important;caret-color:#a78bfa;
}
.stTextInput input:focus{
    border-color:rgba(140,80,255,0.75)!important;
    background:rgba(255,255,255,0.08)!important;
    box-shadow:0 0 40px rgba(124,58,237,0.22)!important;
}
.stTextInput input::placeholder{color:rgba(196,181,253,0.4)!important;}
.stTextInput label{display:none!important;}
.stTextInput>div,.stTextInput>div>div{border:none!important;background:transparent!important;}

/* ── CHIPS ── */
.sv-chips{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:1.2rem 0 2rem;}
.sv-chip{
    font-size:12px;font-family:'Space Grotesk',sans-serif;
    padding:7px 18px;border-radius:99px;
    border:1px solid rgba(140,80,255,0.25);
    background:rgba(124,58,237,0.1);color:#c4b5fd;
    cursor:pointer;transition:all 0.2s;user-select:none;letter-spacing:0.3px;
    text-decoration:none;display:inline-block;
}
.sv-chip:hover{
    background:rgba(124,58,237,0.35);border-color:rgba(140,80,255,0.7);color:#fff;
    transform:translateY(-2px);box-shadow:0 4px 20px rgba(124,58,237,0.4);
}

/* ── SECTION LABEL ── */
.sv-label{
    font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:2px;
    color:rgba(140,80,255,0.55);margin-bottom:16px;
    display:flex;align-items:center;gap:10px;
}
.sv-label::after{content:'';flex:1;height:1px;background:linear-gradient(to right,rgba(140,80,255,0.25),transparent);}

/* ── CARDS ── */
.sv-card{
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(140,80,255,0.18);
    border-radius:18px;padding:22px 26px;margin-bottom:12px;
    display:flex;align-items:center;gap:20px;
    backdrop-filter:blur(20px);
    position:relative;overflow:hidden;
    animation:cardIn 0.45s cubic-bezier(0.34,1.56,0.64,1) both;
    transition:border-color 0.2s,transform 0.2s,box-shadow 0.2s;
}
.sv-card::before{
    content:'';position:absolute;top:0;left:-120%;width:55%;height:100%;
    background:linear-gradient(90deg,transparent,rgba(140,80,255,0.06),transparent);
    transform:skewX(-20deg);transition:left 0.7s ease;
}
.sv-card:hover::before{left:160%;}
.sv-card:hover{border-color:rgba(140,80,255,0.45);transform:translateY(-4px);box-shadow:0 12px 50px rgba(124,58,237,0.2);}
@keyframes cardIn{0%{opacity:0;transform:translateY(24px) scale(0.96);}100%{opacity:1;transform:translateY(0) scale(1);}}

.sv-rank{
    width:38px;height:38px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    font-size:13px;font-weight:700;flex-shrink:0;
    color:#c4b5fd;border:1px solid rgba(140,80,255,0.25);background:rgba(124,58,237,0.12);
}
.sv-rank.r1{background:linear-gradient(135deg,#7c3aed,#a78bfa);color:#fff;border:none;box-shadow:0 0 24px rgba(124,58,237,0.7);}
.sv-rank.r2{background:rgba(124,58,237,0.28);color:#ddd6fe;border-color:rgba(140,80,255,0.4);}

.sv-card-body{flex:1;min-width:0;}
.sv-phrase{font-size:1.05rem;font-weight:500;color:#fff;margin-bottom:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.sv-meta{display:flex;align-items:center;gap:10px;flex-wrap:wrap;}
.sv-gtag{
    font-family:monospace;font-size:12px;padding:4px 13px;border-radius:99px;
    background:rgba(5,150,105,0.12);border:1px solid rgba(52,211,153,0.28);
    color:#34d399;font-weight:600;
}
.sv-badge{font-size:11px;font-weight:600;padding:3px 11px;border-radius:99px;}
.sv-badge.h{background:rgba(5,150,105,0.18);color:#34d399;border:1px solid rgba(52,211,153,0.3);}
.sv-badge.m{background:rgba(186,117,23,0.18);color:#fbbf24;border:1px solid rgba(251,191,36,0.3);}
.sv-badge.l{background:rgba(160,156,192,0.1);color:#a09cc0;border:1px solid rgba(160,156,192,0.2);}

.sv-score{flex-shrink:0;text-align:right;}
.sv-score-n{font-size:24px;font-weight:700;color:#c4b5fd;}
.sv-score-p{font-size:11px;color:rgba(196,181,253,0.4);}
.sv-bar{width:72px;height:3px;background:rgba(255,255,255,0.07);border-radius:99px;overflow:hidden;margin-top:7px;}
.sv-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,#7c3aed,#34d399);}

.sv-empty{text-align:center;padding:4rem 1rem;color:rgba(196,181,253,0.35);font-size:15px;}

/* ── IDLE GRID ── */
.sv-idle-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin-top:4px;}
.sv-idle-card{
    background:rgba(255,255,255,0.025);border:1px solid rgba(140,80,255,0.13);
    border-radius:12px;padding:14px 17px;transition:all 0.2s;
}
.sv-idle-card:hover{background:rgba(124,58,237,0.14);border-color:rgba(140,80,255,0.45);transform:translateY(-3px);box-shadow:0 6px 24px rgba(124,58,237,0.2);}
.sv-idle-g{font-size:11px;color:#34d399;font-weight:600;font-family:monospace;margin-bottom:6px;letter-spacing:0.5px;}
.sv-idle-p{font-size:13px;color:rgba(255,255,255,0.65);line-height:1.4;}

.sv-hr{border:none;border-top:1px solid rgba(140,80,255,0.1);margin:2rem 0;}

/* ── TABLE ── */
.sv-db-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;}
.sv-db-ct{font-size:12px;color:rgba(52,211,153,0.7);background:rgba(5,150,105,0.1);border:1px solid rgba(52,211,153,0.2);padding:3px 13px;border-radius:99px;}
.sv-tw{border:1px solid rgba(140,80,255,0.13);border-radius:14px;overflow:hidden;max-height:430px;overflow-y:auto;}
.sv-tw::-webkit-scrollbar{width:4px;}
.sv-tw::-webkit-scrollbar-thumb{background:rgba(140,80,255,0.28);border-radius:99px;}
.sv-table{width:100%;border-collapse:collapse;font-size:13px;font-family:'Space Grotesk',sans-serif;}
.sv-table th{
    background:rgba(124,58,237,0.14);color:rgba(140,80,255,0.75);
    font-size:11px;text-transform:uppercase;letter-spacing:1px;font-weight:600;
    padding:12px 20px;text-align:left;position:sticky;top:0;z-index:1;
    border-bottom:1px solid rgba(140,80,255,0.12);backdrop-filter:blur(10px);
}
.sv-table td{padding:11px 20px;border-bottom:1px solid rgba(255,255,255,0.035);color:rgba(255,255,255,0.78);}
.sv-table tr:last-child td{border-bottom:none;}
.sv-table tr:hover td{background:rgba(124,58,237,0.1);}
.sv-g1{color:#c4b5fd;font-weight:600;font-family:monospace;}
.sv-g2{color:#34d399;font-weight:600;font-family:monospace;}
            
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# NATIVE SIDEBAR (Replaces broken HTML/JS version)
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sv-sb-title'>🌌 SilentVoice</div>", unsafe_allow_html=True)
    st.markdown("<hr class='sv-sb-hr'>", unsafe_allow_html=True)
    
    # Fully functional filter list that perfectly styles itself
    selected_filter = st.radio("Filters", ["All"] + GESTURES, label_visibility="collapsed")
    
    st.markdown("""
    <div style="margin-top: auto; text-align: center; padding-top: 30px; font-size: 11px; color: rgba(160,156,192,0.4); line-height: 2;">
        121 gesture combos<br><span style="color:rgba(52,211,153,0.5)">● AI semantic engine</span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sv-wrap">
<div class="sv-hero">
  <div class="sv-logo-stack">
    <div class="sv-ring"></div><div class="sv-ring"></div><div class="sv-ring"></div>
    <div class="sv-core">🌌</div>
  </div>
  <div class="sv-title">SilentVoice</div>
  <div class="sv-tagline"><span class="sv-dot"></span>121 gesture combos &nbsp;·&nbsp; semantic AI search</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SEARCH INPUT
# ─────────────────────────────────────────────────────────────────────────────
user_query = st.text_input(
    label="search",
    placeholder="🔍  Type what you want to say...",
    value=st.session_state.chip_query,
    label_visibility="collapsed",
    key="main_search",
)

# Reset chip query after using it so you can type freely afterwards
if st.session_state.chip_query:
    st.session_state.chip_query = ""

# ─────────────────────────────────────────────────────────────────────────────
# NATIVE URL CHIPS (Replaces broken JS DOM manipulation)
# ─────────────────────────────────────────────────────────────────────────────
chips = ["hello friend", "i am hungry", "play music", "i need help", "great job", "call me later", "i am stressed", "thank you"]
chips_html = '<div class="sv-chips">' + "".join(
    # Using real links that safely inform Streamlit to update the state
    f'<a href="?chip={urllib.parse.quote(s)}" target="_self" class="sv-chip">{s}</a>' for s in chips
) + "</div>"
st.markdown(chips_html, unsafe_allow_html=True)

st.markdown('<hr class="sv-hr">', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────────────────────
if user_query.strip():
    q_vec = model.encode(user_query, convert_to_tensor=True)
    hits  = util.semantic_search(q_vec, sentence_embeddings, top_k=5)[0]
    st.markdown(f'<div class="sv-label">Quantum results for <em style="color:#c4b5fd">&ldquo;{user_query}&rdquo;</em></div>', unsafe_allow_html=True)
    any_shown = False
    for i, hit in enumerate(hits):
        idx   = hit["corpus_id"]
        conf  = int(hit["score"] * 100)
        g1,g2 = combos[idx]
        phrase = sentences[idx]
        if conf < 22: continue
        any_shown = True
        rc = "r1" if i==0 else ("r2" if i==1 else "")
        bc = "h" if conf>=70 else ("m" if conf>=45 else "l")
        bl = "Strong sync" if conf>=70 else ("Partial sync" if conf>=45 else "Weak signal")
        st.markdown(f"""
        <div class="sv-card" style="animation-delay:{i*0.08}s">
          <div class="sv-rank {rc}">{i+1}</div>
          <div class="sv-card-body">
            <div class="sv-phrase">{phrase}</div>
            <div class="sv-meta">
              <span class="sv-gtag">{g1} &nbsp;+&nbsp; {g2}</span>
              <span class="sv-badge {bc}">{bl}</span>
            </div>
          </div>
          <div class="sv-score">
            <div class="sv-score-n">{conf}</div>
            <div class="sv-score-p">% match</div>
            <div class="sv-bar"><div class="sv-fill" style="width:{conf}%"></div></div>
          </div>
        </div>""", unsafe_allow_html=True)
    if not any_shown:
        st.markdown('<div class="sv-empty">Signal lost in the void — try rephrasing your thought.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="sv-label">Featured combos</div>', unsafe_allow_html=True)
    samples = [(k,v) for i,(k,v) in enumerate(phrases_dict.items()) if i%12==0][:8]
    idle = '<div class="sv-idle-grid">' + "".join(
        f'<div class="sv-idle-card"><div class="sv-idle-g">{g1} + {g2}</div><div class="sv-idle-p">{p}</div></div>'
        for (g1,g2),p in samples
    ) + "</div>"
    st.markdown(idle, unsafe_allow_html=True)

st.markdown('<hr class="sv-hr">', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE TABLE
# ─────────────────────────────────────────────────────────────────────────────
filtered = {k:v for k,v in phrases_dict.items() if selected_filter=="All" or selected_filter in k}
st.markdown(f"""
<div class="sv-db-head">
  <div class="sv-label" style="margin-bottom:0">Master gesture database</div>
  <div class="sv-db-ct">{len(filtered)} combos</div>
</div>""", unsafe_allow_html=True)

rows = "".join(
    f"<tr><td class='sv-g1'>{g1}</td><td class='sv-g2'>{g2}</td><td>{p}</td></tr>"
    for (g1,g2),p in filtered.items()
)
st.markdown(f"""
<div class="sv-tw">
  <table class="sv-table">
    <thead><tr><th>Gesture 1</th><th>Gesture 2</th><th>Phrase output</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>
</div>""", unsafe_allow_html=True)