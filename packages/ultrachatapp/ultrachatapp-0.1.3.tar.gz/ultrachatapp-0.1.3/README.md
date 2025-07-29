📌 Overview

  ultrachatapp is a Python package that provides a real-time chat system using FastAPI.
  Its primary goal is to enable seamless messaging between experts and customers via WebSockets or REST APIs.
  You can easily integrate this module into your Django or any other backend project to add robust chat       functionality.

🔧 Installation
Install the package using pip:

   pip install ultrachatapp
   If you're using Docker:

 dockerfile
   RUN pip install ultrachatapp
   To install a specific version:
   pip install ultrachatapp==0.1.1

🧠 Prerequisites
   Before using ultrachatapp, make sure your environment includes the following:

     Python 3.8+

     FastAPI or Django-based backend

     Redis (used for message queues or pub/sub if needed)

     PostgreSQL (or any preferred database, if your project uses models)

     Required environment variables (listed below)

🔐 Required Environment Variables

    ultrachatapp relies on several AWS-related environment variables, especially if you're storing chat messages,   media, or files on Amazon S3.

Ensure your .env file or docker-compose configuration includes the following:

    AWS_ACCESS_KEY_ID=your_aws_access_key
    AWS_SECRET_ACCESS_KEY=your_aws_secret_key
    AWS_STORAGE_BUCKET_NAME=your_bucket_name
    AWS_S3_REGION_NAME=your_region
    AWS_S3_CUSTOM_DOMAIN=your_s3_domain

    FERNET_KEY=your_generated_fernet_key

⚙️ How to Use in Your Project

✅ 1. Import and Use Functions
If you're building a chat API in Django or FastAPI, you can directly import the messaging functions:

    from ultrachatapp.logic import send_message
    You can then use this in your API views or business logic.

✅ 2. WebSocket Integration (FastAPI)
If you're using FastAPI and want real-time WebSocket-based chat, simply include the router:

   from fastapi import FastAPI
   from ultrachatapp.routes import chat_router

   app = FastAPI()

   # Include ultrachatapp's WebSocket & HTTP routes
   app.include_router(chat_router, prefix="/chat")


🔄 Example: .env.prod and Docker Compose Setup

docker-compose-prod.yml Example:

  services:
     web:
     build: .
     env_file: .env.prod
     environment:
         - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
         - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
         - FERNET_KEY=${FERNET_KEY}
     ports:
         - "8000:8000"

🧪 Testing Locally

Create a simple test script to try out the message function:

    from ultrachatapp.logic import send_message

    print(send_message(1, 2, "Hello from CLI"))
  Or you can start your server and test the /chat/ endpoints via Postman or the browser.

.

🚀 Deployment Tips
Docker: Add pip install ultrachatapp in your Dockerfile.

   Gunicorn / Uvicorn: Run your FastAPI app with:

   uvicorn main:app --host 0.0.0.0 --port 8000
   Environment: Make sure your .env file is loaded correctly in production.

   Redis: If your chat system uses Redis for pub/sub or background messaging, ensure your Redis URL (redis://...)      is configured and accessible.

