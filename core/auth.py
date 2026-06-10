import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from xml_helper import load_xml

def login_user(username, password):
    tree = load_xml()
    root = tree.getroot()

    for user in root.findall("user"):
        u = user.find("username")
        p = user.find("password")
        a = user.find("is_admin")

        if u is None or p is None:
            continue

        if u.text == username and p.text == password:
            return {
                "id": user.find("id").text if user.find("id") is not None else "",
                "username": username,
                "is_admin": (a.text.lower() == "true") if a is not None else False
            }

    return None