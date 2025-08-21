# 🚀 Archon Plus Quick Reference Card

**For New Chat Sessions**: *"Check HOMELAB_ARCHON_CONTEXT.md for complete setup details"*

---

## 🏠 **Essential Info**
- **Server**: `10.202.70.20`
- **Portainer**: `http://10.202.70.20:9000` (`paddy / P0w3rPla72012@@`)
- **ARCHON-PROD**: `http://10.202.70.20:8181` (Knowledge base for building DEV)
- **ARCHON-DEV**: `http://10.202.70.20:9181` (Testing & template injection)

## 🔧 **Key Rules**
1. **ARCHON-PROD** = Knowledge base for building ARCHON-DEV
2. **ARCHON-DEV** = Testing new features
3. **Restart services** in Portainer (don't redeploy)
4. **Template injection** → Deploy to DEV first

## 🐛 **Known Issues**
- **Knowledge Base Upload Bug**: Confirmed upstream bug (GitHub #388, #313, #302)
  - Upload API succeeds but indexing fails
  - Use UI upload method (more reliable than scripts)
  - Monitor original Archon repo for fixes

## 🎯 **Quick Commands**
```bash
# Health checks
curl http://10.202.70.20:8181/api/health  # Prod
curl http://10.202.70.20:9181/api/health  # Dev

# Helper scripts
python3 homelab_helper.py              # Quick access to credentials
python3 test_knowledge_search.py       # Test what's searchable
```

## 📋 **For Agents**
*"I'm working on Archon Plus (fork of original Archon). See HOMELAB_ARCHON_CONTEXT.md for complete infrastructure details, known issues, and development workflow. Key point: knowledge base upload has confirmed upstream bug affecting indexing pipeline."*

---
**Full Details**: See `HOMELAB_ARCHON_CONTEXT.md`
