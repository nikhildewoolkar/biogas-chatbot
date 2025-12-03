from . import views
# from .views import *
from django.urls import path
urlpatterns=[
    path("",views.home,name="home"),
    path("home/",views.home,name="home"),
    path("login/",views.login,name="login"),
    path("signup/",views.signup,name="signup"),
    path("logout/",views.logout,name="logout"),
    path("profile/",views.profile,name="profile"),
    path("addquery/",views.addquery,name="addquery"),
    path("myqueries/",views.myqueries,name="myqueries"),
    path("changepassword/",views.changepassword,name="changepassword"),
    path("chat/", views_api.chat),
    path("query/", views_api.query),
    path("schema/", views_api.schema),
    path("healthz/", views_api.health),
]