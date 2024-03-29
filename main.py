import streamlit as st
import sqlite3
import os
from dotenv import load_dotenv
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import base64


load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_transcript(youtube_video_url):
    try:
        video_id = None
        if "watch?v=" in youtube_video_url:
            video_id = youtube_video_url.split("watch?v=")[-1]
        elif "youtu.be/" in youtube_video_url:
            video_id = youtube_video_url.split("youtu.be/")[-1]
        if video_id:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = ""
            for i in transcript:
                transcript_text += " " + i["text"]
            return transcript_text
        else:
            st.error("Invalid YouTube video link.")
            return None
    except Exception as e:
        st.error(f"Error extracting transcript: {e}")
        return None

def fetch_transcript(video_id):
    conn = sqlite3.connect('youtube_transcripts.db')
    c = conn.cursor()
    c.execute("SELECT transcript FROM transcripts WHERE video_id = ?", (video_id,))
    transcript_text = c.fetchone()[0]
    conn.close()
    return transcript_text

def get_state():
    return Server.get_current()._session_state

def generate_notes(transcript_text, subject):
    if subject == "Physics":
        prompt = """
            Title: Detailed Physics Notes from YouTube Video Transcript

            As a physics expert, your task is to provide detailed notes based on the transcript of a YouTube video I'll provide. Assume the role of a student and generate comprehensive notes covering the key concepts discussed in the video.

            Your notes should:

            - Highlight fundamental principles, laws, and theories discussed in the video.
            - Explain any relevant experiments, demonstrations, or real-world applications.
            - Clarify any mathematical equations or formulas introduced and provide explanations for their significance.
            - Use diagrams, illustrations, or examples to enhance understanding where necessary.

            Please provide the YouTube video transcript, and I'll generate the detailed physics notes accordingly.
        """
    elif subject == "Chemistry":
        prompt = """
            Title: Detailed Chemistry Notes from YouTube Video Transcript

            As a chemistry expert, your task is to provide detailed notes based on the transcript of a YouTube video I'll provide. Assume the role of a student and generate comprehensive notes covering the key concepts discussed in the video.

            Your notes should:

            - Break down chemical reactions, concepts, and properties explained in the video.
            - Include molecular structures, reaction mechanisms, and any applicable theories.
            - Discuss the significance of the discussed chemistry concepts in various contexts, such as industry, environment, or daily life.
            - Provide examples or case studies to illustrate the practical applications of the concepts discussed.

            Please provide the YouTube video transcript, and I'll generate the detailed chemistry notes accordingly.
        """     

    elif subject == "Mathematics":
        prompt = """
            Title: Detailed Mathematics Notes from YouTube Video Transcript

            As a mathematics expert, your task is to provide detailed notes based on the transcript of a YouTube video I'll provide. Assume the role of a student and generate comprehensive notes covering the key mathematical concepts discussed in the video.

            Your notes should:

            - Outline mathematical concepts, formulas, and problem-solving techniques covered in the video.
            - Provide step-by-step explanations for solving mathematical problems discussed.
            - Clarify any theoretical foundations or mathematical principles underlying the discussed topics.
            - Include relevant examples or practice problems to reinforce understanding.

            Please provide the YouTube video transcript, and I'll generate the detailed mathematics notes accordingly.
        """
    elif subject == "Data Science and Statistics":
        prompt = """
            Title: Comprehensive Notes on Data Science and Statistics from YouTube Video Transcript

            Subject: Data Science and Statistics

            Prompt:

            As an expert in Data Science and Statistics, your task is to provide comprehensive notes based on the transcript of a YouTube video I'll provide. Assume the role of a student and generate detailed notes covering the key concepts discussed in the video.

            Your notes should:

            Data Science:

            Explain fundamental concepts in data science such as data collection, data cleaning, data analysis, and data visualization.
            Discuss different techniques and algorithms used in data analysis and machine learning, including supervised and unsupervised learning methods.
            Provide insights into real-world applications of data science in various fields like business, healthcare, finance, etc.
            Include discussions on data ethics, privacy concerns, and best practices in handling sensitive data.
            Statistics:

            Outline basic statistical concepts such as measures of central tendency, variability, and probability distributions.
            Explain hypothesis testing, confidence intervals, and regression analysis techniques.
            Clarify the importance of statistical inference and its role in drawing conclusions from data.
            Provide examples or case studies demonstrating the application of statistical methods in solving real-world problems.

            Your notes should aim to offer a clear understanding of both the theoretical foundations and practical applications of data science and statistics discussed in the video. Use clear explanations, examples, and visuals where necessary to enhance comprehension.

            Please provide the YouTube video transcript, and I'll generate the detailed notes on Data Science and Statistics accordingly.
        """

    elif subject == "Web Development":
        prompt = """
            Title: Detailed Web Development Notes from YouTube Video Transcript

            As a web development expert, your task is to provide detailed notes based on the transcript of a YouTube video I'll provide. Assume the role of a student and generate comprehensive notes covering the key concepts discussed in the video.

            Your notes should:

            - Cover essential concepts and technologies in web development such as HTML, CSS, JavaScript, etc.
            - Discuss web development frameworks, libraries, and best practices.
            - Explain front-end and back-end development principles and their roles in web development.
            - Explore topics related to web design, user experience (UX), and accessibility.
            - Provide insights into emerging trends and advancements in web development.

            Your notes should aim to offer a clear understanding of both the theoretical foundations and practical applications of web development concepts discussed in the video. Use clear explanations, examples, and code snippets where necessary to enhance comprehension.

            Please provide the YouTube video transcript, and I'll generate the detailed web development notes accordingly.
        """

    elif subject == "Cloud Computing":
        prompt = """
            Title: Detailed Cloud Computing Notes from YouTube Video Transcript

            As a cloud computing expert, your task is to provide detailed notes based on the transcript of a YouTube video I'll provide. Assume the role of a student and generate comprehensive notes covering the key concepts discussed in the video.

            Your notes should:

            - Cover fundamental concepts of cloud computing including infrastructure as a service (IaaS), platform as a service (PaaS), and software as a service (SaaS).
            - Discuss cloud computing architectures, deployment models, and service models.
            - Explain key technologies and tools used in cloud computing such as virtualization, containers, orchestration, etc.
            - Explore topics related to cloud security, compliance, and governance.
            - Provide insights into the practical applications and benefits of cloud computing for businesses and organizations.

            Your notes should aim to offer a clear understanding of both the theoretical foundations and practical applications of cloud computing concepts discussed in the video. Use clear explanations, examples, and diagrams where necessary to enhance comprehension.

            Please provide the YouTube video transcript, and I'll generate the detailed cloud computing notes accordingly.
        """
    elif subject == "Biology":
        prompt = """
            Title: Comprehensive Notes on Biology from YouTube Video Transcript

            Subject: Biology

            Prompt:

            As a biology expert, your task is to provide comprehensive notes based on the transcript of a YouTube video I'll provide. Assume the role of a student and generate detailed notes covering the key concepts discussed in the video.

            Your notes should:

            - Cover fundamental principles of biology including cell biology, genetics, evolution, ecology, etc.
            - Discuss important biological processes, mechanisms, and systems.
            - Explain relevant experiments, discoveries, and case studies in biology.
            - Explore the interrelationships between different organisms and their environments.
            - Provide insights into the applications of biology in areas such as medicine, agriculture, biotechnology, etc.

            Your notes should aim to offer a clear understanding of both the theoretical foundations and practical applications of biology concepts discussed in the video. Use clear explanations, examples, and diagrams where necessary to enhance comprehension.

            Please provide the YouTube video transcript, and I'll generate the detailed notes on Biology accordingly.
        """

    elif subject == "Social Science":
        prompt = """
            Title: Comprehensive Notes on Social Science from YouTube Video Transcript

            Subject: Social Science

            Prompt:

            As an expert in Social Science, your task is to provide comprehensive notes based on the transcript of a YouTube video I'll provide. Assume the role of a student and generate detailed notes covering the key concepts discussed in the video.

            Your notes should:

            - Analyze fundamental theories, concepts, and methodologies in social science disciplines such as sociology, psychology, anthropology, etc.
            - Discuss key findings, experiments, and case studies in relevant areas of social science.
            - Examine the impact of social structures, institutions, and cultural factors on human behavior and society.
            - Explore contemporary issues and debates within the field of social science, including topics like globalization, inequality, gender studies, etc.
            - Provide insights into research methods and ethical considerations in social science research.

            Your notes should aim to offer a clear understanding of both the theoretical frameworks and practical applications of social science concepts discussed in the video. Use clear explanations, examples, and illustrations where necessary to enhance comprehension.

            Please provide the YouTube video transcript, and I'll generate the detailed notes on Social Science accordingly.
        """


    elif subject == "Economics":
        prompt = """
            Title: Detailed Economics Notes from YouTube Video Transcript

            As an economics expert, your task is to provide detailed notes based on the transcript of a YouTube video I'll provide. Assume the role of a student and generate comprehensive notes covering the key concepts discussed in the video.

            Your notes should:

            - Cover fundamental principles of economics including microeconomics and macroeconomics.
            - Discuss key economic theories, models, and concepts such as supply and demand, market structures, economic indicators, etc.
            - Explain relevant economic policies, fiscal and monetary measures, and their impacts on economies.
            - Explore topics related to international trade, globalization, development economics, etc.
            - Provide insights into real-world applications and case studies illustrating economic principles and phenomena.

            Your notes should aim to offer a clear understanding of both the theoretical foundations and practical applications of economics concepts discussed in the video. Use clear explanations, examples, and illustrations where necessary to enhance comprehension.

            Please provide the YouTube video transcript, and I'll generate the detailed economics notes accordingly.
        """
        
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt + transcript_text)
    return response.text

