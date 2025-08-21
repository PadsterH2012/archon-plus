#!/usr/bin/env python3
"""
Verify Archon upload and knowledge base status
"""
import requests
import json
import time

def check_archon_health():
    """Check if Archon services are healthy"""
    print("🏥 CHECKING ARCHON HEALTH")
    print("=" * 40)
    
    # Check prod health
    try:
        response = requests.get("http://10.202.70.20:8181/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Archon-prod health: OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Archon-prod health: {response.status_code}")
    except Exception as e:
        print(f"❌ Archon-prod health: {e}")
    
    # Check dev health  
    try:
        response = requests.get("http://10.202.70.20:9181/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Archon-dev health: OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Archon-dev health: {response.status_code}")
    except Exception as e:
        print(f"❌ Archon-dev health: {e}")

def check_knowledge_sources():
    """Check what sources are in the knowledge base"""
    print("\n📚 CHECKING KNOWLEDGE BASE SOURCES")
    print("=" * 40)
    
    # Check prod sources
    try:
        response = requests.get("http://10.202.70.20:8181/api/knowledge-items", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Archon-prod sources: {len(data.get('sources', []))} found")
            for source in data.get('sources', [])[:5]:  # Show first 5
                print(f"   - {source.get('source_id', 'unknown')}: {source.get('title', 'no title')}")
        else:
            print(f"❌ Archon-prod sources: {response.status_code}")
    except Exception as e:
        print(f"❌ Archon-prod sources: {e}")

def test_upload():
    """Test a simple upload"""
    print("\n🔄 TESTING SIMPLE UPLOAD")
    print("=" * 40)
    
    # Create a simple test file
    test_content = """
# Test Upload Document

This is a test document to verify uploads are working.

## Test Information
- Upload time: """ + str(time.time()) + """
- Server: 10.202.70.20:8181
- Purpose: Verify knowledge base upload functionality

## Homelab Details
- Portainer: 10.202.70.20:9000
- Credentials: paddy / P0w3rPla72012@@
- Archon-prod: Production instance
- Archon-dev: Development instance
"""
    
    try:
        # Write test content to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_path = f.name
        
        # Upload to prod
        with open(temp_path, 'rb') as f:
            files = {'file': f}
            data = {
                'knowledge_type': 'technical',
                'tags': '["test", "homelab", "verification"]'
            }
            
            response = requests.post(
                "http://10.202.70.20:8181/api/documents/upload", 
                files=files, 
                data=data, 
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Test upload successful!")
                print(f"   Progress ID: {result.get('progressId')}")
                print(f"   Filename: {result.get('filename')}")
                return result.get('progressId')
            else:
                print(f"❌ Test upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Test upload error: {e}")
        return None
    finally:
        # Cleanup
        import os
        if 'temp_path' in locals():
            os.unlink(temp_path)

def search_test():
    """Test knowledge base search"""
    print("\n🔍 TESTING KNOWLEDGE BASE SEARCH")
    print("=" * 40)
    
    try:
        # Test search
        search_data = {
            "query": "homelab portainer archon test",
            "match_count": 3
        }
        
        response = requests.post(
            "http://10.202.70.20:8181/api/knowledge-items/search",
            json=search_data,
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Search successful: {len(results.get('results', []))} results")
            for i, result in enumerate(results.get('results', [])[:3]):
                print(f"   {i+1}. {result.get('metadata', {}).get('filename', 'unknown')}")
                print(f"      Score: {result.get('similarity_score', 0):.3f}")
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Search error: {e}")

def main():
    print("🔧 ARCHON UPLOAD VERIFICATION TOOL")
    print("=" * 50)
    
    # Run all checks
    check_archon_health()
    check_knowledge_sources()
    
    # Test upload
    progress_id = test_upload()
    
    if progress_id:
        print(f"\n⏳ Waiting 30 seconds for processing...")
        time.sleep(30)
        
        # Check sources again
        check_knowledge_sources()
        
        # Test search
        search_test()
    
    print("\n✅ Verification complete!")

if __name__ == "__main__":
    main()
