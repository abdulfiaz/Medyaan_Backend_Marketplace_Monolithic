import jwt

def getrolename(request):
    token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
    payload = jwt.decode(token, options={"verify_signature": False})  
    role_name = payload.get('role_name')
    return role_name