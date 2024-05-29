# from django.shortcuts import render, redirect
# from django.contrib.auth.forms import UserCreationForm
# from .models import Userprofile
# from .forms import UserProfileForm

# def signup(request):
#     if request.method=='POST':
#         form = UserCreationForm(request.POST)
#         profile_form = UserProfileForm(request.POST)
#         if form.is_valid() and profile_form.is_valid():
#             user = form.save()
#             Userprofile.objects.create(user=user)
#             profile = profile_form.save(commit=False)
#             profile.user = user
#             profile.save()
#             return redirect('/log-in')
#     else:
#         form = UserCreationForm()
#         profile_form = UserProfileForm()
#     return render(request, 'userprofile/signup.html',{'form':form, 'profile_form': profile_form})

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Userprofile
from .forms import UserProfileForm

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            # Create the user profile with the form data and associate it with the user
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('/log-in')
    else:
        form = UserCreationForm()
        profile_form = UserProfileForm()
    return render(request, 'userprofile/signup.html', {'form': form, 'profile_form': profile_form})
