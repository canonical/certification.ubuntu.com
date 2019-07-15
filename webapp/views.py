from flask import render_template

from webapp.api import get_releases


def desktop():
    release_data = get_releases().json()
    releases = release_data.get("objects")

    return render_template("desktop.html", releases=releases)
