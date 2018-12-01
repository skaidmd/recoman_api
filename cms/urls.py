from django.urls import path
from cms import views


app_name = 'cms'
urlpatterns = [

    path('recoman_top/', views.recoman_top, name='recoman_top'),   # top
    path('recoman_top/search', views.recoman_search, name='recoman_search'),  # search
    path('recoman_top/searchresult', views.recoman_searchresult, name='recoman_searchresult'),  # searchresult
    path('recoman_top/history', views.recoman_history, name='recoman_history'),  # history
]