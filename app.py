import streamlit as st
from groq import Groq
import re
import base64

st.set_page_config(page_title="مساعد طويق - شرح مفصل", layout="centered")
st.title("⚡ مساعد طويق - شرح مفصل")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def clean_chinese(text):
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

# تنسيق يخلي الازرار حلوة
st.markdown("""
<style>
.stButton>button { border-radius: 20px; }
</style>
""", unsafe_allow_html=True)

b64_image = None

# --- شريط الكتابة ---
query = st.text_input("", placeholder="وش تبي تسأل؟", key="q")

# --- سطر الايقونات الصغيرة تحت النص ---
col1, col2, col3, col4 = st.columns([1, 1, 1, 4])

with col1:
    with st.popover("📎", use_container_width=True):
        uploaded = st.file_uploader("ارفع صورة", type=["jpg","png","jpeg"], label_visibility="collapsed")
        if uploaded:
            st.image(uploaded, use_container_width=True)
            b64_image = base64.b64encode(uploaded.getvalue()).decode('utf-8')
            st.session_state['b64'] = b64_image

with col2:
    with st.popover("📸", use_container_width=True):
        cam = st.camera_input("صور", label_visibility="collapsed")
        if cam:
            st.image(cam, use_container_width=True)
            b64_image = base64.b64encode(cam.getvalue()).decode('utf-8')
            st.session_state['b64'] = b64_image

with col3:
    send = st.button("🚀 ارسال", type="primary", use_container_width=True)

# استرجاع الصورة لو موجودة
if 'b64' in st.session_state:
    b64_image = st.session_state['b64']

if send or query:
    if not query and not b64_image:
        st.warning("اكتب سؤال او ارفع صورة")
    else:
        with st.spinner("قاعد أكتب لك شرح مفصل..."):
            if b64_image:
                model = "meta-llama/llama-4-scout-17b-16e-instruct"
                messages = [
                    {"role": "system", "content": "انت دكتور جامعي سعودي خبير تشرح للطلاب. جاوب بالعربي مفصل بدون حروف صينية ولا تختصر ابدا. اذا فيه صورة حلها واشرحها خطوة بخطوة."},
                    {"role": "user", "content": [
                        {"type": "text", "text": query if query else "حل الواجب اللي في الصورة شرح مفصل"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                    ]}
                ]
            else:
                model = "openai/gpt-oss-20b"
                messages = [
                    {"role": "system", "content": "انت دكتور جامعي سعودي خبير تشرح للطلاب. جاوب بالعربي مفصل بدون حروف صينية ولا تختصر ابدا."},
                    {"role": "user", "content": query}
                ]

            response = client.chat.completions.create(model=model, messages=messages)
            answer = clean_chinese(response.choices[0].message.content)
            st.success(answer)
            # امسح الصورة بعد الحل
            if 'b64' in st.session_state:
                del st.session_state['b64']

st.caption("📚 شغال بـ Groq الجديد ⚡")
