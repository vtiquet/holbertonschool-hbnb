#!/usr/bin/python3
"""Script to create an admin user"""

from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Vérifie si l'admin existe déjà
    existing_admin = User.query.filter_by(email="admin@hbnb.com").first()
    
    if existing_admin:
        print("❌ Admin already exists!")
        print(f"   Email: {existing_admin.email}")
        print(f"   ID: {existing_admin.id}")
    else:
        # Crée l'admin
        admin = User(
            first_name="Loïc",
            last_name="Le Guen",
            email="loic@lo.ic",
            is_admin=True
        )
        admin.hash_password("string")  # Hash le mot de passe
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Admin created successfully!")
        print(f"   Email: {admin.email}")
        print(f"   Password: string")
        print(f"   ID: {admin.id}")
        print(f"   Is Admin: {admin.is_admin}")

        admin = User(
            first_name="Valentin",
            last_name="Tiquet",
            email="valentin@val.quet",
            is_admin=True
        )
        admin.hash_password("string")  # Hash le mot de passe
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Admin created successfully!")
        print(f"   Email: {admin.email}")
        print(f"   Password: string")
        print(f"   ID: {admin.id}")
        print(f"   Is Admin: {admin.is_admin}")
