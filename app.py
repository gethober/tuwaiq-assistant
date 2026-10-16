import streamlit as st
from groq import Groq
import base64
import re

st.set_page_config(page_title="مساعد طويق", layout="centered")
st.title("📸 مساعد طويق")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def clean_chinese(t):
    return re.sub(r'[\u4e00-\u9fff]+', '', t)

# --- لقطة وحدة بس ---
st.write("اضغط الكاميرا، خذ لقطة للواجب، وبيحل لك فورا 👇")
pic = st.camera_input("")

if pic:
    # يعرض اللقطة
    st.image(pic, use_column_width=True)

    with st.spinner("🔍 قاعد احلل الصورة واشرح لك..."):
        b64 = base64.b64encode(pic.getvalue()).decode('utf-8')

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": """انت دكتور جامعي سعودي.
                    المطلوب:
                    1- شف الواجب اللي في الصورة
                    2- اشرح الحل خطوة بخطوة بالعربي
                    3- قسم الشرح: الفكرة > الخطوات > الجواب النهائي
                    4- خلك مفصل ولا تختصر
                    5- ممنوع حروف صينية"""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "اشرح لي حل هذا الواجب بالتفصيل"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]
                }
            ]
        )

        ans = clean_chinese(response.choices[0].message.content)

        st.divider()
        st.subheader("✅ الشرح:")
        st.write(ans)

        # زر تحميل الحل
        st.download_button("📥 حفظ الشرح", ans, file_name="al-hal.txt")
