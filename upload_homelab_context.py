#!/usr/bin/env python3
"""
Quick script to upload homelab context to Archon knowledge base
"""
import requests
import tempfile
import os

def upload_to_archon():
    """Upload homelab context to Archon knowledge base"""
    # Read the homelab context file
    with open('homelab_context.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    # Write content to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        # ARCHON-PROD ONLY - This is where documents need to go for helping build archon-dev
        urls = [
            "http://10.202.70.20:8181/api/documents/upload",  # ARCHON-PROD - THE MAIN KNOWLEDGE BASE
        ]

        # Try each URL until one works
        for i, url in enumerate(urls):
            try:
                print(f"🔄 Trying upload to: {url}")

                # Prepare the file upload
                with open(temp_file_path, 'rb') as f:
                    files = {'file': f}
                    data = {
                        'knowledge_type': 'technical',
                        'tags': '["homelab", "archon", "portainer", "credentials", "troubleshooting"]'
                    }

                    response = requests.post(url, files=files, data=data, timeout=30)
                    if response.status_code == 200:
                        print(f"✅ Successfully uploaded homelab context to {url}!")
                        print(f"Response: {response.json()}")
                        return  # Success, exit function
                    else:
                        print(f"❌ Upload failed to {url}: {response.status_code}")
                        print(f"Response: {response.text}")

            except Exception as e:
                print(f"❌ Error uploading to {url}: {e}")

        print("❌ All upload attempts failed")

    except Exception as e:
        print(f"❌ Error uploading: {e}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    upload_to_archon()
