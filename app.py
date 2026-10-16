import streamlit as st
from groq import Groq
import re
import base64

st.set_page_config(page_title="مساعد طويق - شرح مفصل", layout="centered", page_icon="logo.png")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def clean_chinese(text):
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

st.markdown("<style>header {visibility: hidden;}</style>", unsafe_allow_html=True)

col_logo, col_text = st.columns([1, 5])
with col_logo:
    try: st.image("logo.png", width=60)
    except: st.write("🌴")
with col_text:
    st.markdown("### مساعد طويق - شرح مفصل")

if 'b64' not in st.session_state: st.session_state['b64'] = None
if 'last_answer' not in st.session_state: st.session_state['last_answer'] = ""
if 'full_answer' not in st.session_state: st.session_state['full_answer'] = ""

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
                ans = clean_chinese(res.choices[0].message.content)
                st.session_state['full_answer'] = ans
                st.session_state['last_answer'] = ans
            except:
                try:
                    fallback = "qwen/qwen3.8-27b" if st.session_state['b64'] else "openai/gpt-oss-120b"
                    res = client.chat.completions.create(model=fallback, messages=messages)
                    ans = clean_chinese(res.choices[0].message.content)
                    st.session_state['full_answer'] = ans
                    st.session_state['last_answer'] = ans
                except Exception as e:
                    st.error(f"خطأ: {e}")

# --- عرض الجواب مع الازرار ---
if st.session_state['last_answer']:
    st.success(st.session_state['last_answer'])
    
    # ازرار التحكم
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✂️ اختصر لي", use_container_width=True):
            with st.spinner("قاعد اختصر..."):
                try:
                    res = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {"role": "system", "content": "اختصر الكلام التالي بشكل مختصر مفيد بالعربي بدون حروف صينية."},
                            {"role": "user", "content": st.session_state['full_answer']}
                        ]
                    )
                    st.session_state['last_answer'] = clean_chinese(res.choices[0].message.content)
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")
    
    with col_b:
        if st.button("📖 فصل لي الكلام كامل", use_container_width=True):
            with st.spinner("قاعد افصل..."):
                try:
                    res = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {"role": "system", "content": "فصل واشرح الكلام التالي شرح مفصل جدا مقسم بالنقاط وامثلة بالعربي بدون حروف صينية."},
                            {"role": "user", "content": st.session_state['full_answer']}
                        ]
                    )
                    st.session_state['last_answer'] = clean_chinese(res.choices[0].message.content)
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")

    if st.button("↩️ ارجع للأصل"):
        st.session_state['last_answer'] = st.session_state['full_answer']
        st.rerun()

st.caption("📚 شغال بـ Groq الجديد ⚡")
