#!/usr/bin/env python3
"""
Inactivity Logout System Test Script
Tests both backend token expiration and frontend inactivity features
"""

import os
import sys
import django
import requests
import time
from datetime import datetime, timedelta

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.authtoken.models import Token
from apps.core.models import TokenActivity

User = get_user_model()

class InactivityLogoutTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.test_user = None
        self.test_token = None
    
    def setup_test_user(self):
        """Create or get test user"""
        print("🔧 Setting up test user...")
        
        try:
            # Create test user
            email = 'inactivity_test@company.com'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': 'Inactivity',
                    'last_name': 'Test',
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('testpass123')
                user.save()
                print(f"   ✅ Created test user: {email}")
            else:
                print(f"   ℹ️ Using existing test user: {email}")
            
            # Create or get token
            token, created = Token.objects.get_or_create(user=user)
            
            self.test_user = user
            self.test_token = token
            
            # Create TokenActivity record
            activity, created = TokenActivity.objects.get_or_create(
                token=token,
                defaults={'last_activity': timezone.now()}
            )
            
            if created:
                print(f"   ✅ Created token activity record")
            else:
                # Update last activity
                activity.last_activity = timezone.now()
                activity.save()
                print(f"   ✅ Updated token activity record")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error setting up test user: {str(e)}")
            return False
    
    def test_token_validity_endpoint(self):
        """Test the token validity check endpoint"""
        print("\n📡 Testing token validity endpoint...")
        
        if not self.test_token:
            print("   ❌ No test token available")
            return False
        
        try:
            # Set authorization header
            self.session.headers.update({
                'Authorization': f'Token {self.test_token.key}'
            })
            
            # Test endpoint
            response = self.session.get(f"{self.api_base}/auth/check-token/")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Token validity check successful")
                print(f"      Valid: {data.get('valid', 'Unknown')}")
                print(f"      User: {data.get('user', {}).get('email', 'Unknown')}")
                
                token_info = data.get('token_info', {})
                print(f"      Last Activity: {token_info.get('last_activity', 'Unknown')}")
                print(f"      Time Remaining: {token_info.get('time_remaining_seconds', 'Unknown')}s")
                
                return data.get('valid', False)
            else:
                print(f"   ❌ Token validity check failed: {response.status_code}")
                print(f"      Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing token validity: {str(e)}")
            return False
    
    def test_token_refresh_endpoint(self):
        """Test the token refresh endpoint"""
        print("\n🔄 Testing token refresh endpoint...")
        
        try:
            response = self.session.post(f"{self.api_base}/auth/refresh-token/")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Token refresh successful")
                print(f"      Message: {data.get('message', 'Unknown')}")
                print(f"      Time Remaining: {data.get('time_remaining_seconds', 'Unknown')}s")
                return True
            else:
                print(f"   ❌ Token refresh failed: {response.status_code}")
                print(f"      Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing token refresh: {str(e)}")
            return False
    
    def test_token_expiration(self):
        """Test token expiration after inactivity"""
        print("\n⏰ Testing token expiration after inactivity...")
        
        if not self.test_token:
            print("   ❌ No test token available")
            return False
        
        try:
            # Get current activity
            activity = TokenActivity.objects.get(token=self.test_token)
            
            # Simulate old activity (4 minutes ago - past the 3 minute timeout)
            old_time = timezone.now() - timedelta(minutes=4)
            activity.last_activity = old_time
            activity.save()
            
            print(f"   🕐 Set last activity to: {old_time}")
            print(f"   ⏳ Waiting for token expiration check...")
            
            # Test token validity - should be expired
            response = self.session.get(f"{self.api_base}/auth/check-token/")
            
            if response.status_code == 401:
                print(f"   ✅ Token correctly expired (401 Unauthorized)")
                return True
            elif response.status_code == 200:
                data = response.json()
                if not data.get('valid', True):
                    print(f"   ✅ Token marked as invalid")
                    return True
                else:
                    print(f"   ⚠️ Token still valid despite inactivity")
                    print(f"      Response: {data}")
                    return False
            else:
                print(f"   ❌ Unexpected response: {response.status_code}")
                print(f"      Response: {response.text}")
                return False
                
        except TokenActivity.DoesNotExist:
            print(f"   ❌ TokenActivity not found for test token")
            return False
        except Exception as e:
            print(f"   ❌ Error testing token expiration: {str(e)}")
            return False
    
    def test_backend_authentication(self):
        """Test Django's expiring token authentication"""
        print("\n🔐 Testing backend authentication system...")
        
        try:
            from apps.core.authentication import ExpiringTokenAuthentication
            
            auth = ExpiringTokenAuthentication()
            
            # Test with valid token
            print("   🔍 Testing with valid token...")
            
            # Reset token activity to now
            activity = TokenActivity.objects.get(token=self.test_token)
            activity.last_activity = timezone.now()
            activity.save()
            
            # This would normally be called by Django's authentication system
            user, token = auth.authenticate_credentials(self.test_token.key)
            print(f"   ✅ Authentication successful for: {user.email}")
            
            # Test with expired token
            print("   🔍 Testing with expired token...")
            
            # Set old activity time
            old_time = timezone.now() - timedelta(minutes=4)
            activity.last_activity = old_time
            activity.save()
            
            try:
                user, token = auth.authenticate_credentials(self.test_token.key)
                print(f"   ⚠️ Authentication should have failed but didn't")
                return False
            except Exception as e:
                if "expired" in str(e).lower():
                    print(f"   ✅ Authentication correctly failed: {str(e)}")
                    return True
                else:
                    print(f"   ❌ Unexpected authentication error: {str(e)}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Error testing backend authentication: {str(e)}")
            return False
    
    def generate_frontend_test_html(self):
        """Generate HTML file for frontend testing"""
        print("\n📄 Generating frontend test file...")
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inactivity Logout Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .status {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .success {{ background: #d4edda; border: 1px solid #c3e6cb; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; }}
        .error {{ background: #f8d7da; border: 1px solid #f5c6cb; }}
        button {{ padding: 10px 15px; margin: 5px; cursor: pointer; }}
        #log {{ background: #f8f9fa; padding: 15px; margin: 15px 0; height: 300px; overflow-y: auto; }}
    </style>
</head>
<body>
    <h1>Inactivity Logout Test</h1>
    
    <div class="status success">
        <strong>Test Configuration:</strong>
        <ul>
            <li>Timeout: 3 minutes (180 seconds)</li>
            <li>Token Check Interval: 30 seconds</li>
            <li>Warning: 30 seconds before logout</li>
            <li>Test Token: {self.test_token.key if self.test_token else 'N/A'}</li>
            <li>Test User: {self.test_user.email if self.test_user else 'N/A'}</li>
        </ul>
    </div>
    
    <div>
        <h3>Test Actions:</h3>
        <button onclick="loginWithTestToken()">Login with Test Token</button>
        <button onclick="checkTokenValidity()">Check Token Validity</button>
        <button onclick="refreshToken()">Refresh Token</button>
        <button onclick="simulateInactivity()">Simulate 4min Inactivity</button>
        <button onclick="clearLog()">Clear Log</button>
    </div>
    
    <div>
        <h3>Status:</h3>
        <div id="status" class="status">Ready for testing</div>
    </div>
    
    <div>
        <h3>Log:</h3>
        <div id="log"></div>
    </div>
    
    <script>
        const API_BASE = '{self.api_base}';
        const TEST_TOKEN = '{self.test_token.key if self.test_token else ''}';
        
        function log(message, type = 'info') {{
            const logDiv = document.getElementById('log');
            const timestamp = new Date().toLocaleTimeString();
            const entry = document.createElement('div');
            entry.innerHTML = `[${{timestamp}}] ${{message}}`;
            entry.style.color = type === 'error' ? 'red' : type === 'success' ? 'green' : 'black';
            logDiv.appendChild(entry);
            logDiv.scrollTop = logDiv.scrollHeight;
        }}
        
        function updateStatus(message, type = 'success') {{
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = `status ${{type}}`;
        }}
        
        function clearLog() {{
            document.getElementById('log').innerHTML = '';
        }}
        
        function loginWithTestToken() {{
            localStorage.setItem('token', TEST_TOKEN);
            localStorage.setItem('role', 'employee');
            localStorage.setItem('loginTime', new Date().toISOString());
            
            log('Test token stored in localStorage', 'success');
            updateStatus('Logged in with test token', 'success');
        }}
        
        async function checkTokenValidity() {{
            try {{
                const response = await fetch(`${{API_BASE}}/auth/check-token/`, {{
                    method: 'GET',
                    headers: {{
                        'Authorization': `Token ${{TEST_TOKEN}}`,
                        'Content-Type': 'application/json'
                    }}
                }});
                
                const data = await response.json();
                
                if (response.ok) {{
                    log(`Token validity: ${{data.valid ? 'VALID' : 'INVALID'}}`, data.valid ? 'success' : 'error');
                    if (data.token_info) {{
                        log(`Time remaining: ${{data.token_info.time_remaining_seconds}}s`);
                        log(`Last activity: ${{data.token_info.last_activity}}`);
                    }}
                    updateStatus(`Token is ${{data.valid ? 'valid' : 'invalid'}}`, data.valid ? 'success' : 'error');
                }} else {{
                    log(`Token check failed: ${{response.status}} - ${{data.error || 'Unknown error'}}`, 'error');
                    updateStatus('Token check failed', 'error');
                }}
            }} catch (error) {{
                log(`Error checking token: ${{error.message}}`, 'error');
                updateStatus('Token check error', 'error');
            }}
        }}
        
        async function refreshToken() {{
            try {{
                const response = await fetch(`${{API_BASE}}/auth/refresh-token/`, {{
                    method: 'POST',
                    headers: {{
                        'Authorization': `Token ${{TEST_TOKEN}}`,
                        'Content-Type': 'application/json'
                    }}
                }});
                
                const data = await response.json();
                
                if (response.ok) {{
                    log(`Token refreshed: ${{data.message}}`, 'success');
                    log(`Time remaining: ${{data.time_remaining_seconds}}s`);
                    updateStatus('Token refreshed successfully', 'success');
                }} else {{
                    log(`Token refresh failed: ${{response.status}} - ${{data.error || 'Unknown error'}}`, 'error');
                    updateStatus('Token refresh failed', 'error');
                }}
            }} catch (error) {{
                log(`Error refreshing token: ${{error.message}}`, 'error');
                updateStatus('Token refresh error', 'error');
            }}
        }}
        
        function simulateInactivity() {{
            log('Simulating 4 minutes of inactivity on backend...', 'warning');
            updateStatus('Simulating inactivity...', 'warning');
            
            // This would need to be implemented on backend
            // For now, just wait and check token
            setTimeout(() => {{
                log('Checking token after simulated inactivity...');
                checkTokenValidity();
            }}, 2000);
        }}
        
        // Auto-check token every 10 seconds
        setInterval(() => {{
            if (TEST_TOKEN) {{
                checkTokenValidity();
            }}
        }}, 10000);
        
        // Initialize
        log('Frontend test initialized', 'success');
        log(`API Base: ${{API_BASE}}`);
        log(`Test Token: ${{TEST_TOKEN}}`);
    </script>
</body>
</html>"""
        
        test_file = os.path.join(backend_dir, 'inactivity_test.html')
        with open(test_file, 'w') as f:
            f.write(html_content)
        
        print(f"   ✅ Frontend test file created: {test_file}")
        print(f"   🌐 Open in browser: file://{test_file}")
        return test_file
    
    def cleanup(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            if self.test_user:
                # Delete token activity
                TokenActivity.objects.filter(token__user=self.test_user).delete()
                # Delete token
                Token.objects.filter(user=self.test_user).delete()
                # Delete user
                self.test_user.delete()
                print("   ✅ Test user and related data cleaned up")
        except Exception as e:
            print(f"   ⚠️ Cleanup warning: {str(e)}")

def main():
    """Main testing function"""
    print("INACTIVITY LOGOUT SYSTEM TEST")
    print("=" * 50)
    
    tester = InactivityLogoutTester()
    
    # Setup
    if not tester.setup_test_user():
        print("❌ Failed to set up test user")
        return
    
    # Run backend tests
    print(f"\n🔧 BACKEND TESTS")
    print("=" * 30)
    
    backend_tests = [
        ("Token Validity Endpoint", tester.test_token_validity_endpoint),
        ("Token Refresh Endpoint", tester.test_token_refresh_endpoint),
        ("Backend Authentication", tester.test_backend_authentication),
        ("Token Expiration", tester.test_token_expiration),
    ]
    
    backend_results = []
    for test_name, test_func in backend_tests:
        try:
            result = test_func()
            backend_results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} failed with error: {str(e)}")
            backend_results.append((test_name, False))
    
    # Generate frontend test
    print(f"\n🌐 FRONTEND TEST")
    print("=" * 30)
    
    try:
        test_file = tester.generate_frontend_test_html()
        print("   ✅ Frontend test file generated")
    except Exception as e:
        print(f"   ❌ Frontend test generation failed: {str(e)}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed_tests = sum(1 for _, result in backend_results if result)
    total_tests = len(backend_results)
    
    print(f"Backend Tests: {passed_tests}/{total_tests} passed")
    
    for test_name, result in backend_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    if passed_tests == total_tests:
        print("\n🎉 All backend tests passed!")
        print("📱 Frontend test file generated for manual testing")
        print("\n📋 NEXT STEPS:")
        print("1. Start Django server: python manage.py runserver")
        print("2. Open frontend test file in browser")
        print("3. Test inactivity logout in React app")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} backend test(s) failed")
    
    # Cleanup
    cleanup_input = input("\n🧹 Clean up test data? (y/N): ").lower()
    if cleanup_input == 'y':
        tester.cleanup()
    else:
        print("   ℹ️ Test data preserved for further testing")

if __name__ == '__main__':
    main()