import os
import json
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from email_service import EmailService


class EmailReasoning:
    """
    A reasoning module to analyze email content and determine appropriate actions.
    """

    def __init__(self):
        # Keywords for different email types
        self.informational_keywords = [
            'information', 'update', 'notification', 'alert', 'reminder', 'report',
            'summary', 'overview', 'details', 'schedule', 'calendar', 'meeting',
            'agenda', 'announcement', 'news', 'newsletter', 'digest'
        ]

        self.reply_keywords = [
            'reply', 'response', 'answer', 'respond', 'feedback', 'opinion',
            'thoughts', 'question', 'asked', 'need', 'require', 'help', 'assistance',
            'please', 'could you', 'would you', 'can you', 'follow up', 'get back',
            'contact', 'reach out'
        ]

        self.promotional_keywords = [
            'offer', 'discount', 'sale', 'promotion', 'deal', 'free', 'trial',
            'buy', 'purchase', 'limited time', 'exclusive', 'ad', 'advertising',
            'sponsored', 'marketing', 'campaign', 'special', 'price', 'buy now',
            'click here', 'sign up', 'register'
        ]

        self.urgent_keywords = [
            'urgent', 'asap', 'immediately', 'now', 'emergency', 'critical',
            'crucial', 'important', 'deadline', 'today', '24 hours', '48 hours',
            'time sensitive', 'expedited', 'rush', 'priority', 'high priority',
            'action required', 'attention required', 'immediate attention'
        ]

    def analyze_email(self, email_data: Dict[str, str]) -> Dict:
        """
        Analyze an email and determine its type, urgency, and required actions.
        """
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        full_content = f"{subject} {body}"

        # Determine email type
        email_type = self._determine_email_type(full_content)

        # Determine urgency
        urgency = self._determine_urgency(full_content)

        # Determine required action
        action = self._determine_required_action(full_content, email_type)

        # Generate proposed response
        proposed_response = self._generate_proposed_response(email_type, action)

        # Determine next steps
        next_steps = self._generate_next_steps(email_type, action)

        return {
            'email_type': email_type,
            'urgency': urgency,
            'required_action': action,
            'proposed_response': proposed_response,
            'next_steps': next_steps
        }

    def _determine_email_type(self, content: str) -> str:
        """
        Determine the type of email based on content.
        """
        score_info = sum(1 for keyword in self.informational_keywords if keyword in content)
        score_reply = sum(1 for keyword in self.reply_keywords if keyword in content)
        score_promo = sum(1 for keyword in self.promotional_keywords if keyword in content)

        # If multiple types detected, prioritize based on context
        if score_reply > score_info and score_reply > score_promo:
            return "Requires Reply"
        elif score_promo > score_info and score_promo > score_reply:
            return "Promotional"
        elif score_info > 0 or 'information' in content or 'update' in content:
            return "Informational"
        else:
            # If no clear type, determine based on other factors
            if any(keyword in content for keyword in self.reply_keywords):
                return "Requires Reply"
            elif 'urgent' in content or 'asap' in content:
                return "Requires Reply"
            else:
                return "General"

    def _determine_urgency(self, content: str) -> str:
        """
        Determine the urgency level of the email.
        """
        urgency_score = sum(1 for keyword in self.urgent_keywords if keyword in content)

        if urgency_score >= 3:
            return "High"
        elif urgency_score >= 1:
            return "Medium"
        else:
            return "Low"

    def _determine_required_action(self, content: str, email_type: str) -> str:
        """
        Determine the required action based on email type and content.
        """
        if email_type == "Requires Reply":
            if 'urgent' in content or 'asap' in content:
                return "Immediate Response Required"
            else:
                return "Response Required"
        elif email_type == "Promotional":
            return "Review and Decide"
        elif email_type == "Informational":
            return "Read and File"
        else:
            if any(keyword in content for keyword in self.urgent_keywords):
                return "Review and Respond Urgently"
            elif any(keyword in content for keyword in self.reply_keywords):
                return "Consider Response"
            else:
                return "Read and File"

    def _generate_proposed_response(self, email_type: str, action: str) -> str:
        """
        Generate a proposed response based on email type and required action.
        """
        if "Response Required" in action:
            return "Draft a polite and informative response addressing the sender's concerns/questions"
        elif "Review and Decide" in action:
            return "Review promotional content and decide whether to engage or unsubscribe"
        elif "Read and File" in action:
            return "Read the information and file for reference"
        elif "Review and Respond Urgently" in action:
            return "Quickly assess and respond with priority"
        elif "Consider Response" in action:
            return "Evaluate whether a response is necessary and appropriate"
        else:
            return "No specific response required"

    def _generate_next_steps(self, email_type: str, action: str) -> List[str]:
        """
        Generate next steps based on email type and required action.
        """
        steps = []

        if "Response Required" in action:
            steps.extend([
                "Analyze specific requests in email",
                "Draft appropriate response",
                "Review response for clarity and completeness",
                "Send response",
                "File email in appropriate folder"
            ])
        elif "Review and Decide" in action:
            steps.extend([
                "Evaluate promotional offer",
                "Determine relevance to business needs",
                "Decide whether to accept, reject, or investigate further",
                "Take appropriate action",
                "File email in appropriate folder"
            ])
        elif "Read and File" in action:
            steps.extend([
                "Read and acknowledge information",
                "Determine if any follow-up action needed",
                "File email for reference",
                "Update relevant records if necessary"
            ])
        elif "Review and Respond Urgently" in action:
            steps.extend([
                "Quickly assess content and priority",
                "Draft immediate response if needed",
                "Send urgent response",
                "File email with high-priority marker"
            ])
        else:
            steps.extend([
                "Review email content",
                "Determine appropriate action",
                "Execute required action",
                "File email in appropriate location"
            ])

        return steps


