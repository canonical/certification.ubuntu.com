from math import ceil
from re import sub


from flask import render_template, Blueprint, request
from werkzeug.urls import url_encode

from webapp.api import (
    get_releases,
    get_socs,
    get_desktops,
    get_servers,
    get_iot,
    get_laptops,
    get_device_information_by_hardware_id,
    search_devices,
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


def get_pagination_page_array(page, offset, total_pages):
    """
    Return an array of page numbers to display for a given page with
    an offset around it.
    E.g with the current page page=4 and offset 2:
        [2,3,4,5,6]
    The total amount of pages is needed for boundary calculation.
    """
    first_page_to_show = page - offset
    last_page_to_show = page + offset

    first_page_offset = 0

    if first_page_to_show < 1:
        first_page_offset = first_page_to_show * -1 + 1
        first_page_to_show = 1

    print(last_page_to_show)

    if last_page_to_show > total_pages:
        if first_page_to_show > 1 and first_page_offset == 0:
            first_page_to_show = max(
                first_page_to_show - last_page_to_show + total_pages, 1
            )
        last_page_to_show = total_pages
    else:
        last_page_to_show = min(
            total_pages, last_page_to_show + first_page_offset
        )

    return list(range(first_page_to_show, last_page_to_show + 1))


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
    params = {
        "query": request.args.get("query", ""),
        "category": request.args.getlist("category"),
        "vendors": request.args.getlist("vendors"),
        "releases": request.args.getlist("release"),
        "level": request.args.get("level"),
        "page": int(request.args.get("page", 1)),
    }

    if not params["category"]:
        params["category"] = ["Desktop"]

    devices_per_page = 25

    result = search_devices(
        query=params["query"],
        categories=params["category"],
        vendors=params["vendors"],
        releases=params["releases"],
        level=params["level"],
        per_page=devices_per_page,
        page=params["page"],
    )
    devices = result["devices"]
    total_amount_of_devices = result["total"]

    amount_of_pages = ceil(total_amount_of_devices / devices_per_page)
    page = params["page"]

    pages_to_show_in_pagination = get_pagination_page_array(
        page, 4, amount_of_pages
    )

    search_query = url_encode(request.args)
    search_query = sub(r"&page=\d*", "", search_query)

    return render_template(
        "desktop-search.html",
        search_params=params,
        search_fields={"vendors": makes, "releases": releaseList},
        results=devices,
        total_amount_of_devices=result["total"],
        page=params["page"],
        total_pages=total_amount_of_devices / devices_per_page,
        pages_to_show_in_pagination=pages_to_show_in_pagination,
        search_query=search_query,
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
