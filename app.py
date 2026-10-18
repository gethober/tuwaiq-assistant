import streamlit as st
from groq import Groq
import base64, os
import fitz
import docx

st.set_page_config(page_title="بيان", layout="centered", page_icon="📖")

api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)
if not api_key:
    st.error("حط GROQ_API_KEY في secrets.toml"); st.stop()
client = Groq(api_key=api_key)

TEXT_MODEL = "openai/gpt-oss-20b"  # الموديل الوحيد اللي شغال حالياً للمجاني

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
    except Exception as e:
        return f"خطأ قراءة الملف: {e}"

if 'chat' not in st.session_state: st.session_state.chat = []
if 'file_text' not in st.session_state: st.session_state.file_text = None
if 'file_name' not in st.session_state: st.session_state.file_name = None

st.markdown("""
<style>
header{visibility:hidden}
#MainMenu{visibility:hidden}
</style>
<div style='text-align:center;margin-bottom:20px'>
    <h1 style='font-size:90px;font-weight:950;margin:0;color:#34D399'>بيان</h1>
    <p style='color:#9CA3AF;font-weight:700'>مساعدك التقني</p>
</div>
""", unsafe_allow_html=True)

for m in st.session_state.chat:
    with st.chat_message(m["role"]): st.markdown(m["content"])

mode = st.radio(" ", ["📖 تفصيلي", "✂️ مختصر", "⚖️ متوسط"], horizontal=True, label_visibility="collapsed")

prompt = st.chat_input("وش تبي بيان يطلع لك؟", accept_file=True, file_type=["png","jpg","jpeg","webp","pdf","docx","txt","py","js"])

if prompt:
    query = prompt.text.strip() if prompt.text else ""
    uploaded = prompt.files[0] if prompt.files else None

    if uploaded:
        st.session_state.file_name = uploaded.name
        if uploaded.name.lower().endswith((".png",".jpg",".jpeg",".webp")):
            st.session_state.file_text = f"[صورة مرفقة اسمها {uploaded.name} - المستخدم يسأل عنها]"
        else:
            st.session_state.file_text = extract_text(uploaded)

    user_display = query if query else f"📎 {st.session_state.file_name or ''}"
    if user_display:
        st.session_state.chat.append({"role":"user","content":user_display})
        with st.chat_message("user"): st.markdown(user_display)

    full_text = f"ملف: {st.session_state.file_name}\n{st.session_state.file_text or ''}\n\nسؤال: {query or 'اشرح'}"

    if "مختصر" in mode: extra = "اختصر."
    elif "متوسط" in mode: extra = "توازن."
    else: extra = "بتفصيل."

    system_msg = {"role":"system","content":f"أنت بيان، ترد بالعربي. {extra}"}
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat[-6:-1]]

    try:
        with st.chat_message("assistant"):
            with st.spinner("بيان يفكر..."):
                messages = [system_msg] + history + [{"role":"user","content":full_text}]
                res = client.chat.completions.create(model=TEXT_MODEL, messages=messages, temperature=0.5, max_tokens=2048)
                ans = res.choices[0].message.content
                st.markdown(ans)
                st.session_state.chat.append({"role":"assistant","content":ans})
    except Exception as e:
        st.error(f"خطأ: {e}")

if st.button("🗑️ مسح المحادثة"):
    st.session_state.chat=[]; st.session_state.file_text=None; st.session_state.file_name=None
    st.rerun()
