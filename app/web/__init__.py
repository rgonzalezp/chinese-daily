# This file can be empty, but its presence signals Python to treat the directory as a sub-package. 

# Make FastHTML app objects from route modules available for main app to discover routes.
# This also allows cleaner imports in app/main.py like `from .web import routes_notes`

# Assuming each routes_*.py file defines an `app = FastHTML()` instance.

# Existing routes
from . import routes_notes
from . import routes_calendar
from . import routes_tasks

# Our new personalize route
from . import routes_personalize

# For routes_search and routes_export, these will still cause an error
# if the files app/web/routes_search.py and app/web/routes_export.py do not exist.
# We will address this based on user's choice.
# from . import routes_search
# from . import routes_export

__all__ = [
    'routes_notes',
    'routes_calendar',
    'routes_tasks',
    'routes_personalize',
    # 'routes_search', # Add if file exists and is imported
    # 'routes_export', # Add if file exists and is imported
] 