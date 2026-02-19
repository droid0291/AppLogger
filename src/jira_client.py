import requests
from requests.auth import HTTPBasicAuth
import json

class JiraClient:
    def __init__(self, jira_url, email, api_token, project_key):
        """
        Initialize JIRA client.
        
        Args:
            jira_url: JIRA base URL (e.g., 'https://yourcompany.atlassian.net')
            email: Your JIRA account email
            api_token: JIRA API token (generate from account settings)
            project_key: Project key (e.g., 'PROJ')
        """
        self.jira_url = jira_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.project_key = project_key
        self.auth = HTTPBasicAuth(email, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def create_bug(self, summary, description, priority="Medium", labels=None, attachments=None):
        """
        Create a bug ticket in JIRA.
        
        Args:
            summary: Bug title
            description: Detailed description (can use JIRA markdown)
            priority: Bug priority (Critical/High/Medium/Low)
            labels: List of labels/tags
            attachments: List of file paths to attach
        
        Returns:
            Issue key (e.g., 'PROJ-123') if successful, None otherwise
        """
        url = f"{self.jira_url}/rest/api/3/issue"
        
        payload = {
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {
                    "name": "Bug"
                },
                "priority": {
                    "name": priority
                }
            }
        }
        
        if labels:
            payload["fields"]["labels"] = labels
        
        try:
            response = requests.post(
                url,
                data=json.dumps(payload),
                headers=self.headers,
                auth=self.auth
            )
            
            if response.status_code == 201:
                issue_key = response.json()['key']
                print(f"Bug created: {issue_key}")
                
                # Attach files if provided
                if attachments:
                    self.add_attachments(issue_key, attachments)
                
                return issue_key
            else:
                print(f"Failed to create bug: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error creating JIRA bug: {e}")
            return None

    def add_attachments(self, issue_key, file_paths):
        """Add attachments to an existing JIRA issue."""
        url = f"{self.jira_url}/rest/api/3/issue/{issue_key}/attachments"
        
        headers = {
            "Accept": "application/json",
            "X-Atlassian-Token": "no-check"
        }
        
        for file_path in file_paths:
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': f}
                    response = requests.post(
                        url,
                        headers=headers,
                        files=files,
                        auth=self.auth
                    )
                    
                    if response.status_code == 200:
                        print(f"Attached: {file_path}")
                    else:
                        print(f"Failed to attach {file_path}: {response.text}")
            except Exception as e:
                print(f"Error attaching {file_path}: {e}")

    def format_bug_description(self, steps, logs_analysis, device_info, video_path=None):
        """Format a comprehensive bug description for JIRA."""
        description = f"""
*Automated Bug Report*

h3. Steps to Reproduce:
{steps}

h3. Device Information:
* Model: {device_info.get('model', 'N/A')}
* Android Version: {device_info.get('android_version', 'N/A')}
* Build: {device_info.get('build', 'N/A')}

h3. Log Analysis (AI-Generated):
{logs_analysis}

"""
        if video_path:
            description += f"\nh3. Video Recording:\nSee attached video: {video_path}\n"
        
        return description
