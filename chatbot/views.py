from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist
import datetime
from datetime import datetime
import os
from django.conf import settings 
from django.core.mail import send_mail 
import numpy as np
from django.contrib import messages
from subprocess import check_output, CalledProcessError,STDOUT
from django.contrib.auth.models import User, auth
from django.http import HttpResponse, request
from .models import *
from .service import generate_sql
from .database import execute_sql
def home(request):
    return render(request,"home.html")

def signup(request):
    if request.method=='POST':
        first_name=request.POST.get("fname")
        last_name=request.POST.get("lname")
        email=request.POST.get("email")
        username=email
        mobno=request.POST.get("phoneno")
        department=request.POST.get("department")
        password=request.POST.get("pass")
        password1=request.POST.get("pass1")
        def password_check(password):
            SpecialSym =['$', '@', '#', '%']
            val = True
            if len(password) < 8:
                print('length should be at least 6') 
                val = False
            if len(password) > 20: 
                print('length should be not be greater than 8') 
                val = False
            if not any(char.isdigit() for char in password): 
                print('Password should have at least one numeral') 
                val = False
            if not any(char.isupper() for char in password): 
                print('Password should have at least one uppercase letter') 
                val = False
            if not any(char.islower() for char in password): 
                print('Password should have at least one lowercase letter') 
                val = False
            if not any(char in SpecialSym for char in password): 
                print('Password should have at least one of the symbols $@#') 
                val = False
            if val == False: 
                val=True
                return val
        if (password_check(password)): 
            print("y")
        else: 
            print("x")                 
        if password==password1:
            if User.objects.filter(username=username).exists():
                messages.info(request,'Username taken')
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.info(request,'email taken')
                return redirect('signup')
            elif (password_check(password)):
                messages.info(request,'password is not valid(must be combination of (A-Z,a-z,@,1-9))')
                return redirect('signup')
            else:
                user=User.objects.create_user(username=username,password=password,email=email,first_name=first_name,last_name=last_name)
                user.save()
                messages.info(request,"user created succesfully")
                user=auth.authenticate(username=username,password=password)
                if user is not None:
                   auth.login(request,user)
                u = User.objects.get(username=username)
                reg=UserProfile(user=u,usernames=username,department=department,phoneno=mobno,password=password)
                reg.save()
                auth.logout(request)
        else:
            messages.info(request,"password not matching")
            return redirect('signup')
        return redirect('login')
    return render(request,"signup.html")
def login(request):
    if request.method=="POST":
        username=request.POST.get("email")
        password=request.POST.get("pwd")
        user=auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            messages.info(request,"Login successful")
            return render(request,"home.html")
        else:
            messages.info(request,"Invalid Credentials")
            return redirect('login')
    return render(request,"login.html")
def logout(request):
    auth.logout(request)
    return render(request,"login.html")
def profile(request):
    if request.method=="POST":
        fname=request.POST.get("fname")
        lname=request.POST.get("lname")
        email=request.POST.get("email")
        username=request.POST.get("username")
        mobno=request.POST.get("phoneno")
        department=request.POST.get("department")
        User.objects.filter(username=username).update(first_name=fname,last_name=lname)
        UserProfile.objects.filter(usernames=username).update(usernames=username,phoneno=mobno,department=department)
        messages.info(request,"Profile Updated Properly")
        return render(request,"profile.html")    
    return render(request,"profile.html")

def changepassword(request):
    if request.method == 'POST':
        old=request.POST.get("old")
        new1=request.POST.get("new1")
        new2=request.POST.get("new2")
        def passwordcheck(password):
            SpecialSym =['$', '@', '#', '%'] 
            val = True
            if len(password) < 8:
                print('length should be at least 8') 
                val = False
            if len(password) > 20: 
                print('length should be not be greater than 20') 
                val = False
            if not any(char.isdigit() for char in password): 
                print('Password should have at least one numeral') 
                val = False
            if not any(char.isupper() for char in password): 
                print('Password should have at least one uppercase letter') 
                val = False
            if not any(char.islower() for char in password): 
                print('Password should have at least one lowercase letter') 
                val = False
            if not any(char in SpecialSym for char in password): 
                print('Password should have at least one of the symbols $@#') 
                val = False
            return val
        p=request.user
        u1 = UserProfile.objects.get(usernames=p.username)
        if(u1.password==old):
            if(new1==new2):
                password=new1
                if(passwordcheck(password)==True):
                    u = User.objects.get(username=p.username)
                    u.set_password(new1)
                    u.save()
                    UserProfile.objects.filter(usernames=p.username).update(password=new1)
                    messages.info(request,"password Changed succesfully.Login using new Password.")
                    return redirect('logout')
                else:
                    messages.info(request,"Password should contain(0-9,a-z,A-Z,@)")
                    return render(request,"changepassword.html")    
            else:
                messages.info(request,"Password Don't Match")
                id=3
                return render(request,"changepassword.html",{"id":id})
        else:
            messages.info(request,"Old Password is not Correct or error occured.")
            id=3
            return render(request,"changepassword.html",{"id":id})
    id=3
    return render(request,"changepassword.html",{"id":id})

def myqueries(request):
    n=ChatbotLogs.objects.filter(user=request.user)
    return render(request,"myqueries.html",{'n':n})

def addquery(request):
    p1=request.user
    sentence = ""
    sql_query = ""
    result = None
    if request.method=="POST":
        sentence=request.POST.get("query")
        sql_query = generate_sql(sentence)
        print(sentence,sql_query)
        data = execute_sql(sql_query)
        if "error" in data:
            result = data["error"]
        else:
            result = data["rows"]
        log=ChatbotLogs(user=p1,sentence=sentence,query=sql_query,ans=result,timestamp=datetime.now())
        log.save()
    return render(request, "addquery.html", {
        "query": sentence,
        "sql": sql_query,
        "result": result,
    })