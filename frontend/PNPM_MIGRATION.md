# Migrating from npm to pnpm

This project now uses **pnpm** instead of npm for faster installs and better disk space efficiency.

## Why pnpm?

- **Faster**: Installs packages faster than npm
- **Efficient**: Uses hard links to save disk space (one copy of each package version)
- **Strict**: Better dependency management and fewer surprises
- **Compatible**: Works with existing package.json files

## For Existing Developers

If you already have this project set up with npm, here's how to migrate:

### 1. Install pnpm

```bash
# Using npm (ironically)
npm install -g pnpm

# Or using Homebrew (macOS/Linux)
brew install pnpm

# Or using Corepack (Node 16.13+)
corepack enable
corepack prepare pnpm@latest --activate
```

### 2. Remove npm artifacts

```bash
cd frontend

# Remove npm lockfile and node_modules
rm -rf node_modules package-lock.json

# Clean npm cache (optional)
npm cache clean --force
```

### 3. Install with pnpm

```bash
# Install dependencies
pnpm install

# This will create pnpm-lock.yaml
```

### 4. Verify everything works

```bash
# Run dev server
pnpm run dev

# Run tests
pnpm run test

# Build for production
pnpm run build
```

## Docker Users

If you're using Docker (recommended for production), the Dockerfile already handles pnpm:

```bash
# Rebuild the frontend container
docker compose -f docker-compose.prod.yml build frontend

# Or use the helper script
./quick-rebuild.sh
```

## Common pnpm Commands

| npm command | pnpm equivalent |
|-------------|-----------------|
| `npm install` | `pnpm install` |
| `npm install <pkg>` | `pnpm add <pkg>` |
| `npm uninstall <pkg>` | `pnpm remove <pkg>` |
| `npm run <script>` | `pnpm run <script>` or `pnpm <script>` |
| `npm test` | `pnpm test` |
| `npm run dev` | `pnpm dev` |
| `npm run build` | `pnpm build` |

## Troubleshooting

### "command not found: pnpm"

Make sure pnpm is installed globally:
```bash
npm install -g pnpm
```

### Peer dependency warnings

pnpm is stricter about peer dependencies. If you see warnings, they can usually be ignored, or you can add to `.npmrc`:
```
strict-peer-dependencies=false
```

### Module resolution issues

If you get import errors, try:
```bash
pnpm install --force
```

### Still having issues?

You can still use npm if needed:
```bash
npm install
npm run dev
```

But pnpm is recommended for consistency with the team and Docker builds.
