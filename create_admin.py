#!/usr/bin/env python3
"""
Create admin user script
"""
import requests
import json

# API endpoint - PRODUCTION URL
BASE_URL = "https://dama12-scientific-backend.hf.space"

def create_admin_user():
    """Create an admin user via the API"""

    user_data = {
        "email": "admin@attestation.com",
        "name": "Admin User",
        "password": "admin123",
        "institution": "Attestation Labs",
        "role": "admin"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/v1/users/register", json=user_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 201:
            print("✅ Admin user created successfully!")
            print("Email: admin@attestation.com")
            print("Password: admin123")
        else:
            print("❌ Failed to create admin user")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_admin_user()