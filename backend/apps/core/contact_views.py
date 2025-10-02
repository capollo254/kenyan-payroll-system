from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactInquiry
import json
import os
from datetime import datetime

def contact_form_view(request):
    """
    Display the contact form for businesses interested in the full payroll system
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Get the Full System - Kenya Payroll System</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
                font-weight: 300;
            }
            
            .header p {
                font-size: 1.1rem;
                opacity: 0.9;
            }
            
            .form-container {
                padding: 40px 30px;
            }
            
            .form-group {
                margin-bottom: 25px;
            }
            
            .form-row {
                display: flex;
                gap: 20px;
            }
            
            .form-row .form-group {
                flex: 1;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
                font-size: 0.95rem;
            }
            
            .required {
                color: #e74c3c;
            }
            
            input[type="text"],
            input[type="email"],
            input[type="tel"],
            select,
            textarea {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                font-size: 1rem;
                transition: border-color 0.3s ease;
                font-family: inherit;
            }
            
            input:focus,
            select:focus,
            textarea:focus {
                outline: none;
                border-color: #2E7D32;
                box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.1);
            }
            
            textarea {
                resize: vertical;
                min-height: 100px;
            }
            
            .checkbox-group {
                display: flex;
                align-items: flex-start;
                gap: 10px;
                margin-top: 20px;
            }
            
            .checkbox-group input[type="checkbox"] {
                width: auto;
                margin-top: 4px;
            }
            
            .checkbox-group label {
                margin-bottom: 0;
                font-weight: normal;
                font-size: 0.9rem;
                line-height: 1.4;
            }
            
            .submit-btn {
                background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
                color: white;
                padding: 15px 40px;
                border: none;
                border-radius: 8px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                width: 100%;
                margin-top: 20px;
            }
            
            .submit-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(46, 125, 50, 0.3);
            }
            
            .back-link {
                display: inline-block;
                margin-bottom: 20px;
                color: #2E7D32;
                text-decoration: none;
                font-weight: 500;
            }
            
            .back-link:hover {
                text-decoration: underline;
            }
            
            .features {
                background: #f8f9fa;
                padding: 30px;
                margin: 30px 0;
                border-radius: 10px;
            }
            
            .features h3 {
                color: #2E7D32;
                margin-bottom: 15px;
                text-align: center;
            }
            
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            
            .feature-item {
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 0.9rem;
            }
            
            .feature-item::before {
                content: "✅";
                font-size: 1.2rem;
            }
            
            @media (max-width: 768px) {
                .form-row {
                    flex-direction: column;
                    gap: 0;
                }
                
                .header h1 {
                    font-size: 2rem;
                }
                
                .container {
                    margin: 10px;
                }
                
                .form-container {
                    padding: 30px 20px;
                }
            }
            
            .success-message {
                display: none;
                background: #d4edda;
                color: #155724;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                border: 1px solid #c3e6cb;
            }
            
            .error-message {
                display: none;
                background: #f8d7da;
                color: #721c24;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Get the Full Payroll System</h1>
                <p>Transform your payroll management with our comprehensive solution</p>
            </div>
            
            <div class="form-container">
                <a href="/calculator/" class="back-link">← Back to Calculator</a>
                
                <div id="success-message" class="success-message">
                    <h4>Thank you for your interest!</h4>
                    <p>We've received your request and will contact you within 24 hours to discuss your payroll needs.</p>
                </div>
                
                <div id="error-message" class="error-message">
                    <h4>Something went wrong</h4>
                    <p>Please try again or contact us directly at <a href="mailto:info@kenyapayroll.com">info@kenyapayroll.com</a></p>
                </div>
                
                <form id="contactForm" method="POST" action="/contact/submit/">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="company_name">Company Name <span class="required">*</span></label>
                            <input type="text" id="company_name" name="company_name" required>
                        </div>
                        <div class="form-group">
                            <label for="contact_name">Your Full Name <span class="required">*</span></label>
                            <input type="text" id="contact_name" name="contact_name" required>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="job_title">Job Title/Role <span class="required">*</span></label>
                            <input type="text" id="job_title" name="job_title" required placeholder="e.g., HR Manager, CEO, Finance Director">
                        </div>
                        <div class="form-group">
                            <label for="email">Email Address <span class="required">*</span></label>
                            <input type="email" id="email" name="email" required>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="phone">Phone Number <span class="required">*</span></label>
                            <input type="tel" id="phone" name="phone" required placeholder="+254...">
                        </div>
                        <div class="form-group">
                            <label for="employee_count">Number of Employees <span class="required">*</span></label>
                            <select id="employee_count" name="employee_count" required>
                                <option value="">Select range</option>
                                <option value="1-10">1-10 employees</option>
                                <option value="11-50">11-50 employees</option>
                                <option value="51-100">51-100 employees</option>
                                <option value="101-500">101-500 employees</option>
                                <option value="500+">500+ employees</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="industry">Industry/Business Type</label>
                            <input type="text" id="industry" name="industry" placeholder="e.g., Manufacturing, Education, Healthcare">
                        </div>
                        <div class="form-group">
                            <label for="current_method">Current Payroll Method</label>
                            <select id="current_method" name="current_method">
                                <option value="">Select current method</option>
                                <option value="manual">Manual (Excel/Paper)</option>
                                <option value="software">Payroll Software</option>
                                <option value="outsourced">Outsourced Service</option>
                                <option value="none">No formal system</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="primary_interest">Primary Interest <span class="required">*</span></label>
                            <select id="primary_interest" name="primary_interest" required>
                                <option value="">What are you most interested in?</option>
                                <option value="demo">Schedule a Demo</option>
                                <option value="pricing">Get Pricing Information</option>
                                <option value="implementation">Implementation Timeline</option>
                                <option value="features">Learn About Features</option>
                                <option value="migration">Migrate from Current System</option>
                                <option value="consultation">Free Consultation</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="timeline">Implementation Timeline</label>
                            <select id="timeline" name="timeline">
                                <option value="">When do you plan to implement?</option>
                                <option value="immediately">Immediately</option>
                                <option value="1-3-months">1-3 months</option>
                                <option value="3-6-months">3-6 months</option>
                                <option value="6-12-months">6-12 months</option>
                                <option value="planning">Just planning/researching</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="budget_range">Monthly Budget Range (Optional)</label>
                        <select id="budget_range" name="budget_range">
                            <option value="">Select budget range</option>
                            <option value="under-10k">Under KES 10,000</option>
                            <option value="10k-25k">KES 10,000 - 25,000</option>
                            <option value="25k-50k">KES 25,000 - 50,000</option>
                            <option value="50k-100k">KES 50,000 - 100,000</option>
                            <option value="100k+">KES 100,000+</option>
                            <option value="discuss">Prefer to discuss</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="specific_needs">Specific Needs or Challenges</label>
                        <textarea id="specific_needs" name="specific_needs" placeholder="Tell us about your current payroll challenges, specific requirements, or questions you have about our system..."></textarea>
                    </div>
                    
                    <div class="checkbox-group">
                        <input type="checkbox" id="newsletter" name="newsletter" value="yes">
                        <label for="newsletter">I'd like to receive updates about new features and payroll compliance changes in Kenya</label>
                    </div>
                    
                    <div class="checkbox-group">
                        <input type="checkbox" id="terms" name="terms" required>
                        <label for="terms">I agree to be contacted by Kenya Payroll System regarding my inquiry <span class="required">*</span></label>
                    </div>
                    
                    <button type="submit" class="submit-btn">📧 Send My Request</button>
                </form>
                
                <div class="features">
                    <h3>What You Get with the Full System</h3>
                    <div class="feature-grid">
                        <div class="feature-item">Complete Employee Management</div>
                        <div class="feature-item">Automated Payroll Processing</div>
                        <div class="feature-item">Tax Compliance & Reporting</div>
                        <div class="feature-item">Leave Management System</div>
                        <div class="feature-item">Employee Self-Service Portal</div>
                        <div class="feature-item">Digital Payslip Generation</div>
                        <div class="feature-item">NSSF & NHIF Integration</div>
                        <div class="feature-item">KRA Compliance Tools</div>
                        <div class="feature-item">Multi-user Access Control</div>
                        <div class="feature-item">Data Export & Reporting</div>
                        <div class="feature-item">24/7 Technical Support</div>
                        <div class="feature-item">Regular System Updates</div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            document.getElementById('contactForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const submitBtn = document.querySelector('.submit-btn');
                const originalText = submitBtn.textContent;
                
                submitBtn.textContent = 'Sending...';
                submitBtn.disabled = true;
                
                fetch('/contact/submit/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('success-message').style.display = 'block';
                        document.getElementById('contactForm').style.display = 'none';
                        document.getElementById('error-message').style.display = 'none';
                        
                        // Scroll to top to show success message
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    } else {
                        throw new Error(data.error || 'Submission failed');
                    }
                })
                .catch(error => {
                    document.getElementById('error-message').style.display = 'block';
                    document.getElementById('success-message').style.display = 'none';
                    console.error('Error:', error);
                })
                .finally(() => {
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                });
            });
            
            // Function to get CSRF token
            function getCookie(name) {
                let cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim();
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
        </script>
    </body>
    </html>
    """
    return HttpResponse(html_content)

