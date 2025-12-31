# ✅ Deployment Checklist - Hugging Face Spaces

Use this checklist to ensure your deployment goes smoothly!

## Pre-Deployment Checks

- [ ] Test app locally: `py -V:3.13 -m streamlit run app.py`
- [ ] Verify all dependencies work: `py -V:3.13 -c "import streamlit; import cv2; print('OK')"`
- [ ] Ensure `src/` folder is complete and accessible
- [ ] Check `app.py` imports are correct
- [ ] Test with a sample comic image

## Repository Preparation

- [ ] Rename `requirements_hf.txt` to `requirements.txt`
- [ ] Ensure `.gitignore` excludes: `venv/`, `__pycache__/`, `.env`
- [ ] Commit all changes: `git add . && git commit -m "Ready for deployment"`
- [ ] Push to GitHub: `git push origin main`

## Hugging Face Setup

- [ ] Create Hugging Face account (if not already)
- [ ] Create new Space with SDK: "Streamlit"
- [ ] Note your Space URL: `https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME`

## Deployment

### Option A: Git Push (Recommended)
- [ ] Add Hugging Face remote: `git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME`
- [ ] Push to Hugging Face: `git push hf main`
- [ ] Watch build logs in "Logs" tab

### Option B: Web Upload
- [ ] Go to Space → "Files" tab
- [ ] Upload `app.py`
- [ ] Upload `requirements.txt`
- [ ] Upload entire `src/` folder
- [ ] Wait for automatic build

## Post-Deployment

- [ ] Check Space status: Green dot ✅
- [ ] Test live app with sample comic
- [ ] Verify video generation works
- [ ] Test download functionality
- [ ] Check logs for any errors

## Optional Enhancements

- [ ] Set environment variables in Space settings
- [ ] Add OpenAI API key as secret
- [ ] Configure custom domain
- [ ] Add Space description and tags
- [ ] Enable discussions for community feedback

## Performance Testing

- [ ] Test with small comic (1 page)
- [ ] Test with medium comic (3-5 pages)
- [ ] Test with PDF (multi-page)
- [ ] Monitor memory usage in logs
- [ ] Measure processing time

## Share Your Space

- [ ] Share URL on social media
- [ ] Add to GitHub README
- [ ] Create demo video
- [ ] Submit to Hugging Face trending
- [ ] Add badges to README

## Troubleshooting (if issues occur)

**Build fails:**
- [ ] Check requirements.txt for correct versions
- [ ] Review build logs for specific errors
- [ ] Verify Python version (3.13)

**App crashes:**
- [ ] Check "Logs" tab for runtime errors
- [ ] Verify all system dependencies installed
- [ ] Test with smaller file sizes

**Performance issues:**
- [ ] Reduce video FPS in settings
- [ ] Increase minimum bubble area
- [ ] Use Edge TTS instead of OpenAI
- [ ] Process comics page by page

## Maintenance

- [ ] Monitor Space uptime regularly
- [ ] Update dependencies monthly
- [ ] Review and respond to issues
- [ ] Track usage metrics
- [ ] Backup important data

---

## 🎯 Quick Start Commands

```bash
# 1. Test locally
py -V:3.13 -m streamlit run app.py

# 2. Rename requirements
mv requirements_hf.txt requirements.txt

# 3. Add Hugging Face remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME

# 4. Push to Hugging Face
git push hf main

# 5. Monitor build
# Go to: https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME/tree/main
# Click "Logs" tab
```

## 📚 Useful Links

- [Hugging Face Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Your Space Dashboard](https://huggingface.co/spaces)

---

**Good luck with your deployment! 🚀**

