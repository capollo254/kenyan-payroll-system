# Employee Banking API Documentation

This document provides comprehensive information about the enhanced employee banking API endpoints and how to integrate them with the frontend.

## 📋 Overview

The employee banking system has been enhanced to include comprehensive banking information including:
- Bank account details
- Mobile money information
- Account validation and completion tracking
- Kenyan banking system integration

## 🔧 Backend API Endpoints

### Base URL
```
/api/employees/
```

### Authentication
All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## 📡 Available Endpoints

### 1. Get All Employees
```http
GET /api/employees/employees/
```

**Response**: Array of employee objects with complete banking information

**Sample Response**:
```json
[
  {
    "id": 1,
    "full_name": "John Doe",
    "email": "john.doe@company.com",
    "bank_name": "Equity Bank Kenya Limited",
    "bank_code": "68",
    "bank_account_number": "1234567890",
    "account_type_display": "Savings Account",
    "has_complete_banking": true,
    "banking_info": {
      "bank_name": "Equity Bank Kenya Limited",
      "bank_code": "68",
      "account_number": "1234567890"
    }
  }
]
```

### 2. Get Current User's Profile
```http
GET /api/employees/employees/me/
```

**Response**: Current user's complete employee profile

### 3. Get Current User's Banking Details
```http
GET /api/employees/employees/banking_details/
```

**Response**: Detailed banking information for current user

**Sample Response**:
```json
{
  "id": 1,
  "full_name": "John Doe",
  "bank_name": "Equity Bank Kenya Limited",
  "bank_code": "68",
  "bank_branch": "Westlands Branch",
  "bank_branch_code": "068",
  "bank_account_number": "1234567890",
  "account_type": "savings",
  "account_type_display": "Savings Account",
  "account_holder_name": "John Doe",
  "mobile_money_provider": "mpesa",
  "mobile_money_provider_display": "M-Pesa (Safaricom)",
  "mobile_money_number": "0712345678",
  "banking_info_formatted": {
    "bank_name": "Equity Bank Kenya Limited",
    "bank_code": "68",
    "account_number": "1234567890",
    "account_holder": "John Doe"
  },
  "has_complete_banking_info": true
}
```

### 4. Get Banking Details by Employee ID (Admin Only)
```http
GET /api/employees/employees/{id}/banking_details_by_id/
```

**Response**: Banking details for specific employee

### 5. Update Current User's Banking Details
```http
PUT /api/employees/employees/update_banking_details/
```

**Request Body**:
```json
{
  "bank_name": "Equity Bank Kenya Limited",
  "bank_code": "68",
  "bank_branch": "Westlands Branch",
  "bank_branch_code": "068",
  "bank_account_number": "1234567890",
  "account_type": "savings",
  "account_holder_name": "John Doe",
  "mobile_money_provider": "mpesa",
  "mobile_money_number": "0712345678"
}
```

**Response**: Updated banking information with confirmation

### 6. Partially Update Banking Details
```http
PATCH /api/employees/employees/update_banking_details/
```

**Request Body** (partial update):
```json
{
  "bank_account_number": "9876543210",
  "mobile_money_number": "0701234567"
}
```

### 7. Get Employees with Incomplete Banking (Admin Only)
```http
GET /api/employees/employees/employees_with_incomplete_banking/
```

**Response**:
```json
{
  "count": 3,
  "employees": [
    {
      "id": 2,
      "full_name": "Jane Smith",
      "email": "jane.smith@company.com",
      "missing_fields": ["bank_code", "bank_branch_code"],
      "banking_completion_percentage": 75.0
    }
  ]
}
```

---

## 💻 Frontend Integration

### Import the API Functions
```javascript
import {
  getMyBankingDetails,
  updateMyBankingDetails,
  validateBankingInfo,
  formatBankingInfo,
  getAccountTypes,
  getMobileMoneyProviders,
  getKenyanBanks
} from '../api/employees';
```

### Basic Usage Examples

#### 1. Fetch Banking Details
```javascript
const fetchBankingDetails = async () => {
  try {
    const bankingData = await getMyBankingDetails();
    console.log('Banking details:', bankingData);
  } catch (error) {
    console.error('Error:', error.message);
  }
};
```

