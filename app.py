import streamlit as st
from groq import Groq
import re
import base64

st.set_page_config(page_title="مساعد طويق - شرح مفصل", layout="centered", page_icon="logo.png")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def clean_chinese(text):
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

# اخفاء الهيدر وعلامة الرابط
st.markdown("""
<style>
header {visibility: hidden;}
a, .anchor-link, [data-testid="stHeaderActionElements"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

# فوق
col_logo, col_text = st.columns([1, 5])
with col_logo:
    try: 
        st.image("logo.png", width=60)
    except: 
        st.write("🌴")
with col_text:
    st.markdown("### مساعد طويق - شرح مفصل")

if 'b64' not in st.session_state: 
    st.session_state['b64'] = None

# الاختيار قبل الارسال
mode = st.radio(
    "كيف تبي الشرح؟",
    ["📖 فصل لي الكلام كامل", "✂️ اختصر لي", "⚖️ شرح متوسط"],
    horizontal=True
)

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
        if "اختصر" in mode:
            system_prompt = "انت دكتور سعودي. اختصر الجواب في 5 نقاط مختصرة مفيدة بالعربي. ممنوع حروف صينية."
        elif "فصل" in mode:
            system_prompt = "انت دكتور جامعي سعودي خبير. فصل واشرح شرح مفصل جدا جدا مقسم بالنقاط وامثلة وخطوات بالعربي. لا تختصر ابدا. ممنوع حروف صينية."
        else:
            system_prompt = "انت دكتور سعودي. اشرح شرح متوسط واضح بالنقاط بالعربي. ممنوع حروف صينية."

        with st.spinner("قاعد أكتب لك..."):
            try:
                if st.session_state['b64']:
                    model = "qwen/qwen3.6-27b"
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": [
                            {"type": "text", "text": query if query else "حل الواجب اللي في الصورة"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{st.session_state['b64']}"}}
                        ]}
                    ]
                else:
                    model = "openai/gpt-oss-20b"
                    messages = [
                        {"role": "system", "content": system_prompt},
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

# --- تحت مره النهاية ---
st.markdown("<div style='margin-top:120px;'></div>", unsafe_allow_html=True)

# الصورة اللي ارسلتها فوق الكلام
col_a, col_b, col_c = st.columns([2, 1, 2])
with col_b:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        pass

st.markdown("<div style='text-align:center; font-size:55px; font-weight:900; letter-spacing:4px; color:white; margin-top:15px;'>MADE IN SAUDI</div>", unsafe_allow_html=True)
