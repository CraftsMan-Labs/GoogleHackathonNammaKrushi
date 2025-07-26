# Namma Krushi - Quick Setup Guide

## 🚀 5-Minute Setup

### Prerequisites
- Python 3.9+ OR Docker
- Gemini API Key (get from https://makersuite.google.com/app/apikey)

### Option 1: Docker Setup (Recommended)
```bash
# 1. Clone repository
git clone <your-repo>
cd namma-krushi

# 2. Create .env file
echo "GEMINI_API_KEY=your-gemini-api-key-here" > .env

# 3. Run with Docker
docker-compose up -d

# 4. Open browser
http://localhost:8000
```

### Option 2: Local Python Setup
```bash
# 1. Clone repository
git clone <your-repo>
cd namma-krushi

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
echo "GEMINI_API_KEY=your-gemini-api-key-here" > .env

# 5. Run application
python -m uvicorn app.main:app --reload

# 6. Open browser
http://localhost:8000
```

## 📁 Project Structure
```
namma-krushi/
├── app/
│   ├── main.py           # FastAPI application
│   ├── config.py         # Settings (reads .env)
│   ├── database.py       # SQLite setup
│   ├── models.py         # Database models
│   ├── api/
│   │   ├── auth.py       # User authentication
│   │   ├── farms.py      # Farm management
│   │   └── live_chat.py  # WebSocket chat
│   └── services/
│       └── gemini_live.py # Gemini integration
├── static/               # Frontend files
├── data/                # SQLite database
├── .env                 # Your API key
├── requirements.txt     # Python packages
├── Dockerfile          # Docker config
└── docker-compose.yml  # Docker compose
```

## 🔑 Environment Variables
Create `.env` file:
```bash
GEMINI_API_KEY=your-gemini-api-key-here
SECRET_KEY=any-random-secret-key
```

## 💰 Cost Breakdown
- **Gemini API**: Free tier (60 requests/min)
- **Database**: SQLite (free)
- **Hosting**: 
  - Local: $0
  - VPS: ~$5/month
  - GCP e2-micro: Free tier

**Total: $0-5/month**

## 🌟 Key Features
1. **Voice Chat in Kannada** - Real-time conversations
2. **Image Analysis** - Disease detection from photos
3. **Smart TODOs** - AI-generated farming tasks
4. **Offline Capable** - SQLite works without internet
5. **No Cloud Lock-in** - Deploy anywhere

## 🚢 Deployment Options

### Deploy to VPS
```bash
# SSH to your server
ssh user@your-server

# Install Docker
curl -fsSL https://get.docker.com | sh

# Clone and run
git clone <your-repo>
cd namma-krushi
echo "GEMINI_API_KEY=your-key" > .env
docker-compose up -d
```

### Deploy to GCP (Free Tier)
```bash
# Create VM
gcloud compute instances create namma-krushi \
  --machine-type=e2-micro \
  --zone=us-central1-a

# SSH and deploy
gcloud compute ssh namma-krushi
# Follow VPS steps above
```

## 📱 Frontend Access
- Web App: `http://your-server:8000`
- API Docs: `http://your-server:8000/docs`
- WebSocket: `ws://your-server:8000/ws/chat/{user_id}/{farm_id}`

## 🧪 Testing
```bash
# Health check
curl http://localhost:8000/health

# Should return:
{
  "status": "healthy",
  "gemini": "connected",
  "database": "sqlite"
}
```

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Permission Denied (Docker)
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

### Database Issues
```bash
# Reset database
rm data/namma_krushi.db
python -m app.database init_db
```

## 📞 Support
- GitHub Issues: [your-repo]/issues
- Documentation: /DOCS folder

## 🎯 Next Steps
1. Get Gemini API key
2. Run setup (5 minutes)
3. Test voice chat
4. Deploy to server
5. Share with farmers!

---

**Built with ❤️ for Indian Farmers**