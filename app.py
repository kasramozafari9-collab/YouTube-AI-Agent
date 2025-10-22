import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

st.set_page_config(page_title="YouTube AI Agent", page_icon="🎥", layout="wide")

GOOGLE_API_KEY = "AIzaSyAgalqUobZ0vCDhZtIQDsFMadbhrADFJ8E"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def extract_video_id(url):
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    elif 'youtube.com' in url:
        parsed = urlparse(url)
        if parsed.path == '/watch':
            return parse_qs(parsed.query).get('v', [None])[0]
    return None

def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript = transcript_list.find_transcript(['fa'])
            return ' '.join([t['text'] for t in transcript.fetch()])
        except:
            try:
                transcript = transcript_list.find_transcript(['en'])
                return ' '.join([t['text'] for t in transcript.fetch()])
            except:
                transcript = transcript_list.find_generated_transcript(['en', 'fa'])
                return ' '.join([t['text'] for t in transcript.fetch()])
    except:
        return None

def analyze_with_ai(transcript, question):
    prompt = f"متن زیر transcript یک ویدیو یوتیوب است:\n\n{transcript[:10000]}\n\nبر اساس این متن، به سوال زیر پاسخ بده:\n{question}\n\nلطفاً پاسخ کامل و دقیق بده."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"خطا در تحلیل: {str(e)}"

st.title("🎥 YouTube AI Agent")
st.markdown("### دستیار هوشمند تحلیل ویدیوهای یوتیوب")
st.markdown("---")

col1, col2 = st.columns([2, 1])
with col1:
    video_url = st.text_input("🔗 لینک ویدیو یوتیوب:", placeholder="https://www.youtube.com/watch?v=...")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("🔍 تحلیل ویدیو", use_container_width=True)

if analyze_btn and video_url:
    video_id = extract_video_id(video_url)
    if not video_id:
        st.error("❌ لینک نامعتبر است!")
    else:
        with st.spinner("⏳ در حال دریافت متن ویدیو..."):
            transcript = get_transcript(video_id)
        if not transcript:
            st.error("❌ نمی‌توان متن ویدیو را دریافت کرد.")
        else:
            st.success("✅ متن ویدیو دریافت شد!")
            st.video(video_url)
            with st.expander("📝 مشاهده متن ویدیو"):
                st.text_area("متن کامل:", transcript, height=200, disabled=True)
            st.markdown("---")
            st.markdown("### 💬 سوال خود را بپرسید:")
            question = st.text_area("سوال:", placeholder="مثلاً: این ویدیو درباره چیست؟", height=100)
            if st.button("🤖 پاسخ بده", use_container_width=True):
                if question:
                    with st.spinner("🧠 در حال تحلیل..."):
                        answer = analyze_with_ai(transcript, question)
                    st.markdown("### 💡 پاسخ:")
                    st.markdown(answer)
                else:
                    st.warning("⚠️ لطفاً سوالی بپرسید!")

with st.sidebar:
    st.markdown("## 📚 راهنما")
    st.markdown("**چگونه استفاده کنیم:**\n\n1️⃣ لینک ویدیو را وارد کنید\n\n2️⃣ روی تحلیل کلیک کنید\n\n3️⃣ سوال بپرسید\n\n4️⃣ پاسخ دریافت کنید!")
    st.markdown("---")
    st.markdown("**ساخته شده با ❤️ توسط کاسرا**")
