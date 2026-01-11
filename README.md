# Property Agentic Engine 🏠🤖

Multi-agent AI system for comprehensive real estate property research using Perplexity AI.

## 🎯 Features

- **5 Specialized AI Agents** - Property basics, financials, neighborhood, market trends, soft signals
- **24-Hour Caching** - Redis cache eliminates redundant API calls
- **Real-Time Research** - Fresh data from Perplexity's web-connected AI
- **Cost Efficient** - ~$0.025 per property (5 agents × $0.005)
- **Production Ready** - PostgreSQL storage, async processing, error handling

## 📋 Architecture

```
User Request → Cache Check → Multi-Agent Research → Cache & Store → Response
                ↓                    ↓                    ↓
            Redis (24hr)      5 Parallel Agents    PostgreSQL
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Perplexity API key

### Installation

```bash
# 1. Clone repository
git clone <repo-url>
cd property-agentic-engine

# 2. Setup environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
./scripts/install.sh  # Or: pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env with your API keys

# 5. Validate
python scripts/check-env.py
```

### Usage

```bash
# Start API server
python api.py

# Test endpoint
curl "http://localhost:5000/api/property?address=350%20Fifth%20Avenue&city=New%20York&state=NY"
```

## 📚 Documentation

See `development.md` for detailed setup progress and technical documentation.

## 💰 Cost Analysis

- **Per Property:** $0.025 (5 agents × $0.005)
- **1,000 properties:** $25
- **With 24hr cache hit rate of 80%:** $5/day for 1000 daily requests

## 🧪 Testing

```bash
pytest tests/
```

## 📄 License

MIT
