
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from eis.discount.api.campaigns_api import CampaignsApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from eis.discount.api.campaigns_api import CampaignsApi
from eis.discount.api.policy_vouchers_api import PolicyVouchersApi
from eis.discount.api.vouchers_api import VouchersApi
from eis.discount.api.default_api import DefaultApi
