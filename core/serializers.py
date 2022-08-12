from rest_framework import serializers
from rest_framework import serializers

from .models import User,Order,Book,Author,School

class registrationserializer (serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["id","email","fullname","vendor_name","university","phone_number","location","address","password"]
        extra_kwargs={"password":{"write_only":True}}

    def save(self,university=None,location=None):
        user = User.objects.create(
            email=self.validated_data['email'],
            fullname=self.validated_data.get('fullname'),
            phone_number=self.validated_data.get('phone_number'),
            university=university,
            location=location
         )

        user.set_password(self.validated_data['password'])
        user.save()
        return user

class Resetpasswordserializer (serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["email","fullname","university","password","phone_number"]
        extra_kwargs={"password":{"write_only":True}}

    def save(self):
        user = User.objects.get(
            email=self.validated_data['email'],
        )

        user.set_password(self.validated_data['password'])
        user.save()
        return user


class Updateuserserializer (serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["id","email","fullname","university","phone_number","slots","vendor_name","location","address"]

    def save(self):
        user = User.objects.get(
            email=self.validated_data['email'],
        )

        if "fullname" in self.validated_data:
            user.fullname=self.validated_data['fullname']

        if "phone_number" in self.validated_data:
            user.phone_number=self.validated_data['phone_number']
        if "slots" in self.validated_data:
            user.slots=self.validated_data['slots']
        if "vendor_name" in self.validated_data:
            user.vendor_name=self.validated_data['vendor_name']
        user.save()
        return user



class Orderserializer (serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=["id","price","tip","main_dish","supplements","main_dish_amount","supplements_amount","drinks","drinks_amount","place_of_delivery","method_of_payment","phone_number","post"]



class Customerorderserializer (serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=["id","price","tip","main_dish","supplements","main_dish_amount","supplements_amount","drinks","drinks_amount","place_of_delivery","method_of_payment","is_ordered","is_bought",
            "is_delivered","date_added","buyer_phone_number"]


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Author
        fields=["id","name"]

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True, many=True)

    class Meta:
        model = Book
        fields = ('id','author', 'title',)
