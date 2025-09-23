from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from .serializers import PredictRequestSerializer, PredictResponseSerializer
from .ml import predict_price


@method_decorator(csrf_exempt, name="dispatch")
class PredictView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PredictRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            predicted = predict_price(serializer.validated_data)
            response = PredictResponseSerializer({"predicted_price": predicted})
            return Response(response.data)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class PredictPageView(TemplateView):
    template_name = "prices/predict.html"

# Create your views here.
