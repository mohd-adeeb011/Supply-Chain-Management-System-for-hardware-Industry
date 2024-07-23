from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import UserProfileForm

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        # Check business type to conditionally require the shop field
        if form.is_valid() and profile_form.is_valid():
            business_type = profile_form.cleaned_data.get('business_type')
            
            # If business type is 'customer', make 'shop' field optional
            if business_type == 'customer':
                profile_form.cleaned_data['shop'] = ''
                profile_form.fields['shop'].required = False
            
            # Save user and profile
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('/log-in')
        else:
            # Debugging error messages
            print("UserCreationForm errors:", form.errors)
            print("UserProfileForm errors:", profile_form.errors)
    else:
        form = UserCreationForm()
        profile_form = UserProfileForm()
        
    return render(request, 'userprofile/signup.html', {'form': form, 'profile_form': profile_form})
