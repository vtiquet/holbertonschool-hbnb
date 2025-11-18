from app.models.amenity import Amenity
import datetime

def test_amenity_creation():
    # Préparer les valeurs requises par le constructeur
    now_iso = datetime.datetime.now().isoformat()

    # 1. Création de l'Amenity avec TOUS les 4 arguments requis
    amenity = Amenity(
        id="amenity-wifi-id-123",  # 1er arg : id (str)
        name="Wi-Fi",              # 2ème arg : name (str)
        created_at=now_iso,        # 3ème arg : created_at (str)
        updated_at=now_iso         # 4ème arg : updated_at (str)
    )


    assert amenity.name == "Wi-Fi"
    assert amenity.id == "amenity-wifi-id-123"
    assert isinstance(amenity.created_at, str)

    print("Amenity creation test passed!")

test_amenity_creation()