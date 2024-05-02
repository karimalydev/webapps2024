"""
URL configuration for webapps2024 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from register.views import register
from django.contrib.auth.views import LoginView, LogoutView
from payapp.views import transfer_money, transaction_history, request_money, accept_request, decline_request, \
    create_superadmin, admin_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(template_name='register/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('transfer-money/', transfer_money, name='transfer_money'),
    path('transaction-history/', transaction_history, name='transaction_history'),
    path('conversion/', include('currency_conversion.urls')),
    path('request-money/', request_money, name='request_money'),
    path('accept-request/<int:request_id>/', accept_request, name='accept_request'),
    path('decline-request/<int:request_id>/', decline_request, name='decline_request'),
    path("create-admin/",create_superadmin, name="create_admin"),
    path("admin-dashboard/",admin_dashboard, name="users"),

]
