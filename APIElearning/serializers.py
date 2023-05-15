from .models import (
    Demande,
    LinkSource,
    ProgressContenuModule,
    Rating,
    Test,
    Resultat,
    Certificat,
)
from rest_framework import serializers
from .models import (
    Apprenant,
    Formation,
    Module,
    Chapitre,
    Media,
    Feedback,
    Progres,
    Acces,
    Docs,
    Videos,
    Plainte,
    Rating,
)
from rest_framework import serializers
from .models import User, Apprenant, Responsable


# Serializer de la table Test
class TestSer(serializers.ModelSerializer):
    module = serializers.CharField(source="idModule.titre", default=None)

    class Meta:
        model = Test
        fields = "__all__"


# Serializer de la table Resultat
class ResultatSer(serializers.ModelSerializer):
    module = serializers.CharField(source="idTest.idModule.titre", default=None)
    formation = serializers.CharField(
        source="idTest.idModule.formation.titre", default=None
    )
    username = serializers.CharField(source="idUser.email", default=None)

    class Meta:
        model = Resultat
        fields = "__all__"


class UserSer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = "__all__"


class RateSer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"


# Serializer de la table Certificat
class CertificatSer(serializers.ModelSerializer):
    module = serializers.CharField(
        source="idResultat.idTest.idModule.titre", default=None
    )
    formation = serializers.CharField(
        source="idResultat.idTest.idModule.formation.titre", default=None
    )
    username = serializers.CharField(source="idResultat.idUser.email", default=None)
    resultat = serializers.IntegerField(source="idResultat.resultat", default=None)

    class Meta:
        model = Certificat
        fields = "__all__"


# class Apprenant Serializer
class ApprenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apprenant
        fields = "__all__"


# class Feedback plainte
class PlainteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plainte
        fields = "__all__"


# class Formation Serializer
class FormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formation
        fields = "__all__"


# class Module Serializer
class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = "__all__"


# class Chapitre Serializer
class ChapitreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapitre
        fields = "__all__"


class ProgressContenuModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressContenuModule
        fields = "__all__"


class ProgressContenuModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressContenuModule
        fields = "__all__"


class LinkSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkSource
        fields = "__all__"


# class Media Serializer
class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = "__all__"


class DocsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docs
        fields = "__all__"


class VideosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videos
        fields = "__all__"


# class Feedback Serializer
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"


# class Raiting Serializer
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"


# class Progres Serializer
class ProgresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progres
        fields = "__all__"


class LinkSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkSource
        fields = "__all__"


# class Acces Serializer
class AccesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acces
        fields = "__all__"


class UserSer(serializers.ModelSerializer):
    role = serializers.CharField(source="responsable.role", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "address", "image", "role"]


class ApprenantSer(serializers.ModelSerializer):
    class Meta:
        model = Apprenant
        fields = "__all__"


class ResponableSer(serializers.ModelSerializer):
    class Meta:
        model = Responsable
        fields = "__all__"


class DemandeSer(serializers.ModelSerializer):
    class Meta:
        model = Demande
        fields = "__all__"
