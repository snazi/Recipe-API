from rest_framework import serializers

from core.models import Tag

class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for tag objects
    """

    class Meta:
        model = Tag
        fields = ('id', 'name')
        # we want ID to be read only. We should dictate what ID gets assigned where.
        read_only_fields = ('id',)