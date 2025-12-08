# Vercel Serverless Deployment Guide

This guide will help you deploy your FastAPI backend to Vercel's free tier using serverless functions.

## ⚠️ Important Considerations

### Database
- **SQLite will NOT work** in serverless (writes don't persist, concurrent issues)
- **You MUST use PostgreSQL** or another cloud database
- Recommended free options:
  - [Neon.tech](https://neon.tech) - Free PostgreSQL (5GB)
  - [Supabase](https://supabase.com) - Free PostgreSQL (500MB)
  - [Railway.app](https://railway.app) - Free PostgreSQL (5GB)
  - [Render.com](https://render.com) - Free PostgreSQL (90 days)

### ML Models
- Model files in `backend/models/` will be included in deployment
- Ensure models are committed to Git (not in .gitignore)
- First request may be slower due to model loading

### Cold Starts
- First request after inactivity may take 2-5 seconds
- Subsequent requests are fast (< 100ms)
- Free tier has 100GB bandwidth/month

## 📋 Pre-Deployment Checklist

- [ ] Set up PostgreSQL database (see options above)
- [ ] Get database connection string
- [ ] Get DeepSeek API key (for AI features)
- [ ] Ensure all model files are committed to Git
- [ ] Test backend locally with PostgreSQL

## 🚀 Deployment Steps

### Step 1: Set Up PostgreSQL Database

1. Sign up for a free PostgreSQL service (Neon, Supabase, etc.)
2. Create a new database
3. Copy the connection string (format: `postgresql://user:password@host:port/database`)
4. Run migrations to set up schema:
   ```bash
   cd backend
   # Update .env with PostgreSQL URL
   alembic upgrade head
   ```

### Step 2: Prepare Backend for Deployment

1. **Update `.env.example`** with production values (don't commit `.env`)

2. **Ensure models are committed:**
   ```bash
   git add backend/models/*.joblib
   git commit -m "Add ML models"
   ```

3. **Test locally with PostgreSQL:**
   ```bash
   # Update DATABASE_URL in .env to PostgreSQL
   cd backend
   python -m uvicorn app.main:app --reload
   ```

### Step 3: Deploy to Vercel

#### Option A: Via Vercel Dashboard (Recommended)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository
3. **Configure project:**
   - **Root Directory**: `backend` (IMPORTANT!)
   - **Framework Preset**: Other
   - **Build Command**: Leave empty (Vercel auto-detects)
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty

4. **Add Environment Variables:**
   - `DATABASE_URL` = `postgresql://user:pass@host:port/db`
   - `DEEPSEEK_API_KEY` = `your_deepseek_key`
   - `CORS_ORIGINS` = `https://your-frontend.vercel.app` (your frontend URL)
   - `ENVIRONMENT` = `production`

5. Click **Deploy**

#### Option B: Via Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Navigate to backend:
   ```bash
   cd backend
   ```

3. Login:
   ```bash
   vercel login
   ```

4. Deploy:
   ```bash
   vercel
   ```
   - Follow prompts
   - Set root directory to `.` (current directory)
   - Add environment variables when prompted

5. For production:
   ```bash
   vercel --prod
   ```

### Step 4: Set Environment Variables

After deployment, add environment variables in Vercel Dashboard:

1. Go to your project → **Settings** → **Environment Variables**
2. Add these variables:

| Variable | Value | Example |
|----------|-------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `DEEPSEEK_API_KEY` | Your DeepSeek API key | `sk-...` |
| `CORS_ORIGINS` | Frontend URL(s) | `https://your-app.vercel.app` |
| `ENVIRONMENT` | `production` | `production` |

3. **Redeploy** after adding variables (Vercel → Deployments → Redeploy)

### Step 5: Test Your Deployment

1. Your API will be at: `https://your-project.vercel.app`
2. Test endpoints:
   - Health: `https://your-project.vercel.app/api/health`
   - Docs: `https://your-project.vercel.app/api/docs`
   - Root: `https://your-project.vercel.app/`

### Step 6: Update Frontend Environment Variable

1. Go to your **frontend** Vercel project
2. **Settings** → **Environment Variables**
3. Add: `VITE_API_BASE_URL` = `https://your-backend.vercel.app`
4. **Redeploy** frontend

## 🔧 Troubleshooting

### Build Fails
- Check build logs in Vercel Dashboard
- Ensure `requirements-vercel.txt` has all dependencies
- Check Python version (Vercel uses Python 3.9 by default)

### Database Connection Errors
- Verify `DATABASE_URL` is correct
- Check if database allows connections from Vercel IPs
- Some free databases require IP whitelisting

### 500 Errors
- Check function logs in Vercel Dashboard
- Verify environment variables are set
- Check if models are accessible (not in .gitignore)

### CORS Errors
- Update `CORS_ORIGINS` to include your frontend URL
- Ensure frontend URL matches exactly (with https://)

### Cold Start Timeouts
- Free tier has 10-second timeout
- Optimize model loading (lazy load if possible)
- Consider upgrading to Pro for longer timeouts

## 📊 Monitoring

- View logs: Vercel Dashboard → Your Project → Functions → Logs
- Monitor usage: Settings → Usage
- Check errors: Deployments → View logs

## 🎯 Next Steps

1. Set up database migrations (if using Alembic)
2. Configure custom domain (optional)
3. Set up monitoring/alerts
4. Optimize cold starts if needed

## 💡 Tips

- Use connection pooling for PostgreSQL (already configured in `database.py`)
- Cache model loading if possible
- Monitor function execution time
- Set up error tracking (Sentry, etc.)

---

**Need Help?** Check Vercel docs: https://vercel.com/docs/functions/serverless-functions/runtimes/python
