Fast Wallet Service

<div align="center">









 







 







 







 









A secure, scalable financial microservice for managing user wallets, transactions, and Paystack payment integration.

Features • Quick Start • API Documentation • Deployment • Contributing

</div>




Table of Contents

•
Overview

•
Features

•
Tech Stack

•
Prerequisites

•
Installation

•
Configuration

•
Running the Application

•
API Documentation

•
Project Structure

•
Deployment

•
Testing

•
Security

•
Contributing

•
License

•
Support




Overview

Fast Wallet Service is a production-ready backend microservice built with FastAPI that provides a complete wallet management system with enterprise-grade security, atomic transactions, and seamless Paystack payment integration.

The service handles:

•
👤 User authentication with JWT tokens

•
💳 Wallet operations (deposits, transfers, balance queries)

•
🔑 API key management with granular permissions

•
💰 Paystack payment integration with webhook handling

•
📊 Complete transaction audit trail

•
🔒 Secure credential storage and validation

Perfect for: FinTech applications, payment platforms, e-commerce backends, and any system requiring secure wallet management.




Features

🔐 Security

•
Dual-layer authentication: JWT tokens for users + SHA-256 hashed API keys for services

•
Permission-based access control: Granular permissions (READ, DEPOSIT, TRANSFER)

•
Webhook signature verification: HMAC-SHA512 validation for Paystack webhooks

•
Secure credential storage: No plaintext passwords or API keys in database

•
CORS protection: Configurable allowed origins

💰 Financial Operations

•
Atomic transactions: All-or-nothing fund transfers prevent data inconsistency

•
Deposit processing: Seamless Paystack payment integration

•
Fund transfers: Direct wallet-to-wallet transfers with validation

•
Balance queries: Real-time wallet balance retrieval

•
Transaction history: Complete audit trail for compliance

🚀 Performance & Scalability

•
Asynchronous I/O: Non-blocking database operations using SQLAlchemy 2.0 async

•
Connection pooling: Efficient database connection management

•
Horizontal scaling: Designed for cloud deployment (Google Cloud Run, AWS, etc.)

•
Caching ready: Redis integration support for future optimization

📚 Developer Experience

•
Auto-generated API docs: Swagger UI and ReDoc documentation

•
Type hints: Full Python type annotations for IDE support

•
Modular architecture: Clean separation of concerns

•
Comprehensive logging: Structured logging for debugging

•
Error handling: Detailed error responses with proper HTTP status codes

🔄 Integration

•
Paystack integration: Full payment processing and webhook handling

•
Google OAuth: Mock OAuth flow (easily replaceable with real OAuth)

•
PostgreSQL/SQLite: Flexible database support

•
Cloud SQL: Native Google Cloud SQL support




Tech Stack

Component
Technology
Version
Framework
FastAPI
0.104+
Python
Python
3.11+
ORM
SQLAlchemy
2.0+
Database
PostgreSQL / SQLite
15 / Latest
Authentication
JWT (python-jose)
3.3+
Async
asyncpg
0.29+
Validation
Pydantic
2.5+
Server
Uvicorn
0.24+
Deployment
Docker
Latest





Prerequisites

Before you begin, ensure you have:

•
Python 3.11+ - Download

•
pip - Python package manager (comes with Python)

•
PostgreSQL 15+ (for production) - Download

•
Docker (for containerization) - Download

•
Git - Download

•
Paystack Account - Sign up

Optional

•
Google Cloud SDK - For GCP deployment

•
Postman - For API testing




Installation

1. Clone the Repository

Bash


git clone https://github.com/yourusername/fast_wallet_service.git
cd fast_wallet_service


2. Create Virtual Environment

Bash


# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate


3. Install Dependencies

Bash


# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt


4. Verify Installation

Bash


# Check Python version
python --version

# Check installed packages
pip list | grep -E "fastapi|sqlalchemy|uvicorn"





Configuration

1. Create Environment File

Create a .env file in the project root:

Bash


cp .env.example .env


2. Configure Environment Variables

Edit .env with your settings:

Bash


# Application Settings
APP_NAME="Fast Wallet Service"
DEBUG=True
ENVIRONMENT="development"

# Database Configuration
DATABASE_URL="sqlite:///./wallet.db"  # For development
# DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/wallet_db"  # For PostgreSQL

# Security
SECRET_KEY="your-super-secret-key-change-this"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OAuth Configuration (Mock )
GOOGLE_CLIENT_ID="mock-client-id"
GOOGLE_CLIENT_SECRET="mock-client-secret"
GOOGLE_REDIRECT_URI="http://localhost:8000/auth/google/callback"

