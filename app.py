import streamlit as st
from groq import Groq
import re

st.set_page_config(page_title="مساعد طويق - شرح مفصل", layout="centered")
st.title("⚡ مساعد طويق - شرح مفصل")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def clean_chinese(text):
    return re.sub(r'[\u4e00-\u9fff]+', '', text)

query = st.text_input("وش تبي تسأل؟", placeholder="مثال: ايش هي برمجة صفحات الانترنت؟")

if query:
    with st.spinner("قاعد أكتب لك شرح مفصل..."):
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {'role': 'system', 'content': "انت دكتور جامعي سعودي خبير تشرح للطلاب بالعربي بالتفصيل بدون اختصار"},
                {'role': 'user', 'content': query}
            ]
        )
        answer = clean_chinese(response.choices[0].message.content)
        st.success(answer)

st.caption("📚 شغال بـ Groq الجديد ⚡")
