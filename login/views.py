from django.shortcuts import render, HttpResponse, redirect

from django.contrib import messages

from .models import User, Post, Comment, Relationship, RELATIONSHIP_FOLLOWING

import bcrypt

import app1.urls

# Create your views here.

def login_register(request):
    return render(request, "login.html")

def register(request):
    if len(User.objects.filter(email=request.POST["email"])):
        messages.error(request, "User already exits")
        return redirect("/login_register?original_url="+ str(request.GET.get("original_url")))
    else:
        errors = User.objects.basic_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
        else:
            hash1 = bcrypt.hashpw(request.POST["password"].encode(), bcrypt.gensalt()).decode()
            print(hash1)
            newuser = User.objects.create(first_name=request.POST["first_name"], last_name=request.POST["last_name"], email=request.POST["email"], password=hash1)
            request.session["userid"] = newuser.id
            #messages.success(request, "User successfully registered!")
            print("redirect", request.GET["original_url"])
            return redirect(request.GET["original_url"])
    return redirect("/login_register?original_url="+ str(request.GET.get("original_url")))

def login(request):
    try:
        User.objects.get(email=request.POST["email"])
    except:
        messages.error(request,"User/password do not match.")
        return redirect("/login_register?original_url="+ str(request.GET.get("original_url")))
    email_match = User.objects.get(email=request.POST["email"]) 
    if bcrypt.checkpw(request.POST["password"].encode(), email_match.password.encode()):
        request.session["userid"] = email_match.id
        #messages.success(request, "Successfully logged in!")
        print("redirect", request.GET["original_url"])
        if request.GET["original_url"]:
            return redirect(request.GET["original_url"])
        else:
            return redirect("/")
    else:
        messages.error(request, "User/password do not match.")
        return redirect("/login_register?original_url="+ str(request.GET.get("original_url")))

def logout(request):
    request.session.clear()
    return redirect("/")