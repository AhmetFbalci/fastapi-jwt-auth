# FastAPI JWT & Google OAuth2 Authentication Service

FastAPI, SQLAlchemy 2.0, PostgreSQL ve Authlib kullanılarak geliştirilmiş modern, güvenli ve genişletilebilir bir kimlik doğrulama (Authentication & Authorization) API servisi.

Hem geleneksel **E-posta & Şifre** ile kayıt/giriş mekanizmasını hem de **Google OAuth 2.0** ile sosyal giriş ve kayıt akışını destekler. JWT tabanlı Access Token ve veritabanı destekli Refresh Token (iptal/revocation özellikli) mimarisine sahiptir.

---

## 🚀 Özellikler

- 🔐 **JWT Kimlik Doğrulama**:
  - **Access Token**: Kısa ömürlü (15 dakika) erişim anahtarı.
  - **Refresh Token**: Uzun ömürlü (7 gün) oturum yenileme anahtarı.
  - **Token Revocation (Kara Liste / İptal)**: Refresh token'lar veritabanında benzersiz `jti` (JWT ID) ile saklanır ve `/auth/logout` yapıldığında iptal edilir (`revoked=True`).
- 🌐 **Google OAuth 2.0 Entegrasyonu**:
  - `Authlib` ve `Starlette SessionMiddleware` ile güvenli OpenID Connect akışı.
  - **İki Aşamalı Google Kayıt Akışı**: Google ile ilk defa giriş yapan kullanıcılara 5 dakikalık geçici `google_pending` token verilir; kullanıcı platform için benzersiz bir `username` seçerek kaydını tamamlar.
- 🛡️ **Parola Güvenliği**: Passlib ve `bcrypt` algoritması ile tek yönlü güvenli şifreleme.
- 🗄️ **Gelişmiş İlişkisel Model Mimarisi**:
  - Kullanıcılar (`users`), oturum yenileme token'ları (`refresh_tokens`) ve çoklu sağlayıcı destekli kimlik hesapları (`auth_accounts`).
- 🔄 **Alembic Veritabanı Migrasyonları**: Veritabanı şema değişiklikleri versiyon kontrolü altında yönetilir.
- ⚡ **Asenkron & Hızlı**: FastAPI ve Starlette mimarisi üzerinde yüksek performans.
- 📖 **Etkileşimli API Dokümantasyonu**: Swagger UI ve ReDoc entegrasyonu.

---

## 📁 Proje Dizin Yapısı

```text
fastapi-jwt-auth/
├── alembic/                      # Alembic veritabanı migrasyon dosyaları
│   ├── versions/                 # Migrasyon versiyon script'leri
│   └── env.py                    # Alembic SQLAlchemy ortam yapılandırması
├── app/
│   ├── core/
│   │   └── security.py           # JWT üretimi/doğrulama, şifre hashleme, get_current_user
│   ├── models/                   # SQLAlchemy veritabanı modelleri
│   │   ├── AuthAccount.py        # Harici kimlik sağlayıcı (Google vb.) modelleri
│   │   ├── refresh_token.py      # Refresh token takip ve iptal tablosu
│   │   └── user.py               # Kullanıcı ana tablosu
│   ├── routers/                  # API yönlendiricileri (Endpoints)
│   │   ├── auth.py               # Standart kimlik doğrulama (Login, Register, Refresh, Logout, Me)
│   │   └── google_auth.py        # Google OAuth2 (Login, Callback, Complete)
│   ├── schemas/                  # Pydantic doğrulama şemaları
│   │   ├── token.py              # Token yanıt şemaları
│   │   └── user.py               # Kullanıcı girdi/çıktı şemaları
│   ├── database.py               # DB bağlantısı ve Session Dependency (getdb)
│   └── main.py                   # FastAPI uygulaması ve middleware kurulumu
├── .env.example                  # Örnek çevre değişkenleri şablonu
├── alembic.ini                   # Alembic konfigürasyon dosyası
├── requirements.txt              # Python bağımlılıkları listesi
└── README.md                     # Proje dokümantasyonu
```

---

## 🛠️ Teknolojiler ve Kütüphaneler

