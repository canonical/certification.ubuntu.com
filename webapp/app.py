# Packages
import flask
from canonicalwebteam.flask_base.app import FlaskBase
from canonicalwebteam.http import CachedSession

# Local
from webapp.api import CertificationAPI


app = FlaskBase(
    __name__,
    "certification.ubuntu.com",
    template_folder="../templates",
    static_folder="../static",
    template_404="404.html",
    template_500="500.html",
)

api = CertificationAPI(
    base_url="https://certification.canonical.com/api/v1",
    session=CachedSession(),
)


@app.route("/hardware/<canonical_id>")
def hardware(canonical_id):
    model_info = api.certifiedmodel(canonical_id)
    model_devices = api.certifiedmodeldevices(
        canonical_id=canonical_id, limit="0"
    )["objects"]
    model_releases = api.certifiedmodeldetails(
        canonical_id=canonical_id, limit="0"
    )["objects"]

    hardware_details = {}

    for device in model_devices:
        device_info = {
            "name": f"{device['make']} {device['name']}",
            "bus": device["bus"],
            "identifier": device["identifier"],
        }

        category = device["category"]
        if category != "BIOS":
            category = category.lower()

        if category in hardware_details:
            hardware_details[category].append(device_info)
        else:
            hardware_details[category] = [device_info]

    release_details = {"components": {}, "releases": []}

    for model_release in model_releases:
        ubuntu_version = model_release["certified_release"]
        arch = ""
        if model_release["architecture"] == "amd64":
            arch = "64 Bit"
        else:
            arch = "32 Bit"

        release_info = {
            "name": f"Ubuntu {ubuntu_version} {arch}",
            "kernel": model_release["kernel_version"],
            "bios": model_release["bios"],
            "version": ubuntu_version,
        }
        release_details["releases"].append(release_info)

        for device_category, devices in model_release.items():
            if (
                device_category
                in ["video", "processor", "network", "wireless"]
                and devices
            ):
                if device_category in release_details["components"]:
                    release_details["components"][device_category] += devices
                else:
                    release_details["components"][device_category] = devices

    details = {
        "id": canonical_id,
        "name": model_info.get("model"),
        "vendor": model_info.get("make"),
        "major_release": model_info.get("major_release"),
        "hardware_details": hardware_details,
        "release_details": release_details,
    }

    return flask.render_template("hardware.html", details=details)


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/desktop")
def desktop():
    releases = []
    vendors = []

    for release in api.certifiedreleases(limit="0")["objects"]:
        if int(release["desktops"]) > 0 or int(release["laptops"]) > 0:
            releases.append(release)

    for vendor in api.certifiedmakes(limit="0")["objects"]:
        if int(vendor["desktops"]) > 0 or int(vendor["laptops"]) > 0:
            vendors.append(vendor)

    return flask.render_template(
        "desktop/index.html", releases=releases, vendors=vendors
    )


@app.route("/server")
def server():
    vendors = api.vendorsummaries_server()["vendors"]

    releases = []

    for vendor in vendors:
        for release in vendor["releases"]:
            if release not in releases:
                releases.append(release)

    return flask.render_template(
        "server/index.html", releases=releases, vendors=vendors
    )


@app.route("/iot")
def iot():
    return flask.render_template(
        "iot/index.html",
        releases=api.certifiedreleases(smart_core__gte="1")["objects"],
        vendors=api.certifiedmakes(smart_core__gte="1")["objects"],
    )


@app.route("/soc")
def soc():
    return flask.render_template(
        "soc/index.html",
        releases=api.certifiedreleases(soc__gte="1")["objects"],
        vendors=api.certifiedmakes(soc__gte="1")["objects"],
    )
