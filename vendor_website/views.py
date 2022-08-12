from django.shortcuts import render
from rest_framework.authtoken.models import Token
# Create your views here.
from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.mail import send_mail

from django.contrib.auth import login,logout

from core.models import Location,User
from django.contrib.auth.hashers import check_password

#=========================api stuff==========================


#================MAIN CODE=================================


#=====================================================

def signout(request):
    logout(request)
    return redirect('index')

#=====================================================

def signin(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        email, password = request.POST['email'], request.POST['password']
        
        if email == "" or password == "":
            messages.error(request, "Please complete all fields!")
            return redirect("login")
        try:
            account=  User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "invalid email address")
            return redirect(signin)
        if account:
            token=Token.objects.get_or_create(user=account)[0].key
            if check_password(password,account.password):

                login(request,account)
                return redirect ("index")


        
    
    return render(request, "login.html")


#=====================================================



def signup(request):
    locations=Location.objects.all()
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        full_name = request.POST['fname']
        email = request.POST['email']
        address = request.POST['b-address']
        phone = request.POST['digits']
        brand_name = request.POST['brand_name']
        location = request.POST['city']        
        password = request.POST['password']
        password2 = request.POST['confirm-password']
       
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "User already exists!")
                return redirect("signup")
            else:
                user=User(email=email,fullname=full_name,location=location,
                address=address,vendor_name=brand_name,phone_number=phone,social_links=request.POST['social_links'])
                user.set_password(password)
                user.save()
                send_mail(
                    "Ongoing Registration",
                    "Hey {}, we will contact you shortly after your details have been fully processeed ".format(user.vendor_name),
                    'Eathub',
                    [str(user.email)],
                )
                token = Token.objects.get_or_create(user=user)[0].key
                return redirect("login")
        else:
            messages.error(request, "Passwords do not match!")
            return redirect("signup")
    
    return render(request, "signup.html",{"locations":locations})


#=======================================================

def index(request):
    '''
    if request.user.is_authenticated:
        try:
            current_user = f"{request.user.username}"
            vendor_user = Vendor.objects.get(email=current_user) 
            firstname = vendor_user.full_name.split(" ")[1]
        except Exception:
            firstname = "Vendor"
            
        context = {
            'the_user':firstname,
        }
        return render(request, "index.html", context)
    '''
    return render(request, "index.html")