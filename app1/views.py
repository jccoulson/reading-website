from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from app1.forms import JoinForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from personalization.models import PersonalInfo
from app1.models import Activity
from books.models import BookReview
from personalization.models import FavoriteBooks

def about(request):
    return render(request, 'app1/about.html')

@login_required(login_url='/login/')
def home(request):
    current_profile = ""
    activity = Activity.objects.all()
    activity_profile_pic = []

    #display activities ordered by when object was created
    for act in Activity.objects.all()[:5]: #show most recent 5 activities
        temp_profile = PersonalInfo.objects.get(user = act.user)
        activity_profile_pic.append(temp_profile.personal_image)

    #needs to be zipepd togethor to go through two lists at once in template
    activity = zip(activity, activity_profile_pic)

    #create a default profile on homepage if user has no profile
    if PersonalInfo.objects.filter(user= request.user):
        current_profile = PersonalInfo.objects.get(user = request.user)
    else:
        PersonalInfo(user=request.user).save()
        current_profile = PersonalInfo.objects.get(user=request.user)

    context = {
        "current_profile": current_profile,
        "activity": activity,
    }
    return render(request, "app1/home.html", context)

def join(request):
    if (request.method == "POST"):
        join_form = JoinForm(request.POST)
        if (join_form.is_valid()):
            # Save form data to DB
            user = join_form.save()
            # Encrypt the password
            user.set_password(user.password)
            # Save encrypted password to DB
            user.save()
            # Success! Redirect to home page.
            return redirect("/")
        else:
            # Form invalid, print errors to console
            page_data = { "join_form": join_form }
            return render(request, 'app1/join.html', page_data)
    else:
        join_form = JoinForm()
        page_data = { "join_form": join_form }
        return render(request, 'app1/join.html', page_data)

def user_login(request):
    if (request.method == 'POST'):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # First get the username and password supplied
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            # Django's built-in authentication function:
            user = authenticate(username=username, password=password)
            # If we have a user
            if user:
                #Check it the account is active
                if user.is_active:
                    # Log the user in.
                    login(request,user)
                    # Send the user back to homepage
                    return redirect("/")
                else:
                    # If account is not active:
                    return HttpResponse("Your account is not active.")
            else:
                # NOTE: Commenting out below lines for demo
                # print("Someone tried to login and failed.")
                # print("They used username: {} and password: {}".format(username,password))
                return render(request, 'app1/login.html', {"login_form": LoginForm})
        else:
            return render(request, 'app1/login.html', {"login_form": LoginForm})
    else:
        #Nothing has been provided for username or password.
        return render(request, 'app1/login.html', {"login_form": LoginForm})

#@login_required(login_url='/login/')
def user_logout(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return redirect("/")