# Paystack Configuration
PAYSTACK_SECRET_KEY="sk_test_your_test_key"
PAYSTACK_PUBLIC_KEY="pk_test_your_test_key"
PAYSTACK_WEBHOOK_SECRET="test-webhook-secret"

# Logging
LOG_LEVEL="DEBUG"

# CORS Settings
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:8000"


3. Generate Secure Credentials

Bash


# Generate a secure SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32 ))"

# Generate a secure PAYSTACK_WEBHOOK_SECRET
python3 -c "import secrets; print(secrets.token_urlsafe(32))"


4. Database Setup (PostgreSQL)

Bash


# Create database
createdb wallet_db

# Create user
createuser wallet_user

# Set password
psql -c "ALTER USER wallet_user WITH PASSWORD 'your_secure_password';"

# Grant privileges
psql -d wallet_db -c "GRANT ALL PRIVILEGES ON DATABASE wallet_db TO wallet_user;"





Running the Application

Development Mode

Bash


# Start the development server with auto-reload
uvicorn fast_wallet_service.main:app --reload --host 0.0.0.0 --port 8000


The application will be available at:

•
API: http://localhost:8000

•
Swagger UI: http://localhost:8000/docs

•
ReDoc: http://localhost:8000/redoc

Production Mode

Bash


# Start the production server
uvicorn fast_wallet_service.main:app --host 0.0.0.0 --port 8000 --workers 4


Using Docker

Bash


# Build Docker image
docker build -t fast-wallet-service:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="sqlite:///./wallet.db" \
  -e SECRET_KEY="your-secret-key" \
  fast-wallet-service:latest





API Documentation

Base URL

Plain Text


http://localhost:8000


Authentication

The API supports two authentication methods:

1. JWT Token (User Authentication )

Bash


# Get JWT token
curl -X GET "http://localhost:8000/auth/google/callback?code=test_code"

# Use token in requests
curl -X GET "http://localhost:8000/wallet/balance" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"


2. API Key (Service Authentication )

Bash


# Use API key in requests
curl -X GET "http://localhost:8000/wallet/balance" \
  -H "x-api-key: YOUR_API_KEY"


Core Endpoints

Authentication

Plain Text


POST   /auth/google/callback          - Authenticate user and get JWT token


Wallet Operations

Plain Text


GET    /wallet/balance                - Get wallet balance
POST   /wallet/deposit                - Initiate deposit
POST   /wallet/transfer               - Transfer funds to another wallet
GET    /wallet/transactions           - Get transaction history


API Key Management

Plain Text


POST   /keys/create                   - Create new API key
POST   /keys/rollover                 - Rotate API key
GET    /keys/list                     - List all API keys


Webhooks

Plain Text


POST   /wallet/paystack/webhook       - Paystack webhook handler


Example Requests

1. Authenticate User

Bash


curl -X GET "http://localhost:8000/auth/google/callback?code=test_code" \
  -H "Content-Type: application/json"

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }


2. Create API Key

Bash


curl -X POST "http://localhost:8000/keys/create" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-service",
    "permissions": ["read", "deposit"],
    "expiry": "1D"
  }'

# Response:
# {
#   "api_key": "sk_live_abc123def456...",
#   "name": "my-service",
#   "permissions": ["read", "deposit"],
#   "expires_at": "2025-12-11T10:30:00Z"
# }


3. Check Wallet Balance

Bash


curl -X GET "http://localhost:8000/wallet/balance" \
  -H "x-api-key: sk_live_abc123def456..."

# Response:
# {
#   "balance": 5000.00,
#   "currency": "NGN",
#   "wallet_number": "185ddca7f9d549c"
# }


4. Initiate Deposit

Bash


curl -X POST "http://localhost:8000/wallet/deposit" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000
  }'

# Response:
# {
#   "reference": "ref_abc123def456",
#   "authorization_url": "https://checkout.paystack.com/...",
#   "access_code": "access_code_123"
# }


5. Transfer Funds

Bash


curl -X POST "http://localhost:8000/wallet/transfer" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_wallet_number": "recipient_wallet_id",
    "amount": 2000
  }'

# Response:
# {
#   "transaction_id": "txn_abc123def456",
#   "status": "success",
#   "amount": 2000,
#   "recipient_wallet": "recipient_wallet_id"
# }


Interactive API Documentation

