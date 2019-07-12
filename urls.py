from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chart', views.chart, name='chart'),
    path('config', views.config, name='config'),
    path('image', views.image, name='image'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
