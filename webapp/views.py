from flask import render_template, Blueprint, request

from webapp.api import (
    get_releases,
    get_socs,
    get_desktops,
    get_servers,
    get_iot,
    get_laptops,
    get_device_information_by_hardware_id,
    search_for_desktops,
)


certification_blueprint = Blueprint(
    "certification",
    __name__,
    template_folder="/templates",
    static_folder="/static",
)


@certification_blueprint.route("/hardware/<hardware_id>")
def hardware(hardware_id):
    modelinfo_data = get_device_information_by_hardware_id(hardware_id)

    hardware_details = {}
    for component in modelinfo_data.get("hardware_details"):
        category = component.get("category")
        if category != "BIOS":
            category = category.lower()
        if category not in hardware_details:
            hardware_details[category] = []

        hardware_info = {
            "name": f"{component.get('make')} {component.get('name')}",
            "bus": component.get("bus"),
            "identifier": component.get("identifier"),
        }

        hardware_details[category].append(hardware_info)

    release_details = {"components": {}, "releases": []}
    for release in modelinfo_data.get("release_details"):
        release_version = release["certified_release"]
        release_name = (
            "Ubuntu "
            f"{release_version} "
            f"{ '64 Bit' if release['architecture'] == 'amd64' else '32 Bit'}"
        )
        release_info = {
            "name": release_name,
            "kernel": release["kernel_version"],
            "bios": release["bios"],
            "release_version": release_version,
        }
        release_details["releases"].append(release_info)

        for key, values in release.items():
            if key in ["video", "processor", "network", "wireless"] and values:
                devices = []
                for name in values:
                    # Device cant be in releasedetails but not hardwaredetails.
                    # Would be an API error, since its the same machine
                    device = next(
                        (
                            x
                            for x in hardware_details[key]
                            if name in x["name"]
                        ),
                        None,
                    )
                    devices.append(device)

                if key in release_details["components"]:
                    release_details["components"][key] = (
                        release_details["components"][key] + devices
                    )
                else:
                    release_details["components"][key] = devices

    details = {
        "id": hardware_id,
        "name": modelinfo_data.get("model"),
        "vendor": modelinfo_data.get("make"),
        "major_release": modelinfo_data.get("major_release"),
        "hardware_details": hardware_details,
        "release_details": release_details,
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


@certification_blueprint.route("/desktop/models")
def desktop_models():
    desktop_data = get_desktops().json()
    makes = []
    for dictionary in desktop_data["objects"]:
        if dictionary["desktops"] != "0":
            makes.append(dictionary["make"])
    release_data = get_releases().json()
    releaseList = []
    for dictionary in release_data["objects"]:
        if dictionary["desktops"] != "0":
            releaseList.append(dictionary["release"])
    print(release_data)
    params = {
        "query": request.args.get("query"),
        "category": request.args.getlist("category"),
        "vendors": request.args.getlist("vendors"),
        "release": request.args.getlist("release"),
        "level": request.args.get("level"),
    }
    results = search_for_desktops(
        params["query"],
        params["category"],
        params["vendors"],
        params["release"],
        params["level"],
    )

    return render_template(
        "search.html",
        search_params=params,
        search_fields={"vendors": makes, "releases": releaseList},
        results=results,
    )


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
