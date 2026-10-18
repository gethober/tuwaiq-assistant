import streamlit as st
from groq import Groq
from PIL import Image
import re
import base64
import os

st.set_page_config(page_title="مساعد طويق", layout="centered", page_icon="icon.png")

# --- الاتصال بـ Groq ---
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

def clean_chinese(text):
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

st.markdown("""
<style>
header {visibility: hidden;}
a, .anchor-link, [data-testid="stHeaderActionElements"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

# --- حفظ الذاكرة ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [] # هنا يتذكر كل المحادثة
if 'b64' not in st.session_state: 
    st.session_state['b64'] = None

# فوق
col_logo, col_text = st.columns([1, 5])
with col_logo:
    try: st.image("logo.png", width=60)
    except: st.write("🌴")
with col_text:
    st.markdown("### مساعد طويق - شرح مفصل")

# --- عرض المحادثة القديمة ---
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

mode = st.radio("كيف تبي الشرح؟", ["📖 فصل لي الكلام كامل", "✂️ اختصر لي", "⚖️ شرح متوسط"], horizontal=True)
query = st.text_input("وش تبي تسأل؟", placeholder="مثال: ايش هي برمجة صفحات الانترنت؟")

c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    with st.popover("📎 رفع", use_container_width=True):
        up = st.file_uploader(" ", type=["jpg","png","jpeg"], label_visibility="collapsed")
        if up:
            st.session_state['b64'] = base64.b64encode(up.getvalue()).decode('utf-8')
with c2:
    with st.popover("📸 كاميرا", use_container_width=True):
        cam = st.camera_input(" ", label_visibility="collapsed")
        if cam:
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
        # احفظ سؤال المستخدم في الذاكرة
        user_content = query if query else "حل الواجب اللي في الصورة"
        st.session_state.chat_history.append({"role": "user", "content": user_content})
        with st.chat_message("user"):
            st.markdown(user_content)

        if "اختصر" in mode:
            system_prompt = "انت دكتور سعودي. اختصر الجواب في 5 نقاط مختصرة مفيدة بالعربي. ممنوع حروف صينية. وتذكر كلامنا السابق."
        elif "فصل" in mode:
            system_prompt = "انت دكتور جامعي سعودي خبير. فصل واشرح شرح مفصل جدا مقسم بالنقاط وامثلة. لا تختصر. وتذكر كلامنا السابق."
        else:
            system_prompt = "انت دكتور سعودي. اشرح شرح متوسط واضح بالنقاط بالعربي. وتذكر كلامنا السابق."

        # جهز الرسائل مع الذاكرة
        messages = [{"role": "system", "content": system_prompt}]
        # اضف اخر 10 رسائل فقط عشان لا يثقل
        for m in st.session_state.chat_history[-10:]:
            messages.append(m)

        with st.spinner("قاعد أكتب لك..."):
            try:
                if st.session_state['b64']:
                    model = "meta-llama/llama-4-scout-17b-16e-instruct"
                    messages[-1] = {"role": "user", "content": [
                        {"type": "text", "text": user_content},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{st.session_state['b64']}"}}
                    ]}
                else:
                    model = "openai/gpt-oss-20b"

                res = client.chat.completions.create(model=model, messages=messages)
                answer = clean_chinese(res.choices[0].message.content)
                
                with st.chat_message("assistant"):
                    st.success(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})

            except Exception as e:
                st.error(f"خطأ: {e}")

        st.session_state['b64'] = None

st.markdown("<div style='margin-top:120px;'></div>", unsafe_allow_html=True)
col_a, col_b, col_c = st.columns([2, 1, 2])
with col_b:
    try: st.image("logo.png", use_container_width=True)
    except: pass
st.markdown("<div style='text-align:center; font-size:55px; font-weight:900; letter-spacing:4px; color:white; margin-top:15px;'>MADE IN SAUDI</div>", unsafe_allow_html=True)
