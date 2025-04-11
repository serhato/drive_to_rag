import streamlit as st
import requests
import os
import time
import json
from typing import Optional

# Page configuration
st.set_page_config(page_title="Drive File Uploader", page_icon="📤", layout="centered")

# Constants - REPLACE WITH YOUR N8N WEBHOOK URL
N8N_WEBHOOK_URL = "https://n8n-dash.wiz2biz.ai/webhook-test/streamlit-drive-upload"

def upload_file_to_drive(file, folder_id: Optional[str] = None) -> dict:
    """
    Upload a file to Google Drive via n8n webhook
    
    Args:
        file: The file object from Streamlit's file_uploader
        folder_id: Optional Google Drive folder ID to upload to
    
    Returns:
        dict: Response from n8n webhook
    """
    try:
        # Create form data with file and metadata
        files = {'file': (file.name, file.getvalue(), file.type)}
        
        # Add optional folder ID if provided
        data = {}
        if folder_id:
            data['folder_id'] = folder_id
            
        # Send request to n8n webhook
        response = requests.post(
            N8N_WEBHOOK_URL, 
            files=files,
            data=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return {"success": False, "error": response.text}
    except Exception as e:
        st.error(f"Upload failed: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    # App title and description
    st.title("📤 Google Drive File Uploader")
    st.markdown("Upload files directly to your Google Drive using n8n backend")
    
    # Optional folder ID input
    with st.expander("Advanced Options"):
        folder_id = st.text_input(
            "Google Drive Folder ID (optional)", 
            help="If left empty, files will be uploaded to the default location configured in n8n"
        )
    
    # File uploader widget
    uploaded_file = st.file_uploader("Choose a file", type=None, accept_multiple_files=False)
    
    if uploaded_file is not None:
        # Display file info
        file_details = {
            "FileName": uploaded_file.name,
            "FileType": uploaded_file.type,
            "FileSize": f"{uploaded_file.size / 1024:.2f} KB"
        }
        st.write("File Details:")
        st.json(file_details)
        
        # Upload button
        if st.button("Upload to Drive"):
            with st.spinner('Uploading file to Google Drive...'):
                # Start upload process
                result = upload_file_to_drive(uploaded_file, folder_id if folder_id else None)
                
                # Display result
                if result.get("success", False):
                    st.success("File uploaded successfully! 🎉")
                    
                    # Show file info if available
                    if "file_info" in result:
                        st.write("Drive File Details:")
                        st.json(result["file_info"])
                        
                    # Add link to file if available
                    if "webViewLink" in result.get("file_info", {}):
                        st.markdown(f"[View file in Google Drive]({result['file_info']['webViewLink']})")
                else:
                    st.error(f"Upload failed: {result.get('error', 'Unknown error')}")
    
    # Display setup instructions
    with st.expander("How to set up n8n"):
        st.markdown("""
        ### n8n Setup Instructions
        
        1. In your n8n instance, create a new workflow
        2. Add a **Webhook node** as the trigger
            - Set Method to POST
            - Enable "Response Mode"
        3. Add a **Google Drive node** connected to the Webhook
            - Set Operation to "Upload"
            - Set Binary Property to "file"
            - Connect your Google account
            - Configure other options as needed
        4. Copy the Webhook URL and paste it in this app's code
        5. Activate the workflow in n8n
        
        For more details, see the [n8n Google Drive documentation](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.googledrive/).
        """)

if __name__ == "__main__":
    main()