"""
URL configuration for InterfaceAutoTest project.

The `urlpatterns` list routes URLs to server. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function server
    1. Add an import:  from my_app import server
    2. Add a URL to urlpatterns:  path('', server.home, name='home')
Class-based server
    1. Add an import:  from other_app.server import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('interfacetestplatform.urls')),  # 指向interfacetestplatform应用的urls.py
]
