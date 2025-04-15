# Developer Guide

## Overview

This developer guide provides technical information for developers who want to extend, modify, or contribute to the Intelligent Multi-Agent Email Automation System. It covers the system architecture, code organization, development environment setup, and best practices for development.

## System Architecture

The system follows a microservices architecture with specialized agents that work together to process emails. Each agent is responsible for a specific task in the email processing pipeline:

1. **Email Ingestion Agent**: Connects to email providers and retrieves emails
2. **Classification Agent**: Categorizes emails into predefined classes
3. **Summarization & Extraction Agent**: Generates summaries and extracts key data
4. **Response Generation Agent**: Creates context-aware reply drafts
5. **Integration & Orchestration Agent**: Coordinates between agents and external services

The system uses:
- MongoDB for data storage
- Redis for caching
- FastAPI for the backend API
- React with Material-UI for the frontend

## Code Organization

The codebase is organized as follows:

```
email_automation_system/
├── agents/                  # Agent implementations
│   ├── ingestion/           # Email Ingestion Agent
│   ├── classification/      # Classification Agent
│   ├── summarization/       # Summarization & Extraction Agent
│   ├── response/            # Response Generation Agent
│   └── integration/         # Integration & Orchestration Agent
├── backend/                 # Backend API
│   ├── config/              # Configuration files
│   ├── routers/             # API route handlers
│   ├── api.py               # API router setup
│   ├── auth.py              # Authentication module
│   ├── cache.py             # Redis cache module
│   ├── config.py            # Configuration module
│   ├── database.py          # MongoDB database module
│   ├── main.py              # Main application entry point
│   ├── models.py            # Data models
│   └── requirements.txt     # Backend dependencies
├── docs/                    # Documentation
│   ├── diagrams/            # Architecture diagrams
│   ├── api_reference.md     # API reference documentation
│   ├── architecture.md      # Architecture documentation
│   └── user_guide.md        # User guide
├── frontend/                # Frontend application
│   ├── public/              # Static assets
│   └── src/                 # React source code
│       ├── components/      # Reusable UI components
│       ├── pages/           # Page components
│       └── services/        # API service clients
└── tests/                   # Test suites
    ├── test_api.py          # API endpoint tests
    ├── test_frontend.py     # Frontend UI tests
    ├── test_integration.py  # Integration tests
    ├── test_system.py       # System component tests
    └── run_tests.sh         # Test runner script
```

## Development Environment Setup

### Prerequisites

- Python 3.8+
- Node.js 14+
- MongoDB 4.4+
- Redis 6.0+
- Git

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/email-automation-system.git
   cd email-automation-system
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. Start MongoDB and Redis:
   ```bash
   # Using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:4.4
   docker run -d -p 6379:6379 --name redis redis:6.0
   ```

6. Start the backend server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

3. Start the frontend development server:
   ```bash
   npm start
   ```

## Development Workflow

### Adding a New Feature

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Implement your feature
3. Write tests for your feature
4. Run tests to ensure everything works:
   ```bash
   cd tests
   ./run_tests.sh
   ```

5. Update documentation if necessary
6. Commit your changes:
   ```bash
   git add .
   git commit -m "Add your feature description"
   ```

7. Push your branch and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

### Modifying an Agent

Each agent is designed to be modular and independent. To modify an agent:

1. Locate the agent's implementation in the `agents/` directory
2. Modify the agent's code
3. Update the agent's tests in the `tests/` directory
4. Run tests to ensure the agent works correctly
5. Update the API if necessary to expose new functionality

### Adding a New Integration

To add a new integration service:

1. Create a new integration handler in the `agents/integration/` directory
2. Update the `IntegrationOrchestrationAgent` to use the new integration
3. Add API endpoints for the new integration in `backend/routers/integration.py`
4. Update the frontend to support the new integration
5. Add tests for the new integration
6. Update documentation to include the new integration

## API Development

### Adding a New Endpoint

1. Identify the appropriate router in `backend/routers/`
2. Add your new endpoint function with appropriate decorators
3. Update the API documentation in `docs/api_reference.md`
4. Add tests for your new endpoint in `tests/test_api.py`

Example:
```python
@router.post("/your-endpoint", response_model=YourResponseModel)
async def your_endpoint(data: YourRequestModel, current_user: User = Depends(get_current_active_user)):
    """
    Your endpoint description.
    """
    # Your endpoint implementation
    return {"result": "success"}
```

### Authentication and Authorization

The system uses JWT-based authentication. To secure your endpoints:

1. Import the authentication dependencies:
   ```python
   from ..auth import get_current_active_user, has_role, User
   ```

2. Add the appropriate dependency to your endpoint:
   ```python
   # For any authenticated user
   @router.get("/endpoint", response_model=ResponseModel)
   async def endpoint(current_user: User = Depends(get_current_active_user)):
       # Implementation
       
   # For users with specific roles
   @router.get("/admin-endpoint", response_model=ResponseModel)
   async def admin_endpoint(current_user: User = Depends(has_role(["admin"]))):
       # Implementation
   ```

## Frontend Development

### Component Structure

The frontend follows a component-based architecture using React and Material-UI:

- `components/`: Reusable UI components
- `pages/`: Page components
- `services/`: API service clients

### Adding a New Page

1. Create a new page component in `frontend/src/pages/`
2. Add the page to the routing in `frontend/src/App.js`
3. Create any necessary API service functions in `frontend/src/services/`
4. Update the navigation in `frontend/src/components/Sidebar.js`

