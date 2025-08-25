#!/usr/bin/env python3
"""
Feedback Handler for Layout Classification System

This script processes user feedback about misclassified images and creates
a review queue for human moderators to evaluate and potentially create new layout buckets.
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class FeedbackHandler:
    def __init__(self, feedback_file: str = "feedback_queue.csv"):
        self.feedback_file = Path(feedback_file)
        self.feedback_file.parent.mkdir(exist_ok=True)
        
        # Initialize feedback file if it doesn't exist
        if not self.feedback_file.exists():
            self._create_feedback_file()
    
    def _create_feedback_file(self):
        """Create the initial feedback CSV file with headers"""
        headers = [
            'timestamp', 'site', 'cluster_id', 'feedback_type', 'feedback_text', 
            'status', 'reviewer_notes', 'action_taken'
        ]
        
        with open(self.feedback_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    
    def submit_feedback(self, site: str, cluster_id: str, feedback_type: str, 
                       feedback_text: str) -> bool:
        """
        Submit new feedback for review
        
        Args:
            site: 'folklife' or 'festival'
            cluster_id: The cluster ID being reviewed
            feedback_type: 'flag' or 'correct'
            feedback_text: User's explanation
        
        Returns:
            bool: True if feedback was saved successfully
        """
        try:
            feedback_data = {
                'timestamp': datetime.now().isoformat(),
                'site': site,
                'cluster_id': cluster_id,
                'feedback_type': feedback_type,
                'feedback_text': feedback_text,
                'status': 'pending',
                'reviewer_notes': '',
                'action_taken': ''
            }
            
            with open(self.feedback_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=feedback_data.keys())
                writer.writerow(feedback_data)
            
            print(f"✅ Feedback submitted for {site} cluster {cluster_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving feedback: {e}")
            return False
    
    def get_pending_feedback(self, site: Optional[str] = None) -> List[Dict]:
        """
        Get all pending feedback items, optionally filtered by site
        
        Args:
            site: Optional site filter ('folklife' or 'festival')
        
        Returns:
            List of pending feedback items
        """
        pending = []
        
        try:
            with open(self.feedback_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['status'] == 'pending':
                        if site is None or row['site'] == site:
                            pending.append(row)
        except FileNotFoundError:
            pass
        
        return pending
    
    def review_feedback(self, timestamp: str, reviewer_notes: str, 
                       action_taken: str, status: str = 'reviewed') -> bool:
        """
        Mark feedback as reviewed by a human moderator
        
        Args:
            timestamp: The timestamp of the feedback to review
            reviewer_notes: Notes from the human reviewer
            action_taken: What action was taken (e.g., 'new_bucket_created', 'reclassified')
            status: New status (default: 'reviewed')
        
        Returns:
            bool: True if feedback was updated successfully
        """
        try:
            # Read all feedback
            feedback_items = []
            with open(self.feedback_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['timestamp'] == timestamp:
                        row['status'] = status
                        row['reviewer_notes'] = reviewer_notes
                        row['action_taken'] = action_taken
                    feedback_items.append(row)
            
            # Write back updated feedback
            with open(self.feedback_file, 'w', newline='') as f:
                if feedback_items:
                    writer = csv.DictWriter(f, fieldnames=feedback_items[0].keys())
                    writer.writeheader()
                    writer.writerows(feedback_items)
            
            print(f"✅ Feedback from {timestamp} marked as reviewed")
            return True
            
        except Exception as e:
            print(f"❌ Error updating feedback: {e}")
            return False
    
    def get_feedback_summary(self) -> Dict:
        """Get a summary of all feedback statistics"""
        try:
            total = 0
            pending = 0
            reviewed = 0
            by_site = {'folklife': 0, 'festival': 0}
            by_type = {'flag': 0, 'correct': 0}
            
            with open(self.feedback_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total += 1
                    by_site[row['site']] += 1
                    by_type[row['feedback_type']] += 1
                    
                    if row['status'] == 'pending':
                        pending += 1
                    elif row['status'] == 'reviewed':
                        reviewed += 1
            
            return {
                'total_feedback': total,
                'pending_review': pending,
                'reviewed': reviewed,
                'by_site': by_site,
                'by_type': by_type
            }
            
        except FileNotFoundError:
            return {
                'total_feedback': 0,
                'pending_review': 0,
                'reviewed': 0,
                'by_site': {'folklife': 0, 'festival': 0},
                'by_type': {'flag': 0, 'correct': 0}
            }

def main():
    """Example usage of the feedback handler"""
    handler = FeedbackHandler()
    
    # Example: Submit some feedback
    handler.submit_feedback(
        site='festival',
        cluster_id='123',
        feedback_type='flag',
        feedback_text='This image has a completely different header layout and should be in a separate cluster.'
    )
    
    handler.submit_feedback(
        site='folklife',
        cluster_id='45',
        feedback_type='correct',
        feedback_text='This is a unique navigation pattern that should have its own layout bucket.'
    )
    
    # Show summary
    summary = handler.get_feedback_summary()
    print("\n📊 Feedback Summary:")
    print(f"Total feedback: {summary['total_feedback']}")
    print(f"Pending review: {summary['pending_review']}")
    print(f"Reviewed: {summary['reviewed']}")
    print(f"By site: {summary['by_site']}")
    print(f"By type: {summary['by_type']}")
    
    # Show pending feedback
    pending = handler.get_pending_feedback()
    if pending:
        print(f"\n⏳ Pending Feedback ({len(pending)} items):")
        for item in pending:
            print(f"  • {item['site']} cluster {item['cluster_id']}: {item['feedback_type']}")
            print(f"    {item['feedback_text'][:100]}...")
            print()

if __name__ == '__main__':
    main()
