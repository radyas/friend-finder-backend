from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from users.models import User, Roles
from users.serializers import UserSerializer, ProfileUpdateSerializer, UserResetPasswordSerializer, \
    AuthRegisterSerializer, LoginSerializer, UserMatchingSerializer


class AuthViewSet(ViewSet):
    permission_classes = []

    @action(methods=['post'], detail=False)
    def register(self, request):
        serializer = AuthRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False, url_path='reset-password')
    def reset_password(self, request):
        serializer = UserResetPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.user
            user.set_password(serializer.validated_data.get('new_password'))
            user.save()
            return Response()

    @action(methods=['post'], detail=False)
    def token(self, request):
        serializer = LoginSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'me' and self.request.method in ['put', 'patch']:
            return ProfileUpdateSerializer
        elif self.action == 'matched':
            return UserMatchingSerializer
        else:
            return UserSerializer

    def get_permissions(self):
        if self.action in ['me', 'matched']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]

        return [permission() for permission in permission_classes]

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    def filter_queryset(self, queryset):
        return queryset.filter(Q(is_active=True) & ~Q(role=Roles.SUPER_ADMIN))

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        if request.method == 'get':
            serializer = self.get_serializer()
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(data=request.data, instance=request.user, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def matched(self, request):
        data = []
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)

