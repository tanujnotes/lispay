from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from drfapp.serializers import UserSerializer
from regapp.models import MyUser


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_creators(request):
    users = MyUser.objects.all()
    serializer = UserSerializer(users, many=True)
    return JsonResponse({"users": serializer.data}, safe=False)
