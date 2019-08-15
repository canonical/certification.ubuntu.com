# Standard library
import os

# Packages
import flask
from canonicalwebteam.flask_base.app import FlaskBase

# Local
from webapp.api import get, get_device_information_by_hardware_id


dir_path = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(dir_path)
templates_dir = os.path.join(app_dir, "templates")

app = FlaskBase(
    __name__,
    "certification.ubuntu.com",
    template_folder=templates_dir,
    static_folder="../static",
    template_404="404.html",
    template_500="500.html",
)


@app.route("/hardware/<hardware_id>")
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

    return flask.render_template("hardware.html", details=details)


@app.route("/desktop")
def desktop():
    release_data = get("certifiedreleases?format=json").json()
    releases = [
        release
        for release in release_data.get("objects")
        if release.get("desktops") != "0" or release.get("laptops") != "0"
    ]

    desktop_data = get("certifiedmakes/?format=json&desktops__gte=1").json()
    laptop_data = get("certifiedmakes/?format=json&laptops__gte=1").json()

    vendors = {
        entry["make"]: entry
        for entry in desktop_data.get("objects") + laptop_data.get("objects")
    }.values()

    return flask.render_template(
        "desktop.html", releases=releases, vendors=vendors
    )


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/server")
def server():
    vendor_data = get("vendorsummaries/server/?format=json").json()
    vendors = vendor_data.get("vendors")

    all_releases = []

    for vendor in vendors:
        for release in vendor["releases"]:
            if release not in all_releases:
                all_releases.append(release)

    return flask.render_template(
        "server.html", releases=all_releases, vendors=vendors
    )


@app.route("/iot")
def iot():
    release_data = get("certifiedreleases?format=json").json()
    releases = [
        release
        for release in release_data.get("objects")
        if release.get("smart_core") != "0"
    ]

    vendors_data = get("certifiedmakes/?format=json&smart_core__gte=1").json()
    vendors = vendors_data.get("objects")

    return flask.render_template(
        "iot.html", releases=releases, vendors=vendors
    )


@app.route("/soc")
def soc():
    release_data = get("certifiedreleases?format=json").json()
    releases = [
        release
        for release in release_data.get("objects")
        if release.get("soc") != "0"
    ]

    vendors_data = get("certifiedmakes/?format=json&soc__gte=1").json()
    vendors = vendors_data.get("objects")

    return flask.render_template(
        "soc.html", releases=releases, vendors=vendors
    )
