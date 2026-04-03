from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import FinancialRecord


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()
        return instance


class FinancialRecordSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FinancialRecord
        fields = ['id', 'user', 'amount', 'type', 'category', 'date', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
