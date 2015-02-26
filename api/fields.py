from tastypie.fields import DictField
 
from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.helpers import ThumbnailError
 
 
class SorlThumbnailField(DictField):
    """
    api field used to return a thumbnail generated with
    sorl-thumbnail python library
    """
    help_text = """
        A dictionary with thumbnail info. Ex: {'url': /media/cache/ba/29/ba29...34939f8f2acd38e8e73.jpg, 'width': 100, 'height': 100}
    """
 
    def __init__(self, **kwargs):
        kwargs['readonly'] = True
        self.thumb_options = kwargs.pop('thumb_options', {})
        super(SorlThumbnailField, self).__init__(**kwargs)
 
    def convert(self, value):
        if value is None or not hasattr(value, 'url'):
            return None


        try:
            options = self.thumb_options.copy()
            geometry = options.pop('geometry', '200x200')
            thumbnail = get_thumbnail(value, geometry, **options)

            dict_thumbnail = dict(
                url = thumbnail.url,
                width = thumbnail.width,
                height = thumbnail.height,
                style={True: 'portrait', False: 'landscape'}[thumbnail.is_portrait()]
            )
        except ThumbnailError:
            dict_thumbnail = None
        return dict_thumbnail