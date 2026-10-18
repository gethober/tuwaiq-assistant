import streamlit as st
from groq import Groq
from PIL import Image
import re, base64, os
import fitz  # PDF
import docx  # Word

st.set_page_config(page_title="بيان - مساعدك التقني", layout="centered", page_icon="icon.png")
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

def clean_chinese(text):
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

def extract_text_from_file(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf" or uploaded_file.name.endswith(".pdf"):
            doc = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
            text = "".join([p.get_text() for p in doc])
            return text[:15000]
        elif uploaded_file.name.endswith(".docx"):
            doc = docx.Document(uploaded_file)
            text = "\n".join([p.text for p in doc.paragraphs])
            return text[:15000]
        elif uploaded_file.name.endswith((".txt", ".py", ".js", ".html", ".css", ".json", ".csv")):
            return uploaded_file.getvalue().decode('utf-8', errors='ignore')[:15000]
        else:
            return None
    except Exception as e:
        return f"ما قدرت اقرأ الملف: {e}"

# ذاكرة
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'b64' not in st.session_state: st.session_state['b64'] = None
if 'file_text' not in st.session_state: st.session_state['file_text'] = None
if 'file_name' not in st.session_state: st.session_state['file_name'] = None

# --- ستايل بيان الجديد ---
st.markdown("""
<style>
header {visibility: hidden;}
.stButton>button[kind="primary"] {
    background-color: #0F5D2F !important;
    border-color: #0F5D2F !important;
    color: white !important;
}
.stButton>button[kind="primary"]:hover {
    background-color: #0A4221 !important;
}
</style>
<div style='text-align: center; margin-top: -30px; margin-bottom: 20px;'>
    <h1 style='font-size: 85px; font-weight: 900; color: #0F5D2F; margin: 0; line-height: 0.9; font-family: sans-serif;'>بيان</h1>
    <p style='font-size: 22px; color: #5a5a5a; margin-top: 8px; letter-spacing: 1px;'>مساعدك التقني</p>
</div>
""", unsafe_allow_html=True)

# عرض الشات القديم
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

mode = st.radio("كيف تبي الشرح؟", ["📖 فصل لي الكلام كامل", "✂️ اختصر لي", "⚖️ شرح متوسط"], horizontal=True, label_visibility="collapsed")

uploaded = st.file_uploader("📎 ارفع أي ملف هنا (صورة، PDF، وورد، كود...)", type=None)

if uploaded:
    st.session_state.file_name = uploaded.name
    if uploaded.type.startswith("image/"):
        st.image(uploaded, width=300)
        st.session_state['b64'] = base64.b64encode(uploaded.getvalue()).decode('utf-8')
        st.session_state['file_text'] = None
    else:
        text = extract_text_from_file(uploaded)
        if text:
            st.success(f"✅ تم قراءة {uploaded.name} ({len(text)} حرف)")
            with st.expander("شوف النص المستخرج"):
                st.text(text[:2000])
            st.session_state['file_text'] = text
            st.session_state['b64'] = None
        else:
            st.error("ما قدرت اقرأ الملف")

query = st.text_input("وش تبي تسأل عن الملف؟", placeholder="مثال: اشرح لي هذا الملف، لخصه، حل الواجب...")

col1, col2 = st.columns(2)
with col1:
    send = st.button("🚀 ارسال", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.file_text = None
        st.session_state.b64 = None
        st.rerun()

if send:
    if not query and not st.session_state.file_text and not st.session_state.b64:
        st.warning("اكتب سؤال او ارفع ملف")
    else:
        if st.session_state.file_text:
            user_content = f"ملف مرفوع اسمه {st.session_state.file_name}:\n---\n{st.session_state.file_text}\n---\n سؤال المستخدم: {query if query else 'اشرح لي هذا الملف كامل'}"
        elif st.session_state.b64:
            user_content = query if query else "اشرح الصورة"
        else:
            user_content = query

        st.session_state.chat_history.append({"role": "user", "content": f"📎 {st.session_state.file_name + ': ' if st.session_state.file_name else ''}{user_content[:200]}"})
        with st.chat_message("user"):
            st.markdown(user_content[:1000] + "...")

        # ربط طريقة الشرح بالبرومبت
        if "اختصر" in mode:
            extra = "اختصر الشرح وخلك مباشر."
        elif "متوسط" in mode:
            extra = "اشرح شرح متوسط مو طويل ولا قصير."
        else:
            extra = "فصل الشرح بالتفصيل الممل مع امثلة."

        system_prompt = f"انت مساعد اسمه بيان، مساعدك التقني. دكتور سعودي خبير. اشرح الملف المرفوع بالعربي بالتفصيل. {extra} تذكر محادثتنا السابقة."

        messages = [{"role": "system", "content": system_prompt}]
        for m in st.session_state.chat_history[-8:]:
            messages.append(m)
        messages.append({"role": "user", "content": user_content})

        with st.spinner("بيان قاعد يقرأ ملفك..."):
            try:
                if st.session_state.b64:
                    model = "meta-llama/llama-4-scout-17b-16e-instruct"
                    messages[-1] = {"role": "user", "content": [
                        {"type": "text", "text": user_content},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{st.session_state['b64']}"}}
                    ]}
                else:
                    model = "openai/gpt-oss-20b"

                res = client.chat.completions.create(model=model, messages=messages, temperature=0.6)
                answer = clean_chinese(res.choices[0].message.content)
                
                with st.chat_message("assistant"):
                    st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"خطأ: {e}")
