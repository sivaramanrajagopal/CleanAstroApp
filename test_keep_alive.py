#!/usr/bin/env python3
"""
Test script for the keep-alive service
"""

import os
import time
from keep_alive import start_keep_alive, stop_keep_alive

def test_keep_alive():
    """Test the keep-alive service"""
    print("🧪 Testing Keep-Alive Service")
    print("=" * 50)
    
    # Test 1: No URL set
    print("\n1️⃣ Testing without RENDER_APP_URL:")
    service1 = start_keep_alive()
    if service1 and service1.is_alive():
        print("✅ Service started successfully")
        stop_keep_alive()
    else:
        print("ℹ️ Service not started (expected - no URL configured)")
    
    # Test 2: With test URL
    print("\n2️⃣ Testing with test URL:")
    test_url = "https://httpbin.org/get"
    print(f"URL: {test_url}")
    
    service2 = start_keep_alive(test_url)
    if service2 and service2.is_alive():
        print("✅ Service started successfully")
        print("⏰ Running for 10 seconds to test pings...")
        
        # Let it run for 10 seconds
        time.sleep(10)
        
        print("🛑 Stopping service...")
        stop_keep_alive()
        print("✅ Service stopped")
    else:
        print("❌ Failed to start service")
    
    # Test 3: Environment variable
    print("\n3️⃣ Testing with environment variable:")
    os.environ['RENDER_APP_URL'] = "https://httpbin.org/status/200"
    service3 = start_keep_alive()
    if service3 and service3.is_alive():
        print("✅ Service started from environment variable")
        time.sleep(5)
        stop_keep_alive()
    else:
        print("❌ Failed to start service from environment variable")
    
    print("\n🎯 Keep-Alive Test Complete!")

if __name__ == "__main__":
    test_keep_alive() 