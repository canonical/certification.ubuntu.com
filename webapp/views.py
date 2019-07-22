from flask import render_template

from webapp.api import (
    get_releases,
    get_socs,
    get_desktops,
    get_servers,
    get_iot,
    get_laptops,
)


def desktop():
    release_data = get_releases().json()
    releases = [
        release
        for release in release_data.get("objects")
        if release.get("desktops") != "0" or release.get("laptops") != "0"
    ]

    desktop_data = get_desktops().json()
    laptop_data = get_laptops().json()

    vendors = {
        entry["make"]: entry
        for entry in desktop_data.get("objects") + laptop_data.get("objects")
    }.values()

    return render_template("desktop.html", releases=releases, vendors=vendors)


def server():
    vendor_data = get_servers().json()
    vendors = vendor_data.get("vendors")

    all_releases = []

    for vendor in vendors:
        for release in vendor["releases"]:
            if release not in all_releases:
                all_releases.append(release)

    return render_template(
        "server.html", releases=all_releases, vendors=vendors
    )


def iot():
    release_data = get_releases().json()
    releases = [
        release
        for release in release_data.get("objects")
        if release.get("smart_core") != "0"
    ]

    vendors_data = get_iot().json()
    vendors = vendors_data.get("objects")

    return render_template("iot.html", releases=releases, vendors=vendors)


def soc():
    release_data = get_releases().json()
    releases = [
        release
        for release in release_data.get("objects")
        if release.get("soc") != "0"
    ]

    vendors_data = get_socs().json()
    vendors = vendors_data.get("objects")

    return render_template("soc.html", releases=releases, vendors=vendors)
