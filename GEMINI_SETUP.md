# 🔑 Google Gemini API Setup Guide

## Step 1: Get Your Gemini API Key

1. **Visit**: https://ai.google.dev/
2. **Click "Get API Key"** or go to: https://makersuite.google.com/app/apikey
3. **Create a new API key** in Google Cloud project
4. **Copy** the generated key
5. ✅ It's FREE to use (with rate limits)

## Step 2: Add to .env File

Open `backend/.env` and replace:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

With:

```
GEMINI_API_KEY=AIzaSyD...your-actual-key-here
```

**Example:**
```
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_MODEL=gemini-pro
```

## Step 3: Install Dependencies

Run this command in your backend folder:

```bash
pip install -r requirements.txt
```

This will install `google-generativeai` package.

## Step 4: Verify Setup

When you start the backend, you should see:
```
Google Gemini client initialized successfully with model: gemini-pro
```

If you see:
```
Google Gemini API key not found or invalid. Using rule-based recommendations.
```

Then the API key is not configured correctly.

## ✅ Benefits of Google Gemini:

✅ **FREE** (No credit card required initially)
✅ **Fast** responses
✅ **Good quality** AI recommendations
✅ **Flexible** model options (gemini-pro, gemini-pro-vision)
✅ **Generous rate limits** for testing

## 📊 Available Models:

- `gemini-pro` - Text-based recommendations (Recommended)
- `gemini-pro-vision` - Can also process images

## ⚠️ Important Notes:

- **Keep your API key SECRET** - Don't commit it to GitHub!
- **Free tier** has rate limits (check at https://ai.google.dev/)
- **No credit card** required for free tier
- Can upgrade to paid tier if needed

## 🚀 Ready to Run:

1. Add your Gemini API key to `.env`
2. Run: `pip install -r requirements.txt`
3. Start backend: `python main.py`
4. Now Google Gemini will provide AI-powered recommendations!

---

**Questions or Issues?** Check Google's documentation: https://ai.google.dev/tutorials/python_quickstart
