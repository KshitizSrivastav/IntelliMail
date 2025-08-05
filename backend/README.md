# IntelliMail Backend

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google OAuth2 Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback

# Security
SECRET_KEY=your_secret_key_here

# Application Configuration
DEBUG=True
```

## Setup Instructions

1. Install dependencies directly:
```bash
pip install -r requirements.txt
```

2. Set up Google OAuth2:
   - Go to Google Cloud Console
   - Create a new project or select existing
   - Enable Gmail API
   - Create OAuth2 credentials
   - Download credentials.json (optional, or use environment variables)

3. Run the server:
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