@csrf_exempt
def contact_form_submit(request):
    """
    Handle contact form submission
    """
    if request.method == 'POST':
        try:
            # Extract form data
            data = {
                'company_name': request.POST.get('company_name'),
                'contact_name': request.POST.get('contact_name'),
                'job_title': request.POST.get('job_title'),
                'email': request.POST.get('email'),
                'phone': request.POST.get('phone'),
                'employee_count': request.POST.get('employee_count'),
                'industry': request.POST.get('industry'),
                'current_method': request.POST.get('current_method'),
                'primary_interest': request.POST.get('primary_interest'),
                'timeline': request.POST.get('timeline'),
                'budget_range': request.POST.get('budget_range'),
                'specific_needs': request.POST.get('specific_needs'),
                'newsletter': request.POST.get('newsletter'),
                'submission_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Create email content
            email_subject = f"New Payroll System Inquiry - {data['company_name']}"
            email_body = f"""
New inquiry for the full payroll system:

COMPANY INFORMATION:
- Company: {data['company_name']}
- Contact Person: {data['contact_name']}
- Job Title: {data['job_title']}
- Email: {data['email']}
- Phone: {data['phone']}

COMPANY DETAILS:
- Number of Employees: {data['employee_count']}
- Industry: {data['industry'] or 'Not specified'}
- Current Payroll Method: {data['current_method'] or 'Not specified'}

REQUIREMENTS:
- Primary Interest: {data['primary_interest']}
- Implementation Timeline: {data['timeline'] or 'Not specified'}
- Budget Range: {data['budget_range'] or 'Not specified'}

SPECIFIC NEEDS:
{data['specific_needs'] or 'None specified'}

ADDITIONAL INFO:
- Newsletter Subscription: {'Yes' if data['newsletter'] else 'No'}
- Submission Date: {data['submission_date']}

Please respond within 24 hours.
            """
            
            # Save to log file for backup (better to use database in production)
            log_file_path = os.path.join(os.path.dirname(__file__), '../../contact_inquiries.log')
            try:
                with open(log_file_path, 'a') as f:
                    f.write(f"{datetime.now().isoformat()}: {json.dumps(data)}\n")
                print(f"Form data logged for {data['company_name']}")
            except Exception as e:
                print(f"Logging failed: {e}")
                # Log writing failure is not critical
            
            # Save to database for Django admin management
            try:
                contact_inquiry = ContactInquiry.objects.create(
                    company_name=data['company_name'],
                    contact_name=data['contact_name'],
                    job_title=data['job_title'],
                    email=data['email'],
                    phone=data['phone'],
                    employee_count=data['employee_count'],
                    industry=data['industry'],
                    current_method=data['current_method'],
                    primary_interest=data['primary_interest'],
                    timeline=data['timeline'],
                    budget_range=data['budget_range'],
                    specific_needs=data['specific_needs'],
                    newsletter=data['newsletter'] == 'yes',
                    status='new'  # Default status for new inquiries
                )
                print(f"Contact inquiry saved to database: ID {contact_inquiry.id} for {data['company_name']}")
            except Exception as e:
                print(f"Database save failed: {e}")
                # Database failure is logged but doesn't break the form
            
            # Send email notification to admin
            try:
                send_mail(
                    email_subject,
                    email_body,
                    'noreply@localhost',  # From email
                    ['constantive@gmail.com'],   # Primary recipient
                    fail_silently=False,
                )
                print(f"Admin notification sent successfully for inquiry from {data['company_name']}")
            except Exception as e:
                print(f"Admin email sending failed: {e}")
            
            # Send confirmation email to the person who submitted the form
            confirmation_subject = "Thank you for your interest in Kenya Payroll System"
            confirmation_body = f"""
Dear {data['contact_name']},

Thank you for your interest in our Kenya Payroll System!

We have received your inquiry and our team will review your requirements carefully. Here's a summary of what you submitted:

COMPANY INFORMATION:
- Company: {data['company_name']}
- Contact Person: {data['contact_name']}
- Job Title: {data['job_title']}
- Email: {data['email']}
- Phone: {data['phone']}

REQUIREMENTS:
- Number of Employees: {data['employee_count']}
- Primary Interest: {data['primary_interest']}
- Implementation Timeline: {data['timeline'] or 'Not specified'}

NEXT STEPS:
Our team will contact you within 24 hours to discuss your payroll needs and answer any questions you may have.

In the meantime, feel free to explore our calculator at: http://127.0.0.1:8000/calculator/

Thank you for considering Kenya Payroll System for your business needs.

Best regards,
Kenya Payroll System Team
Email: constantive@gmail.com
            """
            
            try:
                send_mail(
                    confirmation_subject,
                    confirmation_body,
                    'noreply@localhost',  # From email
                    [data['email']],  # Send to the person who submitted the form
                    fail_silently=False,
                )
                print(f"Confirmation email sent to {data['email']}")
            except Exception as e:
                print(f"Confirmation email sending failed: {e}")
                # Confirmation email failure is not critical for form success
            
            return HttpResponse(
                json.dumps({'success': True, 'message': 'Thank you for your inquiry!'}),
                content_type='application/json'
            )
            
        except Exception as e:
            return HttpResponse(
                json.dumps({'success': False, 'error': str(e)}),
                content_type='application/json',
                status=400
            )
    
    return HttpResponse(
        json.dumps({'success': False, 'error': 'Invalid request method'}),
        content_type='application/json',
        status=405
    )