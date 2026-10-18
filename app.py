import streamlit as st
from groq import Groq
import base64, os
import fitz, docx

st.set_page_config(page_title="بيان", layout="centered", page_icon="📖")

api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)
if not api_key:
    st.error("حط GROQ_API_KEY"); st.stop()
client = Groq(api_key=api_key)

def extract_text(file):
    try:
        name = file.name.lower()
        data = file.getvalue()
        if name.endswith(".pdf"):
            doc = fitz.open(stream=data, filetype="pdf")
            return "".join([p.get_text() for p in doc])[:15000]
        if name.endswith(".docx"):
            d = docx.Document(file)
            return "\n".join([p.text for p in d.paragraphs])[:15000]
        return data.decode('utf-8', errors='ignore')[:15000]
    except: return None

if 'chat' not in st.session_state: st.session_state.chat = []
if 'b64' not in st.session_state: st.session_state.b64 = None
if 'file_text' not in st.session_state: st.session_state.file_text = None

st.markdown("""
<style>
header{visibility:hidden}
#MainMenu{visibility:hidden}
.stButton>button[kind="primary"]{background:#0F5D2F!important}
</style>
<div style='text-align:center;margin-bottom:20px'>
    <h1 style='font-size:90px;font-weight:950;margin:0;color:#34D399;text-shadow:0 0 20px rgba(52,211,153,.5);-webkit-text-stroke:1.5px #064E3B'>بيان</h1>
    <p style='color:#9CA3AF;font-weight:700'>مساعدك التقني</p>
</div>
""", unsafe_allow_html=True)

for m in st.session_state.chat:
    with st.chat_message(m["role"]): st.markdown(m["content"])

mode = st.radio(" ", ["📖 تفصيلي", "✂️ مختصر", "⚖️ متوسط"], horizontal=True, label_visibility="collapsed")

# --- هذا هو الحل: chat_input فيه مشبك داخل ويدعم Ctrl+V ---
prompt = st.chat_input(
    "وش تبي بيان يطلع لك من الملف؟ 📎 تقدر تلصق الصورة هنا Ctrl+V",
    accept_file=True,
    file_type=["png","jpg","jpeg","webp","pdf","docx","txt","py","js"]
)

if prompt:
    query = prompt.text
    uploaded = prompt.files[0] if prompt.files else None

    if uploaded:
        st.session_state.file_name = uploaded.name
        if uploaded.name.lower().endswith((".png",".jpg",".jpeg",".webp")):
            st.session_state.b64 = base64.b64encode(uploaded.getvalue()).decode()
            st.session_state.file_text = None
        else:
            st.session_state.file_text = extract_text(uploaded)
            st.session_state.b64 = None
        with st.chat_message("user"):
            st.markdown(f"📎 {uploaded.name}")
            if st.session_state.b64: st.image(uploaded, width=200)

    if query or uploaded:
        user_display = query or f"📎 {uploaded.name if uploaded else ''}"
        if not uploaded: # اذا ما فيه ملف مرفوع بالضغطه هذي، استخدم اخر ملف
            st.session_state.chat.append({"role":"user","content":user_display})
            with st.chat_message("user"): st.markdown(user_display)

        full = ""
        if st.session_state.file_text:
            full = f"الملف {st.session_state.file_name}:\n{st.session_state.file_text}\n\nسؤال:{query or 'اشرح'}"
        else:
            full = query or "اشرح الصورة"

        extra = "اختصر." if "مختصر" in mode else "متوسط." if "متوسط" in mode else "بتفصيل مع امثلة."
        messages = [{"role":"system","content":f"انت بيان، مساعد تقني. {extra}"}]
        messages += st.session_state.chat[-6:]
        messages.append({"role":"user","content":full})

        with st.chat_message("assistant"):
            with st.spinner("بيان يفكر..."):
                try:
                    if st.session_state.b64:
                        messages[-1] = {"role":"user","content":[
                            {"type":"text","text":full},
                            {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{st.session_state.b64}"}}
                        ]}
                        model="meta-llama/llama-4-scout-17b-16e-instruct"
                    else:
                        model="openai/gpt-oss-20b"
                    
                    res = client.chat.completions.create(model=model, messages=messages, temperature=0.5)
                    ans = res.choices[0].message.content
                    st.markdown(ans)
                    st.session_state.chat.append({"role":"assistant","content":ans})
                except Exception as e:
                    st.error(f"خطأ: {e}")

if st.button("🗑️ مسح المحادثة"):
    st.session_state.chat=[]; st.session_state.file_text=None; st.session_state.b64=None; st.rerun()
