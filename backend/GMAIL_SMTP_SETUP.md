# Gmail SMTP Setup Guide for Kenya Payroll System

## 🚀 **QUICK SETUP STEPS**

### **Step 1: Enable 2-Factor Authentication on Gmail**
1. Go to your Google Account settings: https://myaccount.google.com/
2. Click on "Security" in the left sidebar
3. Under "Signing in to Google", enable "2-Step Verification"
4. Follow the setup process to enable 2FA

### **Step 2: Generate Gmail App Password**
1. Still in Google Account Security settings
2. Under "Signing in to Google", click "App passwords"
3. Select app: "Mail"
4. Select device: "Windows Computer" (or your device type)
5. Click "Generate"
6. **COPY THE 16-CHARACTER PASSWORD** (e.g., `abcd efgh ijkl mnop`)

### **Step 3: Update Your .env File**
Replace `your_gmail_app_password_here` in your `.env` file with the app password:

```env
EMAIL_HOST_USER=constantive@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
DEFAULT_FROM_EMAIL=constantive@gmail.com
```

**⚠️ IMPORTANT:** Use the 16-character app password, NOT your regular Gmail password!

### **Step 4: Test Email Configuration**
Run this command from your backend directory:

```bash
python test_email_functionality.py
```

You should see:
```
✅ Admin email sent successfully!
✅ Confirmation email sent successfully!
```

## 📧 **How It Works Now**

When someone submits the contact form:

1. **You receive**: Business inquiry email at `constantive@gmail.com`
2. **They receive**: Professional confirmation email at their provided address
3. **System logs**: Backup saved to `contact_inquiries.log`

## 🔧 **Troubleshooting**

### **Common Issues:**

**Issue**: "Authentication failed"
- **Solution**: Make sure you're using the 16-character app password, not your Gmail password
- **Check**: 2-Factor Authentication is enabled on Gmail

**Issue**: "SMTPAuthenticationError: Username and Password not accepted"
- **Solution**: Generate a new app password and update .env file
- **Check**: Email address is correct in .env file

**Issue**: "Connection refused"
- **Solution**: Check your internet connection and firewall settings

### **Testing Commands:**
```bash
# Test email functionality
python test_email_functionality.py

# Start Django server to test form
python manage.py runserver
```

## 🔐 **Security Notes**

- ✅ **Safe**: App passwords are specific to applications and can be revoked
- ✅ **Secure**: Your main Gmail password remains private
- ✅ **Isolated**: If compromised, only affects this application
- ✅ **Revocable**: Can be disabled from Google Account settings anytime

## 🎯 **Expected Results**

After setup, form submissions will:
- ✅ Send business inquiries to constantive@gmail.com
- ✅ Send confirmation emails to form submitters
- ✅ Log all submissions to contact_inquiries.log
- ✅ Provide professional customer experience

## 📞 **Need Help?**

If you encounter issues:
1. Check the console output when testing
2. Verify your app password is correct
3. Ensure 2FA is enabled on Gmail
4. Test with the test script first

Your contact form will be fully operational once this setup is complete! 🚀