def generate_pdf(text_content, file_path):
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    y_position = height - 50  # Initial Y position
    text_lines = text_content.split('\n')
    for line in text_lines:
        # Split long lines into smaller chunks to fit within the page width without cutting off words
        chunks = []
        words = line.split()
        current_chunk = ""
        for word in words:
            if len(current_chunk) + len(word) < 90:
                current_chunk += " " + word
            else:
                chunks.append(current_chunk.strip())
                current_chunk = word
        chunks.append(current_chunk.strip())
        for chunk in chunks:
            # Check if adding this line exceeds the page height
            if y_position < 50:
                c.showPage()  # Start a new page
                y_position = height - 50  # Reset Y position for new page
            # Remove formatting tags and write the line of text
            clean_chunk = chunk.replace("**", "").replace("*", "").replace("-", "").strip()
            c.drawString(50, y_position, clean_chunk)
            y_position -= 15  # Adjust Y position for the next line
    c.save()

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href

def main():
    st.title("YouTube Transcript to Detailed Notes Converter")
    
    subject = st.selectbox("Select Subject:", ["Physics", "Chemistry", "Mathematics", "Data Science and Statistics",
                                               "Web Development", "Cloud Computing", "Biology", "Social Science", "Economics"])
    youtube_link = st.text_input("Enter YouTube Video Link:")

    if youtube_link:
        st.subheader("Audio/Video Playback:")
        st.video(youtube_link)

    if st.button("Get Detailed Notes") and youtube_link:
        transcript_text = extract_transcript(youtube_link)
        
        if transcript_text:
            st.success("Transcript extracted successfully!")
            st.session_state.detailed_notes = generate_notes(transcript_text, subject)
            st.markdown("## Detailed Notes:")
            st.write(st.session_state.detailed_notes)

        else:
            st.error("Failed to extract transcript.")

    if st.button("Convert to Hindi"):
        if 'detailed_notes' in st.session_state:
            translator = Translator()
            translated_text = translator.translate(st.session_state.detailed_notes, dest='hi').text
            st.markdown("## Detailed Notes in Hindi:")
            st.write(translated_text)
        else:
            st.warning("Please generate detailed notes before converting to Hindi.")

    if 'detailed_notes' in st.session_state:
        file_path = "detailed_notes.pdf"
        generate_pdf(st.session_state.detailed_notes, file_path)
        st.markdown(get_binary_file_downloader_html(file_path, 'Download PDF'), unsafe_allow_html=True)
    

if __name__ == "__main__":
    main()