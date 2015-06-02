
from django.contrib.auth import get_user_model
from django.utils import timezone
from haystack import indexes
from haystack.fields import CharField
from odmbase.search.search_indexes import CommonSearchIndex

class UserIndex(CommonSearchIndex, indexes.Indexable):

    class Meta:
        model = get_user_model()
        excludes = ['password']

