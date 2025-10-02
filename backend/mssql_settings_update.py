# Modified settings.py section for Microsoft SQL Server support
# This shows how to update the DATABASES configuration

"""
UPDATED DATABASES CONFIGURATION FOR MSSQL SUPPORT
Replace the existing DATABASES section in settings.py with this:
"""

import os
import dj_database_url

# Database Configuration with MSSQL Support
if 'DATABASE_URL' in os.environ:
    # Check if it's an MSSQL connection string
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('mssql://'):
        # Parse MSSQL connection string
        DATABASES = {
            'default': dj_database_url.parse(database_url, conn_max_age=600)
        }
        # Override engine for MSSQL
        DATABASES['default']['ENGINE'] = 'mssql'
        DATABASES['default']['OPTIONS'] = {
            'driver': 'ODBC Driver 17 for SQL Server',
            'MARS_Connection': True,
            'extra_params': 'TrustServerCertificate=yes'
        }
    else:
        # PostgreSQL or other database
        DATABASES = {
            'default': dj_database_url.parse(database_url)
        }
elif os.environ.get('USE_MSSQL'):
    # Use Microsoft SQL Server
    DATABASES = {
        'default': {
            'ENGINE': 'mssql',
            'NAME': os.environ.get('MSSQL_DB_NAME', 'kenyan_payroll_system_db'),
            'USER': os.environ.get('MSSQL_DB_USER', 'sa'),
            'PASSWORD': os.environ.get('MSSQL_DB_PASSWORD', ''),
            'HOST': os.environ.get('MSSQL_DB_HOST', 'localhost'),
            'PORT': os.environ.get('MSSQL_DB_PORT', '1433'),
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
                'MARS_Connection': True,
                'charset': 'utf-8',
                'autocommit': True,
                'extra_params': 'TrustServerCertificate=yes'
            }
        }
    }
elif os.environ.get('RAILWAY_ENVIRONMENT'):
    # Railway build environment - use SQLite temporarily
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
else:
    # Development database (try PostgreSQL first, then MSSQL, then SQLite fallback)
    try:
        # Try PostgreSQL first (existing configuration)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'kenyan_payroll_system_db',
                'USER': 'postgres',
                'PASSWORD': 'September@2025',
                'HOST': 'localhost',
                'PORT': '5432',
            }
        }
    except Exception:
        try:
            # Try Microsoft SQL Server as fallback
            DATABASES = {
                'default': {
                    'ENGINE': 'mssql',
                    'NAME': 'kenyan_payroll_system_db',
                    'USER': 'sa',  # or your MSSQL username
                    'PASSWORD': 'YourMSSQLPassword',
                    'HOST': 'localhost',
                    'PORT': '1433',
                    'OPTIONS': {
                        'driver': 'ODBC Driver 17 for SQL Server',
                        'MARS_Connection': True,
                        'extra_params': 'TrustServerCertificate=yes'
                    }
                }
            }
        except Exception:
            # Final fallback to SQLite
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': BASE_DIR / 'db.sqlite3',
                }
            }