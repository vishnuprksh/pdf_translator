import re
import streamlit as st
import PyPDF2
from groq import Groq


def extract_all_text(pdf_reader: PyPDF2.PdfReader) -> str:
    """Extract text from all pages and return as a single string."""
    text = []
    for page in pdf_reader.pages:
        text.append(page.extract_text())
    return "\n\n--- Page Break ---\n\n".join(text)


def remove_think_tags(text: str) -> str:
    """
    Remove any content enclosed within <think></think> tags from the given text.

    Args:
        text: The text from which to remove the <think> tags and their content.

    Returns:
        The cleaned text with <think></think> content removed.
    """
    # Remove everything between <think> and </think> (including the tags)
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def format_extraction(text: str, api_key: str = "") -> str:
    """
    Format the extracted text using the Groq API.

    Args:
        text: The text to be formatted.
        api_key: (Optional) API key for authentication.

    Returns:
        A string of the formatted extraction.
    """
    try:
        client = Groq(api_key=api_key) if api_key else Groq()
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a language expert who formats the extraction. "
                    "Improve readability while maintaining the original structure."
                )
            },
            {"role": "user", "content": text}
        ]
        completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=messages,
            temperature=0.7,
            max_completion_tokens=4096,
            top_p=0.95,
            stream=True,
            stop=None,
        )
        formatted_response = ""
        for chunk in completion:
            formatted_response += chunk.choices[0].delta.content or ""
        # Remove reasoning parts enclosed in <think> tags
        return remove_think_tags(formatted_response)
    except Exception as e:
        return f"Error in formatting extraction: {str(e)}"


def translate_to_malayalam(text: str, api_key: str = "") -> str:
    """
    Translate text to Malayalam using the Groq API.

    Args:
        text: The text to be translated.
        api_key: (Optional) API key for authentication.

    Returns:
        A string containing the Malayalam translation.
    """
    try:
        client = Groq(api_key=api_key) if api_key else Groq()
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a professional translator. Translate the following text "
                    "to Malayalam while maintaining the original meaning and structure. "
                    "Use Malayalam script."
                )
            },
            {"role": "user", "content": text}
        ]
        completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=messages,
            temperature=0.7,
            max_completion_tokens=4096,
            top_p=0.95,
            stream=True,
            stop=None,
        )
        translation_response = ""
        for chunk in completion:
            translation_response += chunk.choices[0].delta.content or ""
        # Remove reasoning parts enclosed in <think> tags
        return remove_think_tags(translation_response)
    except Exception as e:
        return f"Error in translation: {str(e)}"


def main() -> None:
    st.title("PDF Viewer App with Extraction Formatting and Malayalam Translation")

    # API Key input widget (for Groq API, if required)
    api_key = st.text_input("Enter API Key (if required)", type="password")

    # File uploader widget
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # Display file details
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB"
        }
        st.write("File Details:")
        for key, value in file_details.items():
            st.write(f"- {key}: {value}")

        # Read PDF content
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            num_pages = len(pdf_reader.pages)

            st.write(f"Number of pages: {num_pages}")

            # Add view mode selector
            view_mode = st.radio(
                "Select View Mode",
                ["Complete Document", "Individual Pages"]
            )

            if view_mode == "Complete Document":
                # Extract text
                raw_text = extract_all_text(pdf_reader)

                # Create tabs for raw, formatted extraction, and translated content
                tab1, tab2, tab3 = st.tabs(
                    ["Raw Content", "Formatted Extraction", "Malayalam Translation"]
                )

                with tab1:
                    st.subheader("Raw Document Content")
                    st.text_area("Raw Content", raw_text, height=400)

                with tab2:
                    st.subheader("Formatted Extraction")
                    if st.button("Format Extraction"):
                        with st.spinner("Formatting extraction..."):
                            formatted_text = format_extraction(raw_text, api_key)
                            st.session_state['formatted_text'] = formatted_text
                            st.text_area("Formatted Extraction", formatted_text, height=400)
                            # Add download button
                            st.download_button(
                                label="Download Formatted Extraction",
                                data=formatted_text.encode(),
                                file_name=f"{uploaded_file.name}_formatted.txt",
                                mime="text/plain"
                            )

                with tab3:
                    st.subheader("Malayalam Translation")
                    if st.button("Translate to Malayalam"):
                        with st.spinner("Translating to Malayalam..."):
                            # Use formatted extraction if available, otherwise use raw text
                            text_to_translate = st.session_state.get('formatted_text', raw_text)
                            malayalam_text = translate_to_malayalam(text_to_translate, api_key)
                            st.text_area("Malayalam Content", malayalam_text, height=400)
                            # Add download button for Malayalam text
                            st.download_button(
                                label="Download Malayalam Translation",
                                data=malayalam_text.encode("utf-8"),
                                file_name=f"{uploaded_file.name}_malayalam.txt",
                                mime="text/plain"
                            )

            else:
                # Add a page selector
                page_number = st.number_input(
                    "Select a page",
                    min_value=1,
                    max_value=num_pages,
                    value=1
                )

                # Get page content
                page = pdf_reader.pages[page_number - 1]
                raw_text = page.extract_text()

                # Create tabs for raw, formatted extraction, and translated content
                tab1, tab2, tab3 = st.tabs(
                    ["Raw Content", "Formatted Extraction", "Malayalam Translation"]
                )

                with tab1:
                    st.subheader(f"Raw Content - Page {page_number}")
                    st.text_area("Raw Content", raw_text, height=300)

                with tab2:
                    st.subheader(f"Formatted Extraction - Page {page_number}")
                    if st.button("Format Extraction"):
                        with st.spinner("Formatting extraction..."):
                            formatted_text = format_extraction(raw_text, api_key)
                            st.session_state[f'formatted_text_page_{page_number}'] = formatted_text
                            st.text_area("Formatted Extraction", formatted_text, height=300)

                with tab3:
                    st.subheader(f"Malayalam Translation - Page {page_number}")
                    if st.button("Translate to Malayalam"):
                        with st.spinner("Translating to Malayalam..."):
                            # Use formatted extraction if available, otherwise use raw text
                            text_to_translate = st.session_state.get(
                                f'formatted_text_page_{page_number}', raw_text
                            )
                            malayalam_text = translate_to_malayalam(text_to_translate, api_key)
                            st.text_area("Malayalam Content", malayalam_text, height=300)

        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
    else:
        st.info("Please upload a PDF file.")


if __name__ == "__main__":
    main()
