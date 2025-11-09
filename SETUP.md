# Setup and Running Instructions

## Prerequisites

- Python 3.11 or higher
- Node.js 16 or higher
- npm or yarn
- Poppler (required for PDF processing)

### Installing Poppler on Windows:

1. Download Poppler for Windows
2. Extract to: `C:\Users\<username>\poppler\poppler-23.11.0`
3. Add to PATH:
   ```powershell
   # Add Poppler to user PATH (run once)
   $popplerBin = "C:\Users\$env:USERNAME\poppler\poppler-23.11.0\Library\bin"
   setx PATH "$env:PATH;$popplerBin"
   
   # Verify installation (in a new terminal)
   pdftocairo -v
   ```

#### macOS:
```bash
brew install poppler
```

#### Linux:
```bash
sudo apt-get install poppler-utils
```

## Backend Setup

1. Navigate to the backend directory:
```powershell
cd backend
```

2. Create and activate virtual environment:
```powershell
# Create venv if not exists
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\activate
```

3. Install Python dependencies:
```powershell
pip install -r requirements.txt
```

4. Set up environment for OCR:
```powershell
# Set UTF-8 encoding for OCR (run once)
setx PYTHONIOENCODING utf-8
setx PYTHONUTF8 1

# For current session
$env:PYTHONIOENCODING = 'utf-8'
chcp 65001
```

5. (Optional) Set up OpenAI API:
   - Create `.env` file with:
     ```
     OPENAI_API_KEY=your_key_here
     ```
   - Without key, system uses rule-based recommendations

6. Start the backend server:
```powershell
# Ensure you're in backend folder with .venv activated
& ".\.venv\Scripts\python.exe" -m uvicorn main:app --reload
```

The backend will run on `http://127.0.0.1:8000`

## Frontend Setup

1. Navigate to the frontend directory:
```powershell
cd frontend
```

2. Install Node dependencies:
```powershell
npm install
```

3. Start the development server:
```powershell
npm start
```

The frontend will automatically open in your browser at `http://localhost:3000`

## Running the Project

You'll need two PowerShell windows, one for backend and one for frontend.

### PowerShell Window 1 (Backend):
```powershell
# 1. Go to project and backend folder
cd "path\to\major project\New folder\backend"

# 2. Activate virtual environment
.\.venv\Scripts\activate

# 3. Set UTF-8 for current session
$env:PYTHONIOENCODING = 'utf-8'
chcp 65001

# 4. Start backend
& ".\.venv\Scripts\python.exe" -m uvicorn main:app --reload
```

### PowerShell Window 2 (Frontend):
```powershell
# 1. Go to frontend folder
cd "path\to\major project\New folder\frontend"

# 2. Start frontend
npm start
```

## Using the Application

1. Keep both PowerShell windows open and running
2. Frontend opens automatically at http://localhost:3000
3. Upload a Form-16 PDF or enter details manually
4. View tax calculations and recommendations

## API Endpoints

- `POST /api/analyze-form16` - Upload and analyze Form-16 PDF
- `POST /api/calculate-tax` - Calculate tax based on manual input
- `POST /api/calculate-tax-realtime` - Real-time tax calculations

## Troubleshooting

### PDF Processing Issues
1. Verify Poppler installation:
   ```powershell
   # Check Poppler is in PATH
   pdftocairo -v
   
   # If not found, add to current session
   $popplerBin = "C:\Users\$env:USERNAME\poppler\poppler-23.11.0\Library\bin"
   $env:Path = "$popplerBin;$env:Path"
   ```

### OCR Issues
1. Console encoding problems:
   ```powershell
   # Set UTF-8 for current session
   $env:PYTHONIOENCODING = 'utf-8'
   chcp 65001
   
   # Or permanently (then restart terminal)
   setx PYTHONIOENCODING utf-8
   setx PYTHONUTF8 1
   ```
2. First run downloads models (may take a few minutes)
3. Ensure PDF is clear and readable

### Backend Errors
1. Check Python version (should be 3.11+):
   ```powershell
   python --version
   ```
2. Verify virtual environment:
   - Terminal should show `(.venv)`
   - If not: `.\.venv\Scripts\activate`
3. Reinstall dependencies if needed:
   ```powershell
   pip install -r requirements.txt
   ```

### Frontend Errors
1. Clear npm cache and reinstall:
   ```powershell
   npm cache clean --force
   rm -r node_modules
   npm install
   ```
2. Verify backend is running (http://127.0.0.1:8000)
3. Check Node.js version (16+)

## Notes

- First OCR run may take longer as EasyOCR downloads models
- Without OpenAI API key, recommendations will be rule-based (still functional)
- For production, consider using a more robust OCR solution or fine-tuned models
- If you see npm audit warnings, you can fix them with: `npm audit fix --force` (optional)
- Ensure Poppler is installed and in system PATH before running the backend
- Windows users might need to restart their terminal after installing Poppler

## Environment Variables

Create a `.env` file in the backend directory with:
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

This is required for LLM-based recommendations. Without it, the system will fall back to rule-based recommendations.
