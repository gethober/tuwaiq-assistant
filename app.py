import streamlit as st
from groq import Groq
import re
import base64

st.set_page_config(page_title="مساعد طويق - شرح مفصل", layout="centered", page_icon="logo.png")

# --- اللوغو فوق بالنص بدون حد ---
col_logo1, col_logo2, col_logo3 = st.columns([1, 1, 1])
with col_logo2:
    st.image("logo.png", use_container_width=True)

st.markdown("<h2 style='text-align:center;'>⚡ مساعد طويق - شرح مفصل</h2>", unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def clean_chinese(text):
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

if 'b64' not in st.session_state:
    st.session_state['b64'] = None

query = st.text_input("وش تبي تسأل؟", placeholder="مثال: ايش هي برمجة صفحات الانترنت؟")

c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    with st.popover("📎 رفع", use_container_width=True):
        up = st.file_uploader(" ", type=["jpg","png","jpeg"], label_visibility="collapsed")
        if up:
            st.image(up)
            st.session_state['b64'] = base64.b64encode(up.getvalue()).decode('utf-8')
with c2:
    with st.popover("📸 كاميرا", use_container_width=True):
        cam = st.camera_input(" ", label_visibility="collapsed")
        if cam:
            st.image(cam)
            st.session_state['b64'] = base64.b64encode(cam.getvalue()).decode('utf-8')
with c3:
    send = st.button("🚀 ارسال", type="primary", use_container_width=True)

if st.session_state['b64']:
    st.success("📷 تم حفظ الصورة")
    if st.button("❌ احذف الصورة"):
        st.session_state['b64'] = None
        st.rerun()

if send:
    if not query and not st.session_state['b64']:
        st.warning("اكتب سؤال او ارفع صورة")
    else:
        with st.spinner("قاعد أكتب لك..."):
            try:
                if st.session_state['b64']:
                    model = "qwen/qwen3.6-27b"
                    messages = [
                        {"role": "system", "content": "انت دكتور جامعي سعودي خبير. اشرح بالعربي شرح مفصل مقسم بالنقاط. ممنوع حروف صينية. حل الصورة واشرحها خطوة بخطوة."},
                        {"role": "user", "content": [
                            {"type": "text", "text": query if query else "حل الواجب اللي في الصورة شرح مفصل"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{st.session_state['b64']}"}}
                        ]}
                    ]
                else:
                    model = "openai/gpt-oss-20b"
                    messages = [
                        {"role": "system", "content": "انت دكتور جامعي سعودي خبير. اشرح بالعربي شرح مفصل مقسم بالنقاط بدون حروف صينية."},
                        {"role": "user", "content": query}
                    ]
                res = client.chat.completions.create(model=model, messages=messages)
                st.success(clean_chinese(res.choices[0].message.content))
            except:
                try:
                    fallback = "qwen/qwen3.8-27b" if st.session_state['b64'] else "openai/gpt-oss-120b"
                    res = client.chat.completions.create(model=fallback, messages=messages)
                    st.success(clean_chinese(res.choices[0].message.content))
                except Exception as e:
                    st.error(f"خطأ: {e}")

st.caption("📚 شغال بـ Groq الجديد ⚡")
