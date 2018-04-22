# -*- coding: utf-8 -*-
from flask import request
from werkzeug.exceptions import BadRequest


class ControllerException(BadRequest):
    def __init__(self, message, status_code=400):
        super(ControllerException, self).__init__(message)
        self.status_code = status_code

    def to_dict(self):
        data = {
            'status_code': self.status_code,
            'message': str(self),
            'data': request.data
        }
        return data


class Controller(object):
    def __init__(self, application):
        self.__application__ = application
        self.__dao__ = application.dao

    @property
    def application(self):
        return self.__application__

    @property
    def dao(self):
        return self.__dao__

    @property
    def shipment_dao(self):
        return self.dao.of('shipments')

    @property
    def offer_dao(self):
        return self.dao.of('offers')
