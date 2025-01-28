import streamlit as st
import PyPDF2
import io
from openai import OpenAI
import os

def extract_all_text(pdf_reader):
    """Extract text from all pages and return as a single string."""
    text = []
    for page in pdf_reader.pages:
        text.append(page.extract_text())
    return "\n\n--- Page Break ---\n\n".join(text)

def format_with_gpt(text, api_key):
    """Format text using GPT API."""
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",  # You can adjust the model as needed
            messages=[
                {
                    "role": "system",
                    "content": "You are a language expert who converts the extracted pdf content into a readable format without over modifications. Maintain the original structure but improve readability."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error in GPT formatting: {str(e)}"

def main():
    st.title("PDF Viewer App with GPT Formatting")
    
    # API Key input (you might want to use st.secrets in production)
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    
    # Add a file uploader widget
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None and api_key:
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
                
                # Create tabs for raw and formatted content
                tab1, tab2 = st.tabs(["Raw Content", "GPT Formatted Content"])
                
                with tab1:
                    st.subheader("Raw Document Content")
                    st.text_area("Raw Content", raw_text, height=400)
                
                with tab2:
                    st.subheader("GPT Formatted Content")
                    if st.button("Format with GPT"):
                        with st.spinner("Formatting content with GPT..."):
                            formatted_text = format_with_gpt(raw_text, api_key)
                            st.text_area("Formatted Content", formatted_text, height=400)
                            
                            # Add download buttons
                            st.download_button(
                                label="Download Formatted Text",
                                data=formatted_text.encode(),
                                file_name=f"{uploaded_file.name}_formatted.txt",
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
                
                # Create tabs for raw and formatted content
                tab1, tab2 = st.tabs(["Raw Content", "GPT Formatted Content"])
                
                with tab1:
                    st.subheader(f"Raw Content - Page {page_number}")
                    st.text_area("Raw Content", raw_text, height=300)
                
                with tab2:
                    st.subheader(f"GPT Formatted Content - Page {page_number}")
                    if st.button("Format with GPT"):
                        with st.spinner("Formatting content with GPT..."):
                            formatted_text = format_with_gpt(raw_text, api_key)
                            st.text_area("Formatted Content", formatted_text, height=300)
            
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
    
    elif uploaded_file and not api_key:
        st.warning("Please enter your OpenAI API key to enable GPT formatting.")

if __name__ == "__main__":
    main()