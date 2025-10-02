#!/usr/bin/env python3
"""
Database Migration Script: PostgreSQL to Microsoft SQL Server
This script helps migrate the Kenyan Payroll System database
"""

import os
import sys
import subprocess
from pathlib import Path

def install_mssql_dependencies():
    """Install required packages for MSSQL support"""
    print("📦 Installing MSSQL Dependencies...")
    
    packages = [
        'django-mssql-backend>=2.8.1',
        'pyodbc>=4.0.30'
    ]
    
    for package in packages:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                          check=True, capture_output=True)
            print(f"   ✅ Installed: {package}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            return False
    
    return True

def backup_current_database():
    """Create a backup of current PostgreSQL data"""
    print("💾 Creating Database Backup...")
    
    try:
        # Export data using Django's dumpdata command
        subprocess.run([
            sys.executable, 'manage.py', 'dumpdata', 
            '--exclude=contenttypes', '--exclude=auth.Permission',
            '--output=postgresql_backup.json'
        ], check=True)
        print("   ✅ PostgreSQL data exported to postgresql_backup.json")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to backup database: {e}")
        return False

def update_environment_config():
    """Update environment configuration for MSSQL"""
    print("⚙️ Updating Environment Configuration...")
    
    # Read current .env file
    env_file = Path('.env')
    if not env_file.exists():
        print("   ❌ .env file not found")
        return False
    
    # Create backup of current .env
    env_backup = Path('.env.postgresql.backup')
    env_file.rename(env_backup)
    print(f"   ✅ Backed up .env to {env_backup}")
    
    # Copy MSSQL configuration
    mssql_env = Path('.env.mssql')
    if mssql_env.exists():
        mssql_env.rename(env_file)
        print("   ✅ Applied MSSQL environment configuration")
        return True
    else:
        print("   ❌ MSSQL environment file (.env.mssql) not found")
        return False

def run_migrations():
    """Run Django migrations for MSSQL"""
    print("🔄 Running Database Migrations...")
    
    try:
        # Make migrations
        subprocess.run([sys.executable, 'manage.py', 'makemigrations'], check=True)
        print("   ✅ Created migrations")
        
        # Apply migrations
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("   ✅ Applied migrations to MSSQL")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Migration failed: {e}")
        return False

def load_data_backup():
    """Load PostgreSQL data into MSSQL"""
    print("📥 Loading Data Backup...")
    
    backup_file = Path('postgresql_backup.json')
    if not backup_file.exists():
        print("   ⚠️ No backup file found. Starting with fresh database.")
        return True
    
    try:
        subprocess.run([
            sys.executable, 'manage.py', 'loaddata', 
            'postgresql_backup.json'
        ], check=True)
        print("   ✅ Data loaded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to load data: {e}")
        print("   💡 You may need to create a superuser manually")
        return False

def create_superuser():
    """Prompt to create a new superuser"""
    print("👤 Creating Superuser...")
    
    try:
        subprocess.run([sys.executable, 'manage.py', 'createsuperuser'], check=True)
        print("   ✅ Superuser created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️ Superuser creation skipped: {e}")
        return True

def test_mssql_connection():
    """Test the MSSQL database connection"""
    print("🔗 Testing MSSQL Connection...")
    
    try:
        result = subprocess.run([
            sys.executable, '-c',
            """
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1')
print('Connection successful!')
"""
        ], capture_output=True, text=True, check=True)
        
        print("   ✅ MSSQL connection successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ MSSQL connection failed: {e}")
        print(f"   Error output: {e.stderr}")
        return False

def main():
    """Main migration process"""
    print("POSTGRESQL TO MSSQL MIGRATION")
    print("=" * 50)
    print("This script will migrate your payroll system from PostgreSQL to MSSQL")
    print("Make sure you have:")
    print("• Microsoft SQL Server installed and running")
    print("• ODBC Driver 17 for SQL Server installed")
    print("• Appropriate database permissions")
    print("• Updated .env.mssql with your MSSQL credentials")
    
    response = input("\nDo you want to continue? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    # Change to backend directory
    if not Path('manage.py').exists():
        print("Please run this script from the Django backend directory")
        return
    
    steps = [
        ("Install MSSQL Dependencies", install_mssql_dependencies),
        ("Backup Current Database", backup_current_database),
        ("Update Environment Config", update_environment_config),
        ("Run Migrations", run_migrations),
        ("Load Data Backup", load_data_backup),
        ("Create Superuser", create_superuser),
        ("Test MSSQL Connection", test_mssql_connection),
    ]
    
    for step_name, step_function in steps:
        print(f"\n{step_name}...")
        if not step_function():
            print(f"❌ Migration failed at: {step_name}")
            return
    
    print("\n" + "=" * 50)
    print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
    print("✅ Your payroll system is now running on Microsoft SQL Server")
    print("📝 Next steps:")
    print("   • Test all functionality")
    print("   • Update any deployment configurations")
    print("   • Consider backing up the MSSQL database")

if __name__ == '__main__':
    main()