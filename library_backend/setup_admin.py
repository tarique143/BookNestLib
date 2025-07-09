# # file: setup_admin.py
# import os
# import sys
# from sqlalchemy.orm import Session
# from database import SessionLocal, engine # Database connection
# from auth import get_password_hash # Password hash karne ke liye

# # Project ke root folder ko path me add karein
# sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '.')))

# # Sabhi models ko import karein
# from models.user_model import User, Role
# from models.permission_model import Permission

# def setup_initial_data():
#     """
#     Database me initial Admin role, user, aur permissions set up karta hai.
#     """
#     db: Session = SessionLocal()
#     print("Connecting to the database...")

#     try:
#         # --- 1. Admin Role Check karein aur Banayein ---
#         admin_role = db.query(Role).filter(Role.name == "Admin").first()
#         if not admin_role:
#             print("Admin role not found. Creating one...")
#             admin_role = Role(name="Admin")
#             db.add(admin_role)
#             db.commit()
#             db.refresh(admin_role)
#             print("Admin role created successfully.")
#         else:
#             print("Admin role already exists.")

#         # --- 2. Librarian Role Check karein aur Banayein ---
#         librarian_role = db.query(Role).filter(Role.name == "Librarian").first()
#         if not librarian_role:
#             print("Librarian role not found. Creating one...")
#             librarian_role = Role(name="Librarian")
#             db.add(librarian_role)
#             db.commit()
#             print("Librarian role created successfully.")
#         else:
#             print("Librarian role already exists.")
            
#         # --- 3. Admin User Check karein aur Banayein ---
#         admin_user = db.query(User).filter(User.username == "admin").first()
#         if not admin_user:
#             print("Admin user not found. Creating one...")
#             admin_password = "admin" # Aap ise badal sakte hain
#             hashed_password = get_password_hash(admin_password)
#             admin_user = User(
#                 username="admin",
#                 email="admin@library.com",
#                 full_name="Library Administrator",
#                 password_hash=hashed_password,
#                 role_id=admin_role.id,
#                 status="Active"
#             )
#             db.add(admin_user)
#             db.commit()
#             print(f"Admin user created with username 'admin' and password '{admin_password}'.")
#         else:
#             print("Admin user already exists.")

#         # --- 4. Sabhi Permissions Banayein ---
#         print("Checking and creating permissions...")
#         all_permissions = [
#             'ROLE_MANAGE', 'ROLE_VIEW', 'USER_MANAGE', 'USER_VIEW',
#             'PERMISSION_MANAGE', 'PERMISSION_VIEW', 'ROLE_PERMISSION_ASSIGN',
#             'BOOK_MANAGE', 'CATEGORY_MANAGE', 'LANGUAGE_MANAGE',
#             'COPY_MANAGE', 'COPY_VIEW', 'LOCATION_MANAGE',
#             'BOOK_ISSUE', 'ISSUE_VIEW', 'REQUEST_CREATE', 'REQUEST_VIEW',
#             'REQUEST_APPROVE', 'LOG_VIEW', 'FILE_UPLOAD', 'DIGITAL_ACCESS_VIEW',
#             'BOOK_PERMISSION_MANAGE', 'BOOK_PERMISSION_VIEW'
#         ]
        
#         existing_permissions = db.query(Permission.name).all()
#         existing_permission_names = {p[0] for p in existing_permissions}
        
#         new_permissions = []
#         for perm_name in all_permissions:
#             if perm_name not in existing_permission_names:
#                 new_permissions.append(Permission(name=perm_name))

#         if new_permissions:
#             db.add_all(new_permissions)
#             db.commit()
#             print(f"{len(new_permissions)} new permissions created.")
#         else:
#             print("All permissions already exist.")

#         # --- 5. Admin Role ko Sabhi Permissions Assign Karein ---
#         print("Assigning all permissions to Admin role...")
#         all_permission_objects = db.query(Permission).all()
#         admin_role.permissions = all_permission_objects
#         db.commit()
#         print("Permissions assigned to Admin role successfully.")

