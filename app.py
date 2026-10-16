import streamlit as st
from groq import Groq
import re
import base64

st.set_page_config(page_title="مساعد طويق - شرح مفصل", layout="centered")
st.title("⚡ مساعد طويق - شرح مفصل")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def clean_chinese(text):
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

# --- زر الكاميرا الاختياري ---
show_cam = st.checkbox("📸 تبي تصور الواجب؟ اضغط هنا")

b64_image = None
if show_cam:
    pic = st.camera_input("خذ لقطة للواجب")
    if pic:
        st.image(pic, caption="تم التقاط الصورة", width=300)
        b64_image = base64.b64encode(pic.getvalue()).decode('utf-8')

# --- نظام النص حقك القديم ---
query = st.text_input("وش تبي تسأل؟", placeholder="مثال: ايش هي برمجة صفحات الانترنت؟ او اتركه فاضي اذا بتحل الصورة")

# زر واحد يحل الكل
if st.button("🚀 حل / اشرح", type="primary") or query:
    if not query and not b64_image:
        st.warning("اكتب سؤال او صور الواجب")
    else:
        with st.spinner("قاعد أكتب لك شرح مفصل..."):
            if b64_image:
                # اذا فيه صورة + نص
                messages = [
                    {
                        'role': 'system',
                        'content': """انت دكتور جامعي سعودي خبير تشرح للطلاب.
                        قوانينك:
                        1- جاوب بالعربي الفصحى مع لمسة عامية خفيفة
                        2- ممنوع تستخدم أي حرف صيني
                        3- اشرح شرح طويل ومفصل ومقسم بالنقاط
                        4- لا تختصر ابدا
                        5- اذا فيه صورة حلها واشرحها"""
                    },
                    {
                        'role': 'user',
                        'content': [
                            {"type": "text", "text": query if query else "حل الواجب اللي في الصورة شرح مفصل"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                        ]
                    }
                ]
                model = "meta-llama/llama-4-scout-17b-16e-instruct"
            else:
                # اذا نص فقط (نظامك القديم)
                messages = [
                    {
                        'role': 'system',
                        'content': """انت دكتور جامعي سعودي خبير تشرح للطلاب.
                        قوانينك:
                        1- جاوب بالعربي الفصحى مع لمسة عامية خفيفة
                        2- ممنوع تستخدم أي حرف صيني
                        3- اشرح شرح طويل ومفصل ومقسم بالنقاط
                        4- لا تختصر ابدا"""
                    },
                    {'role': 'user', 'content': query}
                ]
                model = "openai/gpt-oss-20b"

            response = client.chat.completions.create(model=model, messages=messages)
            answer = clean_chinese(response.choices[0].message.content)
            st.success(answer)

st.caption("📚 شغال بـ Groq الجديد ⚡ - نص + كاميرا اختياري")
