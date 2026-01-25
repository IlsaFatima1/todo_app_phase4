#!/usr/bin/env python3
"""
Test script to check update operations directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_session, init_db
from sqlmodel import select
from models import User

def test_database_operations():
    print("Testing database operations for updates...")

    # Initialize the database
    init_db()
    print("Database initialized.")

    # Create a session
    session_gen = get_session()
    session = next(session_gen)

    try:
        # Check if user with ID 1 exists
        user = session.get(User, 1)
        if user:
            print(f"Found user: ID={user.id}, Name={user.name}, Email={user.email}")
            print(f"User has profile_picture: {hasattr(user, 'profile_picture')}")
            print(f"User profile_picture value: {getattr(user, 'profile_picture', 'NOT FOUND')}")
        else:
            print("No user found with ID 1")

            # List all users
            all_users = session.exec(select(User)).all()
            print(f"All users in database: {len(all_users)}")
            for u in all_users:
                print(f"  - ID: {u.id}, Name: {u.name}, Email: {u.email}")

        # Test email lookup
        email_test = "testuser@example.com"
        existing_user = session.exec(select(User).where(User.email == email_test)).first()
        if existing_user:
            print(f"Found user by email: {existing_user.email}")
        else:
            print(f"No user found with email: {email_test}")

    except Exception as e:
        print(f"Error in database operations: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Close the session
        try:
            next(session_gen)
        except StopIteration:
            pass

if __name__ == "__main__":
    test_database_operations()