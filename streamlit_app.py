import streamlit as st
import re
from googletrans import Translator
import logging

# Suppress Streamlit warnings
logging.getLogger('streamlit').setLevel(logging.ERROR)

# Initialize Translator
translator = Translator()

# Custom CSS for Azure-themed UI
st.markdown(
    """
    <style>
    .stApp {
        background-color: #15202b;
        color: white;
        font-family: Arial, sans-serif;
    }
    .stButton > button {
        background-color: #007fbf;
        color: white;
        border-radius: 20px;
        border: none;
    }
    .stTextInput > div > div > input {
        background-color: #2c3947;
        color: white;
        border: 1px solid #007fbf;
        border-radius: 20px;
    }
    .footer {
        text-align: center;
        font-size: 14px;
        margin-top: 20px;
        color: #999;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("SRT Subtitle Translator")
st.write("Upload your SRT file and choose the target language to translate.")

# File Upload
uploaded_file = st.file_uploader("Choose an SRT file", type="srt")

if uploaded_file is not None:
    content = uploaded_file.read().decode('utf-8')
    lines = content.split('\n')

    # Extract text without timestamps
    def clean_and_extract(lines):
        cleaned_lines = []
        temp_lines = []
        for line in lines:
            # Check for timestamp pattern
            if re.match(r'^\d{2}:\d{2}:\d{2}[,.]\d{3} --> \d{2}:\d{2}:\d{2}[,.]\d{3}$', line):
                continue
            # Check for index pattern (just numbers)
            if re.match(r'^\d+$', line):
                continue
            # If line is empty or not a timestamp/index, add to temp_lines
            if line == '':
                if temp_lines:
                    cleaned_text = '\n'.join(temp_lines)
                    cleaned_lines.append(cleaned_text)
                temp_lines = []
            else:
                temp_lines.append(line)
        if temp_lines:
            cleaned_text = '\n'.join(temp_lines)
            cleaned_lines.append(cleaned_text)
        return cleaned_lines

    texts = clean_and_extract(lines)

    # Choose Target Language
    target_language = st.text_input("Enter target language code (e.g., 'en', 'fr'):").lower()
    
    if st.button("Translate"):
        translated_texts = []
        for text in texts:
            try:
                translated = translator.translate(text, dest=target_language)
                if translated and translated.text:
                    translated_texts.append(translated.text)
                else:
                    st.error(f"Translation failed for text: {text}")
            except Exception as e:
                st.error(f"Translation error: {e}")

        # Reformat SRT with translated text
        new_lines = []
        text_iter = iter(translated_texts)
        index = 1
        for line in lines:
            if re.match(r'^\d+$', line):
                new_lines.append(line)
            elif re.match(r'^\d{2}:\d{2}:\d{2}[,.]\d{3} --> \d{2}:\d{2}:\d{2}[,.]\d{3}$', line):
                new_lines.append(line)
                try:
                    new_lines.append(next(text_iter))
                except StopIteration:
                    break
            elif line == '':
                new_lines.append(line)
            else:
                new_lines.append(line)  # Fallback in case of unexpected lines

        new_content = '\n'.join(new_lines)

        # Download Button
        st.download_button(
            label="Download Translated SRT File",
            data=new_content,
            file_name="translated_subtitles.srt",
            mime="text/plain"
        )

# Footer
st.markdown(
    """
    <div class="footer">
        Designed by <a href="https://github.com/kayhgng" style="color: #007fbf; text-decoration: none;">alikay_h</a>
    </div>
    """,
    unsafe_allow_html=True
)
