# Quick Setup Guide for Singl News

This guide will get you up and running with Singl News in under 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

## Quick Start (Docker)

### 1. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your preferred editor
```

Minimum required configuration:
```env
OPENAI_API_KEY=sk-your-key-here
```

### 2. Start the Application

```bash
# Build and start all services
docker-compose up --build
```

This will:
- Start PostgreSQL database
- Build and start the FastAPI backend
- Build and start the SvelteKit frontend
- Run database migrations
- Begin generating the story

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Watch It Work

The system will:
1. Fetch RSS feeds from major news sources
2. Generate the first story version (takes ~30 seconds)
3. Continue updating every 30 minutes (configurable)

You can watch the logs:
```bash
docker-compose logs -f backend
```

## Local Development (Without Docker)

### Backend

```bash
# 1. Start PostgreSQL (local or Docker)
docker run -d -p 5432:5432 -e POSTGRES_USER=singl -e POSTGRES_PASSWORD=singl -e POSTGRES_DB=singl postgres:16

# 2. Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
export DATABASE_URL="postgresql+psycopg2://singl:singl@localhost:5432/singl"
export OPENAI_API_KEY="your-key-here"

# 4. Run migrations
alembic upgrade head

# 5. Start backend
python -m app.main
```

Backend will be available at http://localhost:8000

### Frontend

```bash
cd frontend
pnpm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env
echo "VITE_WS_URL=ws://localhost:8000/ws/story" >> .env

pnpm run dev
```

Frontend will be available at http://localhost:3000

## Configuration Options

### Update Frequency

Change how often the story updates:
```env
SINGL_UPDATE_MINUTES=15  # Update every 15 minutes
```

### Model Selection

Use a different OpenAI model:
```env
SINGL_MODEL_NAME=gpt-4-turbo-preview
# or
SINGL_MODEL_NAME=gpt-3.5-turbo
```

### Custom RSS Feeds

Add your own news sources:
```env
SINGL_FEEDS=http://rss.cnn.com/rss/cnn_topstories.rss,https://your-feed.com/rss
```

### Context Window

Adjust how much history is used for context:
```env
SINGL_CONTEXT_STEPS=5   # Use last 5 versions (lighter)
# or
SINGL_CONTEXT_STEPS=20  # Use last 20 versions (more context)
```

## Useful Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop everything
docker-compose down

# Stop and remove all data
docker-compose down -v

# Run tests
make test

# Access database
docker-compose exec db psql -U singl -d singl
```

## Troubleshooting

### "No stories available yet"

The first story is being generated. Wait 30-60 seconds and refresh.

### Database connection errors

```bash
# Check if database is running
docker-compose ps

# Restart database
docker-compose restart db
```

### OpenAI API errors

- Check your API key is correct
- Verify you have credits: https://platform.openai.com/account/usage
- Check rate limits

### WebSocket not connecting

- Ensure backend is running
- Check browser console for errors
- Verify CORS settings in backend config

### Port already in use

Change ports in docker-compose.yml:
```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Use port 8001 instead
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Explore the API at http://localhost:8000/docs
- Monitor the story evolution in the frontend

## Production Deployment

For production deployment, see:
- `docker-compose.prod.yml` for production configuration
- `.env.production.example` for production environment variables
- README.md section on deployment

---

**Remember**: The first story generation takes a minute. Be patient, and soon you'll witness THE STORY begin to unfold.
