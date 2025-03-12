from django.shortcuts import render, redirect
from .forms import UserForms
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required

User = get_user_model()

# Create your views here.
from django.http import HttpResponse


def login_page(request):
    '''Login function to authenticate users'''
    
    if request.user.is_authenticated:
            return redirect("home")
        
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Login Successful")
                print(f"User authenticated: {request.user.is_authenticated}")  # Debugging
                print(f"User: {request.user}")
                return redirect("home") 
            else:
                messages.error(request, "Invalid credentials")
    return render (request, "login.html", {})

def register_page(request):
    '''Register function to create new users'''
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == 'POST':
        username = request.POST.get("username") or None
        email = request.POST.get("email") or None
        password = request.POST.get("password") or None
        
        if username and email and password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
            else:
                try:
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()
                    messages.success(request, "Registration Successful")
                    login(request, user)
                    return redirect("home")
                except Exception as e:
                    print(e)
                    messages.error(request, "Registration Failed")

    return render (request, "register.html", {})

@login_required
def home_page(request):
    print(f"User authenticated: {request.user.is_authenticated}")  # Debugging
    print(f"User: {request.user}")
    return render (request, "home.html")

def logout_page(request):
    logout(request)
    messages.success(request, "Logged out successful!")
    return redirect("/login/")