from ..models.place import Place
from ..models.user import User
from ..models.review import Review
from ..models.amenity import Amenity
import datetime
import uuid # ⬅️ NOUVEL IMPORT NÉCESSAIRE

def test_place_creation_and_relationships():
    # Préparation des données temporelles
    now = datetime.datetime.now()
    
    # 1. Création de l'Owner (TOUS les 7 arguments sont fournis)
    owner = User(
        id=str(uuid.uuid4()),
        first_name="Alice", 
        last_name="Smith", 
        email="alice.smith@example.com",
        is_admin=False,
        created_at=now,
        updated_at=now
    )
    
    # 2. Correction : Création de la Place avec TOUS les 9 arguments requis
    place = Place(
        id=str(uuid.uuid4()), # ⬅️ ARGUMENT 'id' AJOUTÉ
        title="Cozy Apartment", 
        description="A nice place to stay", 
        price=100.0, # Utilisation de float pour respecter la validation
        latitude=37.7749, 
        longitude=-122.4194, 
        owner=owner, # NOTE : Doit être l'OBJET User pour passer la validation
        created_at=now,  # ⬅️ ARGUMENT 'created_at' AJOUTÉ
        updated_at=now   # ⬅️ ARGUMENT 'updated_at' AJOUTÉ
    )
    
    # 3. Création d'une Review (TOUS les arguments sont fournis)
    review = Review(
        id=str(uuid.uuid4()),
        text="Great stay!", 
        rating=5, 
        place=place, 
        user=owner,
        created_at=now,
        updated_at=now
    )
    
    # 4. Création d'une Amenity (TOUS les arguments sont fournis)
    amenity = Amenity(
        id=str(uuid.uuid4()),
        name="Wifi",
        created_at=now,
        updated_at=now
    )
    
    # Ajout des relations
    place.add_review(review)
    place.add_amenity(amenity)
    
    # 5. Assertions (Tests de vérification)
    
    # Vérification des attributs de base
    assert place.title == "Cozy Apartment"
    assert place.price == 100.0
    assert isinstance(place.owner, User)
    
    # Vérification des relations (Reviews)
    assert len(place.reviews) == 1
    assert place.reviews[0].text == "Great stay!"
    
    # Vérification des relations (Amenities)
    assert len(place.amenities) == 1
    assert place.amenities[0].name == "Wifi"
    
    print("Place model and relationship tests passed successfully!")

# Exécution du test
test_place_creation_and_relationships()