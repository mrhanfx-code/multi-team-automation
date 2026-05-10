# Google Cloud Console Setup Guide for MFM Corporation

This guide provides step-by-step instructions for setting up Google Cloud Console and OAuth credentials for the MFM Corporation Multi-Team Automation System.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Google Cloud Console Setup](#google-cloud-console-setup)
3. [OAuth Credentials Creation](#oauth-credentials-creation)
4. [Service Account Configuration](#service-account-configuration)
5. [API Enablement](#api-enablement)
6. [Environment Configuration](#environment-configuration)
7. [Testing Integration](#testing-integration)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have:

- A Google Account with administrative privileges
- A Google Cloud Platform (GCP) project
- Billing enabled on your GCP project
- Basic understanding of Google Cloud services

## Google Cloud Console Setup

### Step 1: Create a New GCP Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "NEW PROJECT"
4. Enter project details:
   - **Project name**: `mfm-corporation-automation`
   - **Organization**: Select your organization (if applicable)
   - **Location**: Choose your preferred location
5. Click "CREATE"

### Step 2: Enable Required APIs

Navigate to "APIs & Services" > "Library" and enable the following APIs:

1. **Google Drive API**
   - Search for "Google Drive API"
   - Click "ENABLE"

2. **Google Sheets API**
   - Search for "Google Sheets API"
   - Click "ENABLE"

3. **Google Calendar API**
   - Search for "Google Calendar API"
   - Click "ENABLE"

4. **Identity and Access Management (IAM) API**
   - Search for "IAM API"
   - Click "ENABLE"

5. **Cloud Resource Manager API**
   - Search for "Cloud Resource Manager API"
   - Click "ENABLE"

### Step 3: Configure OAuth Consent Screen

1. Navigate to "APIs & Services" > "OAuth consent screen"
2. Choose "External" for User Type
3. Click "CREATE"

#### App Information
- **App name**: `MFM Corporation Automation System`
- **User support email**: Your support email address
- **App logo**: Upload your company logo (optional)
- **Application home page**: `https://mfmcorporation.com`
- **Privacy policy URL**: `https://mfmcorporation.com/privacy`
- **Terms of service URL**: `https://mfmcorporation.com/terms`
- **Authorized domain**: `mfmcorporation.com`
- **Developer contact information**: Your email address

#### Scopes
Add the following OAuth scopes:
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/drive.file`
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/calendar`
- `https://www.googleapis.com/auth/userinfo.email`
- `https://www.googleapis.com/auth/userinfo.profile`

#### Test Users
Add test users (your email address) for initial testing.

## OAuth Credentials Creation

### Step 1: Create OAuth 2.0 Client ID

1. Navigate to "APIs & Services" > "Credentials"
2. Click "+ CREATE CREDENTIALS"
3. Select "OAuth client ID"
4. Configure the client:
   - **Application type**: "Web application"
   - **Name**: `MFM Automation Web Client`
   - **Authorized JavaScript origins**: `http://localhost:8000`, `http://localhost:3000`
   - **Authorized redirect URIs**: 
     - `http://localhost:8000/auth/callback`
     - `http://localhost:3000/auth/callback`
     - `https://yourdomain.com/auth/callback`
5. Click "CREATE"

### Step 2: Create Service Account

1. In the "Credentials" page, click "+ CREATE CREDENTIALS"
2. Select "Service account"
3. Configure the service account:
   - **Service account name**: `mfm-automation-service`
   - **Service account ID**: `mfm-automation-service@mfm-corporation-automation.iam.gserviceaccount.com`
   - **Description**: `Service account for MFM Corporation Automation System`
4. Click "CREATE AND CONTINUE"

#### Grant Permissions
- Select role: "Project" > "Editor"
- Click "CONTINUE"

#### Finalize
- Skip adding users (optional)
- Click "DONE"

### Step 3: Generate Service Account Key

1. Find your service account in the list
2. Click on the service account name
3. Go to the "KEYS" tab
4. Click "ADD KEY" > "Create new key"
5. Select key type: "JSON"
6. Click "CREATE"
7. **IMPORTANT**: Download and securely store the JSON key file
8. Rename the file to `service-account-key.json`

## Service Account Configuration

### Step 1: Enable Domain-Wide Delegation

1. Go to [Google Workspace Admin Console](https://admin.google.com/)
2. Navigate to "Security" > "API Controls" > "Domain-wide Delegation"
3. Click "Add New"
4. Enter the following:
   - **Client ID**: From your service account details
   - **OAuth scopes**:
     ```
     https://www.googleapis.com/auth/drive
     https://www.googleapis.com/auth/spreadsheets
     https://www.googleapis.com/auth/calendar
     ```
5. Click "Authorize"

### Step 2: Share Drive Access

1. Open Google Drive
2. Create a new folder named `MFM Corporation Automation`
3. Right-click the folder and select "Share"
4. Add your service account email address
5. Grant "Editor" permissions
6. Click "Send"

## API Enablement

### Verify API Status

1. In Google Cloud Console, go to "APIs & Services" > "Enabled APIs"
2. Verify all required APIs are enabled:
   - ✅ Google Drive API
   - ✅ Google Sheets API
   - ✅ Google Calendar API
   - ✅ IAM API
   - ✅ Cloud Resource Manager API

### API Quotas and Limits

1. Navigate to "APIs & Services" > "Quotas"
2. Review and adjust quotas if necessary:
   - Drive API: 10,000 requests per day
   - Sheets API: 100 requests per minute
   - Calendar API: 10,000 requests per day

## Environment Configuration

### Step 1: Set Up Environment Variables

Create a `.env` file in your project root:

```env
# Google Cloud Configuration
GOOGLE_PROJECT_ID=mfm-corporation-automation
GOOGLE_SERVICE_ACCOUNT_KEY=./service-account-key.json
GOOGLE_OAUTH_CLIENT_ID=your-oauth-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-oauth-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# Google Drive Configuration
GOOGLE_DRIVE_FOLDER_ID=your-drive-folder-id
GOOGLE_DRIVE_ROOT_FOLDER=MFM Corporation Automation

# Google Sheets Configuration
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id

# Google Calendar Configuration
GOOGLE_CALENDAR_ID=your-calendar-id
```

### Step 2: Install Required Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
pip install google-api-python-client google-drive-api
pip install google-api-python-client google-sheets-api
pip install google-api-python-client google-calendar-api
```

### Step 3: Update Configuration Files

Update your `src/config.py` file:

```python
import os
from dotenv import load_dotenv

load_dotenv()

class GoogleCloudConfig:
    PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID')
    SERVICE_ACCOUNT_KEY = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
    OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
    OAUTH_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
    REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
    
    DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    DRIVE_ROOT_FOLDER = os.getenv('GOOGLE_DRIVE_ROOT_FOLDER')
    
    SHEETS_SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
    CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')
```

## Testing Integration

### Step 1: Test Service Account Authentication

Create a test script `test_google_auth.py`:

```python
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

def test_service_account_auth():
    """Test service account authentication"""
    try:
        # Load service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            'service-account-key.json',
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        # Build Drive service
        drive_service = build('drive', 'v3', credentials=credentials)
        
        # Test Drive API
        results = drive_service.files().list(
            pageSize=10,
            fields="files(id, name)"
        ).execute()
        
        files = results.get('files', [])
        print(f"Successfully authenticated! Found {len(files)} files in Drive")
        
        return True
        
    except Exception as e:
        print(f"Authentication failed: {e}")
        return False

if __name__ == "__main__":
    test_service_account_auth()
```

### Step 2: Test OAuth Flow

Create `test_oauth_flow.py`:

```python
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import os

def test_oauth_flow():
    """Test OAuth authentication flow"""
    try:
        # Create OAuth flow
        flow = Flow.from_client_secrets_file(
            'client-secret.json',
            scopes=['https://www.googleapis.com/auth/drive'],
            redirect_uri='http://localhost:8000/auth/callback'
        )
        
        # Generate authorization URL
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        print(f"Go to this URL to authorize the application: {auth_url}")
        print(f"State: {state}")
        
        return auth_url, state
        
    except Exception as e:
        print(f"OAuth flow setup failed: {e}")
        return None, None

if __name__ == "__main__":
    test_oauth_flow()
```

### Step 3: Test API Integration

Create `test_api_integration.py`:

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

def test_drive_integration():
    """Test Google Drive integration"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            'service-account-key.json',
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        drive_service = build('drive', 'v3', credentials=credentials)
        
        # Create a test file
        file_metadata = {
            'name': 'MFM Test File.txt',
            'parents': [os.getenv('GOOGLE_DRIVE_FOLDER_ID')]
        }
        
        media = MediaIoBaseUpload(b'Test content for MFM Corporation', 
                                mimetype='text/plain')
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"Successfully created test file: {file.get('id')}")
        return True
        
    except Exception as e:
        print(f"Drive integration test failed: {e}")
        return False

def test_sheets_integration():
    """Test Google Sheets integration"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            'service-account-key.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        sheets_service = build('sheets', 'v4', credentials=credentials)
        
        # Test reading spreadsheet
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID'),
            range='Sheet1!A1:D10'
        ).execute()
        
        rows = result.get('values', [])
        print(f"Successfully read {len(rows)} rows from spreadsheet")
        return True
        
    except Exception as e:
        print(f"Sheets integration test failed: {e}")
        return False

if __name__ == "__main__":
    test_drive_integration()
    test_sheets_integration()
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Insufficient Permission" Error
**Problem**: Service account lacks necessary permissions
**Solution**: 
- Verify service account has "Editor" role
- Check domain-wide delegation is properly configured
- Ensure Drive folder is shared with service account

#### 2. "Redirect URI Mismatch" Error
**Problem**: OAuth redirect URI doesn't match configuration
**Solution**:
- Verify redirect URI in Google Cloud Console matches your application
- Check for trailing slashes in URLs
- Ensure HTTP vs HTTPS consistency

#### 3. "API Not Enabled" Error
**Problem**: Required APIs are not enabled
**Solution**:
- Go to "APIs & Services" > "Library"
- Enable all required APIs listed in Step 2

#### 4. "Invalid Credentials" Error
**Problem**: Service account key file is invalid or corrupted
**Solution**:
- Download a new service account key
- Verify the JSON file is properly formatted
- Check file permissions

#### 5. "Quota Exceeded" Error
**Problem**: API quota limits exceeded
**Solution**:
- Go to "APIs & Services" > "Quotas"
- Request quota increases if needed
- Implement rate limiting in your application

### Debugging Tips

1. **Enable API Logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check Service Account Status**:
   ```bash
   gcloud auth activate-service-account --key-file=service-account-key.json
   gcloud auth list
   ```

3. **Verify API Access**:
   ```bash
   gcloud services list --enabled
   ```

4. **Test with Google APIs Explorer**:
   Visit [Google APIs Explorer](https://developers.google.com/apis-explorer) to test APIs directly

## Security Best Practices

1. **Key Management**:
   - Store service account keys securely
   - Rotate keys regularly
   - Use different keys for different environments

2. **Access Control**:
   - Follow principle of least privilege
   - Use service accounts only for automated processes
   - Regularly review permissions

3. **Monitoring**:
   - Enable Cloud Audit Logging
   - Monitor API usage and costs
   - Set up alerts for unusual activity

## Next Steps

After completing the Google Cloud Console setup:

1. Update your application configuration with the new credentials
2. Test the integration using the provided test scripts
3. Implement proper error handling and retry logic
4. Set up monitoring and alerting
5. Document your configuration for team members

For additional support, refer to:
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Google Drive API Documentation](https://developers.google.com/drive/api)
- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