Example page component:
```jsx
import React, { useState, useEffect } from 'react';
import { Container, Typography } from '@mui/material';
import { yourApiService } from '../services/api';

function YourPage() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    const fetchData = async () => {
      const result = await yourApiService();
      setData(result);
    };
    
    fetchData();
  }, []);
  
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Your Page Title
      </Typography>
      {/* Your page content */}
    </Container>
  );
}

export default YourPage;
```

### API Service Integration

Create API service functions in `frontend/src/services/` to interact with the backend API:

```javascript
// api.js
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with auth header
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Your API service function
export const yourApiService = async () => {
  try {
    const response = await api.get('/your-endpoint');
    return response.data;
  } catch (error) {
    console.error('Error calling API:', error);
    throw error;
  }
};
```

## Testing

### Writing Tests

The system uses Python's `unittest` framework for backend tests and Selenium for frontend tests. When writing tests:

1. Create test cases that cover both normal and edge cases
2. Mock external dependencies when appropriate
3. Use descriptive test method names
4. Add comments explaining complex test scenarios

Example test case:
```python
def test_email_classification(self):
    """Test email classification functionality."""
    # Arrange
    test_email = {
        "message_id": "test123",
        "subject": "Test Subject",
        "from_address": "sender@example.com",
        "to": "recipient@example.com",
        "body": "This is a test email body."
    }
    
    # Act
    result = self.classification_agent.classify_email(test_email)
    
    # Assert
    self.assertIsNotNone(result)
    self.assertIn("predicted_category", result)
    self.assertIn("confidence", result)
    self.assertGreaterEqual(result["confidence"], 0.0)
    self.assertLessEqual(result["confidence"], 1.0)
```

### Running Tests

Run all tests using the provided script:
```bash
cd tests
./run_tests.sh
```

Run a specific test file:
```bash
python -m unittest tests/test_system.py
```

Run a specific test case:
```bash
python -m unittest tests.test_system.TestEmailAutomationSystem.test_email_classification
```

## Performance Optimization

### Database Optimization

- Use appropriate indexes for frequently queried fields
- Implement caching for frequently accessed data
- Use aggregation pipelines for complex queries
- Consider sharding for large datasets

### API Optimization

- Implement pagination for endpoints that return large datasets
- Use async/await for I/O-bound operations
- Implement request validation to catch errors early
- Use response compression

### Frontend Optimization

- Implement code splitting to reduce initial load time
- Use React.memo for expensive components
- Optimize images and assets
- Implement virtualization for long lists

## Deployment

### Backend Deployment

The backend can be deployed using Docker:

1. Build the Docker image:
   ```bash
   docker build -t email-automation-backend .
   ```

2. Run the container:
   ```bash
   docker run -d -p 8000:8000 \
     -e MONGODB_URL=mongodb://mongo:27017 \
     -e REDIS_HOST=redis \
     --name email-automation-backend \
     email-automation-backend
   ```

### Frontend Deployment

The frontend can be deployed as a static site:

1. Build the production bundle:
   ```bash
   cd frontend
   npm run build
   ```

2. Serve the static files using Nginx or a similar web server

### Docker Compose

For a complete deployment, use Docker Compose:

```yaml
version: '3'

services:
  mongodb:
    image: mongo:4.4
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"

  redis:
    image: redis:6.0
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    depends_on:
      - mongodb
      - redis
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    depends_on:
      - backend
    ports:
      - "80:80"

volumes:
  mongodb_data:
  redis_data:
```

## Security Best Practices

### Authentication and Authorization

- Use JWT tokens with appropriate expiration times
- Implement role-based access control
- Store passwords using bcrypt or similar hashing algorithms
- Use HTTPS for all communications

### Data Protection

- Encrypt sensitive data at rest
- Implement proper input validation
- Use parameterized queries to prevent injection attacks
- Implement rate limiting to prevent abuse

### API Security

- Validate all input data
- Implement proper error handling
- Use CORS to restrict access to trusted domains
- Implement API key rotation

## Troubleshooting

### Common Development Issues

1. **MongoDB Connection Issues**
   - Check if MongoDB is running: `docker ps | grep mongo`
   - Verify connection string in configuration

2. **Redis Connection Issues**
   - Check if Redis is running: `docker ps | grep redis`
   - Verify Redis host and port in configuration

3. **API Errors**
   - Check API logs for detailed error messages
   - Verify authentication token is valid
   - Check request format against API documentation

4. **Frontend Build Issues**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check for JavaScript errors in the console
   - Verify environment variables are set correctly

## Contributing

### Code Style

- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript/React code
- Write descriptive comments for complex logic
- Use meaningful variable and function names

### Pull Request Process

1. Create a branch for your feature or bugfix
2. Implement your changes with appropriate tests
3. Ensure all tests pass
4. Update documentation as necessary
5. Submit a pull request with a clear description of changes
6. Address any review comments

### Code Review Guidelines

- Check for code correctness and adherence to style guidelines
- Verify that tests cover the new functionality
- Ensure documentation is updated
- Look for potential security issues
- Consider performance implications

## Resources

### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Material-UI Documentation](https://mui.com/getting-started/usage/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Redis Documentation](https://redis.io/documentation)

### Learning Resources

- [Python Asyncio Tutorial](https://realpython.com/async-io-python/)
- [React Hooks Tutorial](https://reactjs.org/docs/hooks-intro.html)
- [JWT Authentication Guide](https://jwt.io/introduction/)
- [MongoDB Best Practices](https://www.mongodb.com/developer/products/mongodb/mongodb-schema-design-best-practices/)
