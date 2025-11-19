# Singl News

**The world's only unified continuous news story.**

Singl News presents a single, perpetually evolving narrative constructed from multiple real RSS news feeds. Instead of fragmenting reality into discrete articles, it recognizes that all events are interconnected threads in one continuous story.

## 🌐 Domains

- **Primary**: `singl.news`
- **Mirror**: `news.ainot.io`

## 🎯 Concept

There is only ONE story in existence. Every news event is just a new paragraph in this ongoing, global, unified narrative. The story evolves forever—never resetting, only growing and recontextualizing what came before.

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI**: OpenAI API for story generation
- **Scheduling**: APScheduler for periodic updates
- **RSS**: Feedparser for news ingestion
- **WebSocket**: Real-time story updates

### Frontend (SvelteKit)
- **Framework**: SvelteKit with TypeScript
- **Styling**: Modern CSS with newspaper design
- **Real-time**: WebSocket client for live updates
- **Features**: Infinite scroll doomscroll experience

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL 16
- **Migrations**: Alembic

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd news.ainot.io
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Start the services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

The system will automatically:
- Initialize the database
- Run migrations
- Fetch RSS feeds
- Generate the first story version
- Continue updating every N minutes (default: 30)

## 🛠️ Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+psycopg2://singl:singl@localhost:5432/singl"
export OPENAI_API_KEY="your-key-here"

# Run migrations
alembic upgrade head

# Start development server
python -m app.main
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev
```

## 📋 Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://singl:singl@db:5432/singl` |
| `OPENAI_API_KEY` | OpenAI API key | **Required** |
| `SINGL_MODEL_NAME` | OpenAI model to use | `gpt-4-turbo-preview` |
| `SINGL_UPDATE_MINUTES` | Minutes between story updates | `30` |
| `SINGL_CONTEXT_STEPS` | Number of recent versions for context | `10` |
| `SINGL_FEEDS` | Comma-separated RSS feed URLs | Multiple defaults |
| `SINGL_LOG_LEVEL` | Logging level | `INFO` |

### Frontend

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |
| `VITE_WS_URL` | WebSocket URL | `ws://localhost:8000/ws/story` |

## 📡 API Endpoints

### REST API

- `GET /api/story/current` - Get the latest story version
- `GET /api/story/history?limit=20&offset=0` - Get paginated story history
- `GET /api/story/{id}` - Get specific story version
- `GET /api/meta` - Get service metadata
- `GET /api/health` - Health check
- `GET /docs` - Interactive API documentation

### WebSocket

- `ws://localhost:8000/ws/story` - Real-time story updates

## 🗄️ Database Schema

### StoryVersion
- `id` - Primary key
- `created_at` - Timestamp (indexed)
- `full_text` - Complete story text
- `summary` - Brief summary
- `context_summary` - Compressed narrative context
- `sources_snapshot` - JSON of contributing feed items
- `token_stats` - JSON of OpenAI usage statistics

### FeedItem
- `id` - Primary key
- `feed_url` - Source feed URL
- `feed_name` - Source name
- `title` - Item title
- `summary` - Item description
- `link` - Item URL
- `published_at` - Publication timestamp
- `fetched_at` - Ingestion timestamp
- `content_hash` - Deduplication hash (unique)
- `raw` - JSON of raw feed data

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## 🎨 Design Philosophy

### In-Character UI
- **No meta-commentary**: Never mentions AI, fiction, or parody
- **Serious tone**: Confident, newspaper-like presentation
- **Minimalist design**: Clean typography, single-column layout
- **Continuous narrative**: History presented as scrollable extensions

### Story Evolution
- **Never resets**: Each update extends the existing narrative
- **Context preservation**: Uses rolling summaries to maintain continuity
- **Seamless integration**: New events woven into established storylines
- **Infinite timeline**: Complete history preserved in database

## 📁 Project Structure

```
news.ainot.io/
├── backend/
│   ├── alembic/              # Database migrations
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app
│   │   ├── config.py        # Settings
│   │   ├── database.py      # DB setup
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── api.py           # REST endpoints
│   │   ├── ws.py            # WebSocket support
│   │   ├── scheduler.py     # Background jobs
│   │   ├── story_service.py # Business logic
│   │   ├── rss_client.py    # Feed fetching
│   │   └── openai_client.py # AI integration
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api.ts       # API client
│   │   │   ├── ws.ts        # WebSocket client
│   │   │   └── config.ts    # Configuration
│   │   └── routes/
│   │       ├── +layout.svelte
│   │       ├── +page.svelte          # Home (live story)
│   │       ├── history/+page.svelte  # Archive
│   │       ├── story/[id]/+page.svelte  # Story detail
│   │       └── about/+page.svelte    # About page
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔄 How It Works

### Story Generation Cycle

1. **RSS Ingestion**
   - Fetches configured RSS feeds
   - Parses and normalizes items
   - Deduplicates and stores in database

2. **Context Building**
   - Retrieves recent story versions
   - Compresses older versions into summary
   - Gathers new feed items since last update

3. **AI Generation**
   - Sends context + recent excerpts + new events to OpenAI
   - Model generates continuation that:
     - Maintains narrative continuity
     - Integrates new developments
     - Preserves established characters/themes
     - Never resets or starts over

4. **Storage & Broadcast**
   - Saves new story version to database
   - Generates context summary for next iteration
   - Broadcasts to all connected WebSocket clients

5. **Repeat**
   - Cycle runs every N minutes (configurable)
   - Story grows perpetually

## 🎭 Character Constraints

### Public-Facing (UI/Website)
- Maintains in-universe character as legitimate news organization
- No admission of being AI-generated or fictional
- Professional, confident tone throughout
- Vague "automated editorial processes" if explanation needed

### Internal (Code/Docs)
- Can freely acknowledge it's an art/experimental project
- Technical documentation can be explicit about implementation
- Comments and internal docs explain actual functionality

## 🚢 Deployment

### Production Considerations

1. **Environment Variables**: Set proper production values
2. **Database**: Use managed PostgreSQL service or proper backups
3. **API Keys**: Secure OpenAI API key management
4. **Domain**: Configure proper CORS and WebSocket origins
5. **Scaling**: Consider rate limits and token costs
6. **Monitoring**: Set up logging and error tracking
7. **SSL**: Use HTTPS and WSS in production

### Example Production Setup

```bash
# Set production environment variables
export OPENAI_API_KEY="sk-..."
export DATABASE_URL="postgresql://..."
export SINGL_WS_ORIGIN="https://singl.news,https://news.ainot.io"

# Build and deploy
docker-compose -f docker-compose.prod.yml up -d
```

## 📜 License

This project is an experimental art/technology piece exploring AI-generated continuous narrative.

## 🤝 Contributing

This is an experimental project. Feel free to fork and create your own variations.

## ⚠️ Important Notes

- **OpenAI Costs**: Running this will consume OpenAI API credits. Monitor your usage.
- **RSS Feed Limits**: Some feeds may have rate limits or restrictions.
- **Database Growth**: Story history grows indefinitely; plan storage accordingly.
- **Ethical Use**: This is clearly an experimental/art project. Don't misrepresent it as actual news.

---

**Remember**: There is only one story. Everything else is commentary.
