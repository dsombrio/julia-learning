#!/usr/bin/env python3
import json, subprocess, sys

# Get access token
token_result = subprocess.run([
    'curl', '-s', '-X', 'POST',
    'https://login.microsoftonline.com/3ac44adf-88d3-4ffe-aa18-d7ac71dc866f/oauth2/v2.0/token',
    '-H', 'Content-Type: application/x-www-form-urlencoded',
    '-d', 'client_id=af03f985-1424-465a-bdbf-0cee6b59743b&client_secret=yx58Q~ztCwAayJ3XO5650qc9N1cNcXmLbSAfTbRl&grant_type=client_credentials&scope=https://graph.microsoft.com/.default'
], capture_output=True, text=True)

token_data = json.loads(token_result.stdout)
access_token = token_data['access_token']

# Read HTML content
with open('/Users/tradbot/.openclaw/workspace/scripts/daily_brief_email.html', 'r') as f:
    html_content = f.read()

# Build email payload
payload = {
    "message": {
        "subject": "Daily Brief - April 30, 2026",
        "body": {"contentType": "HTML", "content": html_content},
        "toRecipients": [{"emailAddress": {"address": "david@traditionsales.com"}}]
    }
}

payload_str = json.dumps(payload)

# Send email
result = subprocess.run([
    'curl', '-s', '-X', 'POST',
    'https://graph.microsoft.com/v1.0/users/tradbot@traditionsales.com/sendMail',
    '-H', f'Authorization: Bearer {access_token}',
    '-H', 'Content-Type: application/json',
    '-d', payload_str
], capture_output=True, text=True)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)