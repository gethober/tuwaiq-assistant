import streamlit as st
from groq import Groq
import re
import base64

st.set_page_config(page_title="مساعد طويق", layout="centered")
st.title("⚡ مساعد طويق - شرح مفصل")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def clean_chinese(text):
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

# تصغير الايقونات
st.markdown("""
<style>
[data-testid="stFileUploader"], [data-testid="stCameraInput"] {
    transform: scale(0.8);
    margin: 0!important;
    padding: 0!important;
}
div[data-testid="stColumn"] { padding: 2px!important; }
</style>
""", unsafe_allow_html=True)

# --- سطر واحد صغير جنب بعض ---
c1, c2, c3, c4 = st.columns([5, 1, 1, 1.5])

with c1:
    query = st.text_input("", placeholder="وش تبي تسأل؟", label_visibility="collapsed")

with c2:
    uploaded = st.file_uploader("📎", type=["jpg","png","jpeg"], label_visibility="collapsed")

with c3:
    cam = st.camera_input("📸", label_visibility="collapsed")

with c4:
    send = st.button("ارسال 🚀", type="primary")

# صورة بدون حد
b64_image = None
if uploaded:
    st.image(uploaded, use_column_width=True) # بدون حد
    b64_image = base64.b64encode(uploaded.getvalue()).decode('utf-8')
elif cam:
    st.image(cam, use_column_width=True) # بدون حد
    b64_image = base64.b64encode(cam.getvalue()).decode('utf-8')

if send:
    if not query and not b64_image:
        st.warning("اكتب سؤال او ارفع صورة")
    else:
        with st.spinner("قاعد أكتب..."):
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

st.caption("📚 Groq الجديد ⚡")
