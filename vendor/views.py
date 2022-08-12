from django.shortcuts import render,get_object_or_404
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from .serializers import ItemSerializer,CategorySerializer,HomeSerializer,OrderSerializer,OrderItemSerializer,itemserializer,LocationSerializer
from .models import *
from core.models import User
from collections import namedtuple
import requests
from core.serializers import registrationserializer
from core.models import Location
import json
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from requests.exceptions import ConnectionError, HTTPError

# Create youggggggr views here.
import rollbar


def send_push_message(token, message):
    try:
        response = PushClient().publish(
            PushMessage(to=token,
                        body=message,
                        data=None))
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': None,
                'errors': exc.errors,
                'response_data': exc.response_data,
            })
        raise
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        rollbar.report_exc_info(
            extra_data={'token': token, 'message': message, 'extra': None})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def createitem(request):
    category=Category.objects.get(id=request.data["category"])
    data = {"quick":"silver"}
    serializer = ItemSerializer(data=request.data)
    if serializer.is_valid():
        item = serializer.save(vendor=request.user,category=category)
        data["message"] = "Item was created successfully"
        data["title"] = item.title
        data["price"] = item.price
        data["category"]=item.category.title
        return Response(data,status=status.HTTP_201_CREATED)


    else:
        data = serializer.errors

        return Response(data,status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def updateitem(request,id):
    item=Item.objects.get(id=id,vendor=request.user)
    data = {"quick":"silver"}
    serializer = ItemSerializer(instance=item,data=request.data)
    if serializer.is_valid():
        item = serializer.save()
        data["message"] = "Item was updated successfully"
        data["title"] = item.title
        data["price"] = item.price
        data["category"]=item.category.title
        return Response(data,status=status.HTTP_201_CREATED)


    else:
        data = serializer.errors

        return Response(data,status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def itemdetail(request,id):
    item=Item.objects.get(id=id)
    data = {"quick":"silver"}
    serializer = ItemSerializer(item,many=False,context={"request": request})

    print(serializer.data)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def search(request):
    item=Item.objects.filter(title__contains=request.data['search']).order_by('vendor__location')
    data = {"quick":"silver"}
    serializer = ItemSerializer(item,many=True)


    return Response(serializer.data,status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def search_by_vendor(request):
    print(request.data['search'])
    user=User.objects.filter(vendor_name__contains=request.data['search'])
    data = {"quick":"silver"}
    serializer=registrationserializer(user, many=True, context={"request": request})

    return Response(serializer.data,status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def search_university(request):
    item=Item.objects.filter(vendor__university=request.user.university,title__contains=request.data['search'])
    data = {"quick":"silver"}
    serializer = ItemSerializer(item,many=True)


    return Response(serializer.data,status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def item_delete(request,id):
    item=Item.objects.get(id=id)
    data = {"message":"ITEM HAS BEEN DELETED"}

    item.delete()

    return Response(data,status=status.HTTP_200_OK)


#NOT YET TESTED
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def view_vendor(request,id):
    item=Item.objects.get(id=id)
    print(item.vendor.vendor_name)
    user=User.objects.get(vendor_name=item.vendor.vendor_name)

    serializer =registrationserializer(user,many=False)


    return Response(serializer.data,status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def category_list(request):
    data={}
    data["sub"]="mehn"
    name=request.data["name"]
    for n in name:
        print(n)
    return Response(data)



@api_view(["GET"])
@permission_classes([AllowAny])
def location_list(request):
    locations=Location.objects.all()
    serializer=LocationSerializer(locations,many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def fullItemlist(request):
    if request.user.university is None :
        data={"message":"you are not in any uni"}
        return Response(data)

    else:
        paginator = PageNumberPagination()
        paginator.page_size = 10
        Home = namedtuple('Home', ('categories', 'items'))

        home=Home(
        categories=Category.objects.all(),
        items=paginator.paginate_queryset(Item.objects.filter(vendor__university=request.user.university).exclude(vendor=request.user), request))

        serializer=HomeSerializer(home)

        return paginator.get_paginated_response(serializer.data)


#NOT YET TESTED
@api_view(["Get"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def marketplace_fullItemlist(request):
    arr=[]
    users=User.objects.filter(location=request.user.location).exclude(fullname=request.user.fullname)
    for user in users:
        if user.vendor_name:
            section={"title":user.vendor_name}
            data= Item.objects.filter(vendor__vendor_name=user.vendor_name,vendor__location=request.user.location).exclude(vendor=request.user)[:4]
            serializer=ItemSerializer(data,many=True,context={"request": request})
            section["data"]=serializer.data
            arr.append(section)
    print(arr)
    return Response(json.dumps(arr))


#NOT TESTED YET
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def marketplace_Itemlist(request,id):

    paginator = PageNumberPagination()
    paginator.page_size = 10

    items=paginator.paginate_queryset(Item.objects.filter(vendor__location=request.user.location,category__id=id).exclude(vendor=request.user), request)



#NOT TESTED
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def marketplace_otherlocations(request):
    arr=[]
    users=User.objects.all().exclude(location=request.user.location)
    for user in users:
        if user.vendor_name:
            section={"title":user.vendor_name}
            data= Item.objects.filter(vendor__vendor_name=user.vendor_name)[:4]
            serializer=ItemSerializer(data,many=True,context={"request": request})
            section["data"]=serializer.data
            arr.append(section)
    print(arr)
    return Response(json.dumps(arr))

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def vendorList(request):
    arr=[]

    section={"title":"Latest vendors" }
    latestVendorsData= User.objects.filter(vendor_name__gte=4)[:7]
    latestVendorSerializer=registrationserializer(latestVendorsData,many=True,context={"request": request})
    section["data"]=latestVendorSerializer.data
    arr.append(section)

    section = {"title": "Vendors near you"}
    VendorsNear = User.objects.filter(vendor_name__gte=4,location=request.user.location)[:7]
    VendorsNearSerializer = registrationserializer(VendorsNear, many=True, context={"request": request})
    section["data"] = VendorsNearSerializer.data
    arr.append(section)

    section = {"title": "Vendors around you"}
    VendorsAround = User.objects.filter(vendor_name__gte=3).exclude(location=request.user.location)[:7]
    VendorsAroundSerializer = registrationserializer(VendorsAround, many=True, context={"request": request})
    section["data"] = VendorsAroundSerializer.data
    arr.append(section)

    print(arr)
    return Response(json.dumps(arr))

#this is the list of vendors based om the locations
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def ListOfVenodrs(request):
    paginator = PageNumberPagination()
    paginator.page_size = 3
    if request.data.get("location")=="same":
        vendors=paginator.paginate_queryset(User.objects.filter(vendor_name__gte=2,location=request.user.location),request)
    if request.data.get("location") == "around":
        vendors=paginator.paginate_queryset(User.objects.filter(vendor_name__gte=2).exclude(location=request.user.location),request)
    if request.data.get("location") == "any":
        vendors = paginator.paginate_queryset(User.objects.filter(vendor_name__gte=2), request)

    serializer=registrationserializer(vendors,many=True)
    return paginator.get_paginated_response(serializer.data)

#NOT TESTED
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def marketplace_otherlocations_category(request,id):

    paginator = PageNumberPagination()
    paginator.page_size = 3

    items=paginator.paginate_queryset(Item.objects.filter(category__id=id).order_by('vendor__location'), request)

    serializer=ItemSerializer(items,many=True)

    return paginator.get_paginated_response(serializer.data)#NOT TESTED YET



@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def vendorItemList(request):

    paginator = PageNumberPagination()
    paginator.page_size = 3
    items=paginator.paginate_queryset(Item.objects.filter(vendor=request.user),request)
    serializer=ItemSerializer(items,many=True)

    return  paginator.get_paginated_response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def vendorItemListId(request,name):
    user=User.objects.get(vendor_name=name)
    items=Item.objects.filter(vendor=user)
    serializer=ItemSerializer(items,many=True,context={"request": request})

    return Response(serializer.data)


class Itemlist(ListAPIView):
    serializer_class=ItemSerializer
    authentication_classes=([TokenAuthentication])
    permission_classes=([IsAuthenticated])

    def get_queryset(self):
        item=Item.objects.filter(category_id=self.request.resolver_match.kwargs['pk'],vendor__university=self.request.user.university).exclude(vendor=self.request.user)
        return item



@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def add_to_cart(request,id):
    data={}
    item=get_object_or_404(Item, id=id)
    print(item.vendor.vendor_name)
    user=User.objects.get(vendor_name=item.vendor.vendor_name)
    print(user.email)
    order_item,created=OrderItem.objects.get_or_create(item=item,vendor=user,is_removed=False,user=request.user,is_ordered=False )
    print ("ok")
    
    if user.pushToken:
        message="your {} has been added to someones cart".format(item.title)
        send_push_message(user.pushToken,message)
    
    order_qs=Order.objects.filter(user=request.user,is_ordered=False,is_delivered=False)
    print ("ok")
    if order_qs:
        order=order_qs[0]
        if order.items.filter(item__id=item.id):
            order_item.quantity+=1
            order_item.save()
            data["message"]="ITEM HAS BEEN INCREASED"

        else:
            order.items.add(order_item)
            data["message"] = "ITEM HAS BEEN ADDED TO CART"

    else:
        order=Order.objects.create(user=request.user)
        order.items.add(order_item)

    return Response(data)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def minus_from_cart(request,id):
    data={}
    item=get_object_or_404(Item, id=id)
    print(item.vendor.vendor_name)
    user=User.objects.get(vendor_name=item.vendor.vendor_name)
    print(user.email)
    order_item,created=OrderItem.objects.get_or_create(item=item,vendor=user,is_removed=False,user=request.user,is_ordered=False )
    print ("ok")

    order_qs=Order.objects.filter(user=request.user,is_ordered=False,is_delivered=False)
    print ("ok")
    if order_qs:
        order=order_qs[0]
        if order.items.filter(item__id=item.id):
            order_item.quantity-=1
            order_item.save()
            data["message"]="ITEM HAS BEEN decreased"

        else:
            data["message"] = "ORDER DOESN'T HAVE THE ITEM"


    else:
        data["message"] = "USER DOES NOT HAVE AN ORDER"

    return Response(data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def remove_from_cart(request,id):
    data = {}
    item = get_object_or_404(Item, id=id)
    user=User.objects.get(vendor_name=item.vendor.vendor_name)


    order_qs = Order.objects.filter(user=request.user, is_ordered=False,is_delivered=False)
    print("ok")
    if order_qs:
        order = order_qs[0]
        if order.items.filter(item__id=item.id):
            order_item = OrderItem.objects.filter (item=item, vendor=user, user=request.user,
                                                                  is_ordered=False,is_removed=False)[0]
            order_item.is_removed=True
            order_item.save()
            order.items.remove(order_item)
            data["message"] = "ITEM HAS BEEN REMOVED"
        else:

            data["message"] = "ORDER DOESN'T HAVE THE ITEM"
    else:
        data["message"] = "USER DOES NOT HAVE AN ORDER"

    return Response(data)

#for removing items in a cart that have already been ordered
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def delete_from_cart(request,id):
    data = {}
    order_item=OrderItem.objects.get(id=id,user=request.user)
    order_item.delete()
    data["message"] = "Item has been deleted"
    return Response(data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def order_summary(request):
    try:
        order=Order.objects.get(user=request.user,is_ordered=False,)
        if order:
            order.set_orderitem_total()
            for item in order.items.all():
                print(item.total_price)
            #print(bok.author.all())
            serializer=OrderSerializer(order,many=False,context={"request": request})
            return Response(serializer.data)

    except Order.DoesNotExist:
        data={}
        data["message"]="user does not have an order"
        return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def ordered_items(request):
    paginator = PageNumberPagination()
    paginator.page_size = 10
    order=paginator.paginate_queryset(OrderItem.objects.filter(vendor=request.user,is_ordered=True,is_removed=False),request)
    #print(bok.author.all())
    serializer=OrderItemSerializer(order,many=True)
    return  paginator.get_paginated_response (serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def pending_items(request):
    order=OrderItem.objects.filter(user=request.user,is_ordered=True,is_accepted=False,is_delivered=False,is_removed=False)
    serializer=OrderItemSerializer(order,many=True,context={"request": request})
    return  Response (serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def accepted_items(request):
    order=OrderItem.objects.filter(user=request.user,is_ordered=True,is_accepted=True,is_delivered=False,is_removed=False)
    serializer=OrderItemSerializer(order,many=True,context={"request": request})
    return  Response (serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def accept_item(request,id):
    order=OrderItem.objects.get(id=id)
    order.is_accepted=True
    order.save()
    serializer=OrderItemSerializer(order,many=False,context={"request": request})
    return  Response (serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def order_price(request):
    data={}
    order=Order.objects.get(user=request.user,is_ordered=False)
    #print(bok.author.all())
    data["TOTAL PRICE"]=order.get_total()
    return Response(data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def orderItem_price(request):
    data={}
    order=OrderItem.objects.get(user=request.user,is_ordered=False)
    #print(bok.author.all())
    data["TOTAL PRICE"]=order.get_total_item_price()
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def checkout(request):
    data={}
    print(request.data.get("delivery_add"))


    if request.data.get("delivery_add")== 'profile address':
        print(request.user.address)
        order=Order.objects.get(user=request.user,is_ordered=False)
        order.delivery_location=request.user.address
        order.save()
    else:
        order=Order.objects.get(user=request.user,is_ordered=False)
        order.delivery_location=request.data.get("delivery_add")
        order.save()

    for orderitems in order.items.all():
        orderitems.delivery_location=order.delivery_location
        orderitems.is_ordered=True
        orderitems.save()

    order.is_ordered=True
    order.save()
#    data["DELIVERY LOCATION"]=order.delivery_location
    return Response(data)



#IS_ORDERED MUST BE CHANGED TO TRUE BCUZ ONLY AN ORDER THAT HAS BEEN ORDERED CAN BE PAID FOR
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def initiate_payment(request,id):
    data={}
    SECRET_KEY="sk_test_7731c88b0b5e13e70f73211704179bd06f354efe"
    payment=Payment(amount=500,email="rcabiodun@gmail.com",user=request.user)
    payment.save()
    order_item=OrderItem.objects.get(id=id,user=request.user)

    order_item.ref=payment.ref
    order_item.save()
    payment.amount=order_item.total_price
    payment.save()
    base_url='https://api.paystack.co'
    path='/transaction/initialize/'
    headers= {
        "Authorization" : 'Bearer sk_test_7731c88b0b5e13e70f73211704179bd06f354efe',
        'Content-Type': 'application/json'
    }
    body={"email":payment.email,"amount":payment.amount_value(),"reference":payment.ref,"callback_url":"https://eathub-cli.herokuapp.com/vendor/verify_payment"}
    url=base_url + path
    response=requests.post(url,headers=headers,json=body)
    print(response.json())
    checkout=(response.json())
    data["message"]="PAYMENT CREATED"
    return Response(checkout['data'])

def verify_payment(request):
    print(request.GET.get('reference'))
    order_item=OrderItem.objects.get(ref=request.GET.get('reference'))
    payment=Payment.objects.get(ref=request.GET.get('reference'))
    verified=payment.verify_payment()
    if verified:
        print("PAYMENT WAS SUCCESSFUL")
        order_item.is_delivered=True
        order_item.save()
        vendor=User.objects.get(id=order_item.vendor.id)
        vendor.wallet+=order_item.total_price
        vendor.save()
    else:
        print("PAYMENT WAS NOT SUCCESSFUL")

    context={"order":order_item}
    return render(request,'vendor/payment_confirmation.html',context)


