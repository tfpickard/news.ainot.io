# Contributing to Singl News

Thank you for your interest in contributing to Singl News! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker and Docker Compose
- PostgreSQL (for local development)
- OpenAI API key

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd news.ainot.io
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Backend setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Frontend setup**
   ```bash
   cd frontend
   npm install
   ```

## Code Style

### Backend (Python)

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings for functions and classes
- Keep functions focused and modular

### Frontend (TypeScript/Svelte)

- Use TypeScript for type safety
- Follow consistent naming conventions
- Keep components small and reusable
- Maintain the in-character design philosophy

## Testing

### Backend Tests

```bash
cd backend
pytest -v
```

Write tests for:
- API endpoints
- Database models
- Service layer logic
- RSS feed parsing

### Frontend Tests

```bash
cd frontend
npm run test
```

Write tests for:
- API client functions
- Store logic
- Utility functions

## Project Structure

### Backend

```
backend/
├── app/
│   ├── main.py          # FastAPI app entry point
│   ├── config.py        # Configuration management
│   ├── models.py        # Database models
│   ├── api.py           # REST endpoints
│   ├── ws.py            # WebSocket handlers
│   ├── scheduler.py     # Background jobs
│   └── ...
├── tests/               # Test files
└── alembic/            # Database migrations
```

### Frontend

```
frontend/
├── src/
│   ├── lib/            # Shared utilities
│   └── routes/         # SvelteKit pages
├── static/             # Static assets
└── tests/              # Test files
```

## Design Philosophy

### In-Character Constraints

When working on user-facing features:

- **Never break character**: The UI presents as a legitimate news service
- **No meta-commentary**: Don't reference AI, fiction, or the experimental nature
- **Serious tone**: Maintain journalistic confidence
- **Minimalist design**: Clean, readable, newspaper-like

Code comments and internal documentation can be explicit about the project's nature.

### Story Evolution

The core concept is a **perpetually evolving single narrative**:

- Each update extends the existing story (never resets)
- Maintain narrative continuity across updates
- Use context summaries to preserve history
- Seamlessly integrate new events into established storylines

## Making Changes

### Feature Development

1. Create a new branch from main
2. Make your changes
3. Add tests for new functionality
4. Update documentation if needed
5. Test locally
6. Submit a pull request

### Database Migrations

When modifying models:

```bash
# Create migration
make migrate-create

# Or manually:
cd backend
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head
```

### API Changes

When modifying the API:

1. Update `app/api.py` endpoints
2. Update `app/schemas.py` Pydantic models
3. Update frontend `src/lib/api.ts` if needed
4. Add tests for new endpoints
5. Update API documentation in README

## Common Tasks

### Running the Full Stack

```bash
# Start all services
make up

# View logs
make logs

# Stop services
make down
```

### Running Individual Services

```bash
# Backend only
make dev-backend

# Frontend only
make dev-frontend
```

### Database Tasks

```bash
# Access database shell
make db-shell

# Run migrations
make migrate
```

## Debugging

### Backend Debugging

- Check logs: `docker-compose logs backend`
- Set `SINGL_LOG_LEVEL=DEBUG` in .env
- Use Python debugger: Add `import pdb; pdb.set_trace()`

### Frontend Debugging

- Check browser console
- Use Svelte DevTools
- Check network tab for API calls

### Common Issues

**Database connection errors:**
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env

**OpenAI API errors:**
- Verify OPENAI_API_KEY is set
- Check rate limits and credits

**WebSocket connection failures:**
- Ensure CORS is configured correctly
- Check SINGL_WS_ORIGIN setting

## Code Review Guidelines

When reviewing pull requests:

- Check code style and consistency
- Verify tests are included
- Ensure documentation is updated
- Test the changes locally
- Check that the "in-character" design is maintained
- Verify no breaking changes to the API

## Questions?

If you have questions about contributing, please:

- Open an issue for discussion
- Check existing documentation
- Review the project README

## License

By contributing, you agree that your contributions will be part of this experimental art/technology project.

---

Thank you for contributing to Singl News! Remember: There is only one story. Everything else is commentary.
