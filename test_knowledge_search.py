#!/usr/bin/env python3
"""
Test what's actually searchable in the knowledge base
"""
import requests
import json

def test_search(query, description):
    """Test a specific search query"""
    print(f"\n🔍 Testing: {description}")
    print(f"Query: '{query}'")
    print("-" * 50)
    
    try:
        response = requests.post(
            "http://10.202.70.20:8181/api/knowledge-items/search",
            json={"query": query, "match_count": 3},
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            found_results = results.get('results', [])
            
            if found_results:
                print(f"✅ Found {len(found_results)} results:")
                for i, result in enumerate(found_results):
                    filename = result.get('metadata', {}).get('filename', 'unknown')
                    source_id = result.get('metadata', {}).get('source_id', 'unknown')
                    score = result.get('similarity_score', 0)
                    content_preview = result.get('content', '')[:100] + "..."
                    
                    print(f"  {i+1}. {filename} (Score: {score:.3f})")
                    print(f"     Source: {source_id}")
                    print(f"     Content: {content_preview}")
            else:
                print("❌ No results found")
        else:
            print(f"❌ Search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🧪 KNOWLEDGE BASE SEARCH TEST")
    print("=" * 60)
    
    # Test searches for content that should be in uploaded files
    test_searches = [
        ("Archon Plus API Reference", "Should find API documentation"),
        ("POST /api/auth/login", "Should find authentication endpoints"),
        ("Business Manager Project Manager", "Should find user roles"),
        ("homelab server configuration portainer", "Should find technical infrastructure"),
        ("What is Archon Plus intelligent task management", "Should find business description"),
        ("User Guide for Business Users", "Should find user guide content"),
        ("Rate Limiting WebSocket Events", "Should find API technical details"),
        ("Project Lifecycle Initiation Planning", "Should find business workflow"),
    ]
    
    for query, description in test_searches:
        test_search(query, description)
    
    print(f"\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("This test shows which uploaded content is actually searchable")
    print("If content doesn't appear, the upload/indexing failed")

if __name__ == "__main__":
    main()
