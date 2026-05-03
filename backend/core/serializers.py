from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False, min_length=12)
    password_confirm = serializers.CharField(trim_whitespace=False)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs
