#!/usr/bin/env python3
"""
Feedback Reviewer - Admin Interface for Layout Classification

This script provides a simple command-line interface for human moderators
to review user feedback and take action on misclassified images.
"""

import csv
from pathlib import Path
from feedback_handler import FeedbackHandler

class FeedbackReviewer:
    def __init__(self):
        self.handler = FeedbackHandler()
    
    def show_pending_feedback(self):
        """Display all pending feedback items"""
        pending = self.handler.get_pending_feedback()
        
        if not pending:
            print("✅ No pending feedback to review!")
            return
        
        print(f"\n⏳ Pending Feedback ({len(pending)} items):")
        print("=" * 80)
        
        for i, item in enumerate(pending, 1):
            print(f"\n{i}. {item['site'].upper()} - Cluster {item['cluster_id']}")
            print(f"   Type: {item['feedback_type'].upper()}")
            print(f"   Submitted: {item['timestamp']}")
            print(f"   Feedback: {item['feedback_text']}")
            print("-" * 40)
    
    def review_feedback(self):
        """Interactive feedback review process"""
        pending = self.handler.get_pending_feedback()
        
        if not pending:
            print("✅ No pending feedback to review!")
            return
        
        while pending:
            self.show_pending_feedback()
            
            try:
                choice = input(f"\nSelect feedback to review (1-{len(pending)}) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    break
                
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(pending):
                    self._process_feedback(pending[choice_idx])
                    # Remove processed feedback from list
                    pending.pop(choice_idx)
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except ValueError:
                print("❌ Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\n👋 Review session ended.")
                break
    
    def _process_feedback(self, feedback_item):
        """Process a single feedback item"""
        print(f"\n🔍 Reviewing: {feedback_item['site'].upper()} Cluster {feedback_item['cluster_id']}")
        print(f"Type: {feedback_item['feedback_type']}")
        print(f"Feedback: {feedback_item['feedback_text']}")
        print("\n" + "=" * 60)
        
        # Get reviewer notes
        notes = input("Reviewer notes: ").strip()
        
        # Get action taken
        print("\nPossible actions:")
        print("1. new_bucket_created - Created new layout bucket")
        print("2. reclassified - Moved to existing bucket")
        print("3. no_action - No changes needed")
        print("4. invalid_feedback - User feedback was incorrect")
        
        action_choice = input("Select action (1-4): ").strip()
        
        action_map = {
            '1': 'new_bucket_created',
            '2': 'reclassified', 
            '3': 'no_action',
            '4': 'invalid_feedback'
        }
        
        action_taken = action_map.get(action_choice, 'unknown')
        
        # Mark as reviewed
        success = self.handler.review_feedback(
            timestamp=feedback_item['timestamp'],
            reviewer_notes=notes,
            action_taken=action_taken
        )
        
        if success:
            print(f"✅ Feedback marked as reviewed with action: {action_taken}")
        else:
            print("❌ Failed to update feedback status")
    
    def show_statistics(self):
        """Display feedback statistics"""
        summary = self.handler.get_feedback_summary()
        
        print("\n📊 Feedback Statistics:")
        print("=" * 40)
        print(f"Total feedback: {summary['total_feedback']}")
        print(f"Pending review: {summary['pending_review']}")
        print(f"Reviewed: {summary['reviewed']}")
        print(f"\nBy site:")
        for site, count in summary['by_site'].items():
            print(f"  {site.capitalize()}: {count}")
        print(f"\nBy type:")
        for ftype, count in summary['by_type'].items():
            print(f"  {ftype.capitalize()}: {count}")
    
    def export_reviewed_feedback(self, output_file: str = "reviewed_feedback.csv"):
        """Export reviewed feedback to CSV for analysis"""
        try:
            reviewed_items = []
            
            with open(self.handler.feedback_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['status'] == 'reviewed':
                        reviewed_items.append(row)
            
            if not reviewed_items:
                print("❌ No reviewed feedback to export")
                return
            
            output_path = Path(output_file)
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=reviewed_items[0].keys())
                writer.writeheader()
                writer.writerows(reviewed_items)
            
            print(f"✅ Exported {len(reviewed_items)} reviewed feedback items to {output_path}")
            
        except Exception as e:
            print(f"❌ Error exporting feedback: {e}")

def main():
    """Main feedback review interface"""
    reviewer = FeedbackReviewer()
    
    while True:
        print("\n🔍 Layout Classification Feedback Reviewer")
        print("=" * 50)
        print("1. Show pending feedback")
        print("2. Review feedback")
        print("3. Show statistics")
        print("4. Export reviewed feedback")
        print("5. Quit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            reviewer.show_pending_feedback()
        elif choice == '2':
            reviewer.review_feedback()
        elif choice == '3':
            reviewer.show_statistics()
        elif choice == '4':
            output_file = input("Output filename (default: reviewed_feedback.csv): ").strip()
            if not output_file:
                output_file = "reviewed_feedback.csv"
            reviewer.export_reviewed_feedback(output_file)
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == '__main__':
    main()
