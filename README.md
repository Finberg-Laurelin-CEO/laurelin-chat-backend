# Laurelin Chat Backend

A Flask-based backend service for the Laurelin chat application, designed to run on Google Cloud Run with integrated AI model support and A/B testing capabilities.

## Features

- **User Authentication**: Google OAuth integration with JWT tokens
- **Chat Management**: Firestore-based chat session and message storage
- **AI Model Integration**: Support for OpenAI GPT and Google Gemini models
- **A/B Testing**: Built-in infrastructure for testing different AI models
- **Cloud Deployment**: Optimized for Google Cloud Run deployment
- **Static Asset Serving**: Serves frontend assets and API documentation

## Architecture

```
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration management
│   ├── models/              # Data models
│   │   ├── user.py         # User model and service
│   │   └── chat.py         # Chat session and message models
│   ├── services/            # Business logic services
│   │   ├── auth_service.py  # Authentication service
│   │   ├── model_service.py # AI model communication
│   │   └── ab_testing_service.py # A/B testing logic
│   └── routes/              # API endpoints
│       ├── auth.py         # Authentication routes
│       ├── chat.py         # Chat management routes
│       ├── models.py       # Model testing routes
│       └── ab_testing.py   # A/B testing routes
├── static/                  # Static assets
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── cloudbuild.yaml         # Cloud Build configuration
└── README.md               # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Authenticate with Google token
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile

### Chat Management
- `GET /api/chat/sessions` - Get user's chat sessions
- `POST /api/chat/sessions` - Create new chat session
- `GET /api/chat/sessions/{id}` - Get specific session
- `POST /api/chat/sessions/{id}/messages` - Send message and get AI response
- `DELETE /api/chat/sessions/{id}` - Delete chat session

### Model Management
- `GET /api/models/available` - Get available AI models
- `POST /api/models/test` - Test specific model
- `GET /api/models/health` - Check model health status

### A/B Testing
- `GET /api/ab-testing/experiments` - Get A/B testing experiments
- `POST /api/ab-testing/experiments/{name}/assign` - Assign user to experiment
- `POST /api/ab-testing/experiments/{name}/track` - Track experiment event
- `GET /api/ab-testing/experiments/{name}/results` - Get experiment results

## Setup and Development

### Prerequisites
- Python 3.11+
- Google Cloud Project with Firestore enabled
- OpenAI API key
- Google AI API key
- Google OAuth client credentials

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd laurelin-chat-backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

The application will be available at `http://localhost:8080`

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FLASK_ENV` | Flask environment (development/production) | Yes |
| `SECRET_KEY` | Flask secret key for JWT signing | Yes |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON | Yes |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `GOOGLE_AI_API_KEY` | Google AI API key | Yes |
| `AB_TEST_ENABLED` | Enable A/B testing (true/false) | No |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | No |

## Deployment

### Google Cloud Run

1. **Enable required APIs**:
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable firestore.googleapis.com
   ```

2. **Deploy using Cloud Build**:
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

3. **Manual deployment**:
   ```bash
   # Build and push image
   docker build -t gcr.io/PROJECT_ID/laurelin-chat-backend .
   docker push gcr.io/PROJECT_ID/laurelin-chat-backend
   
   # Deploy to Cloud Run
   gcloud run deploy laurelin-chat-backend \
     --image gcr.io/PROJECT_ID/laurelin-chat-backend \
     --region us-central1 \
     --platform managed \
     --allow-unauthenticated
   ```

### Environment Configuration

Set environment variables in Cloud Run:
```bash
gcloud run services update laurelin-chat-backend \
  --set-env-vars="FLASK_ENV=production,GOOGLE_CLOUD_PROJECT=your-project-id"
```

## A/B Testing

The application includes built-in A/B testing infrastructure to compare different AI models:

- **Model Comparison**: Tests OpenAI GPT vs Google Gemini
- **Consistent Assignment**: Users are consistently assigned to the same variant
- **Event Tracking**: Tracks user interactions and model performance
- **Results Analysis**: Provides aggregated results for analysis

### Enabling A/B Testing

1. Set `AB_TEST_ENABLED=true` in environment variables
2. The system will automatically assign users to variants
3. Track events using the A/B testing API endpoints
4. Analyze results through the results endpoint

## Integration with Frontend

This backend is designed to work with:
- **Frontend Repository**: [laurelin-inc/frontend-laurelin-chat](https://github.com/laurelin-inc/frontend-laurelin-chat.git) (Angular)
- **Backend Repository**: [laurelin-inc/laurelin-llm-backend](https://github.com/laurelin-inc/laurelin-llm-backend.git)

### CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:4200` (Angular dev server)
- Your production frontend domain

Update `CORS_ORIGINS` environment variable to add additional origins.

## Monitoring and Health Checks

- **Health Endpoint**: `GET /health` - Returns service status
- **Root Endpoint**: `GET /` - Returns basic service information
- **Model Health**: `GET /api/models/health` - Checks AI model connectivity

## Security Considerations

- JWT tokens for authentication
- Google OAuth integration
- CORS protection
- Environment-based configuration
- Non-root container user
- Input validation and error handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Laurelin chat application ecosystem.
