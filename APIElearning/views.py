import os
from django.conf import settings
from django.dispatch import receiver
from .models import Chapitre, LinkSource, ProgressContenuModule, Rating, Test
from .serializers import (
    ChapitreSerializer,
    ProgressContenuModuleSerializer,
    RatingSerializer,
    UserSer,
)
from django.shortcuts import render
from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters
from .models import Demande, Test, Resultat, Certificat
from .serializers import DemandeSer, TestSer, ResultatSer, CertificatSer
from rest_framework.views import APIView
from django.db.models.functions import ExtractYear
from django.core.mail import send_mail
from django.db import models
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import user_passes_test
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    SAFE_METHODS,
    AllowAny,
)
from rest_framework.decorators import api_view, action, permission_classes
from django.db.models.functions import TruncMonth
from django.db.models.functions import ExtractWeekDay

from django.http import JsonResponse
from django.db.models import Count


from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, update_session_auth_hash
from django.http import JsonResponse

from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import ApprenantSer, ResponableSer
from .models import Apprenant, Responsable, User
from rest_framework import viewsets, status
from rest_framework_simplejwt.tokens import RefreshToken


from django.http import HttpResponseBadRequest
from rest_framework import viewsets, filters
from .models import Demande, Test, Resultat, Certificat
from .serializers import DemandeSer, TestSer, ResultatSer, CertificatSer
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import ApprenantSer, ResponableSer
from .models import Apprenant, Responsable, User
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Count, Avg


from .models import Apprenant
from .models import Formation
from .models import Module
from .models import Media
from .models import Feedback
from .models import Progres
from .models import Acces
from .models import Docs
from .models import Videos
from .models import Plainte
from .models import LinkSource

from django.db.models.signals import post_save


from .serializers import ApprenantSerializer
from .serializers import FormationSerializer, UserSer
from .serializers import PlainteSerializer
from .serializers import ModuleSerializer
from .serializers import MediaSerializer
from .serializers import FeedbackSerializer
from .serializers import ProgresSerializer
from .serializers import AccesSerializer
from .serializers import DocsSerializer
from .serializers import VideosSerializer
from .serializers import LinkSourceSerializer


###############################################
# PERMISSIONS METHODS START HERE
###############################################


# check if responsable is SUPERADMIN
class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.responsable.role == "superadmin"
        )


