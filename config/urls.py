from rest_framework.routers import SimpleRouter
from config import views


router = SimpleRouter()
router.register("",views.ConfigView)

app_name="config"
urlpatterns = [
    
]
urlpatterns+=router.urls
