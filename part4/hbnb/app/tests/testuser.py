from app.models.user import User
import datetime # Importation nécessaire pour simuler les horodatages

def test_user_creation():
    # 1. Préparer les valeurs requises par le constructeur
    # (id, is_admin, created_at, updated_at sont requis par votre init)


    now_iso = datetime.datetime.now().isoformat()


    user = User(
        id="test-id-12345",              # 1er arg : id (str)
        first_name="John",               # 2ème arg : first_name (str)
        last_name="Doe",                 # 3ème arg : last_name (str)
        email="john.doe@example.com",    # 4ème arg : email (str)
        is_admin=False,                  # 5ème arg : is_admin (bool)
        created_at=now_iso,              # 6ème arg : created_at (str)
        updated_at=now_iso               # 7ème arg : updated_at (str)
    )


    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john.doe@example.com"
    assert user.is_admin is False 


    assert user.id == "test-id-12345"

    print("User creation test passed!")

test_user_creation()