"""
Example script to test the investment deal analysis API.
This demonstrates how to use the API programmatically.
"""

import requests
import os
import sys

# API endpoint - Change port if your server uses a different port
PORT = os.environ.get('API_PORT', '5001')  # Default to 5001 to avoid macOS AirPlay conflict
BASE_URL = f"http://localhost:{PORT}"
API_URL = f"{BASE_URL}/analyze"
HEALTH_URL = f"{BASE_URL}/health"

def check_server():
    """Check if the Flask server is running"""
    try:
        response = requests.get(HEALTH_URL, timeout=2)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"⚠️ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is the Flask app running?")
        print("   Start it with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {str(e)}")
        return False

def test_analysis(file_path):
    """
    Test the investment deal analysis endpoint.
    
    Args:
        file_path: Path to the investment deal document
    """
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    # Check if server is running first
    if not check_server():
        sys.exit(1)
    
    print(f"\n📤 Uploading file: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/plain')}
            response = requests.post(API_URL, files=files, timeout=300)  # 5 min timeout for analysis
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Analysis complete!")
                print(f"\n📊 Report ID: {result['report_id']}")
                print(f"\n✅ Pros Report Preview:")
                print(result['pros_report'][:500] + "...")
                print(f"\n⚠️ Cons Report Preview:")
                print(result['cons_report'][:500] + "...")
                print(f"\n📈 Final Report Preview:")
                print(result['final_report'][:500] + "...")
                print(f"\n📁 Full reports available at:")
                for report_type, report_path in result['reports'].items():
                    print(f"  - {report_type}: {BASE_URL}{report_path}")
            except ValueError as e:
                print(f"❌ Error parsing JSON response: {str(e)}")
                print(f"Response text: {response.text[:500]}")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except ValueError:
                print(f"Response text: {response.text[:500]}")
    
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The analysis might be taking longer than expected.")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Is the server still running?")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Example usage - replace with your file path
    test_file = "example_deal.txt"
    
    if os.path.exists(test_file):
        test_analysis(test_file)
    else:
        print(f"⚠️ Test file not found: {test_file}")
        print("Create a sample investment deal document to test, or modify the test_file variable.")

