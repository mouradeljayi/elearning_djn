from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import os


# 5 modéles (partie Auth Mourad et Chaima)


# Model for UserManager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


# Model for User
class User(AbstractBaseUser):
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True, max_length=255)
    image = models.ImageField(
        upload_to="uploads/avatars",
        blank=True,
        null=True,
        default="uploads/avatars/paiperleck.jpg",
    )
    address = models.CharField(max_length=255, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        if self.id:
            old_instance = User.objects.get(id=self.id)
            if self.image != old_instance.image:
                if (
                    old_instance.image
                    and old_instance.image != "uploads/avatars/paiperleck.jpg"
                ):
                    os.remove(old_instance.image.path)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


# Model for Apprenant
class Apprenant(User):
    etat = models.BooleanField(default=True)
    def __str__(self):
        return self.email


# Model for Responsable
class Responsable(User):
    ROLE_CHOICES = (
        ("ADMIN", "Admin"),
        ("RESPO", "Respo"),
        ("MASTER", "Master"),
        ("SUPERADMIN", "Superadmin"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="ADMIN")
    etat = models.BooleanField(default=True)

    def __str__(self):
        return self.email


# Model for Plainte
class Plainte(models.Model):
    id = models.AutoField(primary_key=True)
    sujet = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    etat = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.content
    


# Model for Demande
class Demande(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True, max_length=255)
    password = models.CharField(max_length=128)
    image = models.ImageField(upload_to="uploads/avatars", blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    date_demande = models.DateTimeField(auto_now_add=True)
    etat = models.BooleanField(default=True)
    isApproved = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-date_demande']



# 8 modéles (partie Formation Najib et Hatim)
# Model for Formation
class Formation(models.Model):
    id = models.AutoField(primary_key=True)
    titre = models.CharField(null=False, max_length=200)

    description = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        upload_to="uploads/image",
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "jpeg"])],
    )

    etat = models.BooleanField(default=True)

    # other fields and methods

    def save(self, *args, **kwargs):
        if self.id:
            old_instance = Formation.objects.get(id=self.id)
            if self.image != old_instance.image:
                if old_instance.image:
                    os.remove(old_instance.image.path)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre


class Module(models.Model):
    id = models.AutoField(primary_key=True)
    titre = models.CharField(null=False, max_length=200)

    description = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    etat = models.BooleanField(default=True)
    image = models.ImageField(
        upload_to="uploads/image",
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "jpeg"])],
    )

    enrolled = models.BooleanField(default=False)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    responsable = models.ForeignKey(Responsable, on_delete=models.CASCADE)

    # other fields and methods

    def save(self, *args, **kwargs):
        if self.id:
            old_instance = Module.objects.get(id=self.id)
            if self.image != old_instance.image:
                if old_instance.image:
                    os.remove(old_instance.image.path)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre


# Model for Chapiter
class Chapitre(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False, max_length=100)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)


# Model for Media
class Media(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False, max_length=100)
    # url = models.CharField(null=False, max_length=200)
    type = models.CharField(null=False, max_length=200)
    chapitre = models.ForeignKey(Chapitre, on_delete=models.CASCADE)
    # checked = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ProgressContenuModule(models.Model):
    id = models.AutoField(primary_key=True)
    etat = models.BooleanField()
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE)

    def __str__(self):
        return self.description


# !!! inheritance from Media
class Docs(Media):
    file = models.FileField(
        upload_to="uploads/docs",
        null=True,
        default=None,
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "ppt", "pptx"])],
    )
    lienPPT = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.id:
            old_instance = Docs.objects.get(id=self.id)
            if self.file != old_instance.file:
                if old_instance.file:
                    os.remove(old_instance.file.path)
        super().save(*args, **kwargs)


# !!! inheritance from Media
class Videos(Media):
    file = models.FileField(
        upload_to="uploads/videos",
        null=True,
        default=None,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["Mov", "avi", "mp4", "webm", "mkv"]
            )
        ],
    )

    def save(self, *args, **kwargs):
        if self.id:
            old_instance = Videos.objects.get(id=self.id)
            if self.file != old_instance.file:
                if old_instance.file:
                    os.remove(old_instance.file.path)
        super().save(*args, **kwargs)


class LinkSource(Media):
    link = models.TextField()


# Model for Feedback
class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    id_module = models.ForeignKey(Module, on_delete=models.CASCADE)
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE)
    like = models.BooleanField()

    def __str__(self):
        return self.message


# Model for Raiting
class Rating(models.Model):
    id = models.AutoField(primary_key=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE)
    rating = models.IntegerField()


# Model for Progres
class Progres(models.Model):
    id = models.AutoField(primary_key=True)
    progres = models.FloatField()
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE)


# Model for Acces
class Acces(models.Model):
    id = models.AutoField(primary_key=True)
    etat = models.BooleanField(default=False)
    encours = models.BooleanField(default=True)
    refus = models.BooleanField(default=False)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE)

    def __str__(self):
        return self.titre


# 3 modéles (partie test Alio et Amine)


# model de la table test
class Test(models.Model):
    id = models.AutoField(primary_key=True)
    idModule = models.ForeignKey(Module, on_delete=models.CASCADE)
    tempdepassage = models.DurationField(default=timedelta())
    difficulter = models.CharField(max_length=200, default="facile")
    seuil = models.IntegerField()
    description = models.CharField(max_length=200)
    objectif = models.CharField(max_length=200)
    nombredequestion = models.IntegerField(default=1)
    date_ajout = models.DateTimeField(auto_now_add=True)
    question = models.JSONField()

    def __str__(self):
        return str({"Titre du test": self.id})


# model de la table Resultat
class Resultat(models.Model):
    idResult = models.AutoField(primary_key=True)
    idTest = models.ForeignKey(Test, on_delete=models.CASCADE)
    idUser = models.ForeignKey(User, on_delete=models.CASCADE)
    niveau = models.CharField(max_length=200, default="facile")
    valider = models.BooleanField(default=False)
    scoreByChap = models.JSONField()
    date_de_passage = models.DateTimeField(auto_now_add=True)
    resultat = models.FloatField(default=0)
    tentative = models.IntegerField(default=0)

    def __str__(self):
        return str({"id resultat": self.idResult})


# model de la table certificat
class Certificat(models.Model):
    idCertificat = models.AutoField(primary_key=True)
    idResultat = models.ForeignKey(
        Resultat, on_delete=models.CASCADE, default=None, null=True
    )
    certificat_file = models.FileField(
        upload_to="uploads/certificats/", null=True, default=None
    )
    date_obtention = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str({"id certificat": self.idCertificat})
