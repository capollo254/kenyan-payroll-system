#!/usr/bin/env python
"""
Import existing contact inquiries from log file to database
"""
import os
import django
import json
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kenyan_payroll_project.settings')
django.setup()

from apps.core.models import ContactInquiry

def import_existing_inquiries():
    """Import existing inquiries from contact_inquiries.log"""
    
    log_file_path = os.path.join(os.path.dirname(__file__), 'contact_inquiries.log')
    
    if not os.path.exists(log_file_path):
        print("❌ No existing log file found.")
        return
    
    print("🔍 Importing existing contact inquiries from log file...")
    
    imported_count = 0
    errors = 0
    
    try:
        with open(log_file_path, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            try:
                # Parse the log line format: "2025-09-27T23:48:17.808457: json_data"
                if ': {' in line and line.strip():
                    # Find the first occurrence of ': {' to split timestamp and JSON
                    split_index = line.find(': {')
                    timestamp_str = line[:split_index]
                    json_str = line[split_index + 2:]  # Skip ': ' 
                    
                    data = json.loads(json_str.strip())
                    
                    # Check if this inquiry already exists (by email and company)
                    existing = ContactInquiry.objects.filter(
                        email=data['email'],
                        company_name=data['company_name']
                    ).first()
                    
                    if existing:
                        print(f"⚠️  Skipping duplicate: {data['company_name']} - {data['email']}")
                        continue
                    
                    # Create the contact inquiry
                    contact_inquiry = ContactInquiry.objects.create(
                        company_name=data.get('company_name', ''),
                        contact_name=data.get('contact_name', ''),
                        job_title=data.get('job_title', ''),
                        email=data.get('email', ''),
                        phone=data.get('phone', ''),
                        employee_count=data.get('employee_count', '1-10'),
                        industry=data.get('industry', ''),
                        current_method=data.get('current_method', 'manual'),
                        primary_interest=data.get('primary_interest', 'pricing'),
                        timeline=data.get('timeline', ''),
                        budget_range=data.get('budget_range', ''),
                        specific_needs=data.get('specific_needs', ''),
                        newsletter=data.get('newsletter', 'no') == 'yes',
                        status='new'
                    )
                    
                    # Set the submission date from log if available
                    if 'submission_date' in data:
                        try:
                            submission_date = datetime.fromisoformat(data['submission_date'].replace('Z', '+00:00'))
                            contact_inquiry.submission_date = submission_date
                            contact_inquiry.save()
                        except:
                            pass  # Keep auto-generated date
                    
                    imported_count += 1
                    print(f"✅ Imported: {contact_inquiry.company_name} - {contact_inquiry.contact_name}")
                    
            except Exception as e:
                errors += 1
                print(f"❌ Error parsing line: {e}")
                continue
    
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        return
    
    print(f"\n📊 Import Summary:")
    print(f"✅ Successfully imported: {imported_count} inquiries")
    if errors > 0:
        print(f"❌ Errors encountered: {errors}")
    
    # Show total count in database
    total_count = ContactInquiry.objects.count()
    print(f"📈 Total inquiries in database: {total_count}")
    
    # Show hot leads
    hot_leads = ContactInquiry.objects.filter().exclude(status='closed-lost')
    hot_count = sum(1 for inquiry in hot_leads if inquiry.is_hot_lead)
    print(f"🔥 Hot leads identified: {hot_count}")

if __name__ == "__main__":
    import_existing_inquiries()