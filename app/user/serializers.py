from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the users object
    """

    class Meta:
        # this line grabs the user model
        model = get_user_model()
        # this is required. We are making a list that states that I require these fields
        fields = ('email', 'password', 'name')
        # For the password, we have a variable kwards, stands for keyword arguements. This states that the password has some validation and restrictions in this case its the password.
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """
        Create a new user with encrypted password and return it
        """
        # we made this function, now we just call it with the data we've already validated.
        return get_user_model().objects.create_user(**validated_data)

class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for the user authentication object
    """
    # we are stating that email is a charfield
    email = serializers.CharField()
    # we are stating that the password should a charfield. trim whitepaces is for normal blank spaces. This is for human errors
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """
        Validate and authenticate the user
        """
        # attrs will get all the parameters passed from the serializer above. In this case we have both an email and pass
        email = attrs.get('email')
        password = attrs.get('password')

        # now we use the authenticate function.
        user = authenticate(
            # We need to get the data from the request we made. 
            request=self.context.get('request'),
            username=email,
            password=password
        )
        # if the authentication fails, our user becomes null. This function handles that.
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user

        return attrs