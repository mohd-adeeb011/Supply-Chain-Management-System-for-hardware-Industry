from django.contrib import admin
from django.urls import path,include
from core.views import main_page, buy_product, index
from userprofile.views import signup
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core.admin_site import admin_site

admin.site.site_header = "Star Fabricator Supply Chain"

urlpatterns = [
    path('', main_page, name='main_page'),  # Pointing to main_page instead of index
    path('sign-up/', signup, name='signup'),
    path('log-in/', auth_views.LoginView.as_view(template_name="userprofile/login.html"), name='login'),
    path('log-out/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin/', admin_site.urls),
    # path('admin/', admin.site.urls),
    path('buy/<int:product_id>/', buy_product, name='buy_product'),
    path('core/', include('core.urls')),
    path('admin/', admin_site.urls),
]

if settings.DEBUG:
    from django.conf import settings
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)