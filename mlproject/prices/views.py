from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.generic import TemplateView

from .serializers import PredictRequestSerializer, PredictResponseSerializer
from .ml import predict_price


class PredictView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PredictRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        predicted = predict_price(serializer.validated_data)
        response = PredictResponseSerializer({"predicted_price": predicted})
        return Response(response.data)


class PredictPageView(TemplateView):
    template_name = "prices/predict.html"

# Create your views here.
