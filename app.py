import streamlit as st
from groq import Groq
import re
import base64

st.set_page_config(page_title="مساعد طويق - شرح مفصل", layout="centered")
st.title("⚡ مساعد طويق - شرح مفصل")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def clean_chinese(text):
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

st.markdown("""
<style>
small { display: none!important; }
</style>
""", unsafe_allow_html=True)

# --- حفظ الصورة ---
if 'b64' not in st.session_state:
    st.session_state['b64'] = None

query = st.text_input("وش تبي تسأل؟", placeholder="مثال: ايش هي برمجة صفحات الانترنت؟")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    with st.popover("📎 رفع", use_container_width=True):
        uploaded = st.file_uploader(" ", type=["jpg","png","jpeg"], label_visibility="collapsed")
        if uploaded:
            st.image(uploaded) # بدون حد - حجمها الطبيعي
            st.session_state['b64'] = base64.b64encode(uploaded.getvalue()).decode('utf-8')

with col2:
    with st.popover("📸 كاميرا", use_container_width=True):
        cam = st.camera_input(" ", label_visibility="collapsed")
        if cam:
            st.image(cam)
            st.session_state['b64'] = base64.b64encode(cam.getvalue()).decode('utf-8')

with col3:
    send = st.button("🚀 ارسال", type="primary", use_container_width=True)

# عرض الصورة المرفوعة
if st.session_state['b64']:
    st.info("📷 تم حفظ الصورة - جاهزة للحل")
    if st.button("❌ احذف الصورة"):
        st.session_state['b64'] = None
        st.rerun()

if send:
    if not query and not st.session_state['b64']:
        st.warning("اكتب سؤال او ارفع صورة")
    else:
        try:
            with st.spinner("قاعد أكتب لك شرح مفصل..."):
                if st.session_state['b64']:
                    # موديل يفهم الصور - هذا شغال في Groq الحين
                    model = "meta-llama/llama-4-scout-17b-16e-instruct"
                    messages = [
                        {"role": "system", "content": "انت دكتور جامعي سعودي خبير. اشرح بالعربي شرح مفصل مقسم بالنقاط بدون حروف صينية ولا تختصر."},
                        {"role": "user", "content": [
                            {"type": "text", "text": query if query else "حل الواجب اللي في الصورة شرح مفصل خطوة بخطوة"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{st.session_state['b64']}"}}
                        ]}
                    ]
                else:
                    # موديل النص - شغال 100%
                    model = "llama-3.3-70b-versatile"
                    messages = [
                        {"role": "system", "content": "انت دكتور جامعي سعودي خبير. اشرح بالعربي شرح مفصل مقسم بالنقاط بدون حروف صينية ولا تختصر ابدا."},
                        {"role": "user", "content": query}
                    ]

                response = client.chat.completions.create(model=model, messages=messages)
                answer = clean_chinese(response.choices[0].message.content)
                st.success(answer)

        except Exception as e:
            st.error(f"صار خطأ: {e}")
            st.info("جرب موديل ثاني: تأكد انك ضفت GROQ_API_KEY في secrets")

st.caption("📚 شغال بـ Groq الجديد ⚡")
