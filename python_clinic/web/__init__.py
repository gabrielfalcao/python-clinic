# -*- coding: utf-8 -*-
from .ui.endpoints import application

from .server import api
from .api.endpoints import api_v1


__all__ = ('application', 'api', 'api_v1')
