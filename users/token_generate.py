import jwt
from django.conf import settings

def generate_jwt_token(user):
    payload = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_AUTH['JWT_ALGORITHM']
    )
    return token


