# Rebuilding Production Containers

## Issue: Images Not Working & Slow Startup

The image generation wasn't working because:
1. **Pillow** dependency was added but containers weren't rebuilt
2. **Font libraries** were missing from the Docker image

The slow startup is normal for the first build because:
- Backend installs Python dependencies including Pillow
- Frontend compiles the entire SvelteKit app
- Subsequent starts are much faster

## Quick Fix

Run the **quick rebuild** script (uses cache, faster):

```bash
./quick-rebuild.sh
```

This will:
- Rebuild backend and frontend with cache
- Restart all services
- Show logs

## Full Rebuild

If you need a complete rebuild (e.g., after major dependency changes):

```bash
./rebuild-prod.sh
```

This will:
- Stop all containers
- Build everything from scratch (no cache)
- Start all services
- Show logs

**Note:** This takes longer (5-10 minutes) but ensures everything is fresh.

## What Changed

### Backend Dockerfile
Added image processing dependencies:
- `libjpeg-dev` - JPEG support for Pillow
- `zlib1g-dev` - PNG compression
- `libfreetype6-dev` - Font rendering
- `fonts-dejavu-core` - TrueType fonts for text on images

### New Dependencies
- **Pillow** - Python image processing library
- System fonts for quote card generation

### Image Generation
- Endpoint: `/api/story/{id}/quote-image?quote_index=0`
- Generates 1200x630px PNG images
- Includes quote text, category, absurdity score, branding
- Optimized for social media sharing

## Testing Image Generation

After rebuilding, test the image generation:

```bash
# Get the latest story ID
curl http://localhost:8001/api/story/latest | jq .id

# Generate an image for that story
curl "http://localhost:8001/api/story/1/quote-image?quote_index=0" -o test.png

# Verify the image was created
file test.png
```

You should see: `test.png: PNG image data, 1200 x 630, 8-bit/color RGB, non-interlaced`

## Startup Time

**First build:** 5-10 minutes
- Installing all dependencies
- Compiling frontend assets

**Subsequent starts:** 10-30 seconds
- Database migrations
- Service initialization

## Troubleshooting

### Image generation returns errors
Check backend logs:
```bash
docker compose -f docker-compose.prod.yml logs backend | grep -i "image\|pillow\|font"
```

### Frontend not building
Check frontend logs:
```bash
docker compose -f docker-compose.prod.yml logs frontend
```

### Database connection issues
Check if migrations ran:
```bash
docker compose -f docker-compose.prod.yml exec backend alembic current
```

## Environment Variables

Make sure these are set in `.env.production`:

```bash
# Authentication
SINGL_ADMIN_PASSWORD=your_secure_password
SINGL_ADMIN_API_KEY=your_persistent_api_key

# OpenAI (for quote extraction)
OPENAI_API_KEY=your_openai_key

# Database
DATABASE_URL=postgresql://singl:password@db:5432/singl
```

## Manual Build Commands

If you prefer manual control:

```bash
# Stop services
docker compose -f docker-compose.prod.yml down

# Build specific service
docker compose -f docker-compose.prod.yml build backend

# Start services
docker compose -f docker-compose.prod.yml up -d

# View logs
docker compose -f docker-compose.prod.yml logs -f
```
