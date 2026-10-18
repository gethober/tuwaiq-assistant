import streamlit as st
from groq import Groq
import base64, os
import fitz
import docx

st.set_page_config(page_title="بيان", layout="centered", page_icon="📖")

api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)
if not api_key:
    st.error("حط GROQ_API_KEY في secrets.toml"); st.stop()
client = Groq(api_key=api_key)

def extract_text(file):
    try:
        name = file.name.lower()
        data = file.getvalue()
        if name.endswith(".pdf"):
            doc = fitz.open(stream=data, filetype="pdf")
            return "".join([p.get_text() for p in doc])[:15000]
        if name.endswith(".docx"):
            d = docx.Document(file)
            return "\n".join([p.text for p in d.paragraphs])[:15000]
        return data.decode('utf-8', errors='ignore')[:15000]
    except Exception as e:
        return f"خطأ قراءة الملف: {e}"

if 'chat' not in st.session_state: st.session_state.chat = []
if 'b64' not in st.session_state: st.session_state.b64 = None
if 'file_text' not in st.session_state: st.session_state.file_text = None
if 'file_name' not in st.session_state: st.session_state.file_name = None

st.markdown("""
<style>
header{visibility:hidden}
#MainMenu{visibility:hidden}
.stButton>button[kind="primary"]{background:#0F5D2F!important}
</style>
<div style='text-align:center;margin-bottom:20px'>
    <h1 style='font-size:90px;font-weight:950;margin:0;color:#34D399;text-shadow:0 0 20px rgba(52,211,153,.5);-webkit-text-stroke:1.5px #064E3B'>بيان</h1>
    <p style='color:#9CA3AF;font-weight:700'>مساعدك التقني</p>
</div>
""", unsafe_allow_html=True)

for m in st.session_state.chat:
    with st.chat_message(m["role"]): st.markdown(m["content"])

mode = st.radio(" ", ["📖 تفصيلي", "✂️ مختصر", "⚖️ متوسط"], horizontal=True, label_visibility="collapsed")

prompt = st.chat_input(
    "وش تبي بيان يطلع لك من الملف؟ 📎 تقدر تلصق الصورة هنا Ctrl+V",
    accept_file=True,
    file_type=["png","jpg","jpeg","webp","pdf","docx","txt","py","js"]
)

if prompt:
    query = prompt.text.strip() if prompt.text else ""
    uploaded = prompt.files[0] if prompt.files else None

    if uploaded:
        st.session_state.file_name = uploaded.name
        if uploaded.name.lower().endswith((".png",".jpg",".jpeg",".webp")):
            st.session_state.b64 = base64.b64encode(uploaded.getvalue()).decode()
            st.session_state.file_text = None
        else:
            st.session_state.file_text = extract_text(uploaded)
            st.session_state.b64 = None

    user_display = query if query else f"📎 {uploaded.name if uploaded else st.session_state.file_name or ''}"
    if user_display:
        st.session_state.chat.append({"role":"user","content":user_display})
        with st.chat_message("user"):
            st.markdown(user_display)
            if uploaded and uploaded.name.lower().endswith((".png",".jpg",".jpeg",".webp")):
                st.image(uploaded, width=250)

    if st.session_state.file_text:
        full_text = f"اسم الملف: {st.session_state.file_name}\nمحتوى الملف:\n{st.session_state.file_text}\n\nسؤال المستخدم: {query or 'اشرح ولخص'}"
    else:
        full_text = query or "اشرح الصورة بالتفصيل وبالعربي واقرأ كل النص اللي فيها"

    if "مختصر" in mode: extra = "جاوب باختصار شديد ومباشر."
    elif "متوسط" in mode: extra = "جاوب بتوازن بين الاختصار والتفصيل."
    else: extra = "جاوب بتفصيل مع أمثلة واضحة."

    system_msg = {"role":"system","content":f"أنت بيان، مساعد تقني ذكي، ترد بالعربي. {extra}"}
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat[-6:-1]]

    try:
        with st.chat_message("assistant"):
            with st.spinner("بيان يفكر..."):
                if st.session_state.b64:
                    # الموديلات الوحيدة اللي تدعم الصور في Groq حالياً
                    vision_models = [
                        "meta-llama/llama-4-maverick-17b-128e-instruct",
                        "meta-llama/llama-4-scout-17b-16e-instruct"
                    ]
                    
                    messages_with_image = [system_msg] + history + [{"role":"user","content":[
                        {"type":"text","text":full_text},
                        {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{st.session_state.b64}"}}
                    ]}]

                    ans = None
                    last_error = ""
                    for model_name in vision_models:
                        try:
                            res = client.chat.completions.create(
                                model=model_name,
                                messages=messages_with_image,
                                temperature=0.3,
                                max_tokens=2048
                            )
                            ans = res.choices[0].message.content
                            break
                        except Exception as e:
                            last_error = str(e)
                            continue
                    
                    if not ans:
                        st.error(f"كل موديلات الصور فشلت. آخر خطأ: {last_error}")
                        st.stop()
                else:
                    model_name = "llama-3.3-70b-versatile"
                    messages = [system_msg] + history + [{"role":"user","content":full_text}]
                    res = client.chat.completions.create(model=model_name, messages=messages, temperature=0.5, max_tokens=2048)
                    ans = res.choices[0].message.content

                st.markdown(ans)
                st.session_state.chat.append({"role":"assistant","content":ans})

    except Exception as e:
        st.error(f"خطأ: {e}")

if st.button("🗑️ مسح المحادثة"):
    st.session_state.chat=[]; st.session_state.file_text=None; st.session_state.b64=None; st.session_state.file_name=None
    st.rerun()
