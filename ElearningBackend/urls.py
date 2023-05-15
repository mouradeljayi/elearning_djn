from django import views
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers
from APIElearning.views import (
    ChapitreViewSet,
    LinkSourceViewSet,
    PlainteViewSet,
    ProgressContenuModuleViewSet,
    RatingViewSet,
    UserDetailsAPIView,
    AccesViewSet,
    ApprenantTokenObtainPairView,
    ApprenantViewSet,
    DemandeRegisterViewSet,
    DocsViewSet,
    FeedbackViewSet,
    FormationViewSet,
    ModuleViewSet,
    ProgresViewSet,
    ResonsableViewSet,
    ResponsableTokenObtainPairView,
    TestView,
    ResultatView,
    CertificatView,
    VideosViewSet,
    approve_demande,
    get_apprenants_with_access,
    refuse_demande,
    change_password,
    get_user_image,
    update_apprenant_etat,
    update_user,
    update_respo_role,
    update_respo_etat,
)
from APIElearning.views import (
    UserDetailsAPIView,
    AccesViewSet,
    ApprenantTokenObtainPairView,
    ApprenantViewSet,
    DemandeRegisterViewSet,
    DocsViewSet,
    FeedbackViewSet,
    FormationViewSet,
    ModuleViewSet,
    ProgresViewSet,
    ResonsableViewSet,
    ResponsableTokenObtainPairView,
    TestView,
    ResultatView,
    CertificatView,
    VideosViewSet,
    approve_demande,
)
from APIElearning.views import (
    AccesViewSet,
    ApprenantTokenObtainPairView,
    ApprenantViewSet,
    DemandeRegisterViewSet,
    MediaViewSet,
    DocsViewSet,
    FeedbackViewSet,
    FormationViewSet,
    ModuleViewSet,
    ProgresViewSet,
    ResonsableViewSet,
    ResponsableTokenObtainPairView,
    TestView,
    ResultatView,
    CertificatView,
    VideosViewSet,
    approve_demande,
)

from rest_framework_simplejwt.views import TokenRefreshView
from django.conf.urls.static import static


# Define a router to handle API endpoints
router = routers.DefaultRouter()
router.register(r"test", TestView)
router.register(r"resultat", ResultatView)
router.register(r"certificat", CertificatView)
router.register(r"apprenants", ApprenantViewSet, basename="apprenants")
router.register(r"responsables", ResonsableViewSet, basename="responsables")
router.register(r"demandes", DemandeRegisterViewSet, basename="demandes")
router.register(r"formation", FormationViewSet, basename="formation")
router.register(r"module", ModuleViewSet, basename="module")
router.register(r"chapitre", ChapitreViewSet, basename="chapitre")
router.register(r"media", MediaViewSet, basename="media")
router.register(r"docs", DocsViewSet, basename="docs")
router.register(r"videos", VideosViewSet, basename="videos")
router.register(r"feedback", FeedbackViewSet, basename="feedback")
router.register(r"rating", RatingViewSet, basename="rating")
router.register(r"progres", ProgresViewSet, basename="progres")
router.register(r"acces", AccesViewSet, basename="acces")
router.register(r"plainte", PlainteViewSet, basename="plainte")
router.register(r"link", LinkSourceViewSet, basename="link")

router.register(r"link", LinkSourceViewSet, basename="link")


from django.contrib.staticfiles.views import serve

# Acces to rest api from routes


router.register(
    r"progressmodcontent",
    ProgressContenuModuleViewSet,
    basename="progressmodcontent",
)


from django.contrib.staticfiles.views import serve

# Acces to rest api from routes


router.register(
    r"progressmodcontent",
    ProgressContenuModuleViewSet,
    basename="progressmodcontent",
)


# scpecify routes
urlpatterns = [
    # path("view_ppt/<int:pk>/", views.view_ppt, name="view_ppt"),
    # re_path(r"^static/(?P<path>.+)\.pptx$", serve),
    path("admin/", admin.site.urls),
    # root route
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("approve_demande/<int:demande_id>/", approve_demande, name="approve_demande"),
    path("refuse_demande/<int:demande_id>/", refuse_demande, name="refuse_demande"),
    path("apprenants/<int:user_id>/image", get_user_image, name="get_user_image"),
    path("responsables/<int:user_id>/image", get_user_image, name="get_user_image"),
    path("user_update/<int:user_id>/", update_user, name="update_user"),
    path("role_update/<int:user_id>/", update_respo_role, name="update_respo_role"),
    path("etat_update/<int:user_id>/", update_respo_etat, name="update_respo_etat"),
    path("etatAppr_update/<int:user_id>/", update_apprenant_etat, name="update_apprenant_etat"),

    path("password_update/<int:user_id>/", change_password, name="change_password"),
    path('api/apprenants/<int:responsable_id>/', get_apprenants_with_access, name='apprenants_with_access'),

    path(
        "token/apprenant/",
        ApprenantTokenObtainPairView.as_view(),
        name="apprenant_token_obtain_pair",
    ),
    path(
        "token/responsable/",
        ResponsableTokenObtainPairView.as_view(),
        name="responsable_token_obtain_pair",
    ),
    path(
        "token/apprenant/refresh/",
        TokenRefreshView.as_view(),
        name="apprenant_token_refresh",
    ),
    path(
        "token/responsable/refresh/",
        TokenRefreshView.as_view(),
        name="responsable_token_refresh",
    ),
    path("auth/user/", UserDetailsAPIView.as_view(), name="user_detail"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
