from django.contrib import admin
from django.urls import path, include

urlpatterns = [
   # path('admin/', admin.site.urls),
    path('', include('yandex.urls')),
    path('', include('tebot.urls')),
]
