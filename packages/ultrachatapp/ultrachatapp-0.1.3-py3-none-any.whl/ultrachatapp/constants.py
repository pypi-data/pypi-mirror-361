from dotenv import load_dotenv
import os

# Step 1: Get absolute path to root .env
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
ENV_PATH = os.path.join(ROOT_DIR, '.env')

# Step 2: Load .env
# print("🔍 Loading .env from:", ENV_PATH)
load_dotenv(dotenv_path=ENV_PATH)

# Step 3: Load env variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION')
NOTIFICATION_URL = "http://localhost:8001/notify"

# ✅ Step 4: Debug prints

# Step 5: Validation
if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, AWS_REGION]):
    raise EnvironmentError("❌ Missing one or more AWS S3 environment variables in .env file.")
