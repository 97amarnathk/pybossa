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
from pybossa.model.blogpost import Blogpost
from . import BaseFactory, factory
from helper.repositories import memo_blog_repo
from pybossa.repositories import BlogRepository

blog_repo = BlogRepository(db)

class BlogpostFactory(BaseFactory):
    class Meta:
        model = Blogpost

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        blogpost = model_class(*args, **kwargs)
        blog_repo.save(blogpost)
        return blogpost

    id = factory.Sequence(lambda n: n)
    title = u'Blogpost title'
    body = u'Blogpost body text'
    app = factory.SubFactory('factories.AppFactory')
    app_id = factory.LazyAttribute(lambda blogpost: blogpost.app.id)
    owner = factory.SelfAttribute('app.owner')
    user_id = factory.LazyAttribute(
        lambda blogpost: blogpost.owner.id if blogpost.owner else None)


class BlogpostFactoryMemory(BlogpostFactory):

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        blogpost = model_class(*args, **kwargs)
        memo_blog_repo.save(blogpost)
        return blogpost

    app = factory.SubFactory('factories.AppFactoryMemory')
