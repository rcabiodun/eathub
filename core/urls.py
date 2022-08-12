from .views import *
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
urlpatterns = [
    path('',reg,name="registration"),
    path('login/',login,name="login"),

    path('logout/',logout),
    #this is to display the user profile
    path('profile/',profile),
    path('books/',books),
    #When the user clicks on the 'i want to be a buyer' button,this url updates that user to a buyer
    #so he or she can be displayed on the buyer list
    path('update_buyer/',update_buyer,name="main"),

    #The user will no longer be a buyer and would be removed from the buyer list
    path('delete_post/', delete_post,),

    #this url takes in the id of a particular buyer gotten from the buyers list
    #NOTE THE ID IS SUBMITED WITH THE ORDER FORM
    path('create_order/<id>/',create_order),


    path('slot/',slots),

    path('name/',name),

    #for an order to be accepted by the buyer the id of that order must be submitted to this url
    path('accept_order/<id>/', order_accepted),

    path('bought_order/<id>/', order_bought),

    path('delivered_order/<id>/', order_delivered),

    #if an order is declined by the buyer the id must be submitted here so that it can be deleted
    #or when an order has been delivered to the user the id msut be submitted here so that the order
    #can be deleted from the database

    path('delete_order/<id>/',delete_order,name="delete_order"),

    path('resetpassword/',reset_password,name="reset"),

    #this is to update user profile.NOTE:THE EMAIL MUST ALWAYS BE SUBMITTED WITH THE DATA TO BE UPDATED
    path('update_user/',update_user,name="update_user"),

    #this is just the list of buyers
    path('buyer_list/',Buyer_list.as_view(),name="buyer_list"),

    #the list of orders that the buyer has already accepted
    path('buyer_order_list/',Buyer_order_list.as_view(),name="order_list"),

    #list of orders yet to be acepted by the buyer
    path('incoming_order_list/',Incoming_order_list.as_view()),

    #this is where a customer can see his or her orders that has been accepted buy the buyer
    path('customer_order_list/',customer_order_list.as_view(),name="order_list"),
]

#NOTE:ONCE AN ORDER IS DELIVERED,IT MUST BE DELETED FROM THE DATABASE
#P.S USE THE DELETE URL