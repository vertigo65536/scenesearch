from rest_framework import serializers
from .models import Quote
class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = ['quote_id', 'episode_id', 'quote_index', 'quote_text', 'quote_start', 'quote_end', 'quote_thumb_path']
