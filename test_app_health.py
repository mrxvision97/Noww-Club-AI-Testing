"""
Test script to verify the Streamlit app is working with vision board functionality
"""
import requests
import time

def test_app_health():
    """Test if the Streamlit app is responding"""
    urls = ["http://localhost:5000", "http://127.0.0.1:5000", "http://0.0.0.0:5000"]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ App is responding at {url} with status code: {response.status_code}")
            return True, url
        except Exception as e:
            print(f"❌ Failed to connect to {url}: {e}")
    
    return False, None

def test_streamlit_health(base_url):
    """Test if Streamlit is running properly"""
    try:
        # Streamlit health endpoint
        health_url = f"{base_url}/_stcore/health"
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit core is healthy")
            return True
        else:
            print(f"⚠️ Streamlit health check returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Streamlit health check failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Streamlit App Health...")
    print("=" * 50)
    
    # Test 1: Basic app response
    app_healthy, working_url = test_app_health()
    
    # Test 2: Streamlit health
    streamlit_healthy = False
    if app_healthy:
        streamlit_healthy = test_streamlit_health(working_url)
    
    print("\n" + "=" * 50)
    print("🏁 Test Results:")
    print(f"✅ App Response: {'HEALTHY' if app_healthy else 'FAILED'}")
    print(f"✅ Streamlit Core: {'HEALTHY' if streamlit_healthy else 'FAILED'}")
    
    if app_healthy:
        print(f"\n🎉 SUCCESS! Your app is running properly!")
        print(f"🌐 Access it at: {working_url}")
        print("🎨 Try saying: 'Create a vision board for me'")
    else:
        print("\n❌ App is not responding properly. Please check the terminal for errors.")
