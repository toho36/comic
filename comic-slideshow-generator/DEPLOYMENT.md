# 🚀 Deployment Guide - Hugging Face Spaces

This guide will help you deploy your Comic Slideshow Generator to Hugging Face Spaces.

## 📋 Prerequisites

- GitHub account with your code pushed
- Hugging Face account ([sign up free](https://huggingface.co/join))
- All dependencies installed locally (✅ completed!)

## 🎯 Step-by-Step Deployment

### 1. Prepare Your Repository

First, ensure your repository is ready for deployment:

```bash
# Navigate to project directory
cd comic-slideshow-generator

# Create a virtual environment (if not already created)
py -V:3.13 -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Test locally
py -V:3.13 -m streamlit run app.py
```

### 2. Create Hugging Face Space

1. Go to [huggingface.co](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in the details:
   - **Owner**: Your username
   - **Space name**: `comic-slideshow-generator` (or your preferred name)
   - **SDK**: `Streamlit`
   - **Visibility**: `Public` (recommended) or `Private`
4. Click **"Create Space"**

### 3. Connect GitHub Repository

You have two options:

#### Option A: Upload via Git (Recommended)

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit with Streamlit app"

# Add Hugging Face remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME

# Push to Hugging Face
git push hf main
```

#### Option B: Connect via Web UI

1. Go to your new Space on Hugging Face
2. Click **"Files"** tab
3. Click **"Upload files"**
4. Upload these files:
   - `app.py`
   - `requirements_hf.txt` (rename to `requirements.txt`)
   - `src/` folder (entire directory)
   - `.env` file (if you want to set default configs)

### 4. Configure Requirements

Rename `requirements_hf.txt` to `requirements.txt`:

```bash
mv requirements_hf.txt requirements.txt
git add requirements.txt
git commit -m "Update requirements for deployment"
git push hf main
```

### 5. Set Environment Variables (Optional)

If you want to set default API keys or configs:

1. Go to your Space on Hugging Face
2. Click **"Settings"** tab
3. Scroll to **"Variables and secrets"**
4. Add any environment variables:
   - `OPENAI_API_KEY` (if you want to use OpenAI TTS by default)
   - `TTS_PROVIDER=edge`
   - `OCR_LANGUAGES=eng,ces`
5. Click **"Save"**

### 6. Wait for Build

Hugging Face will automatically:
1. Install all dependencies
2. Build the Space
3. Deploy the app

This typically takes **3-5 minutes**. You'll see the build logs in the **"Logs"** tab.

### 7. Access Your App

Once the build is complete:
- Your app will be available at: `https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME`
- You can share this URL with others!

## 🔍 Monitoring & Logs

### View Logs
- Go to your Space
- Click **"Logs"** tab
- Monitor real-time activity and errors

### Check Build Status
- Green dot ✅ = Running successfully
- Yellow dot ⚠️ = Building/Loading
- Red dot ❌ = Error (check logs)

## 🐛 Troubleshooting

### Issue: Build Fails

**Check logs for common errors:**

1. **Module not found**
   ```bash
   # Ensure requirements.txt is correct
   cat requirements.txt
   ```

2. **Permission errors**
   ```bash
   # Check file permissions are correct
   git ls-files
   ```

3. **Memory exceeded**
   - Free Spaces have 16GB RAM
   - If processing large comics, consider:
     - Reducing video FPS in settings
     - Processing smaller batches
     - Upgrading to paid tier ($9/month for 32GB RAM)

### Issue: App Crashes When Processing

**Possible causes:**
1. **Tesseract not found** - Should be pre-installed on Spaces
2. **FFmpeg missing** - Should be pre-installed on Spaces
3. **Memory limit** - Try processing smaller comics

**Solution:** Add error handling in `app.py` (already included)

### Issue: Slow Performance

**Optimization tips:**
1. Reduce video FPS (12-15 instead of 24)
2. Increase minimum bubble area (fewer detections)
3. Use Edge TTS instead of OpenAI (faster)
4. Process comics page by page

### Issue: Deployment URL Not Working

**Steps:**
1. Check **Logs** tab for errors
2. Click **"Refresh"** on the Space page
3. Wait 5-10 minutes for propagation
4. If still failing, try restarting:
   - Go to **"Settings"** tab
   - Click **"Factory Reset"**

## 📊 Performance Monitoring

### Usage Limits (Free Tier)

| Resource | Limit |
|----------|-------|
| RAM | 16 GB |
| CPU | 2 vCPUs |
| Storage | 10 GB |
| Bandwidth | Unlimited |
| Monthly Runtime | Limited (soft limit) |

### Paid Tiers

If you need more resources:
- **CPU Upgrade**: $9/month (32GB RAM, 8 vCPUs)
- **GPU Support**: $0.10-0.30/hour (varies by GPU)
- **Private Spaces**: Available on all tiers

## 🔄 Updating Your Space

After making changes to your code:

```bash
# Commit changes
git add .
git commit -m "Add new feature"

# Push to Hugging Face
git push hf main

# Space will auto-rebuild
```

## 🌐 Custom Domain (Optional)

To use your own domain:

1. Go to **"Settings"** tab
2. Scroll to **"Custom Domain"**
3. Add your domain (e.g., `comics.yourdomain.com`)
4. Update DNS records:
   - CNAME: `huggingface.co`

## 📈 Analytics

Track usage with:

1. **Spaces Analytics** - Built-in visitor metrics
2. **Hugging Face Hub** - View likes, downloads, forks
3. **Streamlit Analytics** - Add tracking code to `app.py`

## 🔒 Security Best Practices

1. **Never commit** `.env` files with API keys
2. **Use** Hugging Face Secrets for sensitive data
3. **Set appropriate** visibility (Public vs Private)
4. **Monitor logs** for suspicious activity
5. **Regular updates** - Keep dependencies fresh

## 📚 Additional Resources

- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Community Spaces](https://huggingface.co/spaces) - Explore others' work

## 🎉 Success!

Once deployed, share your Space with:
- Link: `https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME`
- Embed on your website
- Share on social media

---

**Need help?** Check the logs or open an issue on GitHub!

