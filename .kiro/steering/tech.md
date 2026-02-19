# Technology Stack

## Backend (tradewizard-agents)

### Runtime & Language
- Node.js 18+
- TypeScript 5.9+ with strict mode
- ESM modules (type: "module")

### AI & Workflow Framework
- **LangGraph**: Multi-agent workflow orchestration with state management
- **LangChain**: LLM integrations and tool-calling capabilities
- **Opik**: LLM observability, tracing, and cost tracking

### LLM Providers
- OpenAI (GPT-4, GPT-4-turbo, GPT-4o-mini)
- Anthropic (Claude-3-sonnet, Claude-3-haiku)
- Google (Gemini-1.5-pro, Gemini-1.5-flash, Gemini-2.5-flash)
- Amazon Nova (via AWS Bedrock)

### Database & Storage
- Supabase (PostgreSQL) for persistence
- LangGraph checkpointers: memory, sqlite, postgres

### External APIs
- Polymarket CLOB API (@polymarket/clob-client)
- NewsData.io API for news intelligence
- Polymarket Gamma API for market data

### Testing
- Vitest for unit and integration tests
- fast-check for property-based testing
- 30s timeout for LLM-dependent tests

### Build & Development
- esbuild for production builds
- tsx for development with hot reload
- ESLint + Prettier for code quality

## Python Backend (doa)

### Runtime & Language
- Python 3.10+
- Type hints with mypy

### AI Framework
- LangGraph for workflow orchestration
- LangChain for LLM integrations
- Digital Ocean Gradient AI Platform
- Opik for observability

### LLM Models
- Llama-3.3-70b-instruct (default)
- Llama-3.1-8b-instruct (budget option)

### Database
- Supabase (PostgreSQL)
- SQLAlchemy for ORM

### Testing
- pytest with pytest-asyncio
- Hypothesis for property-based testing
- pytest-cov for coverage

### Code Style
- PEP 8 guidelines
- Black formatter (120 char line length)
- flake8 for linting
- snake_case for functions/variables
- PascalCase for classes

## Frontend (tradewizard-frontend)

### Framework
- Next.js 16 with App Router
- React 19
- TypeScript 5

### Styling
- Tailwind CSS 4
- Framer Motion for animations
- Lucide React for icons

### State Management
- TanStack React Query (@tanstack/react-query)

### Authentication & Blockchain
- Magic Link SDK for authentication
- ethers.js v5 for Ethereum interactions
- viem for modern Ethereum utilities

### Data Fetching
- Supabase client (@supabase/supabase-js)
- Polymarket CLOB client

### UI Components
- Recharts for data visualization
- react-intersection-observer for lazy loading

## Common Commands

### Backend (tradewizard-agents)

```bash
# Development
npm run dev              # Start with hot reload
npm run build            # Build for production
npm start                # Run production build

# Testing
npm test                 # Run all tests
npm run test:watch       # Watch mode
npm run test:e2e         # End-to-end tests

# CLI
npm run cli -- analyze <condition-id>  # Analyze market
npm run cli -- history <condition-id>  # Query history

# Monitoring Service
npm run monitor:start    # Start monitoring
npm run monitor:stop     # Stop monitoring
npm run monitor:status   # Check status

# Database
npm run migrate          # Run migrations
npm run migrate:status   # Check migration status

# Code Quality
npm run lint             # Check linting
npm run lint:fix         # Fix linting issues
npm run format           # Format code
npm run format:check     # Check formatting
```

### Python Backend (doa)

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Development
python main.py analyze <condition-id>  # Analyze market
python main.py history <condition-id>  # Query history
python main.py monitor                 # Start monitoring

# Testing
pytest                   # Run all tests
pytest -m "not property" # Unit tests only
pytest -m property       # Property-based tests only
pytest --cov=.          # With coverage

# Code Quality
flake8 . --max-line-length=120
black . --line-length=120
mypy . --ignore-missing-imports

# Database
python -m database.migrations.001_initial_schema
```

### Frontend (tradewizard-frontend)

```bash
# Development
npm run dev              # Start dev server (localhost:3000)
npm run build            # Build for production
npm start                # Run production build

# Code Quality
npm run lint             # Check linting
```

## Configuration Files

- `.env` / `.env.example` - Environment variables
- `package.json` - Node.js dependencies and scripts
- `tsconfig.json` - TypeScript configuration
- `vitest.config.ts` - Vitest test configuration
- `requirements.txt` - Python dependencies
- `.env.production` - Production environment variables
