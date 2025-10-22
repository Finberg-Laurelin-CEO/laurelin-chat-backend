import random
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from google.cloud import firestore
from app.config import Config

class ABTestingService:
    """Service for managing A/B testing between different models"""
    
    def __init__(self):
        self.db = firestore.Client()
        self.experiments_collection = 'ab_experiments'
        self.assignments_collection = 'ab_assignments'
    
    def create_experiment(self, experiment_name: str, variants: Dict[str, float],
                         description: str = None) -> bool:
        """Create a new A/B test experiment"""
        try:
            experiment_data = {
                'name': experiment_name,
                'variants': variants,
                'description': description,
                'status': 'active',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            doc_ref = self.db.collection(self.experiments_collection).document(experiment_name)
            doc_ref.set(experiment_data)
            return True
        except Exception as e:
            print(f"Error creating experiment: {e}")
            return False
    
    def get_experiment(self, experiment_name: str) -> Optional[Dict[str, Any]]:
        """Get experiment configuration"""
        try:
            doc_ref = self.db.collection(self.experiments_collection).document(experiment_name)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting experiment: {e}")
            return None
    
    def assign_user_to_variant(self, user_id: str, experiment_name: str) -> str:
        """Assign user to a variant for the experiment"""
        try:
            # Check if user already has an assignment
            assignment_doc = (self.db.collection(self.assignments_collection)
                            .where('user_id', '==', user_id)
                            .where('experiment_name', '==', experiment_name)
                            .limit(1)
                            .get())
            
            if assignment_doc:
                return assignment_doc[0].to_dict()['variant']
            
            # Get experiment configuration
            experiment = self.get_experiment(experiment_name)
            if not experiment or experiment['status'] != 'active':
                return 'control'  # Default to control if experiment not active
            
            # Use consistent hashing for deterministic assignment
            variant = self._get_consistent_variant(user_id, experiment_name, experiment['variants'])
            
            # Store assignment
            assignment_data = {
                'user_id': user_id,
                'experiment_name': experiment_name,
                'variant': variant,
                'assigned_at': datetime.utcnow()
            }
            
            doc_ref = self.db.collection(self.assignments_collection).add(assignment_data)
            return variant
            
        except Exception as e:
            print(f"Error assigning user to variant: {e}")
            return 'control'
    
    def _get_consistent_variant(self, user_id: str, experiment_name: str, 
                               variants: Dict[str, float]) -> str:
        """Get consistent variant assignment using hash"""
        # Create a hash from user_id and experiment_name
        hash_input = f"{user_id}:{experiment_name}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # Use hash to get a value between 0 and 1
        normalized_hash = (hash_value % 10000) / 10000.0
        
        # Assign variant based on cumulative probability
        cumulative = 0.0
        for variant, probability in variants.items():
            cumulative += probability
            if normalized_hash <= cumulative:
                return variant
        
        # Fallback to first variant
        return list(variants.keys())[0]
    
    def track_event(self, user_id: str, experiment_name: str, event_type: str,
                   event_data: Dict[str, Any] = None) -> bool:
        """Track an event for A/B testing analysis"""
        try:
            event_data = event_data or {}
            event_record = {
                'user_id': user_id,
                'experiment_name': experiment_name,
                'event_type': event_type,
                'event_data': event_data,
                'timestamp': datetime.utcnow()
            }
            
            self.db.collection('ab_events').add(event_record)
            return True
        except Exception as e:
            print(f"Error tracking event: {e}")
            return False
    
    def get_experiment_results(self, experiment_name: str) -> Dict[str, Any]:
        """Get aggregated results for an experiment"""
        try:
            # Get all assignments for this experiment
            assignments = (self.db.collection(self.assignments_collection)
                          .where('experiment_name', '==', experiment_name)
                          .get())
            
            # Get all events for this experiment
            events = (self.db.collection('ab_events')
                     .where('experiment_name', '==', experiment_name)
                     .get())
            
            # Aggregate results
            variant_counts = {}
            event_counts = {}
            
            for assignment in assignments:
                variant = assignment.to_dict()['variant']
                variant_counts[variant] = variant_counts.get(variant, 0) + 1
            
            for event in events:
                event_data = event.to_dict()
                variant = event_data.get('variant', 'unknown')
                event_type = event_data['event_type']
                
                if variant not in event_counts:
                    event_counts[variant] = {}
                event_counts[variant][event_type] = event_counts[variant].get(event_type, 0) + 1
            
            return {
                'experiment_name': experiment_name,
                'variant_assignments': variant_counts,
                'event_counts': event_counts,
                'total_users': sum(variant_counts.values()),
                'total_events': sum(sum(events.values()) for events in event_counts.values())
            }
        except Exception as e:
            print(f"Error getting experiment results: {e}")
            return {}
    
    def initialize_default_experiments(self):
        """Initialize default A/B testing experiments"""
        if not Config.AB_TEST_ENABLED:
            return
        
        # Model comparison experiment
        self.create_experiment(
            experiment_name="model_comparison",
            variants={
                "openai": 0.5,
                "google": 0.5
            },
            description="Compare OpenAI GPT vs Google Gemini performance"
        )
