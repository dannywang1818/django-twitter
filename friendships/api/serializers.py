from accounts.api.serializers import UserSerializerForFriendship
from accounts.services import UserService
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from friendships.services import FriendshipService


class BaseFriendshipSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    has_followed = serializers.SerializerMethodField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def get_user_id(self, obj):
        raise NotImplementedError

    @property
    def _get_following_user_id_set(self):
        if self.context['request'].user.is_anonymous:
            return {}
        if hasattr(self, '_cached_following_user_id_set'):
            return self._cached_following_user_id_set
        user_id_set = FriendshipService.get_following_user_id_set(
            self.context['request'].user.id,
        )
        setattr(self, '_cached_following_user_id_set', user_id_set)
        return user_id_set

    def get_has_followed(self, obj):
        return self.get_user_id(obj) in self._get_following_user_id_set

    def get_user(self, obj):
        user = UserService.get_user_by_id(self.get_user_id(obj))
        return UserSerializerForFriendship(user).data

    def get_created_at(self, obj):
        return obj.created_at


class FollowerSerializer(BaseFriendshipSerializer):
    def get_user_id(self, obj):
        return obj.from_user_id


class FollowingSerializer(BaseFriendshipSerializer):
    def get_user_id(self, obj):
        return obj.to_user_id


class FriendshipSerializerForCreate(serializers.Serializer):

    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    def validate(self, data):
        if data['from_user_id'] == data['to_user_id']:
            raise ValidationError({
                'message': 'from_user_id and to_user_id should be different'
            })
        return data

    def create(self, validated_data):
        from_user_id = validated_data['from_user_id']
        to_user_id = validated_data['to_user_id']
        return FriendshipService.follow(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
        )

    def update(self, instance, validated_data):
        pass