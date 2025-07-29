# run_test.py

try:
    from ultrachatapp.main import app
    print("✅ ultrachatapp.main.app import हो गया!")
    print("🟢 FastAPI app object type:", type(app))
except Exception as e:
    print("❌ Error:", e)
