# 🔑 OpenAI API Setup Guide

## Step 1: Get Your API Key

1. **Visit**: https://platform.openai.com/api-keys
2. **Sign In** to your OpenAI account (or create one at https://platform.openai.com/signup)
3. **Click "Create new secret key"** button
4. **Copy** the generated key (it will look like: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx`)
5. ⚠️ **Save it somewhere safe** - You won't be able to see it again!

## Step 2: Add to .env File

Open `backend/.env` and replace:

```
OPENAI_API_KEY=your_openai_api_key_here
```

With:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

**Example:**
```
OPENAI_API_KEY=sk-proj-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p
OPENAI_MODEL=gpt-3.5-turbo
```

## Step 3: Verify Setup

When you start the backend, you should see:
```
OpenAI client initialized successfully
```

If you see:
```
OpenAI API key not found or invalid. Using rule-based recommendations.
```

Then the API key is not configured correctly.

## ⚠️ Important Notes:

- **Keep your API key SECRET** - Don't commit it to GitHub!
- **Check your usage**: https://platform.openai.com/account/usage/overview
- **Set spending limits** to avoid unexpected charges
- **Free trial** users have a limited quota
- Each API call costs money based on token usage

## 🚀 After Setup:

1. Save the `.env` file
2. Stop the backend server (if running)
3. Start it again: `python main.py`
4. Now OpenAI API will be used for smarter recommendations!

## 📊 Benefits of OpenAI Integration:

✅ Personalized tax recommendations
✅ Context-aware explanations
✅ Better legal references
✅ Smarter deduction suggestions
✅ More natural language responses

---

**Questions?** Reach out for help!
