# Vedic Astrology Application

A comprehensive Vedic astrology API that provides accurate birth chart calculations using True Chitrapaksha Ayanamsa, planetary positions, nakshatras, and Vimshottari Dasha predictions.

## Features

- **Accurate Vedic Astrology Calculations**
  - Birth chart generation using True Chitrapaksha Ayanamsa
  - Support for multiple ayanamsa options (Lahiri, Raman, Krishnamurti)
  - Planetary positions, nakshatras, and zodiac sign placements
  - Vimshottari Dasha predictions with sub-dasha levels
  - Divisional charts (D-2, D-3, D-7, D-9, D-12, D-30)
  - Planetary strength calculations (Bala)
  - Retrograde planet detection

- **User-Friendly Experience**
  - Birth data validation with proper timezone handling
  - Automatic timezone detection from coordinates
  - Support for geocoding birth locations
  - Storage of charts for registered users
  - Anonymous chart creation

- **Modern Architecture**
  - FastAPI for high-performance API endpoints
  - PostgreSQL database with JSONB for flexible data storage
  - Redis caching for improved performance
  - JWT authentication with refresh tokens
  - Rate limiting for API protection

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (optional)
- Swiss Ephemeris files (included in the repository)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/VivXwan/astrology-app.git
   cd astrology-app
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file with your database credentials and other configuration options:
   ```
   DATABASE_URL=postgresql://username:password@host:port/database_name
   SECRET_KEY=your-secure-secret-key-here
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
   ```

5. Start the application:
   ```bash
   uvicorn app:app --reload
   ```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/users` | POST | Create a new user |
| `/login` | POST | Authenticate and receive JWT token |
| `/refresh` | POST | Refresh access token |
| `/logout` | POST | Invalidate refresh token |
| `/charts` | POST | Generate a new chart |
| `/charts/{chart_id}` | GET | Retrieve a saved chart |
| `/geocode` | POST | Search for locations |
| `/health` | GET | Health check endpoint |

## API Documentation

Will be added soon.

## Chart Generation Example

```python
import requests

url = "http://localhost:8000/charts"
data = {
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 10,
    "minute": 30,
    "second": 0,
    "latitude": 28.6139,
    "longitude": 77.2090
}

response = requests.post(url, json=data)
chart = response.json()
```

## Authentication Example

```python
import requests

# Register user
register_url = "http://localhost:8000/users"
user_data = {
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword"
}
requests.post(register_url, json=user_data)

# Login
login_url = "http://localhost:8000/login"
login_data = {
    "email": "john@example.com",
    "password": "securepassword"
}
response = requests.post(login_url, json=login_data)
tokens = response.json()

# Use token for authenticated requests
headers = {
    "Authorization": f"Bearer {tokens['access_token']}"
}
chart_data = {...}  # Birth data as shown in the chart generation example
response = requests.post("http://localhost:8000/charts", json=chart_data, headers=headers)
```

## Deployment Considerations

For production deployment, consider:

1. **Security**
   - Use HTTPS with proper TLS certificates
   - Implement proper secrets management
   - Set specific CORS origins
   - Configure rate limiting appropriately

2. **Performance**
   - Set up proper Redis caching
   - Configure database connection pooling
   - Consider containerization with Docker

3. **Monitoring**
   - Add application monitoring
   - Set up error tracking
   - Configure proper logging

## License

[MIT License](LICENSE)

## Acknowledgements

- [Swiss Ephemeris](https://www.astro.com/swisseph/) for precise astronomical calculations
- [FastAPI](https://fastapi.tiangolo.com/) for the high-performance API framework
- [SQLAlchemy](https://www.sqlalchemy.org/) for database ORM
- [PostgreSQL](https://www.postgresql.org/) for reliable data storage 
