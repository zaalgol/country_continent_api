# Country-Continent API

## Overview

A FastAPI application that allows CRUD operations on countries and continents, with capabilities to search, paginate, and filter data based on update timestamps.

## Features

- **Async FastAPI:** Leveraging asynchronous programming for high performance.
- **CRUD Operations:** Create, Read, Update, Delete for Countries and Continents.
- **Pagination:** Efficient data retrieval with pagination support.
- **Filtering:** Search by `updated_at` timestamp.
- **Database:** PostgreSQL with SQLAlchemy and Alembic for migrations.
- **Testing:** Comprehensive unit and integration tests using pytest and pytest-asyncio.
- **Logging:** Configured logging for monitoring and debugging.
- **Deployment:** Deployable to Heroku with CI/CD integration via GitHub Actions.

## Setup and Installation

### Prerequisites

- Python 3.10
- PostgreSQL
- Git
- Heroku CLI

### Local Development

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

2. **Create a Virtual Environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a .env file in the root directory and add:
   ```bash
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/countries_db
   AWS_ACCESS_KEY_ID=your_aws_access_key_id
   AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
   AWS_S3_BUCKET=your_s3_bucket_name
   ```

5. **Run Database Migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Seed Initial Data:**
   ```bash
   python app/initial_data.py
   ```

7. **Start the Application:**
   ```bash
   python run.py
   ```

8. **Access API Documentation:**

   Navigate to http://localhost:8000/docs to view the interactive Swagger UI.



