from rest_framework.routers import SimpleRouter
from config import views


router = SimpleRouter()
router.register("white_list_files",views.WhiteListFilesView)
router.register("daas_configs",views.DaasMetaConfigView)
router.register("",views.ConfigView)

app_name="config"
urlpatterns = [
    
]
urlpatterns+=router.urls
