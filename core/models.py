from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('This object requires an email')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that uses email instead of username"""
    email = models.EmailField(max_length=25, unique=True,null=True)
    #fullname is compulsory
    fullname = models.CharField(max_length=255,null=True)
    #university is cumpulsory
    university = models.CharField(max_length=20,null=True,blank=True)
    location = models.CharField(max_length=20,null=True,blank=True)

    address = models.CharField(max_length=20,null=True,blank=True)
    vendor_name = models.CharField(max_length=20,null=True,blank=True)
    #phone number is cumpulsory
    phone_number= models.CharField(max_length=25,null=True,blank=True)
    pushToken = models.CharField(max_length=225, null=True, blank=True)
    wallet=models.IntegerField(default=10)
    social_links=models.CharField(max_length=300,null=True,blank=True)
    slots=models.IntegerField(null=True,blank=True)
    is_buyer=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return str(self.email)

# Create your models here.
class School(models.Model):
    name=models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Location(models.Model):
    name=models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Post (models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete= models.CASCADE)
    phone_number=models.CharField(max_length=11,null=True)

  #  price= models.IntegerField(null=True,blank=True)

    def __str__(self):
        return str(self.id)


class Order(models.Model):
    supplement=[("meat","meat"),("fish","fish"),("turkey","turkey")]
    drink=[("coke","coke"),("fanta","fanta"),("malt","malt"),("sprites","sprites")]

    customer=models.ForeignKey(settings.AUTH_USER_MODEL,related_name="buyer",on_delete= models.CASCADE,null=True)
    main_dish=models.CharField(max_length=250,null=True,blank=True)
    main_dish_amount=models.IntegerField(null=True,blank=True)
    supplements=models.CharField(max_length=15,null=True,blank=True)
    supplements_amount=models.IntegerField(null=True,blank=True)
    drinks=models.CharField(max_length=15,null=True,blank=True)
    drinks_amount=models.IntegerField(null=True,blank=True)
   #place of delivery
    place_of_delivery=models.CharField(max_length=250,null=True)
   #method of payment
    method_of_payment=models.CharField(max_length=250,null=True)
    phone_number=models.CharField(max_length=11,null=True)
    price=models.IntegerField(null=True)
    tip=models.IntegerField(null=True)
    buyer_phone_number=models.CharField(max_length=11,null=True)
    post=models.ForeignKey(Post,on_delete= models.CASCADE,null=True,blank=True)
    is_ordered=models.BooleanField(default=False)
    is_bought=models.BooleanField(default=False)
    is_delivered=models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True,null=True)

#    is_ordered=models.BooleanField(default=False)



    def __str__(self):
        return str(self.price)


class Menu (models.Model):
    name = models.CharField(max_length=15)
    price= models.IntegerField(null=True,blank=True)
    date_added = models.DateTimeField(auto_now_add=True,null=True)


    def __str__(self):
        return self.name+" "+str(self.price)


class Author(models.Model):
    name = models.CharField(null=True, blank=True,max_length=15)

    def __str__(self):
        return self.name


class Book(models.Model):
    author= models.ManyToManyField(Author)
    title = models.CharField(null=True, blank=True,max_length=15)

    def __str__(self):
        return self.title




