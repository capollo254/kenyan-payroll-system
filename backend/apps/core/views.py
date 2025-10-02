# apps/core/views.py

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.templatetags.static import static
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.middleware.csrf import get_token
from django.utils import timezone
from datetime import timedelta
import os
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes

# Do NOT import serializers at the top of the file to prevent circular imports
# from .serializers import UserSerializer, UserLoginSerializer

def welcome(request):
    # Check if user is authenticated
    is_authenticated = request.user.is_authenticated
    
    if is_authenticated:
        # Show internal dashboard for authenticated users
        return render_internal_dashboard(request)
    else:
        # Show public landing page for unauthenticated users
        return render_public_landing(request)


def render_public_landing(request):
    """
    Public landing page for unauthenticated users
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kenya Payroll System</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                line-height: 1.6; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
                background: white; 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                animation: fadeIn 0.8s ease-in;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            h1 { 
                color: #2c3e50; 
                border-bottom: 4px solid #27ae60; 
                padding-bottom: 15px; 
                margin-bottom: 20px;
                font-size: 2.5em;
                text-align: center;
            }
            h2 { 
                color: #34495e; 
                margin: 25px 0 15px 0; 
                font-size: 1.3em;
                border-left: 4px solid #3498db;
                padding-left: 15px;
            }
            .section { 
                margin: 30px 0; 
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
            .button { 
                display: inline-block; 
                padding: 15px 30px; 
                background: #27ae60; 
                color: white; 
                text-decoration: none; 
                border-radius: 8px; 
                margin: 10px 5px; 
                font-weight: bold;
                font-size: 16px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                text-align: center;
                min-width: 200px;
            }
            .button:hover { 
                background: #2ecc71; 
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.2);
            }
            .button.login { 
                background: #3498db; 
                margin-left: 10px;
            }
            .button.login:hover { 
                background: #2980b9; 
            }
            .hero { 
                text-align: center; 
                margin: 40px 0; 
            }
            .hero p { 
                font-size: 1.2em; 
                color: #7f8c8d; 
                margin: 20px 0; 
            }
            .features { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px; 
                margin: 30px 0; 
            }
            .feature-item { 
                background: white; 
                padding: 20px; 
                border-radius: 8px; 
                border-left: 4px solid #27ae60;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }
            .feature-icon {
                font-size: 2em;
                margin-bottom: 10px;
            }
            .footer { 
                text-align: center; 
                margin-top: 40px; 
                padding-top: 20px; 
                border-top: 1px solid #bdc3c7; 
                color: #7f8c8d; 
            }
            @media (max-width: 768px) {
                .container { padding: 20px; margin: 10px; }
                h1 { font-size: 2em; }
                .button { display: block; margin: 10px 0; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Kenya Payroll System</h1>
            
            <div class="hero">
                <p>Professional payroll calculation system compliant with Kenyan tax laws</p>
                <p>Calculate your net salary including PAYE, NSSF, and NHIF deductions</p>
            </div>
            
            <div class="section" style="text-align: center;">
                <h2>🧮 Free Payroll Calculator</h2>
                <p>Calculate your take-home salary instantly with our free online calculator</p>
                <a href="/calculator/" class="button">Calculate Your Salary</a>
            </div>
            
            <div class="section">
                <h2>✨ Key Features</h2>
                <div class="features">
                    <div class="feature-item">
                        <div class="feature-icon">💰</div>
                        <h3>KRA PAYE Calculations</h3>
                        <p>Accurate tax calculations as per Kenya Revenue Authority guidelines</p>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">🏥</div>
                        <h3>NHIF & NSSF</h3>
                        <p>Automatic deductions for health insurance and social security</p>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">📊</div>
                        <h3>Tax Reliefs</h3>
                        <p>Insurance, medical, and mortgage interest reliefs included</p>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">⚡</div>
                        <h3>Instant Results</h3>
                        <p>Get your net salary calculation in seconds</p>
                    </div>
                </div>
            </div>
            
            <div class="section" style="text-align: center;">
                <h2>👥 For Organizations & Employees</h2>
                <p><strong>Primary Access:</strong> Use our main employee portal for full payroll system access</p>
                <a href="/employee/" class="button login" style="background: #27ae60; font-size: 18px; padding: 15px 30px; margin: 10px;" target="_blank">
                    🌟 Employee Portal Login
                </a>
                <p style="margin: 20px 0; color: #7f8c8d;"><em>Access payslips, profile, leave requests, and admin features</em></p>
                
                <hr style="margin: 30px 0; border: 1px solid #ecf0f1;">
                
                <p><strong>Alternative Access:</strong> System administrators and API access</p>
                <a href="/admin-staff/" class="button" style="background: #8e44ad; margin: 5px;">🔐 Staff Login Only</a>
                <a href="/admin/" class="button" style="background: #e74c3c; margin: 5px;" target="_blank">Django Admin</a>
            </div>
            
            <div class="footer">
                <p><strong>Kenya Payroll System</strong> - Compliant with Kenyan Tax Laws</p>
                <p>© 2025 - Professional Payroll Solutions</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)


def render_internal_dashboard(request):
    """
    Internal dashboard for authenticated users
    """
    user_name = request.user.get_full_name() or request.user.username
    is_admin = request.user.is_staff or request.user.is_superuser
    
    # Prepare conditional content
    admin_buttons = ""
    if is_admin:
        admin_buttons = '''<a href="/admin/" class="button admin" target="_blank">Admin Panel</a>
                <a href="/calculator/" class="button">Test Calculator</a>
                <a href="/api/" class="button">API Documentation</a>'''
    
    admin_sections = ""
    if is_admin:
        admin_sections = '''
            <div class="section">
                <h3>📊 Public Calculator API</h3>
                <p>Test the payroll calculator without authentication:</p>
                <div class="endpoint">GET /api/public/calculator/?basic_salary=100000</div>
                <p><strong>Example response:</strong> Returns PAYE tax, NSSF, NHIF, and net salary calculations.</p>
            </div>
            
            <div class="section">
                <h3>🔐 Authentication Endpoints</h3>
                <div class="endpoint">POST /api/v1/auth/register/ - User Registration</div>
                <div class="endpoint">POST /api/v1/auth/login/ - User Login</div>
                <div class="endpoint">GET /api/v1/auth/profile/ - User Profile</div>
                <div class="endpoint">POST /api/v1/auth/logout/ - User Logout</div>
            </div>
            
            <div class="section">
                <h3>🏢 Core Modules</h3>
                <div class="endpoint">GET/POST /api/v1/employees/ - Employee Management</div>
                <div class="endpoint">GET/POST /api/v1/payroll/ - Payroll Processing</div>
                <div class="endpoint">GET /api/v1/reports/ - Reports & Analytics</div>
                <div class="endpoint">GET /api/v1/notifications/ - System Notifications</div>
            </div>'''
    
    employee_sections = ""
    if not is_admin:
        employee_sections = '''
            <div class="section">
                <h3>👤 Employee Services</h3>
                <div class="features">
                    <div class="feature-item">📄 View and Download Payslips</div>
                    <div class="feature-item">👤 Manage Personal Profile</div>
                    <div class="feature-item">📊 Access Salary Information</div>
                    <div class="feature-item">📞 Contact HR for Support</div>
                </div>
                <p style="text-align: center; margin-top: 20px;">
                    <em>For the best experience, use our main employee portal: 
                    <a href="/employee/" style="color: #27ae60;" target="_blank">Employee Portal</a>
                    </em>
                </p>
            </div>'''
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kenya Payroll System - Dashboard</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                line-height: 1.6; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{ 
                max-width: 1000px; 
                margin: 0 auto; 
                background: white; 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                animation: fadeIn 0.8s ease-in;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 3px solid #27ae60;
            }}
            h1 {{ 
                color: #2c3e50; 
                font-size: 2.2em;
            }}
            .user-info {{
                color: #7f8c8d;
                font-size: 1.1em;
            }}
            .logout-btn {{
                background: #e74c3c;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                text-decoration: none;
                font-size: 14px;
                transition: background 0.3s ease;
            }}
            .logout-btn:hover {{
                background: #c0392b;
            }}
            h3 {{ 
                color: #34495e; 
                margin: 25px 0 15px 0; 
                font-size: 1.3em;
                border-left: 4px solid #3498db;
                padding-left: 15px;
            }}
            .section {{ 
                margin: 30px 0; 
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }}
            .endpoint {{ 
                background: #2c3e50; 
                color: white;
                padding: 12px 15px; 
                margin: 8px 0; 
                border-radius: 6px; 
                font-family: 'Courier New', monospace;
                font-size: 14px;
                overflow-x: auto;
                border-left: 4px solid #27ae60;
            }}
            .button {{ 
                display: inline-block; 
                padding: 12px 25px; 
                background: #27ae60; 
                color: white; 
                text-decoration: none; 
                border-radius: 6px; 
                margin: 8px 5px; 
                font-weight: bold;
                transition: all 0.3s ease;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .button:hover {{ 
                background: #2ecc71; 
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.2);
            }}
            .button.admin {{ background: #e74c3c; }}
            .button.admin:hover {{ background: #c0392b; }}
            .status {{ 
                color: #27ae60; 
                font-weight: bold; 
                font-size: 1.2em;
                text-align: center;
                padding: 15px;
                background: #d5f4e6;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .features {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 15px; 
                margin: 20px 0; 
            }}
            .feature-item {{ 
                background: white; 
                padding: 15px; 
                border-radius: 6px; 
                border-left: 4px solid #3498db;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .footer {{ 
                text-align: center; 
                margin-top: 40px; 
                padding-top: 20px; 
                border-top: 1px solid #bdc3c7; 
                color: #7f8c8d; 
            }}
            @media (max-width: 768px) {{
                .container {{ padding: 20px; margin: 10px; }}
                .header {{ flex-direction: column; text-align: center; gap: 10px; }}
                h1 {{ font-size: 1.8em; }}
                .button {{ display: block; margin: 10px 0; text-align: center; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <h1>Kenya Payroll System</h1>
                    <div class="user-info">Welcome back, {user_name}</div>
                </div>
                <a href="/logout/" class="logout-btn">Logout</a>
            </div>
            
            <div class="status">✅ System Status: Online and Running</div>
            
            <div class="section">
                <h3>🔗 Quick Access</h3>
                {admin_buttons}
            </div>
            {admin_sections}
            {employee_sections}
            <div class="section">
                <h3>ℹ️ System Features</h3>
                <div class="features">
                    <div class="feature-item">✅ KRA PAYE Tax Calculations</div>
                    <div class="feature-item">✅ NSSF Contributions</div>
                    <div class="feature-item">✅ NHIF Deductions</div>
                    <div class="feature-item">✅ Tax Relief (Insurance, Medical, Mortgage)</div>
                    <div class="feature-item">✅ Overtime Calculations</div>
                    <div class="feature-item">✅ Employee Management</div>
                    <div class="feature-item">✅ Report Generation</div>
                    <div class="feature-item">✅ REST API Integration</div>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>Developed with Django REST Framework | Deployed on Railway</strong></p>
                <p>For technical support, contact your system administrator.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)


class UserRegistrationView(APIView):
    """
    API endpoint for user registration.
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        # Import the serializer here, inside the method
        from .serializers import UserSerializer
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    """
    API endpoint for user login, which returns an authentication token.
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        # Import the serializer here, inside the method
        from .serializers import UserLoginSerializer

        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            role = 'admin' if user.is_superuser else 'employee'
            return Response({'token': token.key, 'role': role}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    """
    API endpoint to retrieve the current authenticated user's profile.
    Requires authentication via token in the Authorization header.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Import the serializer here, inside the method
        from .serializers import UserSerializer
        
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserLogoutView(APIView):
    """
    API endpoint to log out a user by deleting their authentication token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except settings.AUTH_USER_MODEL.auth_token.RelatedObjectDoesNotExist:
            return Response({'error': 'Token not found.'}, status=status.HTTP_400_BAD_REQUEST)


def calculator_page(request):
    """
    Serve the HTML calculator page - FREE PUBLIC ACCESS (no authentication required)
    This is the public payroll calculator advertised on the home page
    """
    # Path to the calculator HTML file
    calculator_file = os.path.join(settings.BASE_DIR.parent, 'payroll_calculator.html')
    
    try:
        with open(calculator_file, 'r', encoding='utf-8') as file:
            html_content = file.read()
            
        # Replace the API endpoint in the HTML to point to our Django API
        # html_content = html_content.replace(
        #     'http://127.0.0.1:8000/api/public/calculator/',
        #     '/api/public/calculator/'
        # )
        
        # Add navigation button - inject it after the header section
        back_button_html = '''
        <div style="position: fixed; top: 20px; left: 20px; z-index: 1000;">
            <a href="/" style="
                display: inline-block;
                background: #3498db;
                color: white;
                padding: 12px 20px;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            " onmouseover="this.style.background='#2980b9'; this.style.transform='translateY(-2px)';" 
               onmouseout="this.style.background='#3498db'; this.style.transform='translateY(0)';">
                ← Back to Home
            </a>
        </div>
        '''
        
        # Inject the back button after the opening body tag
        html_content = html_content.replace('<body>', '<body>' + back_button_html)
        
        return HttpResponse(html_content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse(
            '<h1>Calculator page not found</h1><p>The payroll calculator HTML file could not be found.</p>',
            status=404
        )


def api_root(request):
    """
    API Root - Shows all available API endpoints (Admin access only)
    """
    # Check if user is authenticated and has admin privileges
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not (request.user.is_staff or request.user.is_superuser):
        # Non-admin users get redirected to home with a message
        from django.contrib import messages
        messages.error(request, 'Access denied. API documentation is restricted to administrators.')
        return redirect('home')
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kenya Payroll System - API Documentation</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                line-height: 1.6; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { 
                max-width: 1000px; 
                margin: 0 auto; 
                background: white; 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 { 
                color: #2c3e50; 
                border-bottom: 4px solid #27ae60; 
                padding-bottom: 15px; 
                margin-bottom: 30px;
                font-size: 2.5em;
                text-align: center;
            }
            h2 { 
                color: #34495e; 
                margin: 30px 0 15px 0; 
                font-size: 1.5em;
                border-left: 4px solid #3498db;
                padding-left: 15px;
            }
            .section { 
                margin: 30px 0; 
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
            .endpoint { 
                background: #2c3e50; 
                color: white;
                padding: 12px 15px; 
                margin: 8px 0; 
                border-radius: 6px; 
                font-family: 'Courier New', monospace;
                font-size: 14px;
                border-left: 4px solid #27ae60;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .method { 
                background: #27ae60; 
                color: white; 
                padding: 4px 8px; 
                border-radius: 4px; 
                font-size: 12px;
                font-weight: bold;
            }
            .method.post { background: #e74c3c; }
            .method.put { background: #f39c12; }
            .method.delete { background: #e74c3c; }
            .method.patch { background: #9b59b6; }
            .description { 
                color: #7f8c8d; 
                font-size: 14px; 
                margin: 5px 0;
                font-style: italic;
            }
            .auth-required {
                background: #fff3cd;
                color: #856404;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                margin: 5px 0;
                border: 1px solid #ffeaa7;
            }
            .back-link {
                display: inline-block;
                background: #3498db;
                color: white;
                padding: 12px 20px;
                text-decoration: none;
                border-radius: 6px;
                margin-bottom: 20px;
                transition: background 0.3s ease;
            }
            .back-link:hover {
                background: #2980b9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Home</a>
            <h1>🚀 API Documentation</h1>
            
            <div class="section">
                <h2>🔓 Public Endpoints (No Authentication Required)</h2>
                
                <div class="endpoint">
                    <span>GET /api/public/calculator/</span>
                    <span class="method">GET</span>
                </div>
                <div class="description">Calculate payroll with query parameters: ?basic_salary=100000</div>
                
                <div class="endpoint">
                    <span>POST /api/public/calculator/</span>
                    <span class="method post">POST</span>
                </div>
                <div class="description">Calculate payroll with JSON body containing salary details</div>
            </div>
            
            <div class="section">
                <h2>🔐 Authentication Endpoints</h2>
                <div class="auth-required">🔑 Authentication Required</div>
                
                <div class="endpoint">
                    <span>POST /api/v1/auth/login/</span>
                    <span class="method post">POST</span>
                </div>
                <div class="description">Login with username/email and password</div>
                
                <div class="endpoint">
                    <span>POST /api/v1/auth/logout/</span>
                    <span class="method post">POST</span>
                </div>
                <div class="description">Logout and invalidate authentication token</div>
                
                <div class="endpoint">
                    <span>POST /api/v1/auth/register/</span>
                    <span class="method post">POST</span>
                </div>
                <div class="description">Register a new user account</div>
            </div>
            
            <div class="section">
                <h2>👥 Employee Management</h2>
                <div class="auth-required">🔑 Authentication Required</div>
                
                <div class="endpoint">
                    <span>GET /api/v1/employees/employees/</span>
                    <span class="method">GET</span>
                </div>
                <div class="description">List all employees with pagination</div>
                
                <div class="endpoint">
                    <span>POST /api/v1/employees/employees/</span>
                    <span class="method post">POST</span>
                </div>
                <div class="description">Create a new employee record</div>
                
                <div class="endpoint">
                    <span>GET /api/v1/employees/employees/me/</span>
                    <span class="method">GET</span>
                </div>
                <div class="description">Get current user's employee profile</div>
                
                <div class="endpoint">
                    <span>GET /api/v1/employees/employees/{id}/</span>
                    <span class="method">GET</span>
                </div>
                <div class="description">Get specific employee details</div>
                
                <div class="endpoint">
                    <span>PUT /api/v1/employees/employees/{id}/</span>
                    <span class="method put">PUT</span>
                </div>
                <div class="description">Update employee information</div>
                
                <div class="endpoint">
                    <span>DELETE /api/v1/employees/employees/{id}/</span>
                    <span class="method delete">DELETE</span>
                </div>
                <div class="description">Delete an employee record</div>
            </div>
            
            <div class="section">
                <h2>💰 Payroll Management</h2>
                <div class="auth-required">🔑 Authentication Required</div>
                
                <div class="endpoint">
                    <span>GET /api/v1/payroll/payroll-runs/</span>
                    <span class="method">GET</span>
                </div>
                <div class="description">List all payroll runs</div>
                
                <div class="endpoint">
                    <span>POST /api/v1/payroll/payroll-runs/</span>
                    <span class="method post">POST</span>
                </div>
                <div class="description">Create a new payroll run</div>
                
                <div class="endpoint">
                    <span>GET /api/v1/payroll/payslips/</span>
                    <span class="method">GET</span>
                </div>
                <div class="description">List payslips with filtering options</div>
                
                <div class="endpoint">
                    <span>POST /api/v1/payroll/calculate/</span>
                    <span class="method post">POST</span>
                </div>
                <div class="description">Calculate payroll for specific employee</div>
            </div>
            
            <div class="section">
                <h2>📊 Reports</h2>
                <div class="auth-required">🔑 Authentication Required</div>
                
                <div class="endpoint">
                    <span>GET /api/v1/reports/</span>
                    <span class="method">GET</span>
                </div>
                <div class="description">Generate payroll reports and analytics</div>
            </div>
            
            <div class="section">
                <h2>🏖️ Leave Management</h2>
                <div class="auth-required">🔑 Authentication Required</div>
                
                <div class="endpoint">
                    <span>GET /api/v1/leaves/</span>
                    <span class="method">GET</span>
                </div>
                <div class="description">List leave requests and balances</div>
                
                <div class="endpoint">
                    <span>POST /api/v1/leaves/</span>
                    <span class="method post">POST</span>
                </div>
                <div class="description">Submit a new leave request</div>
            </div>
            
            <div class="section">
                <h2>🔔 Notifications</h2>
                <div class="auth-required">🔑 Authentication Required</div>
                
                <div class="endpoint">
                    <span>GET /api/v1/notifications/</span>
                    <span class="method">GET</span>
                </div>
                <div class="description">List user notifications</div>
                
                <div class="endpoint">
                    <span>POST /api/v1/notifications/mark-read/</span>
                    <span class="method post">POST</span>
                </div>
                <div class="description">Mark notifications as read</div>
            </div>
            
            <div class="section">
                <h2>📝 Usage Notes</h2>
                <p><strong>Authentication:</strong> Most endpoints require authentication using Token-based authentication. Include the token in the Authorization header: <code>Authorization: Token your_token_here</code></p>
                <p><strong>Content-Type:</strong> Send JSON data with <code>Content-Type: application/json</code></p>
                <p><strong>Pagination:</strong> List endpoints support pagination with <code>?page=1&page_size=20</code> parameters</p>
                <p><strong>Filtering:</strong> Many endpoints support filtering with query parameters</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content, content_type='text/html')


def user_logout_view(request):
    """
    Custom logout view for the web interface
    """
    logout(request)
    return redirect('home')


def user_login_view(request):
    """
    Custom login view for employees that redirects to home page after login
    RESTRICTED TO STAFF USERS ONLY
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if user is staff before allowing login
                if not user.is_staff:
                    messages.error(request, 'Access denied. This login is restricted to staff members only. Please use the main employee portal.')
                    return redirect('/')
                
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.email}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthenticationForm()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Staff Login - Kenya Payroll System</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .login-container {{ 
                background: white; 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                width: 100%;
                max-width: 400px;
                animation: fadeIn 0.8s ease-in;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            h1 {{ 
                color: #2c3e50; 
                text-align: center;
                margin-bottom: 30px;
                font-size: 2em;
                border-bottom: 3px solid #27ae60;
                padding-bottom: 10px;
            }}
            .form-group {{ 
                margin-bottom: 20px; 
            }}
            label {{ 
                display: block; 
                margin-bottom: 5px; 
                color: #34495e;
                font-weight: bold;
            }}
            input[type="text"], input[type="email"], input[type="password"] {{ 
                width: 100%; 
                padding: 12px; 
                border: 2px solid #ddd; 
                border-radius: 8px; 
                font-size: 16px;
                transition: border-color 0.3s ease;
            }}
            input[type="text"]:focus, input[type="email"]:focus, input[type="password"]:focus {{ 
                outline: none;
                border-color: #3498db;
                box-shadow: 0 0 5px rgba(52, 152, 219, 0.3);
            }}
            .button {{ 
                width: 100%;
                padding: 15px; 
                background: #27ae60; 
                color: white; 
                border: none;
                border-radius: 8px; 
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .button:hover {{ 
                background: #219a52; 
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }}
            .back-link {{ 
                display: block;
                text-align: center;
                margin-top: 20px;
                color: #3498db;
                text-decoration: none;
                transition: color 0.3s ease;
            }}
            .back-link:hover {{ 
                color: #2980b9; 
                text-decoration: underline;
            }}
            .messages {{ 
                margin-bottom: 20px; 
            }}
            .message {{ 
                padding: 12px; 
                border-radius: 5px; 
                margin-bottom: 10px;
            }}
            .message.success {{ 
                background: #d4edda; 
                color: #155724; 
                border: 1px solid #c3e6cb;
            }}
            .message.error {{ 
                background: #f8d7da; 
                color: #721c24; 
                border: 1px solid #f5c6cb;
            }}
            .help-text {{ 
                text-align: center; 
                color: #666; 
                margin-top: 20px;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="login-container">
            <h1>🔐 Staff Login</h1>
            
            <div class="messages">
                {"".join([f'<div class="message {msg.tags}">{msg.message}</div>' for msg in messages.get_messages(request)])}
            </div>
            
            <form method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                
                <div class="form-group">
                    <label for="username">Username or Email:</label>
                    <input type="text" id="username" name="username" required value="{form.data.get('username', '') if form.data else ''}">
                </div>
                
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit" class="button">Login</button>
            </form>
            
            <a href="/" class="back-link">← Back to Home</a>
            
            <div class="help-text">
                <p><strong>⚠️ STAFF ACCESS ONLY:</strong> This login is restricted to staff members only.</p>
                <p><strong>For Employees:</strong> <a href="/employee/" style="color: #27ae60;" target="_blank">Use Main Employee Portal</a></p>
                <p><strong>For Admin Access:</strong> <a href="/admin/" style="color: #3498db;" target="_blank">Use Django Admin</a></p>
                <p>Regular employees should use the main portal for full system access.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content, content_type='text/html')


def test_simple_view(request):
    """
    Simple test view to check if function-based views work
    """
    return HttpResponse("Test view working!")


def payslips_view_fixed(request):
    """
    Fixed version of payslips view - simple redirect for testing
    """
    if not request.user.is_authenticated:
        return redirect('login')
    return HttpResponse(f"Payslips view working for user: {request.user}")


def api_docs_view_fixed(request):
    """
    API Documentation view - accessible to all users
    """
    # No authentication required for API documentation
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API Documentation - Kenya Payroll System</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                min-height: 100vh;
                padding: 20px;
                color: #333;
            }
            .container { 
                background: white; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                max-width: 1200px;
                margin: 0 auto;
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #27ae60, #2ecc71);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .content {
                padding: 40px;
            }
            h1 { font-size: 2.5em; margin-bottom: 10px; }
            h2 { color: #2c3e50; margin: 30px 0 15px 0; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            h3 { color: #27ae60; margin: 20px 0 10px 0; }
            .endpoint { 
                background: #ecf0f1; 
                padding: 15px; 
                border-radius: 8px; 
                margin: 10px 0;
                border-left: 4px solid #3498db;
                font-family: 'Courier New', monospace;
            }
            .method { 
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                margin-right: 10px;
            }
            .get { background: #27ae60; color: white; }
            .post { background: #e74c3c; color: white; }
            .put { background: #f39c12; color: white; }
            .delete { background: #8e44ad; color: white; }
            .description { color: #7f8c8d; margin: 10px 0; }
            .auth-note { 
                background: #fff3cd; 
                border: 1px solid #ffeaa7; 
                padding: 15px; 
                border-radius: 8px; 
                margin: 20px 0;
            }
            .public-note { 
                background: #d4edda; 
                border: 1px solid #c3e6cb; 
                padding: 15px; 
                border-radius: 8px; 
                margin: 20px 0;
            }
            .nav-links {
                text-align: center;
                margin: 30px 0;
            }
            .nav-links a {
                display: inline-block;
                padding: 12px 25px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                margin: 0 10px;
                transition: background 0.3s;
            }
            .nav-links a:hover {
                background: #2980b9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Kenya Payroll System API</h1>
                <p>Comprehensive API Documentation for Payroll Operations</p>
            </div>
            
            <div class="content">
                <div class="nav-links">
                    <a href="/">← Back to Home</a>
                    <a href="/calculator/">Salary Calculator</a>
                    <a href="/admin/" target="_blank">Admin Panel</a>
                </div>

                <h2>📋 Public Endpoints</h2>
                <div class="public-note">
                    <strong>✅ No Authentication Required</strong> - These endpoints are publicly accessible
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span> /api/public/calculator/
                    <div class="description">Calculate salary with PAYE tax, NSSF, SHIF, and AHL deductions</div>
                </div>

                <h2>🔐 Authentication Endpoints</h2>
                
                <h3>User Authentication</h3>
                <div class="endpoint">
                    <span class="method post">POST</span> /api/v1/auth/login/
                    <div class="description">Login with username/email and password</div>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span> /api/v1/auth/logout/
                    <div class="description">Logout current user session</div>
                </div>

                <h2>👥 Employee Management</h2>
                <div class="auth-note">
                    <strong>🔒 Authentication Required</strong> - Include session cookies or authentication headers
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span> /api/v1/employees/
                    <div class="description">List all employees (staff only)</div>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span> /api/v1/employees/{id}/
                    <div class="description">Get employee details</div>
                </div>

                <h2>💰 Payroll Operations</h2>
                
                <div class="endpoint">
                    <span class="method get">GET</span> /api/v1/payroll/payslips/
                    <div class="description">Get user's payslips</div>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span> /api/v1/payroll/calculate/
                    <div class="description">Calculate payroll for employee (authenticated version)</div>
                </div>

                <h2>🏖️ Leave Management</h2>
                
                <div class="endpoint">
                    <span class="method get">GET</span> /api/v1/leaves/
                    <div class="description">Get leave requests</div>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span> /api/v1/leaves/
                    <div class="description">Submit leave request</div>
                </div>

                <h2>📊 Reports</h2>
                
                <div class="endpoint">
                    <span class="method get">GET</span> /api/v1/reports/
                    <div class="description">Get payroll reports (admin only)</div>
                </div>

                <h2>🔔 Notifications</h2>
                
                <div class="endpoint">
                    <span class="method get">GET</span> /api/v1/notifications/
                    <div class="description">Get user notifications</div>
                </div>

                <h2>💡 Usage Examples</h2>
                
                <h3>Public Calculator API</h3>
                <div class="endpoint">
                    <strong>Request:</strong><br>
                    POST /api/public/calculator/<br>
                    Content-Type: application/json<br><br>
                    {<br>
                    &nbsp;&nbsp;"gross_salary": "75000",<br>
                    &nbsp;&nbsp;"pension_contribution": "6000",<br>
                    &nbsp;&nbsp;"insurance_premiums": "2500"<br>
                    }
                </div>

                <h3>Authentication</h3>
                <div class="endpoint">
                    <strong>Login Request:</strong><br>
                    POST /api/v1/auth/login/<br>
                    Content-Type: application/json<br><br>
                    {<br>
                    &nbsp;&nbsp;"email": "user@example.com",<br>
                    &nbsp;&nbsp;"password": "your_password"<br>
                    }
                </div>

                <div class="nav-links">
                    <a href="/calculator/">Try Calculator</a>
                    <a href="/employee/">Login</a>
                    <a href="/">Home</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content, content_type='text/html')


def calculator_view_fixed(request):
    """
    Fixed version of calculator view - simple auth check for testing
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Calculator is restricted to administrators.')
        return redirect('home')
    
    return HttpResponse("Calculator view working!")


def my_payslips_view(request):
    """
    Display payslips for the logged-in user
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    user_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>My Payslips - Kenya Payroll System</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{ 
                max-width: 1000px; 
                margin: 0 auto; 
                background: white; 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                animation: fadeIn 0.8s ease-in;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 3px solid #27ae60;
            }}
            h1 {{ 
                color: #2c3e50; 
                font-size: 2.5em;
            }}
            .user-info {{
                color: #7f8c8d;
                font-size: 16px;
                margin-top: 5px;
            }}
            .back-btn {{
                display: inline-block;
                padding: 12px 24px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                transition: all 0.3s ease;
                margin-bottom: 20px;
            }}
            .back-btn:hover {{
                background: #2980b9;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }}
            .payslips-container {{
                margin-top: 30px;
            }}
            .payslip-item {{
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 15px;
                transition: all 0.3s ease;
                cursor: pointer;
            }}
            .payslip-item:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                border-color: #3498db;
            }}
            .payslip-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }}
            .payslip-period {{
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
            }}
            .payslip-amount {{
                font-size: 16px;
                color: #27ae60;
                font-weight: bold;
            }}
            .payslip-details {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }}
            .detail-item {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #ecf0f1;
            }}
            .detail-label {{
                color: #7f8c8d;
                font-weight: 500;
            }}
            .detail-value {{
                color: #2c3e50;
                font-weight: bold;
            }}
            .loading {{
                text-align: center;
                padding: 40px;
                color: #7f8c8d;
                font-size: 18px;
            }}
            .no-payslips {{
                text-align: center;
                padding: 40px;
                color: #7f8c8d;
            }}
            .no-payslips h3 {{
                color: #e74c3c;
                margin-bottom: 10px;
            }}
            .download-btn {{
                background: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: background 0.3s ease;
            }}
            .download-btn:hover {{
                background: #219a52;
            }}
            @media (max-width: 768px) {{
                .container {{ padding: 20px; }}
                .header {{ flex-direction: column; text-align: center; gap: 15px; }}
                h1 {{ font-size: 2em; }}
                .payslip-header {{ flex-direction: column; gap: 10px; }}
                .payslip-details {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-btn">← Back to Home</a>
            
            <div class="header">
                <div>
                    <h1>📄 My Payslips</h1>
                    <div class="user-info">{user_name}</div>
                </div>
            </div>
            
            <div id="loading" class="loading">
                <p>Loading your payslips...</p>
            </div>
            
            <div id="payslips-container" class="payslips-container" style="display: none;">
                <!-- Payslips will be loaded here -->
            </div>
            
            <div id="no-payslips" class="no-payslips" style="display: none;">
                <h3>No Payslips Found</h3>
                <p>You don't have any payslips available yet.</p>
                <p>Please contact HR if you believe this is an error.</p>
            </div>
        </div>
        
        <script>
            // Function to get CSRF token from cookies
            function getCookie(name) {{
                let cookieValue = null;
                if (document.cookie && document.cookie !== '') {{
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {{
                        const cookie = cookies[i].trim();
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {{
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }}
                    }}
                }}
                return cookieValue;
            }}
            
            // Function to format currency
            function formatCurrency(amount) {{
                return new Intl.NumberFormat('en-KE', {{
                    style: 'currency',
                    currency: 'KES'
                }}).format(amount);
            }}
            
            // Function to format date
            function formatDate(dateString) {{
                return new Date(dateString).toLocaleDateString('en-GB', {{
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                }});
            }}
            
            // Function to create payslip HTML
            function createPayslipHTML(payslip) {{
                return `
                    <div class="payslip-item" onclick="toggleDetails(${{payslip.id}})">
                        <div class="payslip-header">
                            <div class="payslip-period">
                                Period: ${{formatDate(payslip.payroll_run.period_start_date)}} - ${{formatDate(payslip.payroll_run.period_end_date)}}
                            </div>
                            <div class="payslip-amount">
                                Net Pay: ${{formatCurrency(payslip.net_pay)}}
                            </div>
                        </div>
                        <div class="payslip-details" id="details-${{payslip.id}}" style="display: none;">
                            <div class="detail-item">
                                <span class="detail-label">Gross Salary:</span>
                                <span class="detail-value">${{formatCurrency(payslip.gross_salary)}}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Overtime Pay:</span>
                                <span class="detail-value">${{formatCurrency(payslip.overtime_pay)}}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Total Gross:</span>
                                <span class="detail-value">${{formatCurrency(payslip.total_gross_income)}}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">PAYE Tax:</span>
                                <span class="detail-value">${{formatCurrency(payslip.paye_tax)}}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">NSSF:</span>
                                <span class="detail-value">${{formatCurrency(payslip.nssf_deduction)}}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">SHIF:</span>
                                <span class="detail-value">${{formatCurrency(payslip.shif_deduction)}}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">AHL:</span>
                                <span class="detail-value">${{formatCurrency(payslip.ahl_deduction)}}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">HELB:</span>
                                <span class="detail-value">${{formatCurrency(payslip.helb_deduction)}}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Total Deductions:</span>
                                <span class="detail-value">${{formatCurrency(payslip.total_deductions)}}</span>
                            </div>
                            <div class="detail-item" style="border-top: 2px solid #27ae60; margin-top: 10px; padding-top: 15px;">
                                <span class="detail-label"><strong>Net Pay:</strong></span>
                                <span class="detail-value" style="color: #27ae60; font-size: 18px;"><strong>${{formatCurrency(payslip.net_pay)}}</strong></span>
                            </div>
                            <div style="margin-top: 15px; text-align: right;">
                                <button class="download-btn" onclick="downloadPDF(${{payslip.id}})">📥 Download PDF</button>
                            </div>
                        </div>
                    </div>
                `;
            }}
            
            // Function to toggle payslip details
            function toggleDetails(payslipId) {{
                const details = document.getElementById(`details-${{payslipId}}`);
                if (details.style.display === 'none') {{
                    details.style.display = 'block';
                }} else {{
                    details.style.display = 'none';
                }}
            }}
            
            // Function to download PDF
            function downloadPDF(payslipId) {{
                window.open(`/api/v1/payroll/payslips/${{payslipId}}/download_pdf/`, '_blank');
            }}
            
            // Load payslips on page load
            document.addEventListener('DOMContentLoaded', function() {{
                fetch('/api/v1/payroll/payslips/', {{
                    credentials: 'include',  // Include cookies for session authentication
                    headers: {{
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }}
                }})
                .then(response => {{
                    if (!response.ok) {{
                        throw new Error('Failed to fetch payslips');
                    }}
                    return response.json();
                }})
                .then(data => {{
                    const loading = document.getElementById('loading');
                    const container = document.getElementById('payslips-container');
                    const noPayslips = document.getElementById('no-payslips');
                    
                    loading.style.display = 'none';
                    
                    if (data.results && data.results.length > 0) {{
                        container.innerHTML = data.results.map(createPayslipHTML).join('');
                        container.style.display = 'block';
                    }} else {{
                        noPayslips.style.display = 'block';
                    }}
                }})
                .catch(error => {{
                    console.error('Error loading payslips:', error);
                    const loading = document.getElementById('loading');
                    const noPayslips = document.getElementById('no-payslips');
                    
                    loading.style.display = 'none';
                    noPayslips.innerHTML = `
                        <h3>Error Loading Payslips</h3>
                        <p>There was an error loading your payslips. Please try again later.</p>
                        <p>If the problem persists, please contact IT support.</p>
                    `;
                    noPayslips.style.display = 'block';
                }});
            }});
        </script>
    </body>
    </html>
    """
    return HttpResponse(html_content, content_type='text/html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_token_validity(request):
    """
    API endpoint to check if the current token is still valid.
    Returns user info and token expiration status.
    """
    try:
        from .models import TokenActivity
        
        user = request.user
        token = request.auth
        
        # Get token activity
        try:
            activity = TokenActivity.objects.get(token=token)
            is_expired = activity.is_expired
            time_remaining = None
            
            if not is_expired:
                timeout = getattr(settings, 'TOKEN_INACTIVITY_TIMEOUT', 180)
                elapsed = (timezone.now() - activity.last_activity).total_seconds()
                time_remaining = max(0, timeout - elapsed)
            
        except TokenActivity.DoesNotExist:
            # Create activity record if it doesn't exist
            activity = TokenActivity.objects.create(
                token=token,
                last_activity=timezone.now()
            )
            is_expired = False
            time_remaining = getattr(settings, 'TOKEN_INACTIVITY_TIMEOUT', 180)
        
        return Response({
            'valid': not is_expired,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'token_info': {
                'last_activity': activity.last_activity,
                'is_expired': is_expired,
                'time_remaining_seconds': int(time_remaining) if time_remaining is not None else None,
            }
        })
        
    except Exception as e:
        return Response({
            'valid': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token_activity(request):
    """
    API endpoint to refresh token activity (reset the inactivity timer).
    """
    try:
        from .models import TokenActivity
        
        token = request.auth
        activity, created = TokenActivity.objects.update_or_create(
            token=token,
            defaults={'last_activity': timezone.now()}
        )
        
        timeout = getattr(settings, 'TOKEN_INACTIVITY_TIMEOUT', 180)
        
        return Response({
            'success': True,
            'message': 'Token activity refreshed',
            'last_activity': activity.last_activity,
            'time_remaining_seconds': timeout
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


def debug_user_check(request):
    """
    Diagnostic endpoint to check if users exist and their status
    """
    from django.contrib.auth import get_user_model
    from django.http import JsonResponse
    
    User = get_user_model()
    
    try:
        # Check for specific email
        email = 'constantive@gmail.com'
        
        debug_info = {
            'total_users': User.objects.count(),
            'superusers': User.objects.filter(is_superuser=True).count(),
            'staff_users': User.objects.filter(is_staff=True).count(),
            'email_check': None,
            'all_emails': list(User.objects.values_list('email', flat=True)),
            'user_model_fields': [f.name for f in User._meta.get_fields()],
            'note': 'This User model uses EMAIL as primary identifier, not username'
        }
        
        # Check specific user
        try:
            user = User.objects.get(email=email)
            debug_info['email_check'] = {
                'exists': True,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
            }
        except User.DoesNotExist:
            debug_info['email_check'] = {
                'exists': False,
                'message': f'User with email {email} does not exist'
            }
        
        return JsonResponse(debug_info, json_dumps_params={'indent': 2})
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'type': type(e).__name__
        }, status=500)

def create_admin_user(request):
    """
    Manual endpoint to create admin user - for debugging deployment issues
    """
    from django.contrib.auth import get_user_model
    from django.http import JsonResponse
    from django.core.management import call_command
    from io import StringIO
    import sys
    
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests allowed"}, status=405)
    
    User = get_user_model()
    
    try:
        # Capture the output of the management command
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        # Call the management command
        call_command("create_admin")
        
        # Restore stdout and get the captured output
        sys.stdout = old_stdout
        command_output = captured_output.getvalue()
        
        # Get updated user stats
        result = {
            "success": True,
            "message": "Admin user creation completed",
            "command_output": command_output,
            "stats": {
                "total_users": User.objects.count(),
                "superusers": User.objects.filter(is_superuser=True).count(),
                "staff_users": User.objects.filter(is_staff=True).count(),
            }
        }
        
        # Check if our specific user was created
        try:
            user = User.objects.get(email="constantive@gmail.com")
            result["created_user"] = {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
            }
        except User.DoesNotExist:
            result["created_user"] = None
        
        return JsonResponse(result, json_dumps_params={"indent": 2})
        
    except Exception as e:
        # Restore stdout in case of error
        sys.stdout = old_stdout
        return JsonResponse({
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }, status=500)


def admin_trigger_page(request):
    """
    Serve the admin trigger page
    """
    from django.http import HttpResponse
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin User Creation Trigger</title>
    <style>
        body {
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .button {
            display: block;
            width: 100%;
            padding: 15px;
            background: #27ae60;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin: 10px 0;
            transition: background 0.3s ease;
        }
        .button:hover {
            background: #2ecc71;
        }
        .button.check {
            background: #3498db;
        }
        .button.check:hover {
            background: #2980b9;
        }
        #result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            white-space: pre-wrap;
            font-family: monospace;
            max-height: 400px;
            overflow-y: auto;
        }
        .success {
            background: #d5f4e6 !important;
            border-color: #27ae60 !important;
            color: #155724;
        }
        .error {
            background: #f8d7da !important;
            border-color: #e74c3c !important;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>?? Admin User Creation Trigger</h1>
        
        <button class="button check" onclick="checkUsers()">
            ?? Check Current Users
        </button>
        
        <button class="button" onclick="createAdmin()">
            ?? Create Admin User
        </button>
        
        <button class="button check" onclick="window.open('/admin/', '_blank')">
            ?? Open Admin Panel
        </button>
        
        <div id="result"></div>
    </div>

    <script>
        function showResult(data, isSuccess = true) {
            const resultDiv = document.getElementById("result");
            resultDiv.innerHTML = JSON.stringify(data, null, 2);
            resultDiv.className = isSuccess ? "success" : "error";
        }

        async function checkUsers() {
            try {
                const response = await fetch("/debug/users/");
                const data = await response.json();
                showResult(data, true);
            } catch (error) {
                showResult({error: error.message}, false);
            }
        }

        async function createAdmin() {
            try {
                document.getElementById("result").innerHTML = "Creating admin user...";
                
                const response = await fetch("/debug/create-admin/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    }
                });
                
                const data = await response.json();
                showResult(data, response.ok);
                
                if (response.ok && data.success) {
                    setTimeout(() => {
                        alert("? Admin user created! You can now login to /admin/ with:\\n\\nEmail: constantive@gmail.com\\nPassword: September@2025.com");
                    }, 1000);
                }
            } catch (error) {
                showResult({error: error.message}, false);
            }
        }

        // Auto-check users on page load
        window.onload = checkUsers;
    </script>
</body>
</html>"""
    
    return HttpResponse(html_content)


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_admin_user_no_csrf(request):
    """
    Manual endpoint to create admin user - CSRF exempt for external calls
    """
    from django.contrib.auth import get_user_model
    from django.http import JsonResponse
    from django.core.management import call_command
    from io import StringIO
    import sys
    
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests allowed"}, status=405)
    
    User = get_user_model()
    
    try:
        # Capture the output of the management command
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        # Call the management command
        call_command("create_admin")
        
        # Restore stdout and get the captured output
        sys.stdout = old_stdout
        command_output = captured_output.getvalue()
        
        # Get updated user stats
        result = {
            "success": True,
            "message": "Admin user creation completed",
            "command_output": command_output,
            "stats": {
                "total_users": User.objects.count(),
                "superusers": User.objects.filter(is_superuser=True).count(),
                "staff_users": User.objects.filter(is_staff=True).count(),
            }
        }
        
        # Check if our specific user was created
        try:
            user = User.objects.get(email="constantive@gmail.com")
            result["created_user"] = {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
            }
        except User.DoesNotExist:
            result["created_user"] = None
        
        return JsonResponse(result, json_dumps_params={"indent": 2})
        
    except Exception as e:
        # Restore stdout in case of error
        sys.stdout = old_stdout
        return JsonResponse({
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }, status=500)


# SECURITY: Disable dangerous debug endpoints in production
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test

def is_superuser_and_debug(user):
    """Only allow superusers in debug mode"""
    return user.is_authenticated and user.is_superuser and settings.DEBUG

@user_passes_test(is_superuser_and_debug)
def debug_user_check_secure(request):
    """
    SECURED: Diagnostic endpoint - requires superuser + debug mode
    """
    # Only accessible if DEBUG=True and user is superuser
    from django.contrib.auth import get_user_model
    from django.http import JsonResponse
    
    User = get_user_model()
    
    try:
        # Check for specific email
        email = "constantive@gmail.com"
        
        debug_info = {
            "total_users": User.objects.count(),
            "superusers": User.objects.filter(is_superuser=True).count(),
            "staff_users": User.objects.filter(is_staff=True).count(),
            "email_check": None,
            "warning": "This endpoint is only available in DEBUG mode to superusers",
            "note": "This User model uses EMAIL as primary identifier, not username"
        }
        
        # Check specific user
        try:
            user = User.objects.get(email=email)
            debug_info["email_check"] = {
                "exists": True,
                "email": user.email,
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
            }
        except User.DoesNotExist:
            debug_info["email_check"] = {
                "exists": False,
                "message": f"User with email {email} does not exist"
            }
        
        return JsonResponse(debug_info, json_dumps_params={"indent": 2})
        
    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "type": type(e).__name__
        }, status=500)


def create_admin_disabled(request):
    """
    SECURITY: Admin creation endpoints disabled in production
    """
    from django.http import JsonResponse
    
    return JsonResponse({
        "error": "SECURITY: Admin creation endpoints have been disabled for security reasons",
        "message": "Admin users should be created through Django management commands on the server",
        "contact": "Contact system administrator for admin account creation",
        "timestamp": "2025-10-02T17:40:00Z"
    }, status=403)


def react_frontend(request):
    """
    Serve the React frontend application
    """
    from django.http import HttpResponse
    from django.conf import settings
    import os
    
    try:
        # Path to the React build index.html
        frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend_build', 'index.html')
        
        with open(frontend_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return HttpResponse(html_content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse("""
        <html>
        <head><title>Frontend Not Available</title></head>
        <body>
            <h1>React Frontend Not Available</h1>
            <p>The React frontend build files are not found.</p>
            <p><a href="/">Return to Main Site</a></p>
        </body>
        </html>
        """, content_type='text/html')


def react_frontend_fixed(request):
    """
    Serve a responsive Employee Portal frontend
    """
    from django.http import HttpResponse
    from django.middleware.csrf import get_token
    from django.contrib.auth import authenticate, login
    from django.contrib import messages
    from django.shortcuts import redirect
    
    # Check if user is already authenticated and show dashboard
    if request.user.is_authenticated:
        # If user is already logged in, show the dashboard
        user = request.user
        user_name = user.first_name or user.email.split('@')[0] if user.email else 'Employee'
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Employee Dashboard - Kenya Payroll System</title>
            <style>
                * {{ 
                    margin: 0; 
                    padding: 0; 
                    box-sizing: border-box; 
                }}
                
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    background: #f8f9fa;
                    min-height: 100vh;
                    line-height: 1.6;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px 0;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                
                .header-content {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 0 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                
                .logo {{
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    font-size: 1.5em;
                    font-weight: bold;
                }}
                
                .user-info {{
                    display: flex;
                    align-items: center;
                    gap: 15px;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 30px 20px;
                }}
                
                .welcome-section {{
                    background: white;
                    padding: 30px;
                    border-radius: 15px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    margin-bottom: 30px;
                    text-align: center;
                }}
                
                .welcome-section h1 {{
                    color: #333;
                    margin-bottom: 10px;
                    font-size: 2.2em;
                }}
                
                .welcome-section p {{
                    color: #666;
                    font-size: 1.1em;
                }}
                
                .dashboard-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 25px;
                    margin-top: 30px;
                }}
                
                .dashboard-card {{
                    background: white;
                    padding: 25px;
                    border-radius: 15px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    cursor: pointer;
                }}
                
                .dashboard-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                }}
                
                .card-icon {{
                    font-size: 3em;
                    margin-bottom: 15px;
                    display: block;
                }}
                
                .card-title {{
                    font-size: 1.3em;
                    font-weight: 600;
                    color: #333;
                    margin-bottom: 10px;
                }}
                
                .card-description {{
                    color: #666;
                    font-size: 0.95em;
                    line-height: 1.5;
                }}
                
                .quick-stats {{
                    background: white;
                    padding: 25px;
                    border-radius: 15px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    margin-bottom: 30px;
                }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                }}
                
                .stat-item {{
                    text-align: center;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 10px;
                }}
                
                .stat-value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #667eea;
                    display: block;
                }}
                
                .stat-label {{
                    color: #666;
                    font-size: 0.9em;
                    margin-top: 5px;
                }}
                
                .logout-btn {{
                    background: #e74c3c;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 500;
                    transition: background 0.3s ease;
                }}
                
                .logout-btn:hover {{
                    background: #c0392b;
                }}
                
                .messages {{
                    margin-bottom: 20px;
                }}
                
                .message {{
                    padding: 12px 15px;
                    border-radius: 8px;
                    margin-bottom: 10px;
                    font-weight: 500;
                }}
                
                .message.success {{
                    background: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }}
                
                /* Mobile Responsiveness */
                @media (max-width: 768px) {{
                    .header-content {{
                        flex-direction: column;
                        gap: 15px;
                        text-align: center;
                    }}
                    
                    .container {{
                        padding: 20px 15px;
                    }}
                    
                    .welcome-section {{
                        padding: 20px;
                    }}
                    
                    .welcome-section h1 {{
                        font-size: 1.8em;
                    }}
                    
                    .dashboard-grid {{
                        grid-template-columns: 1fr;
                        gap: 20px;
                    }}
                    
                    .stats-grid {{
                        grid-template-columns: repeat(2, 1fr);
                    }}
                }}
            </style>
        </head>
        <body>
            <header class="header">
                <div class="header-content">
                    <div class="logo">
                        <span>🏢</span>
                        <span>Kenya Payroll System</span>
                    </div>
                    <div class="user-info">
                        <span>Welcome, {user_name}</span>
                        <form method="post" action="/logout/" style="display: inline;">
                            <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                            <button type="submit" class="logout-btn">Logout</button>
                        </form>
                    </div>
                </div>
            </header>
            
            <div class="container">
                <!-- Display messages -->
                <div class="messages">
                    {"".join([f'<div class="message {msg.tags}">{msg.message}</div>' for msg in messages.get_messages(request)])}
                </div>
                
                <div class="welcome-section">
                    <h1>Welcome to Your Employee Portal</h1>
                    <p>Access all your payroll information, manage your profile, and stay updated with company announcements.</p>
                </div>
                
                <div class="quick-stats">
                    <h2 style="margin-bottom: 20px; color: #333;">Quick Overview</h2>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-value">📄</span>
                            <div class="stat-label">Payslips Available</div>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">🏖️</span>
                            <div class="stat-label">Leave Balance</div>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">💰</span>
                            <div class="stat-label">Current Salary</div>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">📊</span>
                            <div class="stat-label">Tax Reports</div>
                        </div>
                    </div>
                </div>
                
                <div class="dashboard-grid">
                    <div class="dashboard-card" onclick="window.location.href='/my-payslips/'">
                        <span class="card-icon">📄</span>
                        <div class="card-title">My Payslips</div>
                        <div class="card-description">View and download your monthly payslips, P9 forms, and salary statements.</div>
                    </div>
                    
                    <div class="dashboard-card" onclick="alert('Feature coming soon! This will allow you to update your personal information.')">
                        <span class="card-icon">👤</span>
                        <div class="card-title">My Profile</div>
                        <div class="card-description">Update your personal information, contact details, and employment information.</div>
                    </div>
                    
                    <div class="dashboard-card" onclick="alert('Feature coming soon! This will allow you to submit and track leave requests.')">
                        <span class="card-icon">🏖️</span>
                        <div class="card-title">Leave Requests</div>
                        <div class="card-description">Submit leave applications, check your leave balance, and view leave history.</div>
                    </div>
                    
                    <div class="dashboard-card" onclick="alert('Feature coming soon! This will show detailed salary breakdown.')">
                        <span class="card-icon">💰</span>
                        <div class="card-title">Salary Details</div>
                        <div class="card-description">View detailed breakdown of your salary, allowances, and deductions.</div>
                    </div>
                    
                    <div class="dashboard-card" onclick="alert('Feature coming soon! This will provide access to tax documents.')">
                        <span class="card-icon">📊</span>
                        <div class="card-title">Tax Reports</div>
                        <div class="card-description">Access your P9 forms, tax certificates, and annual tax reports.</div>
                    </div>
                    
                    <div class="dashboard-card" onclick="alert('Feature coming soon! This will connect you with HR support.')">
                        <span class="card-icon">📞</span>
                        <div class="card-title">Support</div>
                        <div class="card-description">Get help, contact HR, or report issues with your payroll information.</div>
                    </div>
                </div>
            </div>
            
            <script>
                console.log('🏢 Employee Dashboard Loaded');
                console.log('👤 User: {user_name}');
                console.log('🎯 Dashboard features ready');
            </script>
        </body>
        </html>
        """
        
        return HttpResponse(html_content, content_type='text/html')
    
    # Handle login form submission for anonymous users
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            # Authenticate user with email
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Determine redirect based on user type
                    if user.is_staff or user.is_superuser:
                        messages.success(request, f'Welcome back, {user.first_name or user.email}! Redirecting to admin area.')
                        return redirect('/')
                    else:
                        messages.success(request, f'Welcome back, {user.first_name or user.email}! Taking you to your dashboard.')
                        return redirect('/employee/')  # This will now show the dashboard
                else:
                    messages.error(request, 'Your account is inactive. Please contact your administrator.')
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
        else:
            messages.error(request, 'Please enter both email and password.')
    
    # Create a fully responsive Employee Portal
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Employee Portal - Kenya Payroll System</title>
        <style>
            /* Reset and base styles */
            * {{ 
                margin: 0; 
                padding: 0; 
                box-sizing: border-box; 
            }}
            
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
                line-height: 1.6;
            }}
            
            .container {{
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
                width: 100%;
                max-width: 500px;
                animation: slideUp 0.6s ease-out;
            }}
            
            @keyframes slideUp {{
                from {{
                    opacity: 0;
                    transform: translateY(30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .logo {{
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                margin: 0 auto 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2.5em;
                color: white;
            }}
            
            h1 {{ 
                color: #333; 
                margin-bottom: 10px; 
                font-size: 2.2em;
                font-weight: 700;
            }}
            
            .subtitle {{ 
                color: #666; 
                margin-bottom: 30px; 
                font-size: 1.1em;
                font-weight: 300;
            }}
            
            .messages {{
                margin-bottom: 20px;
            }}
            
            .message {{
                padding: 12px 15px;
                border-radius: 8px;
                margin-bottom: 10px;
                font-weight: 500;
            }}
            
            .message.success {{
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}
            
            .message.error {{
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }}
            
            .login-form {{ 
                margin-top: 30px; 
            }}
            
            .form-group {{ 
                margin-bottom: 20px; 
                text-align: left; 
            }}
            
            label {{ 
                display: block; 
                margin-bottom: 8px; 
                color: #333; 
                font-weight: 500;
                font-size: 0.95em;
            }}
            
            input[type="email"], input[type="password"] {{
                width: 100%;
                padding: 16px;
                border: 2px solid #e1e5e9;
                border-radius: 12px;
                font-size: 16px;
                transition: all 0.3s ease;
                background: #fafafa;
            }}
            
            input[type="email"]:focus, input[type="password"]:focus {{
                outline: none;
                border-color: #667eea;
                background: white;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }}
            
            .login-btn {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 16px 30px;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                width: 100%;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .login-btn:hover {{ 
                transform: translateY(-2px); 
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            }}
            
            .login-btn:active {{
                transform: translateY(0);
            }}
            
            .links {{ 
                margin-top: 25px; 
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .links a {{ 
                color: #667eea; 
                text-decoration: none; 
                font-weight: 500;
                font-size: 0.9em;
                transition: color 0.3s ease;
            }}
            
            .links a:hover {{ 
                color: #764ba2;
                text-decoration: underline; 
            }}
            
            .features {{
                margin-top: 30px;
                text-align: left;
            }}
            
            .features h3 {{
                color: #333;
                margin-bottom: 15px;
                font-size: 1.1em;
                text-align: center;
            }}
            
            .feature-list {{
                list-style: none;
                padding: 0;
            }}
            
            .feature-list li {{
                padding: 8px 0;
                color: #666;
                font-size: 0.9em;
                display: flex;
                align-items: center;
            }}
            
            .feature-list li:before {{
                content: "✓";
                color: #27ae60;
                font-weight: bold;
                margin-right: 10px;
                width: 20px;
            }}
            
            /* Mobile Responsiveness */
            @media (max-width: 768px) {{
                body {{
                    padding: 15px;
                }}
                
                .container {{
                    padding: 30px 25px;
                    border-radius: 15px;
                }}
                
                h1 {{
                    font-size: 1.8em;
                }}
                
                .subtitle {{
                    font-size: 1em;
                }}
                
                input[type="email"], input[type="password"] {{
                    padding: 14px;
                    font-size: 16px; /* Prevents zoom on iOS */
                }}
                
                .login-btn {{
                    padding: 14px 25px;
                    font-size: 15px;
                }}
                
                .links {{
                    flex-direction: column;
                    gap: 15px;
                }}
            }}
            
            /* Small Mobile */
            @media (max-width: 480px) {{
                .container {{
                    padding: 25px 20px;
                }}
                
                .logo {{
                    width: 60px;
                    height: 60px;
                    font-size: 2em;
                }}
                
                h1 {{
                    font-size: 1.6em;
                }}
                
                .features {{
                    margin-top: 20px;
                }}
            }}
            
            /* Large screens */
            @media (min-width: 1200px) {{
                .container {{
                    max-width: 600px;
                    padding: 50px;
                }}
                
                h1 {{
                    font-size: 2.5em;
                }}
            }}
            
            /* Dark mode support */
            @media (prefers-color-scheme: dark) {{
                .container {{
                    background: #1a1a1a;
                    color: #e0e0e0;
                }}
                
                h1, .features h3 {{
                    color: #ffffff;
                }}
                
                .subtitle {{
                    color: #b0b0b0;
                }}
                
                label {{
                    color: #e0e0e0;
                }}
                
                input[type="email"], input[type="password"] {{
                    background: #2a2a2a;
                    border-color: #444;
                    color: #e0e0e0;
                }}
                
                input[type="email"]:focus, input[type="password"]:focus {{
                    background: #333;
                    border-color: #667eea;
                }}
                
                .feature-list li {{
                    color: #b0b0b0;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🏢</div>
            <h1>Employee Portal</h1>
            <p class="subtitle">Kenya Payroll System</p>

            <!-- Display messages -->
            <div class="messages">
                {"".join([f'<div class="message {msg.tags}">{msg.message}</div>' for msg in messages.get_messages(request)])}
            </div>

            <div class="login-form">
                <form method="post" id="loginForm">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">

                    <div class="form-group">
                        <label for="email">Email Address</label>
                        <input type="email" id="email" name="email" required 
                               placeholder="your.email@company.com"
                               autocomplete="email">
                    </div>

                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required 
                               placeholder="Enter your password"
                               autocomplete="current-password">
                    </div>

                    <button type="submit" class="login-btn">
                        🔐 Login to Portal
                    </button>
                </form>
            </div>

            <div class="features">
                <h3>Access Your:</h3>
                <ul class="feature-list">
                    <li>Monthly Payslips & P9 Forms</li>
                    <li>Leave Requests & Balances</li>
                    <li>Employee Profile & Documents</li>
                    <li>Overtime & Allowances</li>
                    <li>Tax Calculations & Reports</li>
                </ul>
            </div>

            <div class="links">
                <a href="/">← Back to Home</a>
                <a href="/admin-staff/">Staff Login</a>
            </div>
        </div>

        <script>
            // Enhanced form handling with loading states
            document.addEventListener('DOMContentLoaded', function() {{
                const form = document.getElementById('loginForm');
                const submitBtn = form.querySelector('.login-btn');
                const originalBtnText = submitBtn.textContent;
                
                form.addEventListener('submit', function(e) {{
                    // Show loading state
                    submitBtn.textContent = '🔄 Logging in...';
                    submitBtn.style.opacity = '0.7';
                    submitBtn.disabled = true;
                    
                    // Re-enable after timeout to prevent permanent disable
                    setTimeout(() => {{
                        submitBtn.textContent = originalBtnText;
                        submitBtn.style.opacity = '1';
                        submitBtn.disabled = false;
                    }}, 5000);
                }});
                
                // Auto-focus email field on desktop
                if (window.innerWidth > 768) {{
                    document.getElementById('email').focus();
                }}
                
                // Add visual feedback for form validation
                const inputs = form.querySelectorAll('input[required]');
                inputs.forEach(input => {{
                    input.addEventListener('invalid', function() {{
                        this.style.borderColor = '#e74c3c';
                        this.style.backgroundColor = '#ffebee';
                    }});
                    
                    input.addEventListener('input', function() {{
                        if (this.validity.valid) {{
                            this.style.borderColor = '#27ae60';
                            this.style.backgroundColor = '#e8f5e8';
                        }} else {{
                            this.style.borderColor = '#e1e5e9';
                            this.style.backgroundColor = '#fafafa';
                        }}
                    }});
                }});
            }});
            
            // Add responsive behavior
            function updateLayout() {{
                const container = document.querySelector('.container');
                if (window.innerHeight < 600) {{
                    container.style.margin = '10px auto';
                }}
            }}
            
            window.addEventListener('resize', updateLayout);
            updateLayout();
            
            console.log('🏢 Employee Portal Loaded');
            console.log('📱 Responsive design active');
            console.log('🎨 Device width:', window.innerWidth + 'px');
        </script>
    </body>
    </html>
    """
    
    return HttpResponse(html_content, content_type='text/html')
