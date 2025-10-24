#!/usr/bin/env python3
"""
Initialize Greenlist - Add initial users to the greenlist

Usage:
    python scripts/init_greenlist.py

Environment Variables:
    GOOGLE_CLOUD_PROJECT - Your GCP project ID (optional if gcloud is configured)
"""

from google.cloud import firestore
from datetime import datetime
import os

# Initialize Firestore
project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
if project_id:
    db = firestore.Client(project=project_id)
else:
    db = firestore.Client()

# Initial greenlist of allowed emails
# TODO: Update this list with your actual admin email addresses
INITIAL_EMAILS = [
    'Joseph.Finberg@laurelin-inc.com',
    # Add more emails as needed
]

def add_to_greenlist(email, added_by='system', notes='Initial greenlist setup'):
    """Add email to greenlist"""
    try:
        normalized_email = email.lower()
        doc_ref = db.collection('greenlist').document(normalized_email)

        # Check if email already exists
        if doc_ref.get().exists:
            print(f"⚠️  {email} already exists in greenlist")
            return False

        doc_ref.set({
            'email': normalized_email,
            'added_by': added_by,
            'added_at': datetime.utcnow(),
            'notes': notes,
            'is_active': True
        })
        print(f"✓ Added {email} to greenlist")
        return True
    except Exception as e:
        print(f"✗ Error adding {email}: {e}")
        return False

def check_greenlist(email):
    """Check if email is on greenlist"""
    try:
        normalized_email = email.lower()
        doc_ref = db.collection('greenlist').document(normalized_email)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            is_active = data.get('is_active', True)
            return is_active
        return False
    except Exception as e:
        print(f"Error checking {email}: {e}")
        return False

def list_greenlist():
    """List all greenlist entries"""
    try:
        docs = db.collection('greenlist').where('is_active', '==', True).stream()
        emails = []
        for doc in docs:
            data = doc.to_dict()
            emails.append(data['email'])
        return emails
    except Exception as e:
        print(f"Error listing greenlist: {e}")
        return []

def main():
    print("=" * 60)
    print("Laurelin Chatbot - Greenlist Initialization")
    print("=" * 60)
    print()

    # Verify Firestore connection
    try:
        db.collection('greenlist').limit(1).get()
        print("✓ Connected to Firestore")
        print()
    except Exception as e:
        print(f"✗ Failed to connect to Firestore: {e}")
        print()
        print("Make sure you have:")
        print("1. Set GOOGLE_CLOUD_PROJECT environment variable")
        print("2. Authenticated with: gcloud auth application-default login")
        return

    print(f"Adding {len(INITIAL_EMAILS)} emails to greenlist...")
    print()

    success_count = 0
    for email in INITIAL_EMAILS:
        if add_to_greenlist(email):
            success_count += 1

    print()
    print("=" * 60)
    print(f"✓ Successfully added {success_count}/{len(INITIAL_EMAILS)} emails to greenlist")
    print("=" * 60)
    print()

    # List all greenlist entries
    print("Current greenlist entries:")
    all_emails = list_greenlist()
    for email in all_emails:
        print(f"  - {email}")

    print()
    print("Greenlist initialization complete!")
    print()
    print("Next steps:")
    print("1. Verify emails are in greenlist:")
    print("   gcloud firestore documents list greenlist")
    print()
    print("2. Test authentication with a greenlist email")
    print()
    print("3. To add more emails, use the API endpoint:")
    print("   POST /api/greenlist/add")

if __name__ == '__main__':
    main()
