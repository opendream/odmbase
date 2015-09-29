from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS, ALL
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField

from .models import Comment
from odmbase.account.api import AutoAssignCreatedByMixinResource, UserReferenceResource
from odmbase.common.api import CommonModelResource, CommonApiKeyAuthentication, CommonResource


from odmbase.api import GENERIC_RESOURCES

class CommentResource(CommonModelResource, AutoAssignCreatedByMixinResource):

    CREATED_BY_FIELD = 'src'
    created_by = fields.ForeignKey(UserReferenceResource, CREATED_BY_FIELD, use_in='detail') #delete parent field
    src = fields.ForeignKey(UserReferenceResource, CREATED_BY_FIELD, full=True, readonly=True)
    dst = fields.ForeignKey(CommonResource, 'dst')

    get_dst = GenericForeignKeyField(GENERIC_RESOURCES, 'get_dst', readonly=True, full=True)

    class Meta:
        queryset = Comment.objects.all()
        resource_name = 'comment'
        authentication = CommonApiKeyAuthentication()
        filtering = {
            'dst': ALL_WITH_RELATIONS,
            'id': ALL
        }
        ordering = ['id']