# check responsables permissions on CRUD ops
class CanViewResponsables(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            # Allow read-only access to all authenticated users
            return request.user.is_authenticated
        else:
            # Only allow superadmins to create, update, or delete Responsable objects
            return (
                request.user.is_authenticated
                and request.user.responsable.role == "superadmin"
            )


class IsResponsable(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_responsable
        return False


###############################################
# PERMISSIONS METHODS END HERE
###############################################


# Create your views here.
class UserView(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = UserSer


class UserView(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = UserSer


# Vue de la table Test avec CRUD
class TestView(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSer
    filter_backends = [filters.SearchFilter]
    search_fields = ['idModule__id']

    # statistique test
    @action(detail=False, methods=["get"])
    def total_questions_by_module(self, request):
        tests = Test.objects.values("titre", "nombredequestion")
        results = []

        for test in tests:
            id_module = test["titre"]
            total_questions = test["nombredequestion"]

            found = False
            for result in results:
                if result["id_module"] == id_module:
                    result["total_questions"] += total_questions
                    found = True
                    break

            if not found:
                results.append(
                    {"id_module": id_module, "total_questions": total_questions}
                )

        return Response(results)


# Vue de la table Resultat avec CRUD
class ResultatView(viewsets.ModelViewSet):
    queryset = Resultat.objects.all()
    serializer_class = ResultatSer
    filter_backends = [filters.SearchFilter]
    search_fields = ["idResult"]

    # incrementation du nombre de tentatives
    def create(self, request, *args, **kwargs):
        id_test = request.data.get("idTest")
        id_user = request.data.get("idUser")
        level = request.data.get("niveau")
        score = request.data.get("resultat")
        tentative = request.data.get("tentative")

        test = Test.objects.get(id=id_test)
        print("le seuil du test est: ",test.seuil)

        # Check if a Resultat object with the same idTest already exists
        try:
            resultat = Resultat.objects.get(
                idTest=id_test, idUser=id_user, niveau=level
            )
            # If the score is less than 80, increment the tentative field
            if score < test.seuil:
                tentative = resultat.tentative + 1
                resultat.tentative = tentative
            else:
                tentative = resultat.tentative + 1
                resultat.tentative = tentative
                resultat.valider = True

            # Update the score regardless of the value
            resultat.resultat = score
            resultat.save()
            serializer = self.get_serializer(resultat)
            return Response(serializer.data)
        except Resultat.DoesNotExist:
            # If a Resultat object with the same idTest does not exist, create a new Resultat object
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(tentative=tentative)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )

    # recuperation des infos de la table resultat en fonction du idUser et idTest
    @action(detail=False, methods=["get"])
    def getidresultat(self, request):
        id_test = request.query_params.get("idTest")
        id_user = request.query_params.get("idUser")
        level = request.query_params.get("niveau")

        try:
            resultat = Resultat.objects.get(
                idTest=id_test, idUser=id_user, niveau=level
            )
            return Response(ResultatSer(resultat).data)
        except Resultat.DoesNotExist:
            return Response("Resultat object does not exist")
        
    
    # Renitialiser les chapitres echoué et recalculer les progres en cas d'echec du test
    @action(detail=False, methods=["get"])
    def restartProgress(self, request):
        id_test =int( request.query_params.get("idTest"))
        id_user = int(request.query_params.get("idUser"))
        nombreMedias =  int(request.query_params.get("totalMedia"))
        failChapter = request.query_params.get("failChapter")
        failChapter = [int(num) for num in failChapter.split(",")]
        print("voici le total des medias pour ce module: ",nombreMedias)
        print("voici le fail chapter recuperer: ",failChapter)
        medias = Media.objects.filter(chapitre__in=failChapter)
        #les id des media pour ce user et module
        print("les medias sont est: ",MediaSerializer(medias,many=True).data)
        mediaIds =  [item.id for item in medias]
        print("Les ids des medias sont: ",mediaIds)

        #update the progress mode content by passing etat to false
        for id in mediaIds:
            ProgressContenuModule.objects.filter(media=id,apprenant=id_user).update(etat=False)


        try:
            test = Test.objects.get(id=id_test)
            moduleId = test.idModule.id
            print("le id du module est: ",moduleId)
            #update the progress
            newProg = 100-(len(mediaIds)/nombreMedias)*100
            print("le nouveau progres est de: ",newProg)
            Progres.objects.filter(module=moduleId,apprenant=id_user).update(progres=newProg)
            return Response(MediaSerializer(medias,many=True).data)
        except Progres.DoesNotExist:
            return Response("Progres object does not exist")

    # nombre total d'admis et non admis
    @action(detail=False, methods=["get"])
    def get_valider_percentage(self, request):
        total_count = Resultat.objects.count()
        true_count = Resultat.objects.filter(valider=True).count()
        false_count = Resultat.objects.filter(valider=False).count()

        if total_count == 0:
            return Response({"message": "No Resultat objects found"})

        return Response({"true_count": true_count, "false_count": false_count})

    # nombre d'admis et non admis par tentative
    @action(detail=False, methods=["get"])
    def get_tentative_counts(self, request):
        results = Resultat.objects.values('tentative') \
        .annotate(true_counts=Count('idResult', filter=models.Q(valider=True)),
                  false_counts=Count('idResult', filter=models.Q(valider=False))) \
        .order_by('tentative')

        return Response({"counts":[{'tentative': r['tentative'], 'true_counts': r['true_counts'], 'false_counts': r['false_counts']} for r in results]})
        

    # moyenne de note de tous le users par modules
    @action(detail=False, methods=["get"])
    def get_module_average_results(self, request):
        module_results = Resultat.objects.values("idTest__idModule__titre").annotate(
            average_result=Avg("resultat")
        )
        module_results_list = []
        for result in module_results:
            module_results_list.append(
                {
                    "module": result["idTest__idModule__titre"],
                    "average_result": round(result["average_result"], 2),
                }
            )
        return Response({"module_results": module_results_list})


# Vue de la table Certificat avec CRUD
class CertificatView(viewsets.ModelViewSet):
    queryset = Certificat.objects.all()
    serializer_class = CertificatSer
    filter_backends = [filters.SearchFilter]
    search_fields = ["idResultat__idUser__id"]

    @action(detail=False, methods=["get"])
    def module_count(self, request):
        # Get the number of certificates for each module
        module_counts = (
            Certificat.objects.values("idResultat__idTest__idModule__titre")
            .annotate(module_count=Count("idResultat__idTest__idModule"))
            .order_by("idResultat__idTest__idModule__titre")
        )
        return Response(module_counts)


# CRUD For  Plainte
class PlainteViewSet(viewsets.ModelViewSet):
    serializer_class = PlainteSerializer
    queryset = Plainte.objects.all()
    
    filter_backends = [filters.SearchFilter]
    search_fields = ["user__id"]

    @action(detail=False, methods=['get'])
    def plaintes_per_month(self, request):
        qs = self.filter_queryset(self.get_queryset())
        qs = qs.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id'))
        return Response(qs)

    @action(detail=False, methods=['get'])
    def plaintes_per_day(self, request):
        qs = self.filter_queryset(self.get_queryset())
        qs = qs.annotate(day_of_week=ExtractWeekDay('created_at')).values('day_of_week').annotate(count=Count('id'))
        return Response(qs)
    

class FormationViewSet(viewsets.ModelViewSet):
    serializer_class = FormationSerializer
    queryset = Formation.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["etat"]


# CRUD For  Module
class ModuleViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleSerializer
    queryset = Module.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["formation__id"]

    # get module by id_formation and id_responsable
    @action(detail=False, methods=["get"])
    def getModuleById(self, request):
        formation_ = request.query_params.get("idFormation")

        responsable_ = request.query_params.get("idResponsable")

        try:
            resultat = Module.objects.filter(
                formation=formation_, responsable=responsable_
            )
            res = ModuleSerializer(resultat, many=True).data
            return Response(res)
        except Module.DoesNotExist:
            return Response({"status": False})

    @action(detail=False, methods=["get"])
    def formation_count(self, request):
        # Get the number of modules in each formation
        formation_counts = self.queryset.values("formation__titre").annotate(
            count=Count("id")
        )
        return Response(formation_counts)


# CRUD For  Module
class ProgressContenuModuleViewSet(viewsets.ModelViewSet):
    serializer_class = ProgressContenuModuleSerializer
    queryset = ProgressContenuModule.objects.all()


# CRUD For Chapitre
class ChapitreViewSet(viewsets.ModelViewSet):
    serializer_class = ChapitreSerializer
    queryset = Chapitre.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["module__id"]

    # get chapitre by id_Module and id_responsable
    @action(detail=False, methods=["get"])
    def getChapitreById(self, request):
        module_ = request.query_params.get("idModule")

        try:
            resultat = Chapitre.objects.filter(module=module_)
            res = ChapitreSerializer(resultat, many=True).data
            return Response(res)
        except Chapitre.DoesNotExist:
            return Response({"status": False})


# CRUD For Media
class MediaViewSet(viewsets.ModelViewSet):
    serializer_class = MediaSerializer
    queryset = Media.objects.all()


# CRUD For Docs
class DocsViewSet(viewsets.ModelViewSet):
    serializer_class = DocsSerializer
    queryset = Docs.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["chapitre__id"]


# CRUD For Videos
class VideosViewSet(viewsets.ModelViewSet):
    serializer_class = VideosSerializer
    queryset = Videos.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["chapitre__id"]


class LinkSourceViewSet(viewsets.ModelViewSet):
    serializer_class = LinkSourceSerializer
    queryset = LinkSource.objects.all()  # CRUD For  Feedback
    filter_backends = [filters.SearchFilter]
    search_fields = ["chapitre__id"]


# CRUD For  FeedBack
class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["id_module__id"]


# CRUD For  Rating


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    queryset = Rating.objects.all()

    # get Raiting with id module an id apprenant
    @action(detail=False, methods=["get"])
    def getRatingsByIds(self, request):
        module_ = request.query_params.get("idModule")

        apprenant_ = request.query_params.get("idApprenant")

        try:
            resultat = Rating.objects.filter(module=module_, apprenant=apprenant_)
            res = RatingSerializer(resultat, many=True).data
            return Response(res)
        except Rating.DoesNotExist:
            return Response({"status": False})

    # get Raiting with id module
    @action(detail=False, methods=["get"])
    def getRatingsByModule(self, request):
        module_ = request.query_params.get("idModule")

        try:
            resultat = Rating.objects.filter(module=module_)
            res = RatingSerializer(resultat, many=True).data
            return Response(res)
        except Rating.DoesNotExist:
            return Response({"status": False})


# CRUD For  Progres
class ProgresViewSet(viewsets.ModelViewSet):
    serializer_class = ProgresSerializer
    queryset = Progres.objects.all()

    @action(detail=False, methods=["get"])
    def geProgress(self, request):
        module = int(request.query_params.get("idModule"))

        apprennant = int(request.query_params.get("idApprennant"))

        try:
            resultat = Progres.objects.get(module=module, apprenant=apprennant)
            return Response(ProgresSerializer(resultat).data)
        except Progres.DoesNotExist:
            return Response({"status": False})


# CRUD For  Acces
class AccesViewSet(viewsets.ModelViewSet):
    serializer_class = AccesSerializer
    queryset = Acces.objects.all()
    
     #send email to responsable for granting module acces
    def create(self, request, *args, **kwargs):
        # Call the parent's create method to perform the default creation behavior
        response = super().create(request, *args, **kwargs)
        
        # Get the newly created Acces object
        acces = response.data
        
        etat = acces['etat']
        encours = acces['encours']
        refus = acces['refus']
        
        
        apprenant = acces['apprenant']
        
        
        app = Apprenant.objects.filter(id=apprenant)
        app_data =ApprenantSerializer(app,many=True).data
        app_name =  app_data[0]['first_name']
        
        
        module_of_respo = Module.objects.filter(id=acces['module'])
        responsable =ModuleSerializer(module_of_respo,many=True).data
        id_ = responsable[0]['responsable']
        ids = [item['responsable'] for item in responsable]
        mod  = responsable[0]['titre']
        
        print("ids " , ids)
        
        
        res =  Responsable.objects.filter(id=id_)
        r = ResponableSer(res,many=True).data
        email = r[0]['email']
        emails = [item['email'] for item in r]


        print("les emails du responsable est   :",r)
        
        if etat == False and encours == True and refus == False:
            # Prepare email details for the first case
            subject = "Demande d'acces !"
            message = f"L'apprenant  {app_name} demande un acces au module {mod}"
        elif etat == False and encours == True and refus == True:
            # Prepare email details for the second case
            subject = "Demande de reactivation"
            message = f"L'apprenant  {app_name} demande une reactivation au module {mod}"
            print(message)
       
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]  # Replace with the actual recipient email address
        
        # Send the email
        send_mail(subject, message, from_email, recipient_list)
        
        return response

    # get module by responsable
    @action(detail=False, methods=["get"])
    def getModuleById(self, request):
        apprennant_ = request.query_params.get("idApprenant")
        try:
            resultat = Acces.objects.filter(
                # encours=False,
                apprenant=apprennant_
            )
            res = AccesSerializer(resultat, many=True).data
            return Response(res)
        except Acces.DoesNotExist:
            return Response({"status": False})

    # get acces 'encours=true'

    # get demand Acces to Module for responsable
    @action(detail=False, methods=["get"])
    def getDemamdAcces(self, request):        
        module_ = request.query_params.get("idModule")
        try:
            resultat = Acces.objects.filter(module=module_,etat=False, encours=True, refus=False)
            res = AccesSerializer(resultat, many=True).data
            return Response(res)
        except Acces.DoesNotExist:
            return Response({"status": False})

    # get all demand accès
    @action(detail=False, methods=["get"])
    def getAllDemamdAcces(self, request):        
        try:
            resultat = Acces.objects.filter(etat=False, encours=True, refus=False)
            res = AccesSerializer(resultat, many=True).data
            return Response(res)
        except Acces.DoesNotExist:
            return Response({"status": False})

    # get demand reactivation to Module
    @action(detail=False, methods=["get"])
    def getDemamdReactivation(self, request):        
        module_ = request.query_params.get("idModule")
        try:
            resultat = Acces.objects.filter(module=module_,etat=False, encours=True, refus=True)
            res = AccesSerializer(resultat, many=True).data
            return Response(res)
        except Acces.DoesNotExist:
            return Response({"status": False})

    # get all demand reactivation
    @action(detail=False, methods=["get"])
    def getAllDemamdReactivation(self, request):     
        try:
            resultat = Acces.objects.filter(etat=False, encours=True, refus=True)
            res = AccesSerializer(resultat, many=True).data
            return Response(res)
        except Acces.DoesNotExist:
            return Response({"status": False})

    # get acces 'encours=true'

    # get demand Acces to Module by responsable
    @action(detail=False, methods=["get"])
    def getDemamdAccesByResponsable(self, request):        
        responsable_ = int(request.query_params.get("idResponsable"))

        try:
            modules = Module.objects.filter(responsable=responsable_)
            # Extract the list of IDs
            id_list = [item.id for item in modules]
            resultat = Acces.objects.filter(module__in=id_list,etat=False, encours=True, refus=False)
            res = AccesSerializer(resultat, many=True).data
            return Response(res)
        except Acces.DoesNotExist:
            return Response({"status": False})

    # get demand Acces to Module by responsable
    @action(detail=False, methods=["get"])
    def getDemamdReactivationByResponsable(self, request):        
        responsable_ = int(request.query_params.get("idResponsable"))

        try:
            modules = Module.objects.filter(responsable=responsable_)
            # Extract the list of IDs
            id_list = [item.id for item in modules]
            resultat = Acces.objects.filter(module__in=id_list,etat=False, encours=True, refus=True)
            res = AccesSerializer(resultat, many=True).data
            return Response(res)
        except Acces.DoesNotExist:
            return Response({"status": False})

    # get module by responsable
    @action(detail=False, methods=["get"])
    def getEtatAccesInModule(self, request):
        try:
            resultat = Acces.objects.exclude(etat=False, encours=True, refus=False)
            res = AccesSerializer(resultat, many=True).data
            return Response(res)
        except Acces.DoesNotExist:
            return Response({"status": False})


# Initialisation de progressModContent apres chaque avoir accordé l'acces au module à un apprenant
@receiver(post_save, sender=Acces)
def create_or_update_progresscontenumodule(sender, instance, created, **kwargs):
    if not created:
        if instance.etat:
            print("Acces accordé: ")
            module_id = instance.module.id
            # media = Media.objects.filter(module=module_id)
            chapitre = Chapitre.objects.filter(module=module_id)
            id_chapitre = ChapitreSerializer(chapitre, many=True).data

            print("Chapitres : ", chapitre)
            # id_media = MediaSerializer(media, many=True).data
            print("Nombre total des chapitres : ", len(id_chapitre))
            taille = len(id_chapitre)
            appr = Apprenant.objects.get(id=instance.apprenant.id)

            for chap in id_chapitre:
                media = Media.objects.filter(chapitre=chap["id"])
                serialMedia = MediaSerializer(media, many=True).data
                for mdia in media:
                    print("le media est", mdia)
                    if mdia.type != "Link":
                        print("le type du media est", mdia.type)
                        progress, _ = ProgressContenuModule.objects.get_or_create(
                            media=mdia, apprenant=appr, etat=False
                        )
                progress.save()

        else:
            print("Acces refusé: ")

        return

    if created:
        print("Ajout: ")
        return
@receiver(post_save, sender=Docs)
def create_or_update_progresDocsContent(sender, instance, created, **kwargs):
    if not created:
        print("update: ")
        mod = instance.chapitre.module
        print("le id du module: ", mod.id)

        return

    if created:
        print("Ajout: ")
        # l'identifiant du media est:
        id_media = instance.id
        mod = instance.chapitre.module
        acces = Acces.objects.filter(module=mod)
        accesData = AccesSerializer(acces, many=True).data
        apprenants = [d["apprenant"] for d in accesData]
        print("la liste des id d'apprenants: ", apprenants)
        print("l'identifiant du media est: ", id_media)
        for appr_id in apprenants:
            appr = Apprenant.objects.get(id=appr_id)
            med = Media.objects.get(id=id_media)
            if not ProgressContenuModule.objects.filter(
                media=med, apprenant=appr
            ).exists():
                progress, _ = ProgressContenuModule.objects.get_or_create(
                    media=med, apprenant=appr, etat=False
                )
                progress.save()

        return


# ajout du media dans progressModContent apres l'ajout ou modification d'un nouveau media video au module
@receiver(post_save, sender=Videos)
def create_or_update_progresVideosContent(sender, instance, created, **kwargs):
    if not created:
        print("update: ")
        mod = instance.chapitre.module
        print("le id du module: ", mod.id)

        return

    if created:
        print("Ajout: ")
        # l'identifiant du media est:
        id_media = instance.id
        mod = instance.chapitre.module
        acces = Acces.objects.filter(module=mod)
        accesData = AccesSerializer(acces, many=True).data
        apprenants = [d["apprenant"] for d in accesData]
        print("la liste des id d'apprenants: ", apprenants)
        print("l'identifiant du media est: ", id_media)
        for appr_id in apprenants:
            appr = Apprenant.objects.get(id=appr_id)
            med = Media.objects.get(id=id_media)
            if not ProgressContenuModule.objects.filter(
                media=med, apprenant=appr
            ).exists():
                progress, _ = ProgressContenuModule.objects.get_or_create(
                    media=med, apprenant=appr, etat=False
                )
                progress.save()

        return



def get_image(request, filename):
    image_path = os.path.join(settings.MEDIA_ROOT, filename)
    with open(image_path, "rb") as f:
        return HttpResponse(f.read(), content_type="image/jpeg")
    serializer_class = AccesSerializer
    queryset = Acces.objects.all()


# Apprenant CRUD
class ApprenantViewSet(viewsets.ModelViewSet):
    serializer_class = ApprenantSer
    queryset = Apprenant.objects.all()
    def create(self, request, *args, **kwargs):
        selected_items = request.data.get('selectedItems')
        email = request.data.get('email')
        if email and Apprenant.objects.filter(email=email).exists():
            error_data = {'message': 'Ce mail existe déja', 'selected_items': request.data.get('selectedItems')}
            return JsonResponse(error_data, status=400)

        try:
            apprenant = super().create(request, *args, **kwargs).data
            # Create Access objects for each selected module
            for module_id in selected_items:
                Acces.objects.create(
                    apprenant_id=apprenant['id'],
                    module_id=module_id,
                    etat=True,
                    encours=False,
                    refus=False
                )
            return Response(apprenant, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            # If a validation error is raised, return a 400 response with the error message
            return HttpResponseBadRequest("Vieullez remplir tous les champs")
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.responsable.role in ['admin', 'superadmin']
    # get apprenants by year
    @action(detail=False, methods=['get'])
    def apprenant_count_by_year(self, request):
        apprenants_by_year = Apprenant.objects.annotate(year=ExtractYear('date_creation')).values('year').annotate(count=Count('id'))
        data = {
            'apprenants_by_year': apprenants_by_year,
        }
        return Response(data)



# Responsable CRUD
class ResonsableViewSet(viewsets.ModelViewSet):
    serializer_class = ResponableSer
    queryset = Responsable.objects.all()

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        if email and Responsable.objects.filter(email=email).exists():
            return HttpResponseBadRequest("Ce mail existe déja")

        try:
            # Call the parent create method to perform the create operation
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            # If a validation error is raised, return a 400 response with the error message
            return HttpResponseBadRequest("Vieullez remplir tous les champs")

    # permission_classes = [IsAuthenticated, CanViewResponsables]

    # def get_queryset(self):
    #     # Only return Responsable objects with a role of 'admin' or 'superadmin'
    #     return self.queryset.filter(role__in=['admin', 'superadmin'])

    # def get_permissions(self):
    #     # Allow superadmins to create, update, or delete Responsable objects
    #     if self.request.method not in SAFE_METHODS and self.request.user.responsable.role == "superadmin":
    #         return [IsSuperAdmin()]
    #     return super().get_permissions()


# login de l'apprenant
class ApprenantTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        try:
            user = User.objects.select_related("apprenant").get(email=email)
            apprenant = user.apprenant
            if apprenant and apprenant.etat:
                if not user.check_password(password):
                    return Response(
                        {"message": "Email ou mot de passe invalide"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    }
                )
            else:
                return Response(
                    {"message": "Email ou mot de passe invalide"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            return Response(
                {"message": "Email ou mot de passe invalide"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# login du responsable
class ResponsableTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        try:
            user = User.objects.select_related("responsable").get(email=email)
            responsable = user.responsable
            if responsable and responsable.etat:
                if not user.check_password(password):
                    return Response(
                        {"message": "Email ou mot de passe invalide."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "access": str(refresh.access_token),
                        "role": responsable.role,
                        "refresh": str(refresh),
                    }
                )
            else:
                return Response(
                    {"message": "Email ou mot de passe invalide."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            return Response(
                {"message": "Email ou mot de passe invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# Get Auth User Data
class UserDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Enregistrer demande d'inscription + CRUD
class DemandeRegisterViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]

    serializer_class = DemandeSer
    queryset = Demande.objects.all()

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        if email and Demande.objects.filter(email=email).exists():
            return HttpResponseBadRequest("Ce mail existe déja")

        try:
            # Call the parent create method to perform the create operation
            response =  super().create(request, *args, **kwargs)
             # Send an email to the newly created Apprenant
            subject = "Demande d'inscription sur la plateforme E-Learning"
            message = "Une personne avec l'email ! {}, a envoyée une demande d'inscription sur la plateforme E-Learning.".format(
                email
            )
            from_email = "sender@gmail.com"  # replace with your email address
            recipient_list = ["k.erraghi@atexperts.ma"]
            send_mail(subject, message, from_email, recipient_list)
            return response

        except ValidationError as e:
            # If a validation error is raised, return a 400 response with the error message
            return HttpResponseBadRequest("Veuillez remplir tous les champs")


# Approuver la demande d'inscription
def approve_demande(request, demande_id):
    demande = Demande.objects.get(id=demande_id)
    if User.objects.filter(email=demande.email).exists():
        return JsonResponse({"message": "Ce mail existe déja"})

    apprenant = Apprenant.objects.create(
        first_name=demande.first_name,
        last_name=demande.last_name,
        email=demande.email,
        password=demande.password,
        image=demande.image,
        address=demande.address,
    )

    demande.etat = False
    demande.isApproved = True
    demande.save()
    apprenant.save()

    # Send an email to the newly created Apprenant
    subject = "Création de votre compte sur la plateforme E-Learning"
    message = "Félicitaions ! {} {},votre compte à été crée avec succés, vous pouvez maintenant accéder à la plateforme et suivre les formations en utilisant votre email et votre mot de passe.".format(
        apprenant.first_name, apprenant.last_name
    )
    from_email = "sender@gmail.com"  # replace with your email address
    recipient_list = [apprenant.email]
    send_mail(subject, message, from_email, recipient_list)

    return JsonResponse({"message": "Compte crée avec succés."})


# Refuser la demande d'inscription
def refuse_demande(request, demande_id):
    demande = Demande.objects.get(id=demande_id)

    demande.isApproved = False
    demande.etat = False
    demande.save()

    # Send an email to the regused demande
    subject = (
        "Refus de demande de création de votre compte sur la plateforme E-Learning"
    )
    message = "Malheureusement ! {} {} votre compte n'a pas été créé, veuillez essayer une autre fois".format(
        demande.first_name, demande.last_name
    )
    from_email = "sender@gmail.com"  # replace with your email address
    recipient_list = [demande.email]
    send_mail(subject, message, from_email, recipient_list)

    return JsonResponse({"message": "Demande refusée avec succés."})


# get user image function
@permission_classes([IsAuthenticated])
def get_user_image(request, user_id):
    user = get_object_or_404(User, id=user_id)
    image_data = open(user.image.path, "rb").read()
    return HttpResponse(image_data, content_type="image/png")


# update user function
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    # Find the User object with the given ID
    user = User.objects.get(id=user_id)

    # Update the User object with the data from the request
    user.first_name = request.data.get("first_name", user.first_name)
    user.last_name = request.data.get("last_name", user.last_name)
    user.image = request.data.get("image", user.image)
    user.email = request.data.get("email",user.email)
    user.address = request.data.get("address", user.address)

    # Save the updated User object
    user.save(update_fields=["first_name", "last_name", "image","email","address"])

    return Response(
        {"message": "User data updated successfully."}, status=status.HTTP_200_OK
    )


@api_view(["PUT"])
def update_respo_role(request, user_id):
    # Find the User object with the given ID
    respo = Responsable.objects.get(id=user_id)

    # Update the User object with the data from the request
    respo.role = request.data.get("role", respo.role)

    # Save the updated User object
    respo.save(update_fields=["role"])

    return Response(
        {"message": "responsable role updated successfully."}, status=status.HTTP_200_OK
    )


@api_view(["PUT"])
def update_respo_etat(request, user_id):
    # Find the User object with the given ID
    respo = Responsable.objects.get(id=user_id)

    # Update the User object with the data from the request
    etat_str = request.data.get("etat", str(respo.etat)).lower()
    if etat_str == "false":
        etat = False
    else:
        etat = bool(etat_str)
    respo.etat = etat

    # Save the updated User object
    respo.save(update_fields=["etat"])

    return Response(
        {"message": "état responsable mis à jour avec succès."},
        status=status.HTTP_200_OK,
    )
    
@api_view(["PUT"])
def update_apprenant_etat(request, user_id):
    # Find the User object with the given ID
    appr = Apprenant.objects.get(id=user_id)

    # Update the User object with the data from the request
    etat_str = request.data.get("etat", str(appr.etat)).lower()
    if etat_str == "false":
        etat = False
    else:
        etat = bool(etat_str)
    appr.etat = etat

    # Save the updated User object
    appr.save(update_fields=["etat"])

    return Response(
        {"message": "état responsable mis à jour avec succès."},
        status=status.HTTP_200_OK,
    )    

# update password function
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def change_password(request, user_id):
    # Get the current user
    user = User.objects.get(id=user_id)

    # Get the old password, new password and confirm password from the request data
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")
    confirm_password = request.data.get("confirm_password")

    # If authentication is successful, update the password
    if check_password(old_password, user.password):
        if new_password == confirm_password:
            user.password = new_password
            user.save()
            # Update the session to prevent the user from being logged out
            # update_session_auth_hash(request, user)
            return JsonResponse(
                {"success": True, "message": "Password updated successfully."}
            )
        else:
            return JsonResponse(
                {"error": "New password and confirm password do not match."}
            )
    else:
        return JsonResponse({"error": "Old password is incorrect."})

@api_view(["GET"])
def get_apprenants_with_access(request, responsable_id):
    try:
        apprenants = Apprenant.objects.filter(acces__module__responsable_id=responsable_id, acces__etat=True)
        serializer = ApprenantSerializer(apprenants, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Responsable.DoesNotExist:
        return JsonResponse([], safe=False)

