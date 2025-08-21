#!/usr/bin/env python3
"""
Manual upload helper for HOMELAB_ARCHON_CONTEXT.md
Since the upload API has known issues, this script prepares the content for manual UI upload
"""

def main():
    print("📋 HOMELAB ARCHON CONTEXT - MANUAL UPLOAD HELPER")
    print("=" * 60)
    print()
    print("🐛 Due to the known upload API bug (GitHub issues #388, #313, #302),")
    print("   please upload this content manually via the Archon UI:")
    print()
    print("🌐 Upload URL: http://10.202.70.20:8181 (ARCHON-PROD)")
    print("📁 File: HOMELAB_ARCHON_CONTEXT.md")
    print("🏷️  Tags: homelab, archon, context, infrastructure, troubleshooting, reference")
    print("📝 Type: technical")
    print()
    print("=" * 60)
    print("📄 CONTENT TO UPLOAD:")
    print("=" * 60)
    
    try:
        with open('HOMELAB_ARCHON_CONTEXT.md', 'r') as f:
            content = f.read()
        
        print(content)
        
        print("=" * 60)
        print("✅ NEXT STEPS:")
        print("1. Copy the content above")
        print("2. Navigate to: http://10.202.70.20:8181")
        print("3. Go to Knowledge Base section")
        print("4. Upload via UI with the specified tags")
        print("5. Verify it appears in the sources list")
        print()
        print("💡 This document will serve as your reference for all future")
        print("   chat sessions, eliminating the need to repeat setup details!")
        
    except FileNotFoundError:
        print("❌ Error: HOMELAB_ARCHON_CONTEXT.md not found in current directory")
        print("   Make sure you're in the correct directory.")

if __name__ == "__main__":
    main()
