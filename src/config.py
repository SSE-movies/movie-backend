"""Configuration settings for the Movie Backend API."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# API configuration
PORT = os.getenv("PORT", "5000")
PORT = int(PORT)
