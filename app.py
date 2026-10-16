import streamlit as st
from groq import Groq
import re
import base64

st.set_page_config(page_title="مساعد طويق - شرح مفصل", layout="centered")
st.title("⚡ مساعد طويق - شرح مفصل")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def clean_chinese(text):
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

if 'b64' not in st.session_state:
    st.session_state['b64'] = None

query = st.text_input("وش تبي تسأل؟", placeholder="مثال: ايش هي برمجة صفحات الانترنت؟")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    with st.popover("📎 رفع", use_container_width=True):
        uploaded = st.file_uploader(" ", type=["jpg","png","jpeg"], label_visibility="collapsed")
        if uploaded:
            st.image(uploaded) # حجم طبيعي بدون حد
            st.session_state['b64'] = base64.b64encode(uploaded.getvalue()).decode('utf-8')

with col2:
    with st.popover("📸 كاميرا", use_container_width=True):
        cam = st.camera_input(" ", label_visibility="collapsed")
        if cam:
            st.image(cam)
            st.session_state['b64'] = base64.b64encode(cam.getvalue()).decode('utf-8')

with col3:
    send = st.button("🚀 ارسال", type="primary", use_container_width=True)

if st.session_state['b64']:
    st.info("📷 تم حفظ الصورة - جاهزة للحل")
    if st.button("❌ احذف الصورة"):
        st.session_state['b64'] = None
        st.rerun()

if send:
    if not query and not st.session_state['b64']:
        st.warning("اكتب سؤال او ارفع صورة")
    else:
        with st.spinner("قاعد أكتب لك شرح مفصل..."):
            try:
                if st.session_state['b64']:
                    # الموديلات الجديدة اللي تشتغل حاليا
                    # جرب qwen اول لانه شغال 100%
                    model = "qwen/qwen3-32b"
                    # اذا تبي ترجع لـ scout جرب هذا: meta-llama/llama-4-scout-17b-16e-instruct
                    messages = [
                        {"role": "system", "content": "انت دكتور جامعي سعودي خبير. اشرح بالعربي شرح مفصل مقسم بالنقاط. ممنوع حروف صينية. اذا فيه صورة حلها واشرحها خطوة بخطوة ولا تختصر."},
                        {"role": "user", "content": [
                            {"type": "text", "text": query if query else "حل الواجب اللي في الصورة شرح مفصل خطوة بخطوة"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{st.session_state['b64']}"}}
                        ]}
                    ]
                else:
                    # موديل النص الجديد اللي شغال
                    model = "openai/gpt-oss-20b"
                    messages = [
                        {"role": "system", "content": "انت دكتور جامعي سعودي خبير. اشرح بالعربي شرح مفصل مقسم بالنقاط. ممنوع حروف صينية ولا تختصر ابدا."},
                        {"role": "user", "content": query}
                    ]

                response = client.chat.completions.create(model=model, messages=messages)
                st.success(clean_chinese(response.choices[0].message.content))

            except Exception as e:
                error = str(e)
                st.error(f"خطأ: {error}")
                # اذا فشل qwen جرب موديل ثاني تلقائيا
                if "model_not_found" in error.lower() or "404" in error:
                    st.warning("الموديل الحالي مو شغال، جاري التجربة بموديل ثاني...")
                    try:
                        fallback_model = "openai/gpt-oss-120b" if not st.session_state['b64'] else "meta-llama/llama-4-maverick-17b-128e-instruct"
                        response = client.chat.completions.create(model=fallback_model, messages=messages)
                        st.success(clean_chinese(response.choices[0].message.content))
                    except Exception as e2:
                        st.error(f"جرب تحدث الـ API KEY او استخدم موديل: llama-3.1-8b-instant | الخطأ: {e2}")

st.caption("📚 شغال بـ Groq الجديد ⚡")
