# -*- coding: utf8 -*-
# This file is part of PyBossa.
#
# Copyright (C) 2015 SciFabric LTD.
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

import requests
from StringIO import StringIO
from flask.ext.babel import gettext
from pybossa.util import unicode_csv_reader

from .base import _BulkTaskImport, BulkImportException


class _BulkTaskCSVImport(_BulkTaskImport):

    """Class to import CSV tasks in bulk."""

    importer_id = "csv"

    def tasks(self, **form_data):
        """Get tasks from a given URL."""
        dataurl = self._get_data_url(**form_data)
        r = requests.get(dataurl)
        return self._get_csv_data_from_request(r)

    def _get_data_url(self, **form_data):
        """Get data from URL."""
        return form_data['csv_url']

    def _import_csv_tasks(self, csvreader):
        """Import CSV tasks."""
        headers = []
        fields = set(['state', 'quorum', 'calibration', 'priority_0',
                      'n_answers'])
        field_header_index = []
        row_number = 0
        for row in csvreader:
            if not headers:
                headers = row
                self._check_no_duplicated_headers(headers)
                self._check_no_empty_headers(headers)
                field_headers = set(headers) & fields
                for field in field_headers:
                    field_header_index.append(headers.index(field))
            else:
                row_number += 1
                self._check_valid_row_length(row, row_number, headers)
                task_data = {"info": {}}
                for idx, cell in enumerate(row):
                    if idx in field_header_index:
                        task_data[headers[idx]] = cell
                    else:
                        task_data["info"][headers[idx]] = cell
                yield task_data

    def _check_no_duplicated_headers(self, headers):
        if len(headers) != len(set(headers)):
            msg = gettext('The file you uploaded has '
                          'two headers with the same name.')
            raise BulkImportException(msg)

    def _check_no_empty_headers(self, headers):
        stripped_headers = [header.strip() for header in headers]
        if "" in stripped_headers:
            position = stripped_headers.index("")
            msg = gettext("The file you uploaded has an empty header on "
                          "column %(pos)s.", pos=(position+1))
            raise BulkImportException(msg)

    def _check_valid_row_length(self, row, row_number, headers):
        if len(headers) != len(row):
            msg = gettext("The file you uploaded has an extra value on "
                          "row %s." % (row_number+1))
            raise BulkImportException(msg)

    def _get_csv_data_from_request(self, r):
        """Get CSV data from a request."""
        if r.status_code == 403:
            msg = ("Oops! It looks like you don't have permission to access"
                   " that file")
            raise BulkImportException(gettext(msg), 'error')
        if (('text/plain' not in r.headers['content-type']) and
                ('text/csv' not in r.headers['content-type'])):
            msg = gettext("Oops! That file doesn't look like the right file.")
            raise BulkImportException(msg, 'error')

        r.encoding = 'utf-8'
        csvcontent = StringIO(r.text)
        csvreader = unicode_csv_reader(csvcontent)
        return self._import_csv_tasks(csvreader)


class _BulkTaskGDImport(_BulkTaskCSVImport):

    """Class to import tasks from Google Drive in bulk."""

    importer_id = "gdocs"

    def _get_data_url(self, **form_data):
        """Get data from URL."""
        # For old data links of Google Spreadsheets
        if 'ccc?key' in form_data['googledocs_url']:
            return ''.join([form_data['googledocs_url'], '&output=csv'])
        # New data format for Google Drive import is like this:
        # https://docs.google.com/spreadsheets/d/key/edit?usp=sharing
        else:
            return ''.join([form_data['googledocs_url'].split('edit')[0],
                            'export?format=csv'])