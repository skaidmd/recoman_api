from django.urls import path
from cms import views


app_name = 'cms'
urlpatterns = [

    path('api/analyze', views.analyze, name='analyze'),  # analyze
#    path('api/debug', views.debug, name='debug'),  # debug
]