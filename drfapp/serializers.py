from rest_framework import serializers

from regapp.models import MyUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('username', 'full_name', 'short_bio', 'email', 'profile_description', 'picture', 'featured_image',
                  'mobile', 'club_2_reward', 'club_3_reward', 'club_4_reward', 'social_links', 'is_creator')
