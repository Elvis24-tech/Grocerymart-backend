from django.urls import path
from . import views

urlpatterns = [
    path('stkpush/', views.stk_push, name='stk_push'),
]