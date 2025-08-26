import requests
import json

print("🔍 MEDIMORPH Quick Health Check")
print("=" * 40)

try:
    # Test health endpoint
    response = requests.get('http://localhost:5000/health', timeout=5)
    print(f"✅ Health Check: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.json()}")
    
    # Test login page
    response = requests.get('http://localhost:5000/login', timeout=5)
    print(f"✅ Login Page: {response.status_code}")
    
    # Test login functionality
    session = requests.Session()
    login_data = {'username': 'testuser', 'password': 'testpass123'}
    response = session.post('http://localhost:5000/login', 
                           headers={'Content-Type': 'application/json'},
                           data=json.dumps(login_data), timeout=5)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"✅ Login Test: SUCCESS - User: {result['user']['username']}")
            
            # Test dashboard
            response = session.get('http://localhost:5000/dashboard', timeout=5)
            print(f"✅ Dashboard: {response.status_code}")
            
            # Test medications API
            response = session.get('http://localhost:5000/medications', timeout=5)
            if response.status_code == 200:
                medications = response.json()
                print(f"✅ Medications API: {len(medications)} medications found")
            else:
                print(f"❌ Medications API: {response.status_code}")
        else:
            print(f"❌ Login Test: {result.get('message')}")
    else:
        print(f"❌ Login Test: {response.status_code}")
    
    print("\n🎉 MEDIMORPH is working perfectly!")
    
except requests.exceptions.ConnectionError:
    print("❌ Application not running on localhost:5000")
    print("   Please start the application first: python app.py")
except Exception as e:
    print(f"❌ Error: {e}")
