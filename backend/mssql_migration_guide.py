#!/usr/bin/env python3
"""
Microsoft SQL Server Configuration for Kenyan Payroll System
Shows how to modify settings.py to support MSSQL
"""

# Database configuration options for Microsoft SQL Server
MSSQL_DATABASE_CONFIGURATION = '''
# Microsoft SQL Server Database Configuration Options

import os
import dj_database_url

# Option 1: Direct MSSQL Configuration
MSSQL_DIRECT_CONFIG = {
    'default': {
        'ENGINE': 'mssql',  # django-mssql-backend
        'NAME': 'kenyan_payroll_system_db',
        'USER': 'your_mssql_username',
        'PASSWORD': 'your_mssql_password',
        'HOST': 'localhost',  # or your SQL Server instance
        'PORT': '1433',       # default MSSQL port
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'MARS_Connection': True,  # Multiple Active Result Sets
            'charset': 'utf-8',
            'autocommit': True,
            'extra_params': 'TrustServerCertificate=yes'  # For dev environments
        }
    }
}

# Option 2: Using django-pyodbc-azure (Alternative)
MSSQL_PYODBC_CONFIG = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'kenyan_payroll_system_db',
        'USER': 'your_mssql_username',
        'PASSWORD': 'your_mssql_password',
        'HOST': 'localhost',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'MARS_Connection': True,
        }
    }
}

# Option 3: Connection String Approach
MSSQL_CONNECTION_STRING = "mssql://username:password@server:1433/database_name"

# Azure SQL Database Configuration
AZURE_SQL_CONFIG = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'kenyan_payroll_system_db',
        'USER': 'your_azure_username',
        'PASSWORD': 'your_azure_password',
        'HOST': 'your-server.database.windows.net',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'MARS_Connection': True,
            'encrypt': True,
            'trustServerCertificate': False,
        }
    }
}
'''

def show_mssql_migration_guide():
    """Show comprehensive guide for migrating to MSSQL"""
    print("MICROSOFT SQL SERVER MIGRATION GUIDE")
    print("=" * 60)
    
    print("🔄 MIGRATION PROCESS:")
    print("1. Install MSSQL dependencies")
    print("2. Install Microsoft ODBC Driver")
    print("3. Update Django settings")
    print("4. Create new MSSQL database")
    print("5. Run migrations")
    print("6. Migrate data (optional)")
    
    print(f"\n📦 REQUIRED PACKAGES:")
    print("• django-mssql-backend (recommended)")
    print("• Microsoft ODBC Driver 17 for SQL Server")
    print("• pyodbc (automatically installed)")
    
    print(f"\n🗄️ MSSQL SETUP REQUIREMENTS:")
    print("• Microsoft SQL Server 2016+ or Azure SQL Database")
    print("• SQL Server Management Studio (SSMS) - optional")
    print("• Appropriate user permissions (db_owner recommended)")
    
    print(f"\n⚙️ CONFIGURATION OPTIONS:")
    print("• Option 1: django-mssql-backend (easiest)")
    print("• Option 2: django-pyodbc-azure (alternative)")
    print("• Option 3: Connection string approach")
    print("• Option 4: Azure SQL Database")
    
    print(f"\n🔧 WINDOWS AUTHENTICATION:")
    print("For Windows Authentication, use:")
    print("'USER': '',  # Empty for Windows Auth")
    print("'PASSWORD': '',  # Empty for Windows Auth")
    print("'OPTIONS': {'Trusted_Connection': 'yes'}")
    
    print(f"\n📋 MIGRATION COMMANDS:")
    print("1. pip install django-mssql-backend")
    print("2. python manage.py makemigrations")
    print("3. python manage.py migrate")
    print("4. python manage.py createsuperuser")
    
    print(f"\n⚠️ IMPORTANT CONSIDERATIONS:")
    print("• MSSQL has different field length limits")
    print("• Some PostgreSQL-specific features may need adjustment")
    print("• Date/time handling differences")
    print("• Case sensitivity differences")
    
    print(f"\n💾 DATA MIGRATION OPTIONS:")
    print("• Fresh start: Create new database, recreate data")
    print("• Data dump: Export PostgreSQL data, import to MSSQL")
    print("• Django fixtures: Use dumpdata/loaddata commands")
    print("• Custom migration scripts")

if __name__ == '__main__':
    show_mssql_migration_guide()
    print(f"\n{MSSQL_DATABASE_CONFIGURATION}")