#     finally:
#         print("Closing database connection.")
#         db.close()

# if __name__ == "__main__":
#     print("--- Starting Initial Data Setup ---")
#     setup_initial_data()
#     print("--- Setup Complete ---")

# postgressql
# file: setup_admin.py

import os
import sys
from sqlalchemy.orm import Session

# --- NAYA CODE: .env file load karne ke liye ---
from dotenv import load_dotenv
load_dotenv()
# --- KHATAM ---

# Apne project ke root folder ko path me add karein
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '.')))

from database import SessionLocal, engine
from auth import get_password_hash

# Sabhi models ko import karein
from models.user_model import User, Role
from models.permission_model import Permission

def setup_initial_data():
    """Database me initial Admin role, user, aur permissions set up karta hai."""
    db: Session = SessionLocal()
    print("Connecting to the database...")

    try:
        # --- 1. Admin Role ---
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            print("Admin role not found. Creating one...")
            admin_role = Role(name="Admin")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("Admin role created.")
        else:
            print("Admin role already exists.")

        # --- 2. Librarian Role ---
        librarian_role = db.query(Role).filter(Role.name == "Librarian").first()
        if not librarian_role:
            print("Librarian role not found. Creating one...")
            librarian_role = Role(name="Librarian")
            db.add(librarian_role)
            db.commit()
            print("Librarian role created.")
        else:
            print("Librarian role already exists.")
            
        # --- 3. Admin User ---
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("Admin user not found. Creating one...")
            admin_password = "admin"  # Default password
            hashed_password = get_password_hash(admin_password)
            admin_user = User(
                username="admin",
                email="admin@library.com",
                full_name="Library Administrator",
                password_hash=hashed_password,
                role_id=admin_role.id,
                status="Active"
            )
            db.add(admin_user)
            db.commit()
            print(f"Admin user created with username 'admin' and password '{admin_password}'.")
        else:
            print("Admin user already exists.")

        # --- 4. Permissions ---
        print("Checking and creating permissions...")
        all_permissions = [
            'ROLE_MANAGE', 'ROLE_VIEW', 'USER_MANAGE', 'USER_VIEW',
            'PERMISSION_MANAGE', 'PERMISSION_VIEW', 'ROLE_PERMISSION_ASSIGN',
            'BOOK_MANAGE', 'CATEGORY_MANAGE', 'LANGUAGE_MANAGE',
            'COPY_MANAGE', 'COPY_VIEW', 'LOCATION_MANAGE',
            'BOOK_ISSUE', 'ISSUE_VIEW', 'REQUEST_CREATE', 'REQUEST_VIEW',
            'REQUEST_APPROVE', 'LOG_VIEW', 'FILE_UPLOAD', 'DIGITAL_ACCESS_VIEW',
            'BOOK_PERMISSION_MANAGE', 'BOOK_PERMISSION_VIEW'
        ]

        existing_permissions = db.query(Permission.name).all()
        existing_permission_names = {p[0] for p in existing_permissions}
        
        new_permissions = [
            Permission(name=perm_name)
            for perm_name in all_permissions if perm_name not in existing_permission_names
        ]

        if new_permissions:
            db.add_all(new_permissions)
            db.commit()
            print(f"{len(new_permissions)} new permissions created.")
        else:
            print("All permissions already exist.")

        # --- 5. Assign All Permissions to Admin Role ---
        print("Assigning all permissions to Admin role...")
        all_permission_objects = db.query(Permission).all()
        admin_role.permissions = all_permission_objects
        db.commit()
        print("Permissions assigned to Admin role.")

    finally:
        print("Closing database connection.")
        db.close()

if __name__ == "__main__":
    print("--- Starting Initial Data Setup ---")
    setup_initial_data()
    print("--- Setup Complete ---")
