from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient

from recipe import serializers

class BaseViewSetAttr(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """
    Base viewsetfor recipe
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Return objects for the current valid user
        """
        return self.queryset.filter(user = self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """
        Creates a new object
        """
        serializer.save(user = self.request.user)



class TagViewSet(BaseViewSetAttr):
    """
    Manage tags in the database
    """
    
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

class IngredientViewSet(BaseViewSetAttr):
    """
    Manage ingredients in the database
    """

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
