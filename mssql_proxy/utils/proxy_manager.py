# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import os
import logging
import subprocess

_logger = logging.getLogger(__name__)

class Manager:

    def app_command(parameters = {}, exec_cmd = False, app = 'MSSQLProxy'):

        jar_path = '%s/java/%s.jar' % (Manager.back_dir(os.path.realpath(__file__), 2), app)
        command = 'java -jar %s' % jar_path

        # ADD PARAMETERS
        for index in parameters:
            command += ' --%s="%s"' % (index, parameters[index])

        return Manager.shell_exec(command) if exec_cmd else command

    def shell_exec(_command):
        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception as e:
            _logger.error('EXECUTE ERROR: %s', e)

    def back_dir(_path, _positions):
        # Returns number of positions in path

        path_list = _path.strip('/').split('/')
        length = len(path_list)

        if(_positions >= length or _positions < 0):
                return ''

        for i in range(0, _positions):
                path_list.pop()

        return "/%s" % "/".join(path_list)