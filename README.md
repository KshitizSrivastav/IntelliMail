# IntelliMail - AI-Powered Email Assistant

IntelliMail is a full-stack web application that uses Generative AI to summarize long email threads and generate intelligent replies based on tone and context. It integrates Google Gmail API for real-time email access and OpenAI's GPT-4 for summarization and response generation.

## Features

- 🔐 **Google OAuth2 Login** - Secure Gmail access
- 📬 **Email Fetching** - Real-time inbox data from Gmail
- 📄 **AI Summarization** - Summarize email threads using GPT-4
- ✍️ **Smart Reply Generation** - Context-aware replies with tone control
- 🎨 **Tone Control** - Choose from formal, friendly, apologetic tones
- 🖊️ **Edit Before Send** - Review and edit AI-generated drafts
- 📤 **Gmail Integration** - Send emails directly through Gmail API

## Tech Stack

### Frontend
- **React.js** - Component-based UI
- **Tailwind CSS** - Utility-first styling
- **Axios** - API communication

### Backend
- **FastAPI** - Python web framework
- **Uvicorn** - ASGI server

### AI/GenAI
- **OpenAI GPT-4** - Email summarization and reply generation
- **Prompt Engineering** - Dynamic tone-based prompts

### Email Integration
- **Gmail API** - Email operations
- **Google OAuth2** - Secure authentication

## Project Structure

```
intellimail/
├── frontend/              # React + Tailwind UI
│   ├── public/
│   └── src/
│       ├── components/    # UI components
│       ├── pages/         # Main pages
│       ├── App.jsx
│       └── index.js
├── backend/               # FastAPI backend
│   ├── main.py            # Entry point
│   ├── routes/            # API endpoints
│   ├── services/          # Core business logic
│   └── config.py          # Configuration
├── ai/                    # AI prompts and templates
└── requirements.txt       # Dependencies
```

## Quick Start

### 1. Clone and Setup Backend

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project and enable Gmail API
3. Set up OAuth2 credentials
4. Download `credentials.json` to the backend folder

### 3. Environment Variables

Create `backend/config.py`:
```python
OPENAI_API_KEY = "your-openai-api-key"
GOOGLE_CLIENT_ID = "your-google-client-id"
GOOGLE_CLIENT_SECRET = "your-google-client-secret"
```

### 4. Run Backend

```bash
cd backend
uvicorn main:app --reload
```

### 5. Setup Frontend

```bash
cd frontend
npm install
npm start
```

## API Endpoints

- `GET /` - Health check
- `POST /auth/google` - Google OAuth authentication
- `GET /emails` - Fetch user emails
- `POST /summarize` - Summarize email thread
- `POST /reply` - Generate AI reply
- `POST /send` - Send email via Gmail

## Demo

Access the application at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
