from rest_framework import serializers


class PredictRequestSerializer(serializers.Serializer):
    size = serializers.FloatField()
    bedrooms = serializers.IntegerField()
    bathrooms = serializers.IntegerField()
    age = serializers.FloatField()


class PredictResponseSerializer(serializers.Serializer):
    predicted_price = serializers.FloatField()
