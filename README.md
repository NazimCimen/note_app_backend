# Notes App Backend

A professional note-taking application backend built with **FastAPI** and **Supabase**. This API provides secure endpoints for creating, reading, updating, and deleting notes with user authentication.

## 🚀 Features

- **JWT Authentication** with Supabase
- **CRUD Operations** for notes
- **Search Functionality** in notes
- **Pagination Support** for note lists
- **User Isolation** - users can only access their own notes
- **Modern Async/Await** Python architecture
- **Type Safety** with Pydantic schemas
- **Auto-generated API Documentation** with FastAPI

## 📋 API Endpoints

### Authentication
All endpoints require JWT authentication via Bearer token from Supabase.

### Notes Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/notes/` | List user's notes with search & pagination |
| `POST` | `/api/v1/notes/` | Create a new note |
| `GET` | `/api/v1/notes/{id}` | Get a specific note by ID |
| `PUT` | `/api/v1/notes/{id}` | Update a note by ID |
| `DELETE` | `/api/v1/notes/{id}` | Delete a note by ID |

### Additional Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and status |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/docs` | Interactive API documentation (Swagger UI) |
| `GET` | `/redoc` | Alternative API documentation (ReDoc) |

## 🛠️ Technology Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM with async support
- **AsyncPG** - Async PostgreSQL adapter
- **Supabase** - Backend-as-a-Service for authentication and database
- **Pydantic** - Data validation using Python type hints
- **JWT** - JSON Web Tokens for secure authentication
- **Uvicorn** - ASGI server implementation

## 📁 Project Structure

```
note_app_backend/
├── app/
│   ├── middleware/
│   │   └── auth.py          # Authentication middleware
│   ├── models/
│   │   ├── note.py          # Note database model
│   │   └── user.py          # User database model
│   ├── routers/
│   │   └── notes.py         # Note API endpoints
│   ├── schemas/
│   │   └── note.py          # Pydantic schemas for validation
│   ├── services/
│   │   ├── auth.py          # Authentication service
│   │   └── note.py          # Note business logic
│   ├── config.py            # Application configuration
│   └── database.py          # Database connection and setup
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## ⚙️ Setup and Installation

### Prerequisites
- Python 3.8+
- PostgreSQL database (or Supabase)
- Supabase account and project

### 1. Clone the Repository
```bash
git clone <repository-url>
cd note_app_backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

#### For Local Development
Create a `.env` file in the root directory:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Database Configuration (Local PostgreSQL)
DATABASE_URL=postgresql://username:password@localhost:5432/notes_db

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Notes App Backend
DEBUG=true
```

#### For Railway Deployment with Supabase
Use these environment variables in Railway:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Database Configuration (Supabase with PgBouncer)
DATABASE_URL=postgresql://postgres.vrobyncvsszbtsipnyfu:your-password@aws-1-eu-central-1.pooler.supabase.com:6543/postgres?pgbouncer=true

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Notes App Backend
DEBUG=false
```

> **Important**: Use the **pooled connection** (port 6543) for Railway deployment, not the direct connection (port 5432). This ensures compatibility with PgBouncer.

### 5. Run the Application
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Authentication

This API uses Supabase JWT authentication. To use the endpoints:

1. **Sign up/Login** through your Flutter app using Supabase Auth
2. **Get JWT token** from Supabase client
3. **Include token** in API requests:
   ```
   Authorization: Bearer <your-jwt-token>
   ```

### Authentication Flow
1. User authenticates via Supabase (handled by Flutter app)
2. Supabase returns JWT token
3. Flutter app sends JWT token with API requests
4. Backend validates token with Supabase API
5. Backend extracts user ID and processes request

## 💾 Database Schema

### Supabase Table Setup

Run the following SQL in your **Supabase Dashboard → SQL Editor**:

