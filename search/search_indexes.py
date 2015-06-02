
from django.utils import timezone

from haystack import indexes
from haystack.fields import CharField


class CommonSearchIndex(indexes.ModelSearchIndex):

    text = CharField(document=True, use_template=True, template_name='search/indexes/common_text.txt')

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(changed__lte=timezone.now())
