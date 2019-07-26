from flask import render_template, Blueprint

from webapp.api import (
    get_releases,
    get_socs,
    get_desktops,
    get_servers,
    get_iot,
    get_laptops,
    get_device_information_by_hardware_id,
)


certification_blueprint = Blueprint(
    "certification",
    __name__,
    template_folder="/templates",
    static_folder="/static",
)


@certification_blueprint.route("/hardware/<hardwareid>")
def hardware(hardwareid):
    modelinfo_data = get_device_information_by_hardware_id(hardwareid)

    hardware_details = {"categories": {}}
    for component in modelinfo_data.get("hardware_details"):
        category = component.get("category")
        if category not in hardware_details.get("categories"):
            hardware_details.get("categories")[category] = []

        hardware_info = {
            "name": component.get("name"),
            "bus": component.get("bus"),
            "identifier": component.get("identifier"),
        }

        hardware_details.get("categories")[category].append(hardware_info)

    details = {
        "id": hardwareid,
        "name": modelinfo_data.get("model"),
        "vendor": modelinfo_data.get("make"),
        "major_release": modelinfo_data.get("major_release"),
        "hardware_details": hardware_details,
    }

    return render_template("hardware.html", details=details)


@certification_blueprint.route("/desktop")
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


@certification_blueprint.route("/server")
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


@certification_blueprint.route("/iot")
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


@certification_blueprint.route("/soc")
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
