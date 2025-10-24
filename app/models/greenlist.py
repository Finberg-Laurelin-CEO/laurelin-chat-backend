from datetime import datetime
from typing import Optional, Dict, Any, List
from google.cloud import firestore

class GreenlistEntry:
    """Greenlist entry model for Firestore operations"""

    def __init__(self, email: str, added_by: str = None,
                 added_at: datetime = None, notes: str = None,
                 is_active: bool = True):
        self.email = email.lower()  # Store emails in lowercase for consistency
        self.added_by = added_by
        self.added_at = added_at or datetime.utcnow()
        self.notes = notes
        self.is_active = is_active

    def to_dict(self) -> Dict[str, Any]:
        """Convert greenlist entry to dictionary for Firestore"""
        return {
            'email': self.email,
            'added_by': self.added_by,
            'added_at': self.added_at,
            'notes': self.notes,
            'is_active': self.is_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GreenlistEntry':
        """Create greenlist entry from Firestore document"""
        return cls(
            email=data['email'],
            added_by=data.get('added_by'),
            added_at=data.get('added_at'),
            notes=data.get('notes'),
            is_active=data.get('is_active', True)
        )

class GreenlistService:
    """Service class for greenlist operations"""

    def __init__(self):
        self.db = firestore.Client()
        self.collection = 'greenlist'

    def is_email_allowed(self, email: str) -> bool:
        """Check if an email is on the greenlist and active"""
        try:
            normalized_email = email.lower()
            doc_ref = self.db.collection(self.collection).document(normalized_email)
            doc = doc_ref.get()

            if doc.exists:
                data = doc.to_dict()
                return data.get('is_active', True)
            return False
        except Exception as e:
            print(f"Error checking greenlist: {e}")
            return False

    def add_email(self, email: str, added_by: str = None, notes: str = None) -> bool:
        """Add an email to the greenlist"""
        try:
            entry = GreenlistEntry(
                email=email,
                added_by=added_by,
                notes=notes,
                is_active=True
            )
            normalized_email = email.lower()
            doc_ref = self.db.collection(self.collection).document(normalized_email)
            doc_ref.set(entry.to_dict())
            print(f"Added {email} to greenlist")
            return True
        except Exception as e:
            print(f"Error adding to greenlist: {e}")
            return False

    def remove_email(self, email: str) -> bool:
        """Remove an email from the greenlist (soft delete)"""
        try:
            normalized_email = email.lower()
            doc_ref = self.db.collection(self.collection).document(normalized_email)
            doc_ref.update({'is_active': False})
            print(f"Removed {email} from greenlist")
            return True
        except Exception as e:
            print(f"Error removing from greenlist: {e}")
            return False

    def delete_email(self, email: str) -> bool:
        """Permanently delete an email from the greenlist"""
        try:
            normalized_email = email.lower()
            doc_ref = self.db.collection(self.collection).document(normalized_email)
            doc_ref.delete()
            print(f"Permanently deleted {email} from greenlist")
            return True
        except Exception as e:
            print(f"Error deleting from greenlist: {e}")
            return False

    def get_entry(self, email: str) -> Optional[GreenlistEntry]:
        """Get greenlist entry by email"""
        try:
            normalized_email = email.lower()
            doc_ref = self.db.collection(self.collection).document(normalized_email)
            doc = doc_ref.get()
            if doc.exists:
                return GreenlistEntry.from_dict(doc.to_dict())
            return None
        except Exception as e:
            print(f"Error getting greenlist entry: {e}")
            return None

    def list_all(self, active_only: bool = True) -> List[GreenlistEntry]:
        """List all greenlist entries"""
        try:
            query = self.db.collection(self.collection)
            if active_only:
                query = query.where('is_active', '==', True)

            docs = query.stream()
            entries = []
            for doc in docs:
                entries.append(GreenlistEntry.from_dict(doc.to_dict()))
            return entries
        except Exception as e:
            print(f"Error listing greenlist: {e}")
            return []

    def bulk_add_emails(self, emails: List[str], added_by: str = None) -> Dict[str, Any]:
        """Bulk add multiple emails to greenlist"""
        results = {
            'success': [],
            'failed': []
        }

        for email in emails:
            if self.add_email(email, added_by=added_by):
                results['success'].append(email)
            else:
                results['failed'].append(email)

        return results
