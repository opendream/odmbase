from odmbase.common.api import CommonResource
from odmbase.common.models import CommonModel
from account.models import User
from account.api import UserResource

GENERIC_RESOURCES = {
    CommonModel: CommonResource,
    User: UserResource
}

try:

    from api.registers import API_RESOURCES
    for resource in API_RESOURCES:
        GENERIC_RESOURCES[resource._meta.queryset.model] = resource

except ImportError:
    pass