import os

from .base import *

if os.environ.get("ENV_NAME") == 'Production':
    from .production import *
    REST_FRAMEWORK['EXCEPTION_HANDLER'] = 'common.utils.exception_util.exception_handler'
elif os.environ.get("ENV_NAME") == 'Staging':
    from .staging import *

    # REST_FRAMEWORK['EXCEPTION_HANDLER'] = 'common.utils.exception_util.exception_handler'
else:
    from .local import *
