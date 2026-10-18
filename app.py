import streamlit as st
from groq import Groq
import base64, os
import fitz
import docx

st.set_page_config(page_title="بيان - مساعدك التقني", layout="centered", page_icon="📖")

# --- مفتاح API ---
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        st.error("حط GROQ_API_KEY في Secrets")
        st.stop()
client = Groq(api_key=api_key)

def extract_text(uploaded):
    try:
        name = uploaded.name.lower()
        data = uploaded.getvalue()
        if name.endswith(".pdf"):
            doc = fitz.open(stream=data, filetype="pdf")
            return "".join([p.get_text() for p in doc])[:15000]
        if name.endswith(".docx"):
            d = docx.Document(uploaded)
            return "\n".join([p.text for p in d.paragraphs])[:15000]
        return data.decode('utf-8', errors='ignore')[:15000]
    except:
        return None

# --- ذاكرة ---
if 'chat' not in st.session_state: st.session_state.chat = []
if 'b64' not in st.session_state: st.session_state.b64 = None
if 'file_text' not in st.session_state: st.session_state.file_text = None
if 'file_name' not in st.session_state: st.session_state.file_name = None

# --- ستايل بيان + زر الإرفاق أيقونة ---
st.markdown("""
<style>
header{visibility:hidden}
.stButton>button[kind="primary"]{background:#0F5D2F!important;border-color:#0F5D2F!important}

/* زر الإرفاق يصير أيقونة */
div[data-testid="stFileUploader"]{width: 50px;}
div[data-testid="stFileUploader"] section{padding:0!important;min-height:0!important;border:none!important;background:transparent!important}
div[data-testid="stFileUploader"] label{display:none!important}
div[data-testid="stFileUploader"] div[data-testid="stFileUploadDropzone"] button{display:none!important}
div[data-testid="stFileUploader"] small{display:none!important}

/* شكل الأيقونة 📎 */
div[data-testid="stFileUploader"] section::before{
    content: "📎";
    font-size: 26px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    background: #1f2937;
    border: 1px solid #374151;
    border-radius: 12px;
    cursor: pointer;
}
</style>
<div style='text-align:center;margin-bottom:25px'>
    <h1 style='font-size:105px;font-weight:950;margin:0;line-height:0.9;color:#34D399;text-shadow:0 2px 0 #064E3B,0 0 25px rgba(52,211,153,.4);-webkit-text-stroke:1.5px #064E3B'>بيان</h1>
    <p style='font-size:24px;font-weight:700;color:#9CA3AF;margin-top:8px'>مساعدك التقني</p>
</div>
""", unsafe_allow_html=True)

for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

mode = st.radio("طريقة الشرح", ["📖 تفصيلي", "✂️ مختصر", "⚖️ متوسط"], horizontal=True, label_visibility="collapsed")

# --- هنا السطر المهم: السؤال + الأيقونة بنفس السطر ---
col_q, col_file = st.columns([5, 1], gap="small")

with col_file:
    uploaded = st.file_uploader("رفع", type=None, label_visibility="collapsed")

with col_q:
    query = st.text_input("سؤال", placeholder="وش تبي بيان يطلع لك من الملف؟", label_visibility="collapsed")

# معاينة الملف
if uploaded:
    st.session_state.file_name = uploaded.name
    if uploaded.name.lower().endswith((".png",".jpg",".jpeg",".webp")):
        st.image(uploaded, width=200)
        st.session_state.b64 = base64.b64encode(uploaded.getvalue()).decode()
        st.session_state.file_text = None
        st.toast("تم ارفاق الصورة ✅")
    else:
        txt = extract_text(uploaded)
        if txt:
            st.session_state.file_text = txt
            st.session_state.b64 = None
            st.toast(f"تم قراءة {uploaded.name} ✅")
        else:
            st.error("ما قدرت أقرأ الملف")

c1, c2 = st.columns(2)
send = c1.button("🚀 ارسال", type="primary", use_container_width=True)
clear = c2.button("🗑️ مسح", use_container_width=True)

if clear:
    st.session_state.chat = []
    st.session_state.file_text = None
    st.session_state.b64 = None
    st.rerun()

if send:
    if not query and not st.session_state.file_text and not st.session_state.b64:
        st.warning("اكتب سؤال أو ارفق ملف")
        st.stop()

    user_display = query or f"📎 {st.session_state.file_name}"
    st.session_state.chat.append({"role":"user","content":user_display})
    with st.chat_message("user"):
        st.markdown(user_display)

    if st.session_state.file_text:
        full_prompt = f"الملف {st.session_state.file_name}:\n{st.session_state.file_text}\n\nسؤال: {query or 'اشرح الملف'}"
    else:
        full_prompt = query or "اشرح الصورة"

    if "مختصر" in mode: extra = "اختصر."
    elif "متوسط" in mode: extra = "شرح متوسط."
    else: extra = "اشرح بتفصيل مع أمثلة."

    system = f"انت بيان، مساعدك التقني، دكتور سعودي. {extra} جاوب عربي واضح."

    messages = [{"role":"system","content":system}]
    messages += st.session_state.chat[-6:]
    messages[-1] = {"role":"user","content":full_prompt}

    with st.spinner("بيان يفكر..."):
        try:
            if st.session_state.b64:
                messages[-1] = {"role":"user","content":[
                    {"type":"text","text":full_prompt},
                    {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{st.session_state.b64}"}}
                ]}
                model = "meta-llama/llama-4-scout-17b-16e-instruct"
            else:
                model = "openai/gpt-oss-20b"

            res = client.chat.completions.create(model=model, messages=messages, temperature=0.5)
            ans = res.choices[0].message.content
            with st.chat_message("assistant"):
                st.markdown(ans)
            st.session_state.chat.append({"role":"assistant","content":ans})
        except Exception as e:
            st.error(f"خطأ: {e}")

# ملاحظة صغيرة للمستخدم
st.caption("💡 تقدر تلصق الصورة بـ Ctrl+V في خانة الشات، أو تسحبها على أيقونة 📎")
