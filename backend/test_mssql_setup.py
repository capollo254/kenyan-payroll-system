#!/usr/bin/env python3
"""
Microsoft SQL Server Connection Test Script
Tests MSSQL connectivity and configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def test_odbc_driver():
    """Test if ODBC Driver is installed"""
    print("🔧 Testing ODBC Driver Installation...")
    
    try:
        import pyodbc
        drivers = pyodbc.drivers()
        
        # Look for SQL Server drivers
        sql_drivers = [d for d in drivers if 'SQL Server' in d]
        
        if sql_drivers:
            print(f"   ✅ Found ODBC drivers: {sql_drivers}")
            return True
        else:
            print("   ❌ No SQL Server ODBC drivers found")
            print("   💡 Install 'ODBC Driver 17 for SQL Server'")
            return False
            
    except ImportError:
        print("   ❌ pyodbc not installed")
        return False

def test_mssql_package():
    """Test django-mssql-backend installation"""
    print("📦 Testing django-mssql-backend...")
    
    try:
        import mssql
        print("   ✅ django-mssql-backend is installed")
        return True
    except ImportError:
        print("   ❌ django-mssql-backend not installed")
        print("   💡 Run: pip install django-mssql-backend")
        return False

def test_mssql_connection():
    """Test direct MSSQL connection"""
    print("🔗 Testing Direct MSSQL Connection...")
    
    try:
        import pyodbc
        
        # Test connection parameters
        server = 'localhost'
        database = 'master'  # Use master database for initial test
        username = 'sa'
        password = input("Enter MSSQL password for 'sa' user (or press Enter for Windows Auth): ")
        
        if password:
            # SQL Server authentication
            connection_string = f'''
                DRIVER={{ODBC Driver 17 for SQL Server}};
                SERVER={server};
                DATABASE={database};
                UID={username};
                PWD={password};
                TrustServerCertificate=yes;
            '''
        else:
            # Windows authentication
            connection_string = f'''
                DRIVER={{ODBC Driver 17 for SQL Server}};
                SERVER={server};
                DATABASE={database};
                Trusted_Connection=yes;
            '''
        
        # Attempt connection
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()
        
        print(f"   ✅ Connected to SQL Server")
        print(f"   📊 Version: {version[0][:50]}...")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        return False

def test_django_mssql_setup():
    """Test Django with MSSQL configuration"""
    print("⚙️ Testing Django MSSQL Configuration...")
    
    # Create a temporary settings test
    test_settings = """
import os
import sys

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'master',
        'USER': 'sa',
        'PASSWORD': os.environ.get('MSSQL_PASSWORD', ''),
        'HOST': 'localhost',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'MARS_Connection': True,
            'extra_params': 'TrustServerCertificate=yes'
        }
    }
}

# Test the configuration
from django.conf import settings
if not settings.configured:
    settings.configure(DATABASES=DATABASES, INSTALLED_APPS=['django.contrib.contenttypes'])

import django
django.setup()

from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT 1")
result = cursor.fetchone()
print(f"Django MSSQL test result: {result}")
"""
    
    try:
        # Write test file
        test_file = Path('test_django_mssql.py')
        test_file.write_text(test_settings)
        
        # Run test
        env = os.environ.copy()
        if 'MSSQL_PASSWORD' not in env:
            password = input("Enter MSSQL password for Django test: ")
            env['MSSQL_PASSWORD'] = password
        
        result = subprocess.run([
            sys.executable, 'test_django_mssql.py'
        ], capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print("   ✅ Django MSSQL configuration working")
            print(f"   📊 Output: {result.stdout.strip()}")
            success = True
        else:
            print("   ❌ Django MSSQL configuration failed")
            print(f"   📊 Error: {result.stderr}")
            success = False
            
        # Cleanup
        test_file.unlink(missing_ok=True)
        return success
        
    except Exception as e:
        print(f"   ❌ Test setup failed: {str(e)}")
        return False

def show_installation_instructions():
    """Show installation instructions for required components"""
    print("\n📋 MSSQL SETUP INSTRUCTIONS:")
    print("=" * 40)
    
    print("1️⃣ Install Microsoft SQL Server:")
    print("   • SQL Server 2019 Express (free)")
    print("   • SQL Server Developer Edition (free)")
    print("   • Or use Azure SQL Database")
    
    print("\n2️⃣ Install ODBC Driver:")
    print("   • Download: ODBC Driver 17 for SQL Server")
    print("   • URL: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
    
    print("\n3️⃣ Install Python packages:")
    print("   pip install django-mssql-backend pyodbc")
    
    print("\n4️⃣ Configure SQL Server:")
    print("   • Enable TCP/IP protocol")
    print("   • Set static port 1433")
    print("   • Enable SQL Server authentication")
    print("   • Create database user with appropriate permissions")
    
    print("\n5️⃣ Configure Django:")
    print("   • Update settings.py with MSSQL configuration")
    print("   • Update .env file with MSSQL credentials")
    print("   • Run migrations: python manage.py migrate")

def main():
    """Main testing function"""
    print("MICROSOFT SQL SERVER CONNECTIVITY TEST")
    print("=" * 50)
    
    tests = [
        ("ODBC Driver", test_odbc_driver),
        ("django-mssql-backend Package", test_mssql_package),
        ("Direct MSSQL Connection", test_mssql_connection),
        ("Django MSSQL Setup", test_django_mssql_setup),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test error: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for MSSQL migration")
    else:
        print("⚠️ Some tests failed. Check configuration before migration.")
        show_installation_instructions()

if __name__ == '__main__':
    main()