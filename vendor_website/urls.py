from django.urls import path, include

#from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

'''
#======================================
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
# Setup automatic URL routing
# Additionally, we include login URLs for the browsable API.

#===================================================================
'''

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.signin, name="login"),
    path("logout", views.signout, name="logout"),
    path("signup", views.signup, name="signup"),
    
    
    
]
