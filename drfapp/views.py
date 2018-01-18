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


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_user(request):
    username = request.GET.get('username', '')
    users = MyUser.objects.get(username=username)
    serializer = UserSerializer(users, many=False)
    return JsonResponse(serializer.data, safe=False)