- **Dil & Çalışma Zamanı:** Python 3.12+
- **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/) (0.141.x)
- **ASGI Sunucusu:** [Uvicorn](https://www.uvicorn.org/)
- **ORM & Veritabanı:** [SQLAlchemy](https://www.sqlalchemy.org/) 2.0 + [PostgreSQL](https://www.postgresql.org/) (`psycopg2-binary`)
- **Migrasyon:** [Alembic](https://alembic.sqlalchemy.org/)
- **Kimlik & Güvenlik:**
  - [PyJWT](https://pyjwt.readthedocs.io/) (JSON Web Tokens)
  - [Passlib](https://passlib.readthedocs.io/) (`bcrypt`)
  - [Authlib](https://docs.authlib.org/) (OAuth 2.0 / OpenID Connect)
  - [Starlette SessionMiddleware](https://www.starlette.io/)

---

## ⚙️ Kurulum ve Hazırlık

### 1. Ön Gereksinimler
- Sisteminizde **Python 3.12+** kurulu olmalıdır.
- Çalışan bir **PostgreSQL** sunucusu gereklidir.

### 2. Projeyi İndirme ve Sanal Ortam Oluşturma

```bash
# Proje dizinine gidin
cd fastapi-jwt-auth

# Sanal ortamı oluşturun
python3 -m venv .venv

# Sanal ortamı aktif edin:
# Linux / macOS:
source .venv/bin/activate
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1
```

### 3. Bağımlılıkların Yüklenmesi

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Çevre Değişkenlerini (`.env`) Yapılandırma

`.env.example` dosyasını kopyalayarak `.env` oluşturun:

```bash
cp .env.example .env
```

`.env` dosyasını kendi bilgilerinize göre düzenleyin:

```ini
# JWT ve Oturum Güvenliği İçin Gizli Anahtar
SECRET_KEY=buraya_guclu_rastgele_bir_anahtar_yazin
ALGORITHM=HS256

# PostgreSQL Bağlantı Adresi
DATABASE_URL=postgresql+psycopg2://kullanici_adi:sifre@localhost:5432/veritabani_adi

# Google Cloud Console'dan Alınan OAuth Bilgileri
GOOGLE_CLIENT_ID=ornek-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=ornek-client-secret
```

> **İpucu:** Güçlü bir `SECRET_KEY` üretmek için terminalde şu komutu çalıştırabilirsiniz:
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

### 5. Veritabanı Migrasyonlarını Çalıştırma

Alembic ile veritabanı tablolarını senkronize edin:

```bash
alembic upgrade head
```

---

## 🌐 Google Cloud Console OAuth 2.0 Ayarları

Google ile giriş özelliğini kullanabilmek için:

1. [Google Cloud Console](https://console.cloud.google.com/) adresine gidin.
2. Yeni bir proje oluşturun veya mevcut projenizi seçin.
3. **APIs & Services > OAuth consent screen** adımlarından onay ekranını yapılandırın (`External` seçin ve e-posta bilgilerini doldurun).
4. **APIs & Services > Credentials** ekranına gidin.
5. **Create Credentials > OAuth client ID** seçeneğini tıklayın:
   - **Application type:** `Web application`
   - **Name:** `FastAPI Auth Service`
   - **Authorized redirect URIs (Yetkilendirilmiş Yönlendirme URI'leri):**
     ```text
     http://localhost:8000/auth/google/callback
     http://127.0.0.1:8000/auth/google/callback
     ```
6. Oluşturulan **Client ID** ve **Client Secret** değerlerini `.env` dosyanıza kopyalayın.

---

## ▶️ Uygulamayı Başlatma

Geliştirme sunucusunu başlatmak için:

```bash
uvicorn app.main:app --reload
```

Sunucu varsayılan olarak `http://127.0.0.1:8000` adresinde çalışacaktır:
- **Root Endpoint:** `http://127.0.0.1:8000/`
- **Etkileşimli Swagger Dokümantasyonu:** `http://127.0.0.1:8000/docs`
- **Alternatif ReDoc Dokümantasyonu:** `http://127.0.0.1:8000/redoc`

---

## 📡 API Uç Noktaları (Endpoints)

### 1. Kimlik Doğrulama (Auth)

| Metot | Uç Nokta | Açıklama | Yetkilendirme |
|:---:|:---|:---|:---:|
| `POST` | `/auth/register` | Yeni kullanıcı kaydı oluşturur | Herkese Açık |
| `POST` | `/auth/login` | Kullanıcı adı/şifre ile giriş (Access & Refresh Token döner) | Herkese Açık |
| `POST` | `/auth/refresh` | Geçerli refresh token ile yeni bir access token üretir | Herkese Açık |
| `POST` | `/auth/logout` | Refresh token'ı iptal eder (revocation) ve oturumu kapatır | Herkese Açık |
| `GET` | `/auth/me` | Giriş yapmış kullanıcının profil bilgilerini döner | **Bearer Token** |

### 2. Google OAuth Doğrulama

| Metot | Uç Nokta | Açıklama | Yetkilendirme |
|:---:|:---|:---|:---:|
| `GET` | `/auth/google/login` | Google giriş sayfasına yönlendirir | Herkese Açık |
| `GET` | `/auth/google/callback` | Google'dan dönen yetkilendirme kodunu karşılar | Herkese Açık |
| `POST` | `/auth/google/complete` | Yeni Google kullanıcısına kullanıcı adı atayarak kaydı tamamlar | Herkese Açık |

---

## 💡 Kullanım Senaryoları ve Örnek İstekler

### 1. Yeni Kullanıcı Kaydı (`/auth/register`)

**İstek (Request):**
```http
POST /auth/register HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "username": "ahmet",
  "email": "ahmet@example.com",
  "password": "GucluSifre123!"
}
```

**Yanıt (Response - 201 Created):**
```json
{
  "username": "ahmet",
  "email": "ahmet@example.com",
  "is_active": true
}
```

---

### 2. Giriş Yapma (`/auth/login`)

**İstek (Request):**
```http
POST /auth/login HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "username": "ahmet",
  "password": "GucluSifre123!"
}
```

**Yanıt (Response - 200 OK):**
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

---

### 3. Korumalı Uç Noktaya İstek (`/auth/me`)

Alınan `access_token`'ı HTTP header alanına `Bearer` olarak ekleyin:

**İstek (Request):**
```http
GET /auth/me HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer eyJhbGciOi...
```

**Yanıt (Response - 200 OK):**
```json
{
  "id": 1,
  "username": "ahmet",
  "email": "ahmet@example.com",
  "is_active": true,
  "is_superuser": false
}
```

---

### 4. Token Yenileme (`/auth/refresh`)

Access Token süresi dolduğunda elinizdeki `refresh_token` ile yeni bir `access_token` talep edebilirsiniz:

**İstek (Request):**
```http
POST /auth/refresh?refresh_token=eyJhbGciOi... HTTP/1.1
Host: 127.0.0.1:8000
```

**Yanıt (Response - 200 OK):**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

---

### 5. Oturumu Kapatma (`/auth/logout`)

Oturumu sonlandırırken refresh token veritabanında geçersiz kılınır:

**İstek (Request):**
```http
POST /auth/logout?refresh_token=eyJhbGciOi... HTTP/1.1
Host: 127.0.0.1:8000
```

**Yanıt (Response - 200 OK):**
```json
{
  "message": "Succesfully logged out"
}
```

---

## 🔄 Google OAuth Akış Mimarisi

Aşağıdaki diyagramda Google ile oturum açma ve yeni kullanıcı kayıt süreci özetlenmiştir:

```mermaid
sequenceDiagram
    autonumber
    actor User as Kullanıcı / Tarayıcı
    participant App as FastAPI Backend
    participant Google as Google OAuth2 API
    participant DB as PostgreSQL DB

    User->>App: GET /auth/google/login
    App-->>User: Google Giriş Sayfasına Yönlendir (Redirect)
    User->>Google: Kullanıcı Onayı ve Giriş
    Google-->>App: GET /auth/google/callback (state, code)
    App->>Google: Token & Userinfo İsteği
    Google-->>App: Kullanıcı Bilgileri (email, sub, name)
    App->>DB: AuthAccount tablosunda ara (provider='google')
    
    alt Kullanıcı Zaten Varsa
        App->>DB: Refresh token kaydet
        App-->>User: Token (Access & Refresh Token)
    else Kullanıcı İlk Kez Geliyorsa
        App-->>User: requires_username: true & pending_token (5 dk)
        User->>App: POST /auth/google/complete (username, pending_token)
        App->>DB: Yeni User ve AuthAccount oluştur
        App->>DB: Refresh token kaydet
        App-->>User: Token (Access & Refresh Token)
    end
```

---

## 🔒 Güvenlik Notları ve En İyi Uygulamalar

1. **SECRET_KEY Güvenliği:** `.env` dosyasını kesinlikle Git reposuna eklemeyin (`.gitignore` dosyasında yer almalıdır). Canlı (production) ortamında güçlü ve tahmin edilemez rastgele anahtarlar kullanın.
2. **HTTPS Zorunluluğu:** Canlı ortamda OAuth 2.0 yönlendirmeleri ve JWT token alışverişi için mutlaka SSL/TLS sertifikası (HTTPS) kullanılmalıdır.
3. **Token Süreleri:** 
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: 15 dakika (Hassas işlemler için kısa süreli erişim).
   - `REFRESH_TOKEN_EXPIRE_DAYS`: 7 gün.
   - `GOOGLE_PENDING_TOKEN_EXPIRE_MINUTES`: 5 dakika.
4. **Token Kara Listesi:** Kullanıcı çıkış yaptığında (`/auth/logout`) veya bir token ele geçirildiğinde, veritabanındaki `RefreshToken.revoked = True` alanı sayesinde iptal edilir.

---

## 📄 Lisans

Bu proje açık kaynaklıdır ve serbestçe geliştirilmeye uygundur.