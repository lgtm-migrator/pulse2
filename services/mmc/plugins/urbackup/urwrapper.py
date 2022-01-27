# -*- coding: utf-8; -*-
#
# (c) 2022 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import json
import requests
from requests.structures import CaseInsensitiveDict
from mmc.plugins.urbackup import config

try:
    from urllib import urlencode
except:
    from urllib.parse import urlencode

class UrApiWrapper:
    url = ""
    user_login = ""
    password = ""
    ses = ""
    headers = {}
    verify = False
    allow_redirects = True

    def __init__(self):
        _config = config.UrbackupConfig()
        self.url = _config.urbackup_url
        self.user_login = _config.urbackup_username
        self.password = _config.urbackup_password
        self.ses = "" # sessionid

        self.headers = CaseInsensitiveDict()
        self.headers["Accept"] = "application/json"
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.verify = False
        self.allow_redirects = True

    def set_header(self, key, value):
        self.headers[key] = value

    def request(self, action, params, method="POST"):
        url = self.url + "?" + urlencode({"a": action})

        if method == "GET":
            response = requests.get(url, headers=self.headers, data=params, verify=self.verify, allow_redirects=self.allow_redirects)
        if method == "POST":
            response = requests.post(url, headers=self.headers, data=params, verify=self.verify, allow_redirects=self.allow_redirects)

        return response

    def login(self, lang="en"):
        params = {"username": self.user_login, "password": self.password, "plainpw":1, "lang":lang}
        response = self.request("login", params)

        try:
            result = json.loads(response.text)
            if "session" in result:
                self.ses = result["session"]
        except:
            pass

        return response

    def get_session(self):
        session = self.ses
        return session

    @staticmethod
    def response(resp):
        try:
            resp_json = json.loads(resp.text)
        except:
            resp_json = resp.text

        return {"status_code": resp.status_code, "headers": resp.headers, "content": resp_json}

    def get_logs(self, clientid=0):
        self.login()
        params = {"clientid": clientid, "lastid": 0, "ses": self.ses}
        response = self.request("livelog", params)

        return response

    def get_settings_general(self):
        self.login()
        params = {"sa": "general", "ses": self.ses}
        response = self.request("settings", params)

        return response

    def get_clients(self):
        self.login()
        params = {"sa": "listusers", "ses": self.ses}
        response = self.request("settings", params)

        return response

    def get_backups(self):
        self.login()
        params = {"clientid": 0, "ses": self.ses}
        response = self.request("backups", params)

        return response

    def get_status(self):
        self.login()
        params = {"ses": self.ses}
        response = self.request("status", params)

        return response
