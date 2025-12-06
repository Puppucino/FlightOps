# Fix Module Not Found Error

## Problem
```
ModuleNotFoundError: No module named 'pydantic_settings'
```

This happens when dependencies aren't installed or the virtual environment isn't activated.

## Solution

### Step 1: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
cd D:\CursorHackathon\backend
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
cd D:\CursorHackathon\backend
venv\Scripts\activate.bat
```

### Step 2: Install Dependencies

Once the virtual environment is activated (you'll see `(venv)` in your prompt), run:

```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
python -c "import pydantic_settings; print('✓ pydantic_settings installed')"
```

### Step 4: Try Database Initialization Again

```bash
python scripts/init_db.py
```

## Alternative: Install Without Virtual Environment (Not Recommended)

If you want to install globally (not recommended for development):

```bash
cd D:\CursorHackathon\backend
pip install -r requirements.txt
```

## If Virtual Environment Doesn't Exist

Create it first:

```bash
cd D:\CursorHackathon\backend
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Quick Check Script

Run this to check your environment:

```bash
python scripts/install_deps.py
```
