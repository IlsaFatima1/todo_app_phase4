#!/usr/bin/env python3
"""
Script to add missing columns to existing database tables
"""

import sqlite3
import os

def add_profile_picture_column():
    db_path = "./todo_app.db"

    if not os.path.exists(db_path):
        print(f"Database file does not exist: {db_path}")
        return

    print(f"Adding profile_picture column to user table in: {db_path}")

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if profile_picture column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'profile_picture' in columns:
            print("profile_picture column already exists")
        else:
            # Add the profile_picture column
            cursor.execute("ALTER TABLE user ADD COLUMN profile_picture VARCHAR")
            print("Added profile_picture column to user table")

        # Commit the changes
        conn.commit()
        print("Changes committed successfully")

    except sqlite3.Error as e:
        print(f"Error modifying database: {e}")

    finally:
        # Close connection
        conn.close()

    print(f"Column addition completed.")

if __name__ == "__main__":
    add_profile_picture_column()