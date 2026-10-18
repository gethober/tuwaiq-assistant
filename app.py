import streamlit as st
from groq import Groq
import base64, os
import fitz, docx

st.set_page_config(page_title="بيان - مساعدك التقني", layout="centered", page_icon="📖")

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    try: api_key = st.secrets["GROQ_API_KEY"]
    except:
        st.error("حط GROQ_API_KEY في Secrets"); st.stop()
client = Groq(api_key=api_key)

def extract_text(uploaded):
    try:
        name = uploaded.name.lower()
        data = uploaded.getvalue()
        if name.endswith(".pdf"):
            doc = fitz.open(stream=data, filetype="pdf")
            return "".join([p.get_text() for p in doc])[:15000]
        if name.endswith(".docx"):
            d = docx.Document(uploaded)
            return "\n".join([p.text for p in d.paragraphs])[:15000]
        return data.decode('utf-8', errors='ignore')[:15000]
    except: return None

if 'chat' not in st.session_state: st.session_state.chat = []
if 'b64' not in st.session_state: st.session_state.b64 = None
if 'file_text' not in st.session_state: st.session_state.file_text = None
if 'file_name' not in st.session_state: st.session_state.file_name = None

st.markdown("""
<style>
header{visibility:hidden}
.stButton>button[kind="primary"]{background:#0F5D2F!important;border-color:#0F5D2F!important}

/* --- تصليح خانة السؤال والمشبك في نفس الخانة --- */
div[data-testid="stTextInput"]{flex:1}
div[data-testid="stTextInput"] input{
    height: 48px;
    border-radius: 14px !important;
    padding-right: 55px !important;
    background: #22262f !important;
    border: 1px solid #2f3542 !important;
}

/* حاوية الملف */
div[data-testid="stFileUploader"]{
    width: 48px !important;
    margin-left: -58px !important;
    margin-top: 2px;
    z-index: 10;
}
/* اخفاء كل زوايد الـ uploader */
div[data-testid="stFileUploader"] section{
    padding:0!important; border:none!important; background:transparent!important; min-height:0!important;
}
div[data-testid="stFileUploader"] label, div[data-testid="stFileUploader"] small, 
div[data-testid="stFileUploader"] button, div[data-testid="stFileUploader"] section div{
    display:none!important;
}
/* زر المشبك فقط */
div[data-testid="stFileUploader"] [data-testid="stFileUploadDropzone"]{
    display:flex!important;
    width:48px!important; height:48px!important;
    align-items:center; justify-content:center;
    background:#2a303c!important;
    border:1px solid #3a414f!important;
    border-radius:12px!important;
    cursor:pointer;
}
div[data-testid="stFileUploader"] [data-testid="stFileUploadDropzone"]::after{
    content:"📎"; font-size:22px;
}
</style>
<div style='text-align:center;margin-bottom:22px'>
    <h1 style='font-size:95px;font-weight:950;margin:0;line-height:0.9;color:#34D399;text-shadow:0 2px 0 #064E3B,0 0 25px rgba(52,211,153,.4);-webkit-text-stroke:1.5px #064E3B'>بيان</h1>
    <p style='font-size:20px;font-weight:700;color:#9CA3AF;margin-top:8px'>مساعدك التقني</p>
</div>
""", unsafe_allow_html=True)

for m in st.session_state.chat:
    with st.chat_message(m["role"]): st.markdown(m["content"])

mode = st.radio("طريقة الشرح", ["📖 تفصيلي", "✂️ مختصر", "⚖️ متوسط"], horizontal=True, label_visibility="collapsed")

# سطر واحد فيه السؤال والمشبك
col1, col2 = st.columns([1, 0.12], gap="small")
with col1:
    query = st.text_input("سؤال", placeholder="وش تبي بيان يطلع لك من الملف؟", label_visibility="collapsed")
with col2:
    uploaded = st.file_uploader(" ", type=None, label_visibility="collapsed")

if uploaded:
    st.session_state.file_name = uploaded.name
    if uploaded.name.lower().endswith((".png",".jpg",".jpeg",".webp")):
        st.image(uploaded, width=200)
        st.session_state.b64 = base64.b64encode(uploaded.getvalue()).decode()
        st.session_state.file_text = None
        st.toast("✅ تم ارفاق الصورة")
    else:
        txt = extract_text(uploaded)
        if txt:
            st.session_state.file_text = txt; st.session_state.b64 = None
            st.toast(f"✅ {uploaded.name}")
        else: st.error("ما قدرت أقرأ الملف")

c1, c2 = st.columns(2)
send = c1.button("🚀 ارسال", type="primary", use_container_width=True)
clear = c2.button("🗑️ مسح", use_container_width=True)

if clear:
    st.session_state.chat=[]; st.session_state.file_text=None; st.session_state.b64=None; st.rerun()

if send:
    if not query and not st.session_state.file_text and not st.session_state.b64:
        st.warning("اكتب سؤال أو ارفق ملف"); st.stop()

    st.session_state.chat.append({"role":"user","content":query or f"📎 {st.session_state.file_name}"})
    with st.chat_message("user"): st.markdown(query or st.session_state.file_name)

    full = f"الملف {st.session_state.file_name}:\n{st.session_state.file_text}\n\nسؤال: {query or 'اشرح'}" if st.session_state.file_text else (query or "اشرح الصورة")
    extra = "اختصر." if "مختصر" in mode else "شرح متوسط." if "متوسط" in mode else "اشرح بتفصيل مع أمثلة."
    
    messages=[{"role":"system","content":f"انت بيان، مساعدك التقني. {extra}"}]
    messages+=st.session_state.chat[-6:]
    messages[-1]={"role":"user","content":full}

    with st.spinner("بيان يفكر..."):
        try:
            if st.session_state.b64:
                messages[-1]={"role":"user","content":[{"type":"text","text":full},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{st.session_state.b64}"}}]}
                model="meta-llama/llama-4-scout-17b-16e-instruct"
            else: model="openai/gpt-oss-20b"
            res=client.chat.completions.create(model=model,messages=messages,temperature=0.5)
            ans=res.choices[0].message.content
            with st.chat_message("assistant"): st.markdown(ans)
            st.session_state.chat.append({"role":"assistant","content":ans})
        except Exception as e: st.error(f"خطأ: {e}")
