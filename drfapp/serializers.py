from rest_framework import serializers

from regapp.models import MyUser, SubscriptionModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('username', 'first_name', 'short_bio', 'email', 'profile_description', 'picture', 'featured_image',
                  'featured_video', 'mobile', 'club_2_reward', 'club_3_reward', 'club_4_reward', 'social_links',
                  'is_creator', 'featured_text')


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionModel
        fields = ('subscription_id', 'plan', 'subscriber', 'creator', 'status', 'amount', 'paid_count', 'created_at')
