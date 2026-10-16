import streamlit as st
from groq import Groq
import re
import base64

st.set_page_config(page_title="مساعد طويق - شرح مفصل", layout="centered")
st.title("⚡ مساعد طويق - شرح مفصل")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def clean_chinese(text):
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

# --- الشريط جنب بعض ---
col1, col2, col3 = st.columns([6, 1, 1])

with col1:
    query = st.text_input("سؤالك", placeholder="اكتب سؤالك هنا...", label_visibility="collapsed")

with col2:
    # رفع صورة يفتح على طول
    uploaded = st.file_uploader("📎", type=["jpg","png","jpeg"], label_visibility="collapsed")

with col3:
    # كاميرا تفتح على طول
    cam = st.camera_input("📸", label_visibility="collapsed")

# معالجة الصورة
b64_image = None
if uploaded:
    st.image(uploaded, width=200)
    b64_image = base64.b64encode(uploaded.getvalue()).decode('utf-8')
elif cam:
    st.image(cam, width=200)
    b64_image = base64.b64encode(cam.getvalue()).decode('utf-8')

# زر ارسال واحد للكل
if st.button("🚀 ارسال", type="primary", use_container_width=True):
    if not query and not b64_image:
        st.warning("اكتب سؤال او ارفع صورة")
    else:
        with st.spinner("قاعد أكتب لك شرح مفصل..."):
            if b64_image:
                model = "meta-llama/llama-4-scout-17b-16e-instruct"
                messages = [
                    {"role": "system", "content": """انت دكتور جامعي سعودي خبير تشرح للطلاب.
                    1- جاوب بالعربي الفصحى مع لمسة عامية خفيفة
                    2- ممنوع حروف صينية
                    3- اشرح شرح طويل ومفصل ومقسم بالنقاط
                    4- اذا فيه صورة حلها واشرحها خطوة بخطوة
                    5- لا تختصر ابدا"""},
                    {"role": "user", "content": [
                        {"type": "text", "text": query if query else "حل الواجب اللي في الصورة شرح مفصل"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                    ]}
                ]
            else:
                model = "openai/gpt-oss-20b"
                messages = [
                    {"role": "system", "content": """انت دكتور جامعي سعودي خبير تشرح للطلاب.
                    1- جاوب بالعربي الفصحى مع لمسة عامية خفيفة
                    2- ممنوع حروف صينية
                    3- اشرح شرح طويل ومفصل ومقسم بالنقاط
                    4- لا تختصر ابدا"""},
                    {"role": "user", "content": query}
                ]

            response = client.chat.completions.create(model=model, messages=messages)
            answer = clean_chinese(response.choices[0].message.content)
            st.success(answer)

st.caption("📚 شغال بـ Groq الجديد ⚡ | 📎 رفع | 📸 كاميرا")