class Orchestrator:
    """
    Orchestrates the workflow between Needs_Action, Plans, Pending_Approval, and Approved folders.
    """

    def __init__(self):
        self.needs_action_dir = Path('Needs_Action')
        self.plans_dir = Path('Plans')
        self.pending_approval_dir = Path('Pending_Approval')
        self.approved_dir = Path('Approved')  # This will contain manually approved files
        self.done_dir = Path('Done')
        self.logs_dir = Path('Logs')

        # Initialize reasoning module
        self.reasoning = EmailReasoning()

        # Initialize email service
        self.email_service = EmailService()

        self._ensure_directories()
        self.dashboard_path = Path('Dashboard.md')

        # Set up logging
        self._setup_logging()

    def _setup_logging(self):
        """Set up logging to directory"""
        self.logs_dir.mkdir(exist_ok=True)

        log_file = self.logs_dir / f"orchestrator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        for directory in [self.needs_action_dir, self.plans_dir,
                         self.pending_approval_dir, self.done_dir,
                         self.approved_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _read_email_file(self, file_path: Path) -> Dict[str, str]:
        """Read an email file and extract headers and content."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Initialize email data
        email_data = {
            'from': 'Unknown',
            'to': 'Unknown',
            'date': 'Unknown',
            'subject': 'No Subject',
            'body': 'No body content found.',
            'full_content': content
        }

        # Extract headers if present
        lines = content.split('\n')
        in_body = False
        body_lines = []

        for line in lines:
            if line.strip() == '---' and not in_body:
                in_body = True
                continue

            if not in_body and line.startswith('From:'):
                email_data['from'] = line.replace('From:', '').strip()
            elif not in_body and line.startswith('To:'):
                email_data['to'] = line.replace('To:', '').strip()
            elif not in_body and line.startswith('Date:'):
                email_data['date'] = line.replace('Date:', '').strip()
            elif not in_body and line.startswith('Subject:'):
                email_data['subject'] = line.replace('Subject:', '').strip()
            elif in_body:
                body_lines.append(line)

        if body_lines:
            email_data['body'] = '\n'.join(body_lines).strip()

        return email_data

    def _generate_plan(self, email_data: Dict[str, str]) -> Dict:
        """Generate a structured plan based on the email content using the reasoning module."""
        # Use the reasoning module to analyze the email
        reasoning_result = self.reasoning.analyze_email(email_data)

        # Generate email ID
        email_id = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        plan = {
            "email_id": email_id,
            "original_file": email_data['subject'],
            "received_from": email_data['from'],
            "received_date": email_data['date'],
            "email_subject": email_data['subject'],
            "email_body": email_data['body'],
            "email_type": reasoning_result['email_type'],
            "urgency": reasoning_result['urgency'],
            "required_action": reasoning_result['required_action'],
            "proposed_response": reasoning_result['proposed_response'],
            "next_steps": reasoning_result['next_steps'],
            "action_required": "send_email" if "Response Required" in reasoning_result['required_action'] else "process",
            "action_description": reasoning_result['proposed_response'],
            "priority": reasoning_result['urgency'].lower(),  # Could be determined based on content
            "generated_at": datetime.now().isoformat()
        }

        return plan

    def _save_plan(self, plan: Dict, original_filename: str) -> Path:
        """Save the plan as a markdown file in the Plans folder."""
        # Clean the filename for the plan
        clean_name = re.sub(r'[<>:"/\\|?*]', '_', original_filename.split('.')[0])
        if len(clean_name) > 100:
            clean_name = clean_name[:100]

        plan_filename = f"plan_{clean_name}.md"
        plan_path = self.plans_dir / plan_filename

        # Generate structured Plan.md content with the requested format
        next_steps_str = "\n".join([f"    - {step}" for step in plan['next_steps']])

        plan_content = f"""# PLAN