Visit http://localhost:8000/docs for interactive Swagger UI where you can:

•
View all endpoints

•
Test endpoints directly

•
See request/response schemas

•
Download OpenAPI specification




Project Structure

Plain Text


fast_wallet_service/
├── fast_wallet_service/
│   ├── main.py                          # FastAPI application entry point
│   ├── routers/                         # API endpoint definitions
│   │   ├── __init__.py
│   │   ├── auth.py                      # Authentication endpoints
│   │   ├── keys.py                      # API key management endpoints
│   │   ├── wallet.py                    # Wallet operation endpoints
│   │   └── webhook.py                   # Paystack webhook handler
│   ├── core/                            # Business logic and services
│   │   ├── __init__.py
│   │   ├── config.py                    # Configuration management
│   │   ├── db.py                        # Database initialization
│   │   ├── models.py                    # SQLAlchemy ORM models
│   │   ├── security.py                  # JWT and hashing utilities
│   │   ├── wallet_service.py            # Wallet business logic
│   │   ├── api_key_manager.py           # API key generation/validation
│   │   └── paystack_client.py           # Paystack API integration
│   ├── schemas/                         # Pydantic data validation models
│   │   ├── __init__.py
│   │   ├── auth.py                      # Auth request/response schemas
│   │   ├── wallet.py                    # Wallet schemas
│   │   ├── keys.py                      # API key schemas
│   │   └── transaction.py               # Transaction schemas
│   └── dependencies/                    # FastAPI dependency injection
│       ├── __init__.py
│       └── auth.py                      # Authentication middleware
├── tests/                               # Test suite
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_wallet.py
│   ├── test_keys.py
│   └── test_webhook.py
├── .env.example                         # Environment variables template
├── .gitignore                           # Git ignore rules
├── Dockerfile                           # Docker configuration
├── docker-compose.yml                   # Docker Compose configuration
├── requirements.txt                     # Python dependencies
├── README.md                            # This file
└── LICENSE                              # MIT License





Deployment

Google Cloud Platform (GCP )

For detailed deployment instructions, see GCP_DEPLOYMENT_GUIDE.md

Quick deployment:

Bash


# 1. Set up GCP project
gcloud projects create fast-wallet-service
gcloud config set project fast-wallet-service

# 2. Create Cloud SQL database
gcloud sql instances create fast-wallet-db --database-version=POSTGRES_15

# 3. Build and push Docker image
docker build -t gcr.io/fast-wallet-service/app:latest .
docker push gcr.io/fast-wallet-service/app:latest

# 4. Deploy to Cloud Run
gcloud run deploy fast-wallet-service \
  --image=gcr.io/fast-wallet-service/app:latest \
  --platform=managed \
  --region=us-central1


Other Platforms

The service can be deployed to:

•
AWS: ECS, Elastic Beanstalk, Lambda (with API Gateway)

•
Azure: App Service, Container Instances

•
Heroku: Using Procfile and buildpacks

•
DigitalOcean: App Platform or Droplets

•
Self-hosted: Any server with Docker support




Testing

Run Tests

Bash


# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=fast_wallet_service

# Run specific test file
pytest tests/test_wallet.py

# Run with verbose output
pytest -v


Test Coverage

Bash


# Generate coverage report
pytest --cov=fast_wallet_service --cov-report=html

# View report
open htmlcov/index.html


Manual Testing

Use the provided Postman collection or test with curl:

Bash


# Test health check
curl http://localhost:8000/

# Test authentication
curl http://localhost:8000/auth/google/callback?code=test

# Test wallet balance
curl -H "x-api-key: YOUR_API_KEY" http://localhost:8000/wallet/balance





Security

Best Practices Implemented

✅ Secure Authentication:

•
JWT tokens with configurable expiry

•
API key hashing with SHA-256

•
No plaintext credentials in database

✅ Authorization:

•
Permission-based access control

•
Granular permissions (READ, DEPOSIT, TRANSFER )

•
Role-based endpoint access

✅ Data Protection:

•
HTTPS/TLS encryption in production

•
CORS protection

•
SQL injection prevention via SQLAlchemy ORM

•
CSRF protection headers

✅ Webhook Security:

•
HMAC-SHA512 signature verification

•
Idempotent webhook processing

•
Replay attack prevention

✅ Secrets Management:

•
Environment variables for sensitive data

•
Google Secret Manager integration (GCP)

•
No secrets in version control

Security Checklist




Change SECRET_KEY in production




Use strong database passwords




Enable HTTPS/TLS




