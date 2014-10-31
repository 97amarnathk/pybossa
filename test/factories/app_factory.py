# -*- coding: utf8 -*-
# This file is part of PyBossa.
#
# Copyright (C) 2013 SF Isle of Man Limited
#
# PyBossa is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyBossa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyBossa.  If not, see <http://www.gnu.org/licenses/>.

from pybossa.core import db
from pybossa.model.app import App
from . import BaseFactory, factory
from helper.repositories import memo_project_repo
from pybossa.repositories import ProjectRepository

project_repo = ProjectRepository(db)

class AppFactory(BaseFactory):
    class Meta:
        model = App

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        project = model_class(*args, **kwargs)
        project_repo.save(project)
        return project

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: u'My Project number %d' % n)
    short_name = factory.Sequence(lambda n: u'app%d' % n)
    description = u'Project description'
    allow_anonymous_contributors = True
    long_tasks = 0
    hidden = 0
    featured = False
    owner = factory.SubFactory('factories.UserFactory')
    owner_id = factory.LazyAttribute(lambda app: app.owner.id)
    category = factory.SubFactory('factories.CategoryFactory')
    category_id = factory.LazyAttribute(lambda app: app.category.id)
    info = {'task_presenter': '<div></div>'}


class AppFactoryMemory(AppFactory):

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        project = model_class(*args, **kwargs)
        memo_project_repo.save(project)
        return project

    owner = factory.SubFactory('factories.UserFactoryMemory')
    owner_id = factory.LazyAttribute(lambda app: app.owner.id)
    category = factory.SubFactory('factories.CategoryFactoryMemory')
