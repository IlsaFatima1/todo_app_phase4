#!/usr/bin/env python3
"""
Test script to check database operations directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_session, init_db
from user_service import create_user
from models import UserCreate

def test_database():
    print("Testing database operations...")

    # Initialize the database
    init_db()
    print("Database initialized.")

    # Create a session
    session_gen = get_session()
    session = next(session_gen)

    try:
        # Create a test user
        user_data = UserCreate(
            name="Test User",
            email="test@example.com",
            password="password123"
        )

        print(f"Attempting to create user: {user_data.name}, {user_data.email}")

        user = create_user(session, user_data)
        print(f"User created successfully! ID: {user.id}, Name: {user.name}")

        # Verify the user was created
        print(f"User attributes: id={user.id}, name={user.name}, email={user.email}")

    except Exception as e:
        print(f"Error creating user: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Close the session
        try:
            next(session_gen)
        except StopIteration:
            pass

if __name__ == "__main__":
    test_database()