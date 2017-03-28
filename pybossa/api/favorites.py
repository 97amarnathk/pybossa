# -*- coding: utf8 -*-
# This file is part of PYBOSSA.
#
# Copyright (C) 2017 Scifabric LTD.
#
# PYBOSSA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PYBOSSA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PYBOSSA.  If not, see <http://www.gnu.org/licenses/>.
"""
PYBOSSA api module for Favorites via an API.

This package adds GET, POST, PUT and DELETE methods for:
    * Task favorites

"""
import json
from api_base import APIBase
from pybossa.core import task_repo
from flask.ext.login import current_user
from flask import Response, abort
from werkzeug.exceptions import MethodNotAllowed
from pybossa.core import ratelimits
from pybossa.util import jsonpify
from pybossa.ratelimit import ratelimit
from pybossa.error import ErrorStatus
from pybossa.model.task import Task

error = ErrorStatus()


class FavoritesAPI(APIBase):

    """Class API for Favorites."""

    __class__ = Task

    @jsonpify
    @ratelimit(limit=ratelimits.get('LIMIT'), per=ratelimits.get('PER'))
    def get(self, oid):
        """Return all the tasks favorited by current user."""
        try:
            if current_user.is_anonymous():
                raise abort(401)
            uid = current_user.id
            tasks = task_repo.filter_tasks_by_user_favorites(uid)
            data = self._create_json_response(tasks, oid)
            return Response(data, 200,
                            mimetype='application/json')
        except Exception as e:
            return error.format_exception(
                e,
                target=self.__class__.__name__.lower(),
                action='GET')

    @jsonpify
    @ratelimit(limit=ratelimits.get('LIMIT'), per=ratelimits.get('PER'))
    def post(self, oid):
        """Add User ID to task as a favorite."""
        try:
            if current_user.is_anonymous():
                raise abort(401)
            uid = current_user.id
            task = task_repo.get_task_favorited(uid, oid)
            if task is not None:
                raise abort(415)
            task = task_repo.get_task(oid)
            if task.fav_user_ids is None:
                task.fav_user_ids = [uid]
            else:
                task.fav_user_ids.append(uid)
            task_repo.update(task)
            return Response(json.dumps(task), 200,
                            mimetype='application/json')
        except Exception as e:
            return error.format_exception(
                e,
                target=self.__class__.__name__.lower(),
                action='POST')

    @jsonpify
    @ratelimit(limit=ratelimits.get('LIMIT'), per=ratelimits.get('PER'))
    def put(self, oid):
        """Not implemented."""
        try:
            raise MethodNotAllowed
        except Exception as e:
            return error.format_exception(
                e,
                target=self.__class__.__name__.lower(),
                action='PUT')

    @jsonpify
    @ratelimit(limit=ratelimits.get('LIMIT'), per=ratelimits.get('PER'))
    def delete(self, oid):
        """Delete User ID from task as a favorite."""
        try:
            if current_user.is_anonymous():
                raise abort(401)
            uid = current_user.id
            task = task_repo.get_task_favorited(uid, oid)
            if task is not None:
                raise abort(415)
            idx = task.fav_user_ids.index(uid)
            task.fav_user_ids.pop(idx)
            task_repo.update(task)
            return Response(json.dumps(task), 200,
                            mimetype='application/json')
        except Exception as e:
            return error.format_exception(
                e,
                target=self.__class__.__name__.lower(),
                action='DEL')
