# -*- coding: utf-8 -*-

import re
import falcon

from sqlalchemy.orm.exc import NoResultFound
from cerberus import Validator
from cerberus.errors import ValidationError

from app import log
from app.api.common import BaseResource
from app.utils.hooks import auth_required
from app.utils.auth import encrypt_token, hash_password, verify_password, uuid
from app.model import User
from app.errors import (
    AppError,
    InvalidParameterError,
    UserNotExistsError,
    PasswordNotMatch,
)

LOG = log.get_logger()

class Hello(BaseResource):
    def on_get(self, req, res):   
    	self.on_success(res, ['hello'])

