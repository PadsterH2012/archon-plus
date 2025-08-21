#!/usr/bin/env python3
"""
Homelab Helper Script - Quick access to common commands and info
This script helps you remember the things you often forget to tell the agent
"""

import subprocess
import sys
import os

class HomelabHelper:
    def __init__(self):
        self.portainer_url = "10.202.70.20:9000"
        self.portainer_user = "paddy"
        self.portainer_pass = "P0w3rPla72012@@"
        self.archon_prod = "archon-prod (Production)"
        self.archon_dev = "archon-dev (Development)"
        
    def show_menu(self):
        print("\n🏠 HOMELAB HELPER MENU")
        print("=" * 40)
        print("1. Show Portainer Info")
        print("2. Show Archon Services")
        print("3. Check Container Logs")
        print("4. Show Common Commands")
        print("5. Show Agent Reminders")
        print("6. Quick Health Check")
        print("0. Exit")
        print("=" * 40)
        
    def show_portainer_info(self):
        print("\n🐳 PORTAINER INFORMATION")
        print(f"URL: http://{self.portainer_url}")
        print(f"Username: {self.portainer_user}")
        print(f"Password: {self.portainer_pass}")
        print(f"Services: {self.archon_prod}, {self.archon_dev}")
        print("\n💡 Remember: RESTART services, don't redeploy!")
        
    def show_archon_services(self):
        print("\n🤖 ARCHON SERVICES")
        print(f"Production: {self.archon_prod}")
        print(f"Development: {self.archon_dev}")
        print("\n📋 Key Rules:")
        print("- NEVER update archon-prod directly")
        print("- Use archon-dev for testing new features")
        print("- Deploy via Jenkins webhook after successful build")
        print("- Use both MCP servers (archon-dev and archon-prod)")
        
    def check_container_logs(self):
        print("\n📋 CONTAINER LOG ACCESS")
        print("Use sshpass with credentials:")
        print(f"sshpass -p '{self.portainer_pass}' ssh {self.portainer_user}@{self.portainer_url.split(':')[0]}")
        print("\nOr use Portainer web interface for easier log viewing")
        
    def show_common_commands(self):
        print("\n⚡ COMMON COMMANDS")
        print("Restart Archon Dev:")
        print("  - Go to Portainer > Stacks > archon-dev > Restart")
        print("\nCheck Archon Health:")
        print("  - curl http://localhost:8181/api/health")
        print("\nUpload to Knowledge Base:")
        print("  - Use the upload_homelab_context.py script")
        print("\nFactory Reset Dev DB:")
        print("  - Run migration/factory_reset.sql")
        
    def show_agent_reminders(self):
        print("\n🧠 AGENT REMINDERS")
        print("Always tell the agent:")
        print("✅ Use archon-dev for testing, never archon-prod")
        print("✅ Restart services in Portainer, don't redeploy")
        print("✅ Check existing documentation before making changes")
        print("✅ Update task status in Archon after completing work")
        print("✅ Test locally before pushing to Jenkins")
        print("✅ Use factory reset script for dev database issues")
        
    def quick_health_check(self):
        print("\n🏥 QUICK HEALTH CHECK")
        try:
            # Check if we can reach Archon
            result = subprocess.run(['curl', '-s', 'http://localhost:8181/api/health'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ Archon API is responding")
            else:
                print("❌ Archon API not responding")
        except:
            print("❌ Cannot check Archon API (curl not available or timeout)")
            
        # Check if Portainer is reachable
        try:
            result = subprocess.run(['ping', '-c', '1', self.portainer_url.split(':')[0]], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ Portainer host is reachable")
            else:
                print("❌ Portainer host not reachable")
        except:
            print("❌ Cannot ping Portainer host")
            
    def run(self):
        while True:
            self.show_menu()
            try:
                choice = input("\nEnter your choice (0-6): ").strip()
                
                if choice == '0':
                    print("👋 Goodbye!")
                    break
                elif choice == '1':
                    self.show_portainer_info()
                elif choice == '2':
                    self.show_archon_services()
                elif choice == '3':
                    self.check_container_logs()
                elif choice == '4':
                    self.show_common_commands()
                elif choice == '5':
                    self.show_agent_reminders()
                elif choice == '6':
                    self.quick_health_check()
                else:
                    print("❌ Invalid choice. Please try again.")
                    
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    helper = HomelabHelper()
    helper.run()
