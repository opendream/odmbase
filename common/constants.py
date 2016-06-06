# -*- encoding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

''' Todo serve status scope to javascript
def scope_status():
    # Common status
    STATUS_PUBLISHED = 1
    STATUS_PENDING = -1
    STATUS_DRAFT = 0
    STATUS_DELETED = -2

    # Cart status
    STATUS_CANCELLED = -3   # ยกเลิกการซื้อ (โดยใครก็ได้)
    STATUS_PAYING    = -5   # กำลังจ่ายเงิน
    STATUS_PAID      =  2   # จ่ายแล้ว
    STATUS_DELIVERED =  3   # ผู้ซื้อได้รับสินค้าแล้ว
    STATUS_SETTLED   =  4   # ปิดรายการขาย
    STATUS_COMPLETED =  5   # รายการขายสมบูรณ์

    # Product
    OLD_STATUS_SOLD = -4
    STATUS_SOLD = 6

    return locals()

STATUS_MAP = scope_status()

for key, value in STATUS_MAP.iteritems():
    exec('%s = %s' % (key, value))
'''
# Common status
STATUS_PUBLISHED = 1
STATUS_PENDING = -1
STATUS_DRAFT = 0
STATUS_DELETED = -2

# Cart status
STATUS_CANCELLED = -3   # ยกเลิกการซื้อ (โดยใครก็ได้)
STATUS_PAYING    = -5   # กำลังจ่ายเงิน
STATUS_PAID      =  2   # จ่ายแล้ว
STATUS_DELIVERED =  3   # ผู้ซื้อได้รับสินค้าแล้ว
STATUS_SETTLED   =  4   # ปิดรายการขาย
STATUS_COMPLETED =  5   # รายการขายสมบูรณ์

# Product
OLD_STATUS_SOLD = -4
STATUS_SOLD = 6

STATUS_CHOICES = (
    (STATUS_PUBLISHED, _('Published')),
    (STATUS_PENDING, _('Request for Approval')),
    (STATUS_DRAFT, _('Draft')),
    (STATUS_DELETED, _('Deleted')),
    (STATUS_CANCELLED, _('Cancelled')),
    (STATUS_PAYING, _('Paying')),
    (STATUS_PAID, _('Authorized')),
    (STATUS_DELIVERED, _('Delivered')),
    (STATUS_SOLD, _('Sold')),
    (OLD_STATUS_SOLD, _('Old Sold')),
    (STATUS_SETTLED, _('Settled')),
    (STATUS_COMPLETED, _('Completed')),
)

NO_IP = '127.0.0.1'

SHORT_UUID_ALPHABETS = '23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

SUMMARY_MAX_LENGTH = 80

# Constance for python
ENABLE_SHARING_ECONOMY = False
VALUE_SHARING_ECONOMY = 100;
ENABLE_INVITE_METHOD = False;
