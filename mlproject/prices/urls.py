from django.urls import path
from .views import PredictView, PredictPageView

urlpatterns = [
    path('predict/', PredictView.as_view(), name='predict'),
    path('', PredictPageView.as_view(), name='predict_page'),
]
