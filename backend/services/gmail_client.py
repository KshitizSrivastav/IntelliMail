from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
import html2text
from datetime import datetime, timezone
import re

class GmailService:
    def __init__(self, access_token: str):
        self.credentials = Credentials(token=access_token)
        self.service = build('gmail', 'v1', credentials=self.credentials)
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True
    
    def get_emails(self, max_results: int = 10, query: Optional[str] = None) -> List[Dict]:
        """
        Fetch emails from Gmail inbox
        """
        try:
            # Build query
            search_query = query if query else 'in:inbox'
            
            # Get list of messages
            results = self.service.users().messages().list(
                userId='me',
                q=search_query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = self._get_email_data(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
        except Exception as e:
            raise Exception(f"Failed to fetch emails: {str(e)}")
    
    def get_email_detail(self, email_id: str) -> Dict:
        """
        Get detailed information about a specific email
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()
            
            return self._parse_email_detail(message)
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
        except Exception as e:
            raise Exception(f"Failed to fetch email detail: {str(e)}")
    
    def get_thread_emails(self, thread_id: str) -> List[Dict]:
        """
        Get all emails in a thread
        """
        try:
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id,
                format='full'
            ).execute()
            
            emails = []
            for message in thread.get('messages', []):
                email_data = self._parse_email_detail(message)
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
        except Exception as e:
            raise Exception(f"Failed to fetch thread emails: {str(e)}")
    
    def send_email(self, to: str, subject: str, body: str, reply_to_id: Optional[str] = None) -> Dict:
        """
        Send an email through Gmail API
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['To'] = to
            message['Subject'] = subject
            
            # Add body
            text_part = MIMEText(body, 'plain', 'utf-8')
            message.attach(text_part)
            
            # If this is a reply, add necessary headers
            if reply_to_id:
                original_message = self.service.users().messages().get(
                    userId='me',
                    id=reply_to_id,
                    format='full'
                ).execute()
                
                # Add reply headers
                headers = original_message.get('payload', {}).get('headers', [])
                message_id = next((h['value'] for h in headers if h['name'].lower() == 'message-id'), None)
                references = next((h['value'] for h in headers if h['name'].lower() == 'references'), '')
                
                if message_id:
                    message['In-Reply-To'] = message_id
                    message['References'] = f"{references} {message_id}".strip()
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send message
            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return result
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")
    
    def mark_as_read(self, email_id: str) -> bool:
        """
        Mark an email as read
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            return True
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
        except Exception as e:
            raise Exception(f"Failed to mark email as read: {str(e)}")
    
    def _get_email_data(self, message_id: str) -> Optional[Dict]:
        """
        Get basic email data for list view
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            
            headers = message.get('payload', {}).get('headers', [])
            
            # Extract header information
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            # Check if email is read
            label_ids = message.get('labelIds', [])
            is_read = 'UNREAD' not in label_ids
            
            return {
                'id': message['id'],
                'thread_id': message['threadId'],
                'sender': self._extract_email_address(sender),
                'subject': subject,
                'date': self._parse_date(date),
                'snippet': message.get('snippet', ''),
                'is_read': is_read
            }
            
        except Exception as e:
            print(f"Error processing email {message_id}: {str(e)}")
            return None
    
    def _parse_email_detail(self, message: Dict) -> Dict:
        """
        Parse detailed email information
        """
        try:
            headers = message.get('payload', {}).get('headers', [])
            
            # Extract header information
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
            recipient = next((h['value'] for h in headers if h['name'].lower() == 'to'), 'Unknown')
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            # Extract body
            body = self._extract_body(message['payload'])
            
            # Check if email is read
            label_ids = message.get('labelIds', [])
            is_read = 'UNREAD' not in label_ids
            
            return {
                'id': message['id'],
                'thread_id': message['threadId'],
                'sender': self._extract_email_address(sender),
                'recipient': self._extract_email_address(recipient),
                'subject': subject,
                'date': self._parse_date(date),
                'body': body,
                'is_read': is_read
            }
            
        except Exception as e:
            raise Exception(f"Failed to parse email detail: {str(e)}")
    
    def _extract_body(self, payload: Dict) -> str:
        """
        Extract email body from payload
        """
        try:
            body = ""
            
            if 'parts' in payload:
                # Multipart message
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
                    elif part['mimeType'] == 'text/html':
                        if 'data' in part['body']:
                            html_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            body = self.html_converter.handle(html_body)
                            # Only use HTML if no plain text is found
                            if not body.strip():
                                continue
            else:
                # Simple message
                if payload['mimeType'] == 'text/plain':
                    if 'data' in payload['body']:
                        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
                elif payload['mimeType'] == 'text/html':
                    if 'data' in payload['body']:
                        html_body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
                        body = self.html_converter.handle(html_body)
            
            # Clean up the body text
            body = self._clean_body_text(body)
            
            return body
            
        except Exception as e:
            return f"Error extracting body: {str(e)}"
    
    def _extract_email_address(self, email_string: str) -> str:
        """
        Extract email address from string like 'Name <email@domain.com>'
        """
        try:
            # Use regex to extract email from format "Name <email@domain.com>"
            match = re.search(r'<([^>]+)>', email_string)
            if match:
                return match.group(1)
            
            # If no angle brackets, assume the whole string is the email
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email_string)
            if email_match:
                return email_match.group(0)
            
            return email_string
            
        except Exception:
            return email_string
    
    def _parse_date(self, date_string: str) -> str:
        """
        Parse and format date string
        """
        try:
            # Gmail date format parsing could be complex, for now return as is
            # In production, you'd want to parse this properly
            return date_string
            
        except Exception:
            return date_string
    
    def _clean_body_text(self, body: str) -> str:
        """
        Clean up email body text
        """
        try:
            # Remove excessive whitespace
            body = re.sub(r'\n\s*\n', '\n\n', body)
            body = re.sub(r'[ \t]+', ' ', body)
            
            # Remove common email signatures and footers
            body = re.sub(r'\n--\s*\n.*', '', body, flags=re.DOTALL)
            
            return body.strip()
            
        except Exception:
            return body
