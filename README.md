# Notes App Backend

Professional note-taking application backend built with FastAPI and Supabase for technical interview showcase.

## 🚀 Features

- **JWT Authentication**: Secure authentication with Supabase JWT tokens
- **CRUD Operations**: Full Create, Read, Update, Delete operations for notes
- **Search & Filter**: Search notes by title or content (case-insensitive)
- **User Authorization**: Users can only access their own notes
- **Pagination**: Efficient pagination for large note collections
- **Modern Architecture**: Clean, maintainable code structure
- **API Documentation**: Auto-generated interactive API docs

## 📋 API Endpoints

### Authentication
All endpoints require JWT token in Authorization header: `Authorization: Bearer <token>`

### Notes Endpoints
- **GET /api/v1/notes/** - Get all user notes (with search & pagination)
- **POST /api/v1/notes/** - Create a new note
- **GET /api/v1/notes/{id}** - Get specific note by ID
- **PUT /api/v1/notes/{id}** - Update specific note
- **DELETE /api/v1/notes/{id}** - Delete specific note

### System Endpoints
- **GET /** - API information
- **GET /health** - Health check

## 🛠️ Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Supabase**: Backend-as-a-Service with PostgreSQL
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type hints
- **JWT**: JSON Web Tokens for authentication
- **AsyncPG**: Async PostgreSQL adapter

## 📦 Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd note_app_backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
**Windows PowerShell:**
```bash
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```bash
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Configuration
Create a `.env` file in the root directory:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here

# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@db.your-project.supabase.co:5432/postgres

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Notes App Backend
```

## 🚀 Running the Application

### Development Mode (Recommended)
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Direct Python Execution
```bash
python main.py
```

## 📖 API Documentation

Once the server is running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Project Structure

```
note_app_backend/
├── app/
│   ├── __init__.py
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database connection & setup
│   ├── models/
│   │   ├── __init__.py
│   │   └── note.py         # Note SQLAlchemy model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── note.py         # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py         # JWT authentication service
│   │   └── note.py         # Note business logic
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py         # Authentication middleware
│   └── routers/
│       ├── __init__.py
│       └── notes.py        # Notes API routes
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables example
└── README.md              # Project documentation
```

## 🔐 Authentication Flow

1. **Flutter App**: User signs in with Supabase Auth
2. **JWT Token**: Supabase returns JWT token
3. **API Requests**: Flutter sends token in Authorization header
4. **Token Verification**: Backend verifies JWT with Supabase secret
5. **User Context**: Extracted user ID used for authorization

## 🔍 Search & Filtering

The `GET /api/v1/notes/` endpoint supports:
- **search**: Query parameter for searching in title/content
- **page**: Page number for pagination (default: 1)
- **per_page**: Items per page (default: 10, max: 100)

Example:
```
GET /api/v1/notes/?search=meeting&page=1&per_page=20
```

## 🛡️ Security Features

- **JWT Token Verification**: All endpoints verify Supabase JWT tokens
- **User Authorization**: Users can only access their own notes
- **Input Validation**: All inputs validated with Pydantic schemas
- **CORS Configuration**: Configurable CORS for frontend integration
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

## 🧪 Testing the API

### Using curl (after getting JWT token from Supabase):

```bash
# Get all notes
curl -H "Authorization: Bearer <your-jwt-token>" http://localhost:8000/api/v1/notes/

# Create a note
curl -X POST -H "Authorization: Bearer <your-jwt-token>" -H "Content-Type: application/json" \
-d '{"title":"My Note","content":"Note content"}' http://localhost:8000/api/v1/notes/

# Search notes
curl -H "Authorization: Bearer <your-jwt-token>" \
"http://localhost:8000/api/v1/notes/?search=meeting"
```

## 🚀 Production Deployment

1. Set `echo=False` in database.py
2. Configure proper CORS origins
3. Use environment variables for all secrets
4. Set up proper logging
5. Configure database connection pooling
6. Add rate limiting middleware

## 📝 Database Schema

### Notes Table
```sql
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_notes_user_id ON notes(user_id);
CREATE INDEX idx_notes_title ON notes(title);
```

## 🤝 Contributing

This is a technical interview project. Code is structured for:
- **Readability**: Clean, well-documented code
- **Maintainability**: Modular architecture
- **Scalability**: Async operations, proper DB patterns
- **Security**: JWT verification, user authorization
- **Best Practices**: Type hints, error handling, logging
