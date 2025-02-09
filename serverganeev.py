import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Configure Gemini API
genai.configure(api_key="AIzaSyCdM5KhU5s0s_LpxUntadXVo8L6SOLK1tA")


def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([\w-]{11})", url)
    return match.group(1) if match else None


def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except:
        return None


def summarize_text(text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + text)
    return response.text if response else "Error in generating summary."


def simplify_and_translate(summary):
    simple_summary = summarize_text(summary, "Simplify this summary so that even a senior citizen can understand: ")
    hindi_summary = summarize_text(simple_summary, "Translate this English summary into Hindi: ")
    return simple_summary, hindi_summary


# Streamlit UI
st.title("Senior Devta")
st.write(
    "Enter up to 5 YouTube video URLs to get a simplified combined and topic-wise summary in both English and Hindi:")

video_urls = []
for i in range(5):
    url = st.text_input(f"Video {i + 1} URL", "")
    if url:
        video_urls.append(url)

if st.button("Summarize Videos"):
    if not video_urls:
        st.warning("Please enter at least one YouTube URL.")
    else:
        all_transcripts = ""
        individual_summaries = {}
        for url in video_urls:
            video_id = extract_video_id(url)
            if video_id:
                transcript = get_video_transcript(video_id)
                if transcript:
                    all_transcripts += transcript + " "
                    summary = summarize_text(transcript, "Summarize this YouTube transcript: ")
                    simple_summary, hindi_summary = simplify_and_translate(summary)
                    individual_summaries[url] = (simple_summary, hindi_summary)
                else:
                    st.error(f"Could not retrieve transcript for {url}")
            else:
                st.error(f"Invalid YouTube URL: {url}")

        if all_transcripts:
            combined_summary = summarize_text(all_transcripts,
                                              "Provide a detailed combined summary of the following transcripts: ")
            topic_wise_summary = summarize_text(all_transcripts,
                                                "Extract and summarize common topics from these transcripts: ")

            simple_combined_summary, hindi_combined_summary = simplify_and_translate(combined_summary)
            simple_topic_summary, hindi_topic_summary = simplify_and_translate(topic_wise_summary)

            st.subheader("Combined Summary of All Videos (Simple English)")
            st.write(simple_combined_summary)

            st.subheader("Combined Summary in Hindi")
            st.write(hindi_combined_summary)

            st.subheader("Topic-wise Summary (Simple English)")
            st.write(simple_topic_summary)

            st.subheader("Topic-wise Summary in Hindi")
            st.write(hindi_topic_summary)

            for url, (simple_summary, hindi_summary) in individual_summaries.items():
                st.subheader(f"Summary for {url} (Simple English)")
                st.write(simple_summary)

                st.subheader(f"Summary for {url} (Hindi)")
                st.write(hindi_summary)