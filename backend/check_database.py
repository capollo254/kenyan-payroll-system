#!/usr/bin/env python3

import os
import sys
import django
from django.conf import settings

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

def check_database_configuration():
    """Check the current database configuration"""
    print("PAYROLL SYSTEM DATABASE CONFIGURATION")
    print("=" * 50)
    
    # Get database settings
    db_config = settings.DATABASES['default']
    
    print(f"🗄️  DATABASE ENGINE: {db_config['ENGINE']}")
    
    if 'postgresql' in db_config['ENGINE']:
        print(f"📊 DATABASE TYPE: PostgreSQL")
        print(f"🏷️  DATABASE NAME: {db_config.get('NAME', 'Not specified')}")
        print(f"👤 DATABASE USER: {db_config.get('USER', 'Not specified')}")
        print(f"🏠 DATABASE HOST: {db_config.get('HOST', 'Not specified')}")
        print(f"🔌 DATABASE PORT: {db_config.get('PORT', 'Not specified')}")
    elif 'sqlite3' in db_config['ENGINE']:
        print(f"📊 DATABASE TYPE: SQLite")
        print(f"📁 DATABASE FILE: {db_config.get('NAME', 'Not specified')}")
    else:
        print(f"📊 DATABASE TYPE: {db_config['ENGINE']}")
    
    # Check environment variables
    print(f"\n🔧 ENVIRONMENT CONFIGURATION:")
    print(f"   DATABASE_URL exists: {'Yes' if os.environ.get('DATABASE_URL') else 'No'}")
    print(f"   RAILWAY_ENVIRONMENT: {'Yes' if os.environ.get('RAILWAY_ENVIRONMENT') else 'No'}")
    
    # Test database connection
    print(f"\n🔗 DATABASE CONNECTION TEST:")
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result:
            print(f"   ✅ Connection: SUCCESS")
            
            # Try to get database name from connection
            try:
                db_name = connection.get_connection_params().get('database')
                if not db_name:
                    db_name = connection.settings_dict.get('NAME')
                print(f"   📋 Connected Database: {db_name}")
            except:
                print(f"   📋 Connected Database: {db_config.get('NAME', 'Unknown')}")
                
        else:
            print(f"   ❌ Connection: FAILED")
    except Exception as e:
        print(f"   ❌ Connection Error: {str(e)}")
    
    # Check for common database files
    print(f"\n📁 DATABASE FILES CHECK:")
    
    # Check for SQLite
    sqlite_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    if os.path.exists(sqlite_path):
        size = os.path.getsize(sqlite_path) / 1024  # KB
        print(f"   📄 SQLite file: EXISTS (Size: {size:.1f} KB)")
    else:
        print(f"   📄 SQLite file: NOT FOUND")
    
    print(f"\n" + "=" * 50)
    
    # Summary
    if 'postgresql' in db_config['ENGINE']:
        print(f"🎯 SUMMARY: Running on PostgreSQL Database")
        print(f"   Database Name: {db_config.get('NAME', 'kenyan_payroll_system_db')}")
        print(f"   Location: {db_config.get('HOST', 'localhost')}:{db_config.get('PORT', '5432')}")
    elif 'sqlite3' in db_config['ENGINE']:
        print(f"🎯 SUMMARY: Running on SQLite Database")
        print(f"   Database File: {db_config.get('NAME', 'db.sqlite3')}")
    
    return db_config

if __name__ == '__main__':
    check_database_configuration()