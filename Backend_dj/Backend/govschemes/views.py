from rest_framework import generics
from .models import GovernmentScheme
from .serializers import GovernmentSchemeSerializer

class GovernmentSchemeListCreateAPIView(generics.ListCreateAPIView):
    queryset = GovernmentScheme.objects.all()
    serializer_class = GovernmentSchemeSerializer

class GovernmentSchemeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GovernmentScheme.objects.all()
    serializer_class = GovernmentSchemeSerializer
