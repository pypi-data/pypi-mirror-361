# -*- coding: utf-8 -*-
# notebook_utils.py

import json
import os
import urllib

import ipykernel

try:
    from notebook import notebookapp
except ImportError:
    from notebook import app as notebookapp


def currentNBpath():
    """Returns the absolute path of the Notebook or None if it cannot be determined
    NOTE: works only for *Jupyter Notebook* (not Jupyter Lab)
    and when the security is token-based or there is also no password.
    """
    connection_file = os.path.basename(ipykernel.get_connection_file())
    kernel_id = connection_file.split("-", 1)[1].split(".")[0]

    for srv in notebookapp.list_running_servers():
        try:
            if srv["token"] == "" and not srv["password"]:  # No token and no password, ahem...
                req = urllib.request.urlopen(srv["url"] + "api/sessions")
            else:
                req = urllib.request.urlopen(srv["url"] + "api/sessions?token=" + srv["token"])
            sessions = json.load(req)
            for sess in sessions:
                if sess["kernel"]["id"] == kernel_id:
                    return os.path.join(srv["notebook_dir"], sess["notebook"]["path"])
        except OSError:
            pass  # There may be stale entries in the runtime directory
    return None
