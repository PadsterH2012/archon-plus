#!/usr/bin/env python3
"""
ARCH-001 Continuous Watcher

A simple script that continuously monitors ARCH-001 status and alerts when resolved.
Perfect for automated testing without manual intervention.
"""

import time
import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from tests.monitor_arch_001 import ARCH001Monitor


def watch_arch_001(interval=30, max_duration=3600):
    """
    Watch ARCH-001 status continuously
    
    Args:
        interval: Check interval in seconds (default: 30)
        max_duration: Maximum watch duration in seconds (default: 3600 = 1 hour)
    """
    print("🔍 ARCH-001 Continuous Watcher Started")
    print("=" * 50)
    print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")
    print(f"🔄 Check interval: {interval} seconds")
    print(f"⏳ Max duration: {max_duration} seconds ({max_duration//60} minutes)")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)
    
    monitor = ARCH001Monitor("http://10.202.70.20:9181")
    start_time = time.time()
    check_count = 0
    last_status = None
    
    try:
        while True:
            check_count += 1
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Check if max duration exceeded
            if elapsed > max_duration:
                print(f"\n⏰ Maximum duration ({max_duration}s) reached")
                break
            
            # Check ARCH-001 status
            status = monitor.check_arch_001_status()
            current_status = status["status"]
            resolved = status["resolved"]
            
            # Format timestamp
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # Only print if status changed or every 10 checks
            if current_status != last_status or check_count % 10 == 0:
                if resolved:
                    icon = "✅"
                    message = "RESOLVED"
                else:
                    icon = "❌"
                    message = "NOT RESOLVED"
                
                print(f"[{check_count:03d}] {timestamp} | {icon} ARCH-001 {message} | Status: {current_status}")
                
                # Show details for errors
                if not resolved and "error" in status["details"]:
                    error_msg = status["details"]["error"]
                    if len(error_msg) > 80:
                        error_msg = error_msg[:77] + "..."
                    print(f"      └─ Details: {error_msg}")
            
            # If resolved, celebrate and exit
            if resolved:
                print("\n" + "🎉" * 20)
                print("🎉 ARCH-001 HAS BEEN RESOLVED! 🎉")
                print("🎉" * 20)
                print(f"✅ Resolution detected after {elapsed:.1f} seconds ({check_count} checks)")
                print(f"✅ Final status: {current_status}")
                print("✅ Issues Kanban should now work properly!")
                return True
            
            last_status = current_status
            
            # Wait before next check
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Monitoring stopped by user after {elapsed:.1f} seconds")
        return False
    
    print(f"\n⏰ Monitoring completed after {elapsed:.1f} seconds")
    print("❌ ARCH-001 was not resolved during monitoring period")
    return False


def main():
    """Main function with command line argument support"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Watch ARCH-001 status continuously")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds (default: 30)")
    parser.add_argument("--duration", type=int, default=3600, help="Max duration in seconds (default: 3600)")
    parser.add_argument("--quick", action="store_true", help="Quick mode: 10s interval, 5min duration")
    
    args = parser.parse_args()
    
    if args.quick:
        interval = 10
        duration = 300  # 5 minutes
    else:
        interval = args.interval
        duration = args.duration
    
    resolved = watch_arch_001(interval, duration)
    sys.exit(0 if resolved else 1)


if __name__ == "__main__":
    main()
