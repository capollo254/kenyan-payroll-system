-- =====================================================
-- CREATE KENYAN PAYROLL DATABASE ON SQL SERVER
-- Script to create and configure database for Django
-- =====================================================

USE master;
GO

-- Create the database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'kenyan_payroll_system_db')
BEGIN
    CREATE DATABASE [kenyan_payroll_system_db]
    ON 
    ( NAME = 'KenyanPayroll_Data',
      FILENAME = 'C:\Program Files\Microsoft SQL Server\MSSQL15.MSSQLSERVER\MSSQL\DATA\kenyan_payroll_system_db.mdf',
      SIZE = 500MB,
      MAXSIZE = 10GB,
      FILEGROWTH = 50MB )
    LOG ON 
    ( NAME = 'KenyanPayroll_Log',
      FILENAME = 'C:\Program Files\Microsoft SQL Server\MSSQL15.MSSQLSERVER\MSSQL\DATA\kenyan_payroll_system_db.ldf',
      SIZE = 50MB,
      MAXSIZE = 1GB,
      FILEGROWTH = 10MB );
    
    PRINT 'Database created successfully!';
END
ELSE
BEGIN
    PRINT 'Database already exists.';
END
GO

-- Switch to the new database
USE [kenyan_payroll_system_db];
GO

-- Create Django user for the application
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'django_payroll_user')
BEGIN
    CREATE LOGIN [django_payroll_user] WITH PASSWORD = 'DjangoPay2024!@#';
    PRINT 'Login created successfully!';
END
ELSE
BEGIN
    PRINT 'Login already exists.';
END
GO

-- Create user in the database
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'django_payroll_user')
BEGIN
    CREATE USER [django_payroll_user] FOR LOGIN [django_payroll_user];
    PRINT 'Database user created successfully!';
END
ELSE
BEGIN
    PRINT 'Database user already exists.';
END
GO

-- Grant permissions to Django user
ALTER ROLE [db_owner] ADD MEMBER [django_payroll_user];
GO

-- Alternative minimal permissions (more secure)
-- GRANT CREATE TABLE TO [django_payroll_user];
-- GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::[dbo] TO [django_payroll_user];
-- GRANT ALTER ON SCHEMA::[dbo] TO [django_payroll_user];

PRINT 'Permissions granted successfully!';
GO

-- Create schemas for Django apps if needed
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'employees')
BEGIN
    CREATE SCHEMA [employees];
    PRINT 'Employees schema created.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'payroll')
BEGIN
    CREATE SCHEMA [payroll];
    PRINT 'Payroll schema created.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'reports')
BEGIN
    CREATE SCHEMA [reports];
    PRINT 'Reports schema created.';
END
GO

-- Enable case-insensitive collation for Django compatibility
-- (Django expects case-insensitive string comparisons)
ALTER DATABASE [kenyan_payroll_system_db] 
COLLATE SQL_Latin1_General_CP1_CI_AS;
GO

-- Set database options for Django compatibility
ALTER DATABASE [kenyan_payroll_system_db] SET ANSI_NULL_DEFAULT OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET ANSI_NULLS OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET ANSI_PADDING OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET ANSI_WARNINGS OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET ARITHABORT OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET AUTO_CLOSE OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET AUTO_CREATE_STATISTICS ON;
ALTER DATABASE [kenyan_payroll_system_db] SET AUTO_SHRINK OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET AUTO_UPDATE_STATISTICS ON;
ALTER DATABASE [kenyan_payroll_system_db] SET CURSOR_CLOSE_ON_COMMIT OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET CURSOR_DEFAULT GLOBAL;
ALTER DATABASE [kenyan_payroll_system_db] SET CONCAT_NULL_YIELDS_NULL OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET NUMERIC_ROUNDABORT OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET QUOTED_IDENTIFIER OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET RECURSIVE_TRIGGERS OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET ENABLE_BROKER;
ALTER DATABASE [kenyan_payroll_system_db] SET AUTO_UPDATE_STATISTICS_ASYNC OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET DATE_CORRELATION_OPTIMIZATION OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET TRUSTWORTHY OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET ALLOW_SNAPSHOT_ISOLATION OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET PARAMETERIZATION SIMPLE;
ALTER DATABASE [kenyan_payroll_system_db] SET READ_COMMITTED_SNAPSHOT OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET HONOR_BROKER_PRIORITY OFF;
ALTER DATABASE [kenyan_payroll_system_db] SET RECOVERY FULL;
ALTER DATABASE [kenyan_payroll_system_db] SET MULTI_USER;
ALTER DATABASE [kenyan_payroll_system_db] SET PAGE_VERIFY CHECKSUM;
ALTER DATABASE [kenyan_payroll_system_db] SET DB_CHAINING OFF;
GO

-- Create test table to verify setup
CREATE TABLE test_django_connection (
    id INT IDENTITY(1,1) PRIMARY KEY,
    test_message NVARCHAR(255),
    created_at DATETIME2 DEFAULT GETDATE()
);
GO

INSERT INTO test_django_connection (test_message) 
VALUES ('Django MSSQL connection test successful');
GO

-- Verify the setup
SELECT 
    DB_NAME() as DatabaseName,
    SUSER_SNAME() as CurrentUser,
    @@VERSION as SQLServerVersion,
    GETDATE() as CurrentTime;
GO

SELECT * FROM test_django_connection;
GO

-- Show database info
SELECT 
    name as DatabaseName,
    database_id,
    create_date,
    collation_name,
    state_desc as State
FROM sys.databases 
WHERE name = 'kenyan_payroll_system_db';
GO

-- Show user permissions
SELECT 
    dp.name AS principal_name,
    dp.type_desc AS principal_type,
    r.name AS role_name
FROM sys.database_role_members rm
JOIN sys.database_principals dp ON rm.member_principal_id = dp.principal_id
JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
WHERE dp.name = 'django_payroll_user';
GO

PRINT '=================================================';
PRINT 'KENYAN PAYROLL MSSQL DATABASE SETUP COMPLETE!';
PRINT '=================================================';
PRINT 'Database: kenyan_payroll_system_db';
PRINT 'User: django_payroll_user';
PRINT 'Password: DjangoPay2024!@#';
PRINT 'Ready for Django migration!';
PRINT '=================================================';

-- Clean up test table
DROP TABLE test_django_connection;
GO