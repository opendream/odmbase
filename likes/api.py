
from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS, ALL
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField

from goals.api import CommonGoalResource
from goals.models import CommonGoal
from odmbase.account.api import AutoAssignCreatedByMixinResource, UserReferenceResource
from odmbase.common.api import CommonModelResource, CommonApiKeyAuthentication, CommonResource
from odmbase.common.models import CommonModel
from odmbase.likes.models import Like
from updates.api import UpdateResource
from updates.models import Update



class LikeResource(CommonModelResource, AutoAssignCreatedByMixinResource):
    CREATED_BY_FIELD = 'src'
    created_by = fields.ForeignKey(UserReferenceResource, CREATED_BY_FIELD, use_in='detail') #delete parent field
    src = fields.ForeignKey(UserReferenceResource, CREATED_BY_FIELD, full=True, readonly=True)
    dst = fields.ForeignKey(CommonResource, 'dst')

    get_dst = GenericForeignKeyField({
        CommonModel: CommonModelResource,
        CommonGoal: CommonGoalResource,
        Update: UpdateResource
        # Inspiration: InspirationResource # IN THE FUTURE
    }, 'get_dst', readonly=True, full=True)

    class Meta:
        queryset = Like.objects.all()
        resource_name = 'like'
        authentication = CommonApiKeyAuthentication()
        limit = 2
        filtering = {
            'dst': ALL_WITH_RELATIONS,
            'id': ALL
        }
        ordering = ['id']