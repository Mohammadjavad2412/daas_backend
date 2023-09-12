from django.urls import path
from users import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register("daas",views.DaasView)

app_name="users"
urlpatterns = [
    path("login/",views.LogInView.as_view()),
]
urlpatterns+=router.urls