```sql
-- Create the note table
CREATE TABLE IF NOT EXISTS note (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR NOT NULL,
    content TEXT NOT NULL,
    is_favorite BOOLEAN DEFAULT FALSE,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_note_user_id ON note(user_id);
CREATE INDEX IF NOT EXISTS idx_note_created_at ON note(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_note_updated_at ON note(updated_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE note ENABLE ROW LEVEL SECURITY;

-- Create RLS policy to ensure users can only access their own notes
CREATE POLICY "Users can only access their own notes" ON note
    FOR ALL USING (auth.uid() = user_id);

-- Grant necessary permissions
GRANT ALL ON note TO authenticated;
GRANT ALL ON note TO service_role;
```

### Database Schema Overview
- **note**: Stores user notes with RLS enabled
- **auth.users**: Supabase built-in user table (managed automatically)
- **RLS Policies**: Ensure data isolation between users

## 📝 Usage Examples

### Create a Note
```bash
curl -X POST "http://localhost:8000/api/v1/notes/" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Note",
    "content": "This is the content of my note",
    "is_favorite": false
  }'
```

### Get All Notes
```bash
curl -X GET "http://localhost:8000/api/v1/notes/?page=1&per_page=10" \
  -H "Authorization: Bearer <your-jwt-token>"
```

### Search Notes
```bash
curl -X GET "http://localhost:8000/api/v1/notes/?search=important&page=1&per_page=10" \
  -H "Authorization: Bearer <your-jwt-token>"
```

### Update a Note
```bash
curl -X PUT "http://localhost:8000/api/v1/notes/{note-id}" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "content": "Updated content"
  }'
```

### Delete a Note
```bash
curl -X DELETE "http://localhost:8000/api/v1/notes/{note-id}" \
  -H "Authorization: Bearer <your-jwt-token>"
```

## 🧪 Testing

The API includes comprehensive error handling and validation:

- **401 Unauthorized**: Invalid or missing JWT token
- **404 Not Found**: Note doesn't exist or doesn't belong to user
- **422 Unprocessable Entity**: Invalid request data
- **500 Internal Server Error**: Server-side errors

## 🚀 Deployment

### Railway Deployment (Recommended)

Railway is the easiest way to deploy this FastAPI application:

1. **Connect Repository**: Link your GitHub repo to Railway
2. **Set Environment Variables** in Railway dashboard:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-public-key
   SUPABASE_JWT_SECRET=your-jwt-secret
   DATABASE_URL=postgresql://postgres.xxx:password@aws-1-eu-central-1.pooler.supabase.com:6543/postgres?pgbouncer=true
   DEBUG=false
   ```
3. **Deploy**: Railway will automatically detect and deploy your FastAPI app

### Other Deployment Platforms
- **Heroku**: Use Procfile with `web: python main.py`
- **DigitalOcean App Platform**: Use App Spec configuration  
- **Render**: Connect GitHub and deploy automatically
- **AWS/GCP/Azure**: Deploy as containerized application

### Important Notes for Production
- Always use `DEBUG=false` in production
- Use the **pooled connection** (port 6543) for Supabase
- **Tables must be created manually** in Supabase dashboard (see Database Schema section)
- Enable Row Level Security (RLS) policies in Supabase
- The application does NOT auto-create tables - this is by design for production safety

## 🔧 Development

### Code Structure
- **Models**: SQLAlchemy ORM models for database tables
- **Schemas**: Pydantic models for request/response validation
- **Services**: Business logic layer
- **Routers**: FastAPI route handlers
- **Middleware**: Authentication and other cross-cutting concerns

### Key Features
- **Async/Await**: Full async support for better performance
- **Type Hints**: Complete type annotations for better IDE support
- **Error Handling**: Comprehensive exception handling
- **Logging**: Structured logging for debugging and monitoring
- **Security**: JWT validation with Supabase API

## 📄 License

This project is part of a client deliverable and follows the agreed-upon terms.

## 🤝 Support

For technical support or questions about this API, please refer to the API documentation at `/docs` or contact the development team.

---

**Built with ❤️ using FastAPI and Supabase**