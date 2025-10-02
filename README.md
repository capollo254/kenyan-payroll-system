# 🧮 Kenya Payroll Management System

A comprehensive payroll management system built with Django and React, fully compliant with Kenya Revenue Authority (KRA) regulations and the Finance Act 2023.

## ✨ Features

### 🏛️ KRA Compliance
- **PAYE Tax Calculation** - Progressive tax brackets (10%, 25%, 30%, 35%)
- **NSSF Contributions** - 6% of gross salary (capped appropriately)
- **SHIF Contributions** - 2.75% of gross salary
- **Affordable Housing Levy** - 1.5% of gross salary
- **All Tax Reliefs** - Personal, pension, insurance, medical fund, mortgage interest

### 💼 Core Functionality
- **Employee Management** - Complete employee profiles with all necessary details
- **Payroll Processing** - Automated monthly payroll calculations
- **Payslip Generation** - Professional payslips with detailed breakdowns
- **Tax Relief Management** - Comprehensive relief calculations
- **Reporting & Analytics** - Detailed reports and insights
- **Leave Management** - Annual leave tracking and management

### 🌐 Public Calculator
- **Marketing Tool** - Public payroll calculator for your website
- **Real-time Calculations** - Instant salary calculations with all reliefs
- **Beautiful Interface** - Professional, responsive design
- **No Authentication** - Perfect for lead generation

## 🛠️ Technology Stack

### Backend
- **Django 5.0.7** - Python web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Database
- **django-cors-headers** - CORS support

### Frontend
- **React.js** - Modern JavaScript framework
- **HTML/CSS/JavaScript** - For the public calculator

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- PostgreSQL

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure database in settings.py
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Public Calculator
```bash
# Serve the calculator
python -m http.server 3000

# Access at: http://localhost:3000/payroll_calculator.html
```

## 📊 Sample Calculations

**Gross Salary: KSh 100,000**
- PAYE Tax: KSh 10,512.35 (after reliefs)
- NSSF: KSh 4,320.00 (6%)
- SHIF: KSh 2,750.00 (2.75%)
- AHL: KSh 1,500.00 (1.5%)
- **Net Pay: KSh 67,417.65**

## 🎯 Tax Reliefs Supported

- **Personal Relief**: KSh 2,400 monthly
- **Pension Relief**: Up to KSh 30,000 monthly
- **Insurance Relief**: 15% up to KSh 5,000 monthly
- **Medical Fund Relief**: Up to KSh 15,000 monthly
- **Mortgage Interest Relief**: Up to KSh 30,000 monthly

## 📁 Project Structure

```
kenyan_payroll_system/
├── backend/
│   ├── apps/
│   │   ├── core/          # User management
│   │   ├── employees/     # Employee management
│   │   ├── payroll/       # Payroll processing
│   │   ├── compliance/    # KRA calculations
│   │   ├── reports/       # Reporting
│   │   ├── notifications/ # Email notifications
│   │   └── leaves/        # Leave management
│   ├── kenyan_payroll_project/
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── api/
│   └── package.json
├── payroll_calculator.html  # Public calculator
└── README.md
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
```

### Database Setup
```sql
CREATE DATABASE kenyan_payroll_system_db;
```

## 📝 API Endpoints

### Authentication Required
- `POST /api/auth/login/` - User login
- `GET /api/employees/` - List employees
- `POST /api/payroll/` - Process payroll
- `GET /api/reports/` - Generate reports

### Public Endpoints
- `POST /api/public/calculator/` - Public payroll calculator

## 🧪 Testing

```bash
# Run backend tests
python manage.py test

# Test API endpoints
python test_api_endpoints.py

# Test calculations
python test_complete_enhanced_system.py
```

## 📋 Compliance Notes

This system is designed to be compliant with:
- Kenya Revenue Authority (KRA) regulations
- Finance Act 2023
- Employment Act
- National Social Security Fund (NSSF) requirements
- Social Health Insurance Fund (SHIF) requirements

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and inquiries:
- Email: support@yourcompany.com
- Documentation: [Link to docs]
- Issues: [GitHub Issues](https://github.com/yourusername/kenyan-payroll-system/issues)

## 🎉 Acknowledgments

- Kenya Revenue Authority for tax calculation guidelines
- Django community for the excellent framework
- React community for frontend tools

---

**Built with ❤️ for Kenyan businesses**
