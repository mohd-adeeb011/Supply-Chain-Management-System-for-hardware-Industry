from .models import Userprofile

def user_profile(request):
    if request.user.is_authenticated:
        try:
            profile = Userprofile.objects.get(user=request.user)
        except Userprofile.DoesNotExist:
            profile = None
    else:
        profile = None
    return {'user_profile': profile}