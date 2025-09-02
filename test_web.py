#!/usr/bin/env python3
"""
Simple test to verify the web interface is working
"""

import requests
import time
import subprocess
import sys

def test_web_interface():
    """Test if the web interface is accessible."""
    print("🧪 Testing web interface...")
    
    # Try to connect to the web interface
    try:
        response = requests.get("http://127.0.0.1:7860", timeout=5)
        if response.status_code == 200:
            print("✅ Web interface is running and accessible!")
            print("🌐 Open your browser to: http://127.0.0.1:7860")
            return True
        else:
            print(f"⚠️  Web interface responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Web interface is not accessible")
        print("💡 Make sure to run: python ui_gradio.py")
        return False
    except Exception as e:
        print(f"❌ Error testing web interface: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing RAG Document Processor Web Interface")
    print("=" * 50)
    
    # Test web interface
    if test_web_interface():
        print("\n🎉 Web interface is working!")
        print("\n📋 Next steps:")
        print("1. Open your browser to: http://127.0.0.1:7860")
        print("2. Try the 'Text Input' tab with sample text")
        print("3. Try the 'File Upload' tab with a document")
        print("4. Check the JSONL output format")
    else:
        print("\n❌ Web interface test failed")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure the virtual environment is activated")
        print("2. Run: python ui_gradio.py")
        print("3. Wait for the server to start")
        print("4. Check for any error messages")

if __name__ == "__main__":
    main()
