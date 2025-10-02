# EMAIL CONFIGURATION GUIDE
# Add this to your backend/kenyan_payroll_project/settings.py file

# For Gmail SMTP (recommended for testing)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-gmail@gmail.com'  # Your Gmail address
EMAIL_HOST_PASSWORD = 'your-app-password'  # Gmail App Password (not regular password)

# For testing without actual email sending (console output only)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production with custom SMTP server
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'your-smtp-server.com'
# EMAIL_PORT = 587  # or 465 for SSL
# EMAIL_USE_TLS = True  # or EMAIL_USE_SSL = True
# EMAIL_HOST_USER = 'noreply@yourdomain.com'
# EMAIL_HOST_PASSWORD = 'your-password'

# IMPORTANT NOTES:
# 1. CHANGE the email address in contact_views.py line ~513:
#    ['your-email@example.com'] to your actual email
#
# 2. For Gmail, you need an "App Password":
#    - Enable 2FA on your Google account
#    - Go to Google Account settings > Security > App passwords
#    - Generate a new app password for "Mail"
#    - Use this app password, not your regular Gmail password
#
# 3. For production, use environment variables:
#    EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
#    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')