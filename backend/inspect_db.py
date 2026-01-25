#!/usr/bin/env python3
"""
Script to inspect the database schema and check if profile_picture column exists
"""

import sqlite3
import os

def inspect_database():
    db_path = "./todo_app.db"

    if not os.path.exists(db_path):
        print(f"Database file does not exist: {db_path}")
        return

    print(f"Inspecting database: {db_path}")

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get table information for the user table
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()

    print("\nUser table schema:")
    print("CID | Name            | Type        | NotNull | Default | PrimaryKey")
    print("-" * 70)
    for col in columns:
        cid, name, type_, notnull, default, pk = col
        print(f"{cid:3} | {name:15} | {type_:11} | {notnull:7} | {str(default):7} | {pk}")

    # Also check for todos table
    print("\nTodos table schema:")
    print("CID | Name            | Type        | NotNull | Default | PrimaryKey")
    print("-" * 70)
    cursor.execute("PRAGMA table_info(todo)")
    columns = cursor.fetchall()
    for col in columns:
        cid, name, type_, notnull, default, pk = col
        print(f"{cid:3} | {name:15} | {type_:11} | {notnull:7} | {str(default):7} | {pk}")

    # Close connection
    conn.close()

    print(f"\nDatabase inspection completed.")

if __name__ == "__main__":
    inspect_database()