Configure CORS appropriately




Use live Paystack keys in production




Enable database backups




Set up monitoring and alerts




Rotate API keys regularly




Review access logs




Conduct security audit




Contributing

We welcome contributions! Please follow these steps:

1. Fork the Repository

Bash


git clone https://github.com/yourusername/fast_wallet_service.git
cd fast_wallet_service


2. Create a Feature Branch

Bash


git checkout -b feature/your-feature-name


3. Make Changes

•
Follow PEP 8 style guide

•
Add type hints

•
Write tests for new features

•
Update documentation

4. Commit Changes

Bash


git add .
git commit -m "feat: add your feature description"


5. Push to Branch

Bash


git push origin feature/your-feature-name


6. Create Pull Request

•
Describe changes clearly

•
Reference related issues

•
Ensure tests pass

Code Style

Bash


# Format code with black
black fast_wallet_service/

# Check with flake8
flake8 fast_wallet_service/

# Type checking with mypy
mypy fast_wallet_service/





Troubleshooting

Issue: "ModuleNotFoundError: No module named 'fastapi'"

Solution:

Bash


# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt


Issue: "Database connection refused"

Solution:

Bash


# Verify PostgreSQL is running
psql -U postgres

# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL

# For SQLite, ensure directory exists
mkdir -p ./data


Issue: "Invalid webhook signature"

Solution:

Bash


# Verify PAYSTACK_WEBHOOK_SECRET matches Paystack dashboard
# https://dashboard.paystack.co/settings/developers

# Regenerate webhook secret if needed
python3 -c "import secrets; print(secrets.token_urlsafe(32 ))"


Issue: "CORS error when calling from frontend"

Solution:

Bash


# Update ALLOWED_ORIGINS in .env
ALLOWED_ORIGINS="https://your-frontend-domain.com,http://localhost:3000"

# Restart the application


For more issues, see TROUBLESHOOTING.md




Performance Metrics

Benchmarks (Single Instance)

Metric
Value
Requests/Second
1000-5000
Average Latency
<100ms
P99 Latency
<500ms
Concurrent Users
100-500
Memory Usage
100-200MB
CPU Usage
10-30%


Benchmarks are estimates based on typical hardware and may vary.




Roadmap

Current Version (v1.0)

•
✅ User authentication with JWT

•
✅ Wallet operations (deposit, transfer)

•
✅ API key management

•
✅ Paystack integration

•
✅ Transaction history

Planned Features (v1.1)

•
🔄 Real Google OAuth integration

•
🔄 Redis caching for performance

•
🔄 Rate limiting and throttling

•
🔄 Advanced analytics dashboard

•
🔄 Multi-currency support

Future Enhancements (v2.0)

•
📅 Scheduled transactions

•
📅 Recurring payments

•
📅 Dispute resolution system

•
📅 Mobile app support

•
📅 Advanced fraud detection




License

This project is licensed under the MIT License - see the LICENSE file for details.

MIT License Summary

•
✅ Commercial use

•
✅ Modification

•
✅ Distribution

•
✅ Private use

•
❌ Liability

•
❌ Warranty




Support

Getting Help

•
Documentation: GCP_DEPLOYMENT_GUIDE.md, ENVIRONMENT_VARIABLES_GUIDE.md

•
Issues: GitHub Issues

•
Discussions: GitHub Discussions

•
Email: support@example.com

Report a Bug

Found a bug? Please create an issue with:

1.
Description of the problem

2.
Steps to reproduce

3.
Expected behavior

4.
Actual behavior

5.
Environment details (OS, Python version, etc.)

Request a Feature

Have an idea? Open a feature request with:

1.
Clear description of the feature

2.
Use case and benefits

3.
Proposed implementation (optional)

4.
Alternative solutions (optional)




Acknowledgments

•
FastAPI - Modern web framework

•
SQLAlchemy - SQL toolkit and ORM

•
Paystack - Payment processing

•
Google Cloud - Cloud infrastructure

•
Python - Programming language




Changelog

v1.0.0 (2025-12-09)

•
Initial release

•
User authentication with JWT

•
Wallet operations (deposit, transfer, balance)

•
API key management with permissions

•
Paystack payment integration

•
Complete transaction audit trail

•
PostgreSQL and SQLite support

•
Docker containerization

•
Google Cloud Run deployment

•
Comprehensive API documentation




<div align="center">

⬆ back to top

Made with ❤️ by the Fast Wallet Service Team

GitHub • Issues • Discussions

</div>

