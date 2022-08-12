import json
from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.response import Response
from .serializers import registrationserializer,Resetpasswordserializer,Orderserializer,Customerorderserializer,Updateuserserializer,BookSerializer
from rest_framework.authtoken.models import Token
from .models import User,Order,Menu,Post,Book,School,Location

import json


@api_view(["POST"])
@permission_classes([AllowAny])
def reg(request):

    data = {"quick":"silver"}
    serializer = registrationserializer(data=request.data)
    if serializer.is_valid():
        if  request.data.get("university"):
            school = School.objects.get(id=request.data.get("university"))
            user = serializer.save(university=school.name)
        else:
            user = serializer.save()
        if request.data.get('location'):
            location=Location.objects.get(id=request.data.get('location'))
            user.location=location.name
            user.save()
        if request.data.get('vendor_name'):
            user.vendor_name=request.data.get('vendor_name')
            user.save()
        if request.data.get('address'):
            user.address=request.data.get('address')
            user.save()

        token = Token.objects.get_or_create(user=user)[0].key
        print(user.fullname)
        
        data["token"] = token
        return Response(data,status=status.HTTP_201_CREATED)


    else:
        data = serializer.errors

        return Response(data,status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST","GET"])
@permission_classes([AllowAny])
def name(request):

    data = {"quick":"silvermehnnn"}


    return Response(data)



@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_buyer(request):
    data={}
    user=request.user
    user.is_buyer=True
    user.save()
    post=Post(user=request.user,phone_number=request.user.phone_number)
    post.save()
    data["message"]="user is now a buyer"

    return Response(data)



@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    data={}
   # body=json.loads(request.body)
    email=request.data["email"]
    password=request.data["password"]
    #print(request.data["pushToken"])
    #pushToken=request.data["pushToken"]

    try:
        account=  User.objects.get(email=email)
    except User.DoesNotExist:
        data["message"] = "invalid email address"

        return Response(data)
    if account:
        token=Token.objects.get_or_create(user=account)[0].key
        if check_password(password,account.password):


            data["token"]=token

            print(data)
            user= User.objects.get(email=email)
            #user.pushToken=pushToken
            user.save()
            return Response(data)

        else:
            data["message"] = "password is invalid"

            return Response(data)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def logout(request):
    data={}
    token=Token.objects.get(user=request.user)
    token.delete()
    data["message"]="USER IS LOGGED OUT"
    return Response(data,status=status.HTTP_200_OK)




@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    data={}
    user=User.objects.get(email=request.data["email"])
    serializer = Resetpasswordserializer(instance=user,data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        data["message"] = "user updated successfully"
        data["email"] = user.email
        data["university"] = user.phone_number
        data["fullname"] = user.fullname
        data["Password"] = user.password
        return Response(data, status=status.HTTP_201_CREATED)


    else:
        data = serializer.errors

        return Response(data, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def create_order(request,id):
    data={}
    total=0
    pos=Post.objects.get(user__id=id)

    if 'main_dish' in request.data:
        maindishamount=request.data["main_dish_amount"]
        #menu=Menu.objets.get(name=request.data["mains"])
        total+=int(maindishamount)
    if 'supplements' in request.data:
        supplementsamount=request.data["supplements_amount"]
        menu=Menu.objects.get(name=request.data["supplements"])
        total= total+(menu.price*int(supplementsamount))

    if 'drinks' in request.data:
        drinksamount=request.data["drinks_amount"]
        menu=Menu.objects.get(name=request.data["drinks"])
        total= total+(menu.price*int(drinksamount))

    tip=total*30/100
    serializer=Orderserializer(data=request.data)

    if serializer.is_valid():
        post=serializer.save(post=pos,customer=request.user,buyer_phone_number=pos.phone_number ,price=total,tip=tip,phone_number=request.user.phone_number)

        data["message"]="post created"
        data["fee"]=post.price
        data["drinks"]=post.tip

        return Response(data,status=status.HTTP_201_CREATED)

    else:
        data = serializer.errors

        return Response(data, status=status.HTTP_400_BAD_REQUEST)




@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delete_order(request,id):
    post=Order.objects.get(id=id)
    post.delete()
    data={}
    data["message"]="order was deleted"
    return Response(data)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def profile(request):
    print("whats good")
    profile=User.objects.get(email=request.user.email)
    serializer=registrationserializer(profile,many=False)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def vendor_profile(request,name):
    profile=User.objects.get(vendor_name=name)
    serializer=registrationserializer(profile,many=False)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def order_accepted(request,id):
    data={}
    order=Order.objects.get(id=id)
    order.is_ordered=True
    order.save()

    data["message"] = "Order has been accepted"
    return Response(data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def order_bought(request,id):
    data={}
    order=Order.objects.get(id=id)
    order.is_bought=True
    order.save()
    post=Post.objects.get(id=order.post.id)
    user=User.objects.get(email=post.user.email)
    user.slots= user.slots-1
    print(user.email)
    user.save()
    data["message"] = "Order has been bought"
    return Response(data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def order_delivered(request,id):
    data={}
    order=Order.objects.get(id=id)
    order.is_delivered=True
    order.save()

    data["message"] = "Order has been delivered"
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delete_post(request):
    data={}
    post=Post.objects.get(user__email=request.user.email)
    post.delete()

    user=request.user
    user.is_buyer=False
    user.save()
    data["message"] = "User is no longer a buyer"
    return Response(data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def slots(request):
    data={}
    user=request.user
    user.slots=request.data['slots']
    user.save()

    data["message"] = "slots have been updated"
    return Response(data)

a="knmoesmosmf"
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def books(request):
    data={}
    bok=Book.objects.get(id=1)
    print(bok.author.all())
    serializer=BookSerializer(bok,many=False)
    return  Response (serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_user(request):
    data={}
    print(request.data.get('university'))

    user=User.objects.get(email=request.data["email"])
    serializer = Updateuserserializer(instance=user,data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        if request.data.get('university'):
            school = School.objects.get(id=request.data['university'])
            user.university=school.name
            user.save()
        if request.data.get('location'):
            location = Location.objects.get(id=request.data['location'])
            user.location=location.name
            user.save()
        if request.data.get('address'):
            user.address=request.data.get('address')
            user.save()
        data["message"] = "user updated successfully"
        data["email"] = user.email
        data["university"] = user.university
        data["fullname"] = user.fullname
        data["Password"] = user.password
        data["slot"] = user.slots
        data["vendor"] = user.vendor_name
        return Response(data, status=status.HTTP_201_CREATED)


    else:
        data = serializer.errors

        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class Buyer_order_list(ListAPIView):
    serializer_class=Orderserializer
    authentication_classes=([TokenAuthentication])
    permission_classes=([IsAuthenticated])

    def get_queryset(self):
        post=Post.objects.get(user=self.request.user)
        order = Order.objects.filter(post=post,is_ordered=True)
        return order

class Incoming_order_list(ListAPIView):
    serializer_class=Orderserializer
    authentication_classes=([TokenAuthentication])
    permission_classes=([IsAuthenticated])

    def get_queryset(self):
        post=Post.objects.get(user=self.request.user)
        order = Order.objects.filter(post=post,is_ordered=False)
        return order


class Buyer_list(ListAPIView):
    queryset = User.objects.filter(is_buyer=True,slots__gte=1)
    serializer_class = Updateuserserializer
    authentication_classes = ([TokenAuthentication])
    permission_classes = ([IsAuthenticated])

class  customer_order_list(ListAPIView):
    serializer_class = Customerorderserializer
    authentication_classes = ([TokenAuthentication])
    permission_classes = ([IsAuthenticated])

    def get_queryset(self):
        order = Order.objects.filter(customer=self.request.user,is_ordered=True,is_delivered=False)
        return order


