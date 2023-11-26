from django.urls import path
from users import views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView


router = routers.SimpleRouter()
router.register("daas",views.DaasView)
router.register("reset_usage",views.ResetUsage)
router.register("lock_my_account",views.LockRequestView)
router.register("delete_all_desktops",views.DeleteAllDesktops)
router.register("",views.UsersView)

app_name="users"
urlpatterns = [
    path("login/",views.LogInView.as_view(),name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("profile/",views.Profile.as_view({"get":"get"}),name='my_desktop'),
    path("daas/update_usage/",views.UpdateUsage.as_view({"get":"get"}),name="update_usage"),
    path("is_valid_user/",views.IsValidUser.as_view(),name="valid_user"),
]

urlpatterns+=router.urls
