from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS, ALL

from .models import PrivateMessage
from odmbase.account.api import AutoAssignCreatedByMixinResource, UserReferenceResource
from odmbase.common.api import CommonModelResource, CommonApiKeyAuthentication



class MessageResource(CommonModelResource, AutoAssignCreatedByMixinResource):

    CREATED_BY_FIELD = 'src'
    created_by = fields.ForeignKey(UserReferenceResource, CREATED_BY_FIELD, use_in='detail') #delete parent field
    src = fields.ForeignKey(UserReferenceResource, CREATED_BY_FIELD, full=True, readonly=True)
    dst = fields.ForeignKey(UserReferenceResource, 'dst', full=True)

    class Meta:
        queryset = PrivateMessage.objects.all()
        resource_name = 'message'
        authentication = CommonApiKeyAuthentication()
        filtering = {
            'dst': ALL_WITH_RELATIONS,
            'src': ALL_WITH_RELATIONS,
            'id': ALL
        }
        ordering = ['id']