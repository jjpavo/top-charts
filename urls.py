from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chart', views.chart, name='chart'),
]
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
