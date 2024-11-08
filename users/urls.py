from django.conf.urls import url
from django.urls import path
from users import views
from users.views import CreateCustomUserView,RoleMasterCreateView,RefreshTokenView,ChangePassword

app_name = 'users'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('user-create/',CreateCustomUserView.as_view()),
    path('role-create/',RoleMasterCreateView.as_view()),
    path('role_login/',RefreshTokenView.as_view(),name='role_login'),
    path('change_password/',ChangePassword.as_view(),name='change-password'),

]