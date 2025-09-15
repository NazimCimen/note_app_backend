# 📝 Notes App Backend

FastAPI ile geliştirilmiş not alma uygulaması backend servisi. Supabase PostgreSQL veritabanına bağlanır, JWT kimlik doğrulama kullanır ve CRUD işlemleri sağlar.
## 🚀 Özellikler

- JWT token ile kullanıcı doğrulama
- Not oluşturma, okuma, güncelleme, silme
- Başlık ve içerik bazlı arama
- Favori notları filtreleme
- En yeni/en eski sıralama
- Sayfalama desteği

## 🌐 Canlı API

**Vercel Deployment URL**: `https://note-app-backend-3fcfie7ht-nazims-projects-c4c40cbc.vercel.app`

### 📖 API Dokümantasyonu
- **Swagger UI**: `https://note-app-backend-3fcfie7ht-nazims-projects-c4c40cbc.vercel.app/docs`
- **ReDoc**: `https://note-app-backend-3fcfie7ht-nazims-projects-c4c40cbc.vercel.app/redoc`

### 🔑 Test Token
Swagger UI'da test yapabilmek için aşağıdaki token'ı kullanın:
```
eyJhbGciOiJIUzI1NiIsImtpZCI6IklFaVRJc2pUUDFWZVhSZU8iLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3Zyb2J5bmN2c3N6YnRzaXBueWZ1LnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIzNzJjNDUwMC0xZWE2LTQ0OGItOGMyNi02YTI1MDJjZDNjNTMiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU3OTA0MzI1LCJpYXQiOjE3NTc5MDA3MjUsImVtYWlsIjoiY2ltZW5uYXppbS5kZXZAZ21haWwuY29tIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJlbWFpbCIsInByb3ZpZGVycyI6WyJlbWFpbCJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbCI6ImNpbWVubmF6aW0uZGV2QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInN1YiI6IjM3MmM0NTAwLTFlYTYtNDQ4Yi04YzI2LTZhMjUwMmNkM2M1MyJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzU3ODk2NjUyfV0sInNlc3Npb25faWQiOiIzNzVhZDJmZi1jNDE4LTQyYjMtYWVmZS01YTZiMDQ5NzJlNDkiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.UZkEgbAK4N0ebnxvWYXiJ6WWEbqqqQ7tQ7u_6OVjRkM
```


## 📚 API Endpoints

| Method | Endpoint | Açıklama | Auth |
|--------|----------|----------|------|
| GET | `/api/v1/notes/` | Notları listele (arama, filtreleme, sıralama) | ✅ |
| POST | `/api/v1/notes/` | Yeni not oluştur | ✅ |
| GET | `/api/v1/notes/{id}` | Belirli notu getir | ✅ |
| PUT | `/api/v1/notes/{id}` | Notu güncelle | ✅ |
| DELETE | `/api/v1/notes/{id}` | Notu sil | ✅ |
| GET | `/` | API bilgileri | ❌ |
| GET | `/health` | Sağlık kontrolü | ❌ |

### Query Parameters (GET /api/v1/notes/)

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|------------|----------|
| `search` | string | - | Arama terimi |
| `search_in` | enum | `both` | Arama kapsamı: `both`, `title`, `content` |
| `filter_by` | enum | `all` | Filtreleme: `all`, `favorites` |
| `sort_by` | enum | `newest` | Sıralama: `newest`, `oldest` |
| `page` | integer | `1` | Sayfa numarası |
| `per_page` | integer | `10` | Sayfa başına öğe (max: 100) |

## 📁 Klasör Yapısı

```
note_app_backend/
├── app/
│   ├── config.py                # Environment variables
│   ├── database.py              # SQLAlchemy engine ve session
│   ├── middleware/
│   │   └── auth.py              # JWT authentication middleware
│   ├── models/
│   │   └── note.py              # Note veritabanı modeli
│   ├── routers/
│   │   └── notes.py             # Notes API endpoints
│   ├── schemas/
│   │   └── note.py              # Request/Response şemaları
│   └── services/
│       ├── auth.py              # JWT token doğrulama
│       └── note.py              # Note CRUD işlemleri
├── main.py                      # FastAPI uygulama
├── requirements.txt             # Python bağımlılıkları
└── README.md                    # Bu dosya
```

## 🔐 JWT Token Yönetimi

### Nasıl Çalışır
1. Frontend'den gelen JWT token Authorization header'da alınır
2. Token backend'de yerel olarak doğrulanır (Supabase JWT secret ile)
3. Token'dan user_id çıkarılır
4. Tüm veritabanı sorgularında user_id kullanılır

### Kod Yapısı
```python
# middleware/auth.py
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UUID:
    token = credentials.credentials
    user_id = await AuthService.get_user_id_from_token(token)
    return user_id

# services/auth.py
async def verify_supabase_token_local(token: str) -> dict:
    payload = jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"])
    return payload
```

### Kullanım
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/v1/notes/
```

## 🗄️ Supabase PostgreSQL Tabloları

### Users Tablosu (Supabase Auth)
Supabase tarafından otomatik oluşturulur:
```sql
-- Supabase auth.users tablosu
id UUID PRIMARY KEY
email VARCHAR
created_at TIMESTAMP
updated_at TIMESTAMP
```

### Notes Tablosu
```sql
CREATE TABLE note (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR NOT NULL,
    content TEXT NOT NULL,
    is_favorite BOOLEAN DEFAULT FALSE,
    user_id UUID NOT NULL,
    summary TEXT,
    keywords TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_note_user_id ON note(user_id);
CREATE INDEX idx_note_updated_at ON note(updated_at);
```

## 🔧 Kurulum

### 1. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
`.env` dosyası oluşturun:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_public_key
SUPABASE_JWT_SECRET=your_jwt_secret
DATABASE_URL=postgresql://user:password@host:port/database
DEBUG=false
```

### 3. Veritabanı Kurulumu
Supabase Dashboard'da `note` tablosunu oluşturun (yukarıdaki SQL ile).

### 4. Uygulamayı Çalıştır
```bash
python main.py
```

### 5. API Dokümantasyonu
- **Swagger UI**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

---

**Teknoloji**: FastAPI, PostgreSQL, Supabase, JWT