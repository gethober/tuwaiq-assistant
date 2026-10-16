import streamlit as st
from groq import Groq
import re
import base64

st.set_page_config(page_title="مساعد طويق - شرح مفصل", layout="centered")
st.title("⚡ مساعد طويق - شرح مفصل")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def clean_chinese(text):
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

# اخفاء كلام 200MB وتكبير الصورة بدون حد
st.markdown("""
<style>
small, [data-testid="stFileUploaderDropzoneInstructions"] div:last-child { display: none!important; }
[data-testid="stImage"] img { max-width: none!important; width: auto!important; height: auto!important; }
</style>
""", unsafe_allow_html=True)

b64_image = None
query = st.text_input("", placeholder="وش تبي تسأل؟", key="q")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    with st.popover("📎", use_container_width=True):
        uploaded = st.file_uploader(" ", type=["jpg","png","jpeg"], label_visibility="collapsed")
        if uploaded:
            # بدون حد - حجمها الطبيعي
            st.image(uploaded)
            b64_image = base64.b64encode(uploaded.getvalue()).decode('utf-8')
            st.session_state['b64'] = b64_image

with col2:
    with st.popover("📸", use_container_width=True):
        cam = st.camera_input(" ", label_visibility="collapsed")
        if cam:
            st.image(cam)
            b64_image = base64.b64encode(cam.getvalue()).decode('utf-8')
            st.session_state['b64'] = b64_image

with col3:
    send = st.button("🚀 ارسال", type="primary", use_container_width=True)

if 'b64' in st.session_state:
    b64_image = st.session_state['b64']

if send or (query and query!= ""):
    if not query and not b64_image:
        st.warning("اكتب سؤال او ارفع صورة")
    else:
        with st.spinner("قاعد أكتب لك..."):
            if b64_image:
                model = "meta-llama/llama-4-scout-17b-16e-instruct"
                messages = [
                    {"role": "system", "content": "انت دكتور سعودي اشرح مفصل بالعربي بدون حروف صينية ولا تختصر"},
                    {"role": "user", "content": [
                        {"type": "text", "text": query if query else "حل الواجب اللي في الصورة شرح مفصل"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                    ]}
                ]
            else:
                model = "openai/gpt-oss-20b"
                messages = [
                    {"role": "system", "content": "انت دكتور سعودي اشرح مفصل بالعربي بدون حروف صينية ولا تختصر"},
                    {"role": "user", "content": query}
                ]
            res = client.chat.completions.create(model=model, messages=messages)
            st.success(clean_chinese(res.choices[0].message.content))
            if 'b64' in st.session_state:
                del st.session_state['b64']

st.caption("📚 شغال بـ Groq الجديد ⚡")
