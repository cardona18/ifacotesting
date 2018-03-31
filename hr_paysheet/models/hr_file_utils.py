# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os
import subprocess
import sys

_logger = logging.getLogger(__name__)

class FileUtils:

    def back_dir(self, _path, _positions):
        # Returns number of positions in path

        path_list = _path.strip('/').split('/')
        length = len(path_list)

        if(_positions >= length or _positions < 0):
                return ''

        for i in range(0, _positions):
                path_list.pop()

        return "/%s" % "/".join(path_list)

    def locale_format_date(self, _date, _format, _locale, capital=False):
        # Convenrt date to locale format

        locale.setlocale(locale.LC_TIME, _locale)

        date = datetime.strptime(_date, DEFAULT_SERVER_DATE_FORMAT)

        res = date.strftime(_format)

        if(capital):
            s = list(res)
            s[3] = s[3].upper()
            res = "".join(s)

        return res

    def delete_tmp_files(self):

        tmp_path = "%s/tmp" % self.back_dir(os.path.realpath(__file__), 4)

        for filename in os.listdir(tmp_path):

            file = '%s/%s' % (tmp_path, filename)

            t = os.path.getmtime(file)

            fdate = self._utc_to_tz(datetime.fromtimestamp(t), "America/Mexico_City")
            cdate = self._utc_to_tz(datetime.now(), "America/Mexico_City")
            tdiff = (cdate - fdate).days

            if(tdiff >= 1):

                try:
                    subprocess.check_output("rm -rf {file}".format(file=file), shell=True, stderr=subprocess.STDOUT)
                except Exception, e:
                    _logger.error('DELETE ERROR: %s', e)

    def _utc_to_tz(self, _date, _time_zone):

        # CONVER TO UTC
        _date = _date.replace(tzinfo = tz.gettz('UTC'))

        # LOAD TIMEZONE
        to_zone  = tz.gettz(_time_zone)

        return _date.astimezone(to_zone)