## Email Type: {plan['email_type']}
## Urgency: {plan['urgency']}
## Required Action: {plan['required_action']}
## Proposed Response: {plan['proposed_response']}
## Next Steps:
{next_steps_str}

---

## Original Email Details:
- **Subject**: {plan['email_subject']}
- **From**: {plan['received_from']}
- **Date**: {plan['received_date']}

## Email Content:
{plan['email_body']}

## Analysis Summary:
- **ID**: {plan['email_id']}
- **Generated at**: {plan['generated_at']}
"""

        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)

        return plan_path

    def _create_approval_file(self, plan: Dict, original_filename: str) -> Path:
        """Create an approval file in the Pending_Approval folder with correct format."""
        # Create a filename based on the original file
        clean_name = re.sub(r'[<>:"/\\|?*]', '_', original_filename.split('.')[0])
        approval_filename = f"{clean_name}_approval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        approval_path = self.pending_approval_dir / approval_filename

        # Format the approval file according to requirements
        approval_content = f"""Action: Send Email
To: {plan['received_from'].split('<')[-1].replace('>', '') if '<' in plan['received_from'] else plan['received_from']}
Subject: Re: {plan['email_subject']}
Body: {plan['email_body']}

Status: WAITING_APPROVAL
Email_ID: {plan['email_id']}
Original_File: {original_filename}
"""

        with open(approval_path, 'w', encoding='utf-8') as f:
            f.write(approval_content)

        return approval_path

    def _move_to_done(self, file_path: Path, prefix: str = ""):
        """Move the original file to the Done folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if prefix:
            done_filename = f"{prefix}_{file_path.stem}_{timestamp}{file_path.suffix}"
        else:
            done_filename = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        done_path = self.done_dir / done_filename
        file_path.rename(done_path)

    def _update_dashboard(self, action: str, details: str):
        """Update the Dashboard.md file with the latest action."""
        dashboard_content = f"""# Dashboard

## Activity Log

### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {action}

{details}

---
\n"""

        # Read existing content if file exists
        existing_content = ""
        if self.dashboard_path.exists():
            with open(self.dashboard_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()

        # Write new content with existing content appended
        with open(self.dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_content + existing_content)

    def process_needs_action(self):
        """Process all files in the Needs_Action folder."""
        files = list(self.needs_action_dir.glob('*.*'))  # Handle all file types

        if not files:
            self.logger.info("No files in Needs_Action folder to process.")
            print("No files in Needs_Action folder to process.")
            return

        self.logger.info(f"Processing {len(files)} files from Needs_Action folder...")
        print(f"Processing {len(files)} files from Needs_Action folder...")

        for file_path in files:
            try:
                # Read the email file
                email_data = self._read_email_file(file_path)

                # Generate plan using reasoning module
                plan = self._generate_plan(email_data)

                # Save plan
                plan_path = self._save_plan(plan, file_path.name)
                safe_plan_name = plan_path.name.encode('ascii', 'replace').decode('ascii')
                print(f"Generated plan: {safe_plan_name}")
                self.logger.info(f"Generated plan: {safe_plan_name}")

                # Check if action requires sending email
                if plan['action_required'] == 'send_email':
                    # Create approval file in the correct format
                    approval_path = self._create_approval_file(plan, file_path.name)
                    safe_approval_name = approval_path.name.encode('ascii', 'replace').decode('ascii')
                    print(f"Created approval file: {safe_approval_name}")
                    self.logger.info(f"Created approval file: {safe_approval_name}")

                # Move original file to Done
                self._move_to_done(file_path, "processed")

                # Update dashboard
                self._update_dashboard(
                    action="Plan Generated",
                    details=f"Processed {file_path.name}\nPlan: {plan['action_description']}\nStatus: {'Approval Required' if plan['action_required'] == 'send_email' else 'Processed'}"
                )

            except Exception as e:
                safe_file_name = file_path.name.encode('ascii', 'replace').decode('ascii')
                safe_error_msg = str(e).encode('ascii', 'replace').decode('ascii') if e else 'Unknown error'
                print(f"Error processing {safe_file_name}: {safe_error_msg}")
                self.logger.error(f"Error processing {file_path.name}: {str(e)}")
                self._update_dashboard(
                    action="Error Processing",
                    details=f"Error processing {file_path.name}: {str(e)}"
                )

    def process_pending_approval(self):
        """Process all files in the Pending_Approval folder that have been manually approved."""
        approval_files = list(self.pending_approval_dir.glob('*.txt'))

        if not approval_files:
            self.logger.info("No files in Pending_Approval folder to process.")
            print("No files in Pending_Approval folder to process.")
            return

        self.logger.info(f"Checking {len(approval_files)} files in Pending_Approval folder...")
        print(f"Checking {len(approval_files)} files in Pending_Approval folder...")

        for approval_file in approval_files:
            try:
                # Read the approval file to check status
                with open(approval_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if status is APPROVED
                status_line = None
                for line in content.split('\n'):
                    if line.startswith('Status:'):
                        status_line = line
                        break

                if status_line and 'APPROVED' in status_line:
                    # Extract email details
                    lines = content.split('\n')
                    to_email = "default@example.com"  # Default fallback
                    subject = "Default Subject"  # Default fallback
                    body = ""  # Default fallback
                    body_started = False

                    for line in lines:
                        if line.startswith('To:'):
                            to_email = line.replace('To:', '').strip()
                        elif line.startswith('Subject:'):
                            subject = line.replace('Subject:', '').strip()
                        elif line.strip() == 'Body:':
                            body_started = True
                            continue
                        elif line.startswith('Status:') or line.startswith('Email_ID:') or line.startswith('Original_File:'):
                            body_started = False
                            continue
                        elif body_started:
                            body += line + '\n'

                    # Clean up the body
                    body = body.strip()

                    # Send the email using EmailService
                    print(f"Sending email to: {to_email}")
                    print(f"Subject: {subject}")
                    success = self.email_service.send_email(to_email, subject, body)

                    if success:
                        print(f"Email sent successfully for: {subject}")
                        # Move to Done folder
                        self._move_to_done(approval_file, "sent")
                        self.logger.info(f"Email sent and file moved to Done: {approval_file.name}")

                        # Update dashboard
                        self._update_dashboard(
                            action="Email Sent",
                            details=f"Sent email to {to_email}\nSubject: {subject}"
                        )
                    else:
                        print(f"Failed to send email for: {subject}")
                        # We keep the file in Pending_Approval if sending fails
                        self.logger.error(f"Failed to send email for: {subject}")
                        self._update_dashboard(
                            action="Email Send Failed",
                            details=f"Failed to send email to {to_email}\nSubject: {subject}"
                        )

            except Exception as e:
                print(f"Error processing approval file {approval_file.name}: {e}")
                self.logger.error(f"Error processing approval file {approval_file.name}: {str(e)}")
                self._update_dashboard(
                    action="Error Processing Approval",
                    details=f"Error processing approval file {approval_file.name}: {str(e)}"
                )

    def process_approved(self):
        """Process all files in the Approved folder to send emails."""
        # This method is kept for compatibility but the main processing happens in process_pending_approval
        # The Approved folder can be used for manually moved files
        approved_files = list(self.approved_dir.glob('*_approval_*.txt'))

        if not approved_files:
            self.logger.info("No files in Approved folder to process.")
            print("No files in Approved folder to process.")
            return

        self.logger.info(f"Processing {len(approved_files)} approved files...")
        print(f"Processing {len(approved_files)} approved files...")

        for approval_file in approved_files:
            try:
                # Read the approval file
                with open(approval_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract email details
                lines = content.split('\n')
                to_email = "default@example.com"  # Default fallback
                subject = "Default Subject"  # Default fallback
                body = ""  # Default fallback
                body_started = False

                for line in lines:
                    if line.startswith('To:'):
                        to_email = line.replace('To:', '').strip()
                    elif line.startswith('Subject:'):
                        subject = line.replace('Subject:', '').strip()
                    elif line.strip() == 'Body:':
                        body_started = True
                        continue
                    elif line.startswith('Status:') or line.startswith('Email_ID:') or line.startswith('Original_File:'):
                        body_started = False
                        continue
                    elif body_started:
                        body += line + '\n'

                # Clean up the body
                body = body.strip()

                # Send the email using EmailService
                print(f"Sending email to: {to_email}")
                print(f"Subject: {subject}")
                success = self.email_service.send_email(to_email, subject, body)

                if success:
                    print(f"Email sent successfully for: {subject}")
                    # Move to Done folder
                    self._move_to_done(approval_file, "sent")
                    self.logger.info(f"Email sent and file moved to Done: {approval_file.name}")

                    # Update dashboard
                    self._update_dashboard(
                        action="Email Sent",
                        details=f"Sent email to {to_email}\nSubject: {subject}"
                    )
                else:
                    print(f"Failed to send email for: {subject}")
                    # Move back to Pending_Approval if sending fails
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    failed_filename = f"failed_{approval_file.stem}_{timestamp}{approval_file.suffix}"
                    failed_path = self.pending_approval_dir / failed_filename
                    approval_file.rename(failed_path)
                    self.logger.error(f"Failed to send email for: {subject}, moved to Pending_Approval")
                    self._update_dashboard(
                        action="Email Send Failed",
                        details=f"Failed to send email to {to_email}\nSubject: {subject}"
                    )

            except Exception as e:
                print(f"Error processing approved file {approval_file.name}: {e}")
                self.logger.error(f"Error processing approved file {approval_file.name}: {str(e)}")
                self._update_dashboard(
                    action="Error Processing Approved",
                    details=f"Error processing approved file {approval_file.name}: {str(e)}"
                )

    def run(self):
        """Run the orchestrator to process both workflow paths."""
        print("Starting Orchestrator...")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print("\nProcessing Needs_Action folder...")
        self.process_needs_action()

        print("\nProcessing Pending_Approval folder...")
        self.process_pending_approval()

        print("\nProcessing Approved folder...")
        self.process_approved()

        print("\nOrchestrator completed.")

        # Update dashboard with completion
        self._update_dashboard(
            action="Orchestrator Run",
            details="Completed processing Needs_Action, Pending_Approval and Approved folders"
        )


def main():
    """Main function to run the orchestrator."""
    orchestrator = Orchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()