#### 2. Update Banking Information
```javascript
const updateBankingInfo = async (formData) => {
  try {
    const updatedData = await updateMyBankingDetails(formData);
    console.log('Updated successfully:', updatedData);
  } catch (error) {
    console.error('Update failed:', error.message);
  }
};
```

#### 3. Validate Banking Information
```javascript
const validation = validateBankingInfo(bankingData);
console.log('Is complete:', validation.isComplete);
console.log('Missing fields:', validation.missingFields);
console.log('Completion %:', validation.completionPercentage);
```

#### 4. Format Banking Information for Display
```javascript
const formatted = formatBankingInfo(bankingData);
console.log('Display name:', formatted.displayName);
console.log('Full account info:', formatted.fullAccountInfo);
console.log('Is complete:', formatted.isComplete);
```

---

## 🏦 Kenyan Banking Integration

### Supported Account Types
- **Savings Account** (`savings`)
- **Current Account** (`current`) 
- **Fixed Deposit Account** (`fixed`)

### Supported Mobile Money Providers
- **M-Pesa (Safaricom)** (`mpesa`)
- **Airtel Money** (`airtel`)
- **T-Kash (Telkom)** (`tkash`)
- **Equitel** (`equitel`)

### Major Kenyan Banks Included
- KCB Bank Kenya Limited
- Equity Bank Kenya Limited
- Co-operative Bank of Kenya Limited
- Standard Chartered Bank Kenya Limited
- Stanbic Bank Kenya Limited
- I&M Bank Limited
- And 25+ more banks with official bank codes

---

## 🔍 Validation Rules

### Required Fields for Complete Banking Information
1. `bank_name` - Full bank name
2. `bank_code` - Central Bank assigned code
3. `bank_branch` - Bank branch name
4. `bank_branch_code` - Specific branch code
5. `bank_account_number` - Account number
6. `account_type` - Type of account

### Optional Fields
- `account_holder_name` - Defaults to employee full name
- `mobile_money_provider` - Mobile money service
- `mobile_money_number` - Mobile money phone number

---

## 🎨 Frontend Component Example

The `EmployeeBankingDetails.js` component provides a complete implementation:

### Features
- ✅ View banking details
- ✅ Edit banking information
- ✅ Bank dropdown with auto-fill bank codes
- ✅ Account type selection
- ✅ Mobile money configuration
- ✅ Real-time validation
- ✅ Completion status tracking
- ✅ Responsive design

### Usage
```jsx
import EmployeeBankingDetails from '../components/EmployeeBankingDetails';

function MyPage() {
  return (
    <div>
      <EmployeeBankingDetails />
    </div>
  );
}
```

---

## 🧪 Testing

### Run API Tests
```bash
cd backend
python test_banking_api.py
```

### Test Coverage
- ✅ Authentication testing
- ✅ CRUD operations
- ✅ Data validation
- ✅ Error handling
- ✅ Admin permissions
- ✅ Data formatting

---

## 🚀 Deployment Considerations

### Environment Variables
Ensure these are configured:
```env
DATABASE_URL=your-database-url
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com
```

### Database Migrations
```bash
python manage.py makemigrations employees
python manage.py migrate
```

### Static Files
```bash
python manage.py collectstatic
```

---

## 🔐 Security Features

- **JWT Authentication** - All endpoints protected
- **Permission-based Access** - Regular users can only see their own data
- **Admin-only Endpoints** - Sensitive operations require admin privileges
- **Input Validation** - Server-side validation for all data
- **Data Sanitization** - Automatic data cleaning and formatting

---

## 📞 Support

For questions or issues with the banking API:

1. Check the test script output: `python test_banking_api.py`
2. Review Django logs for detailed error messages
3. Verify database migrations are applied
4. Ensure all required fields are properly configured

---

## 🔄 Version History

### v1.0.0 (Current)
- Complete banking information system
- Mobile money integration
- Kenyan banking system support
- Validation and completion tracking
- Frontend React components
- Comprehensive API testing

### Features Coming Soon
- Bank verification integration
- Payroll banking automation  
- Multi-currency support
- Enhanced reporting