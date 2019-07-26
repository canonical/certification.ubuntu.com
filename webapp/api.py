from canonicalwebteam.http import CachedSession


api_session = CachedSession(
    fallback_cache_duration=300, file_cache_directory=".webcache"
)

base_url = "https://certification.ubuntu.com/api/v1"


def get(endpoint):
    return api_session.get(f"{base_url}/{endpoint}")


def get_releases():
    return get("certifiedreleases?format=json")


def get_vendors():
    return get("certifiedmakes?format=json")


def get_releases_by_vendor():
    return get("vendorsummaries/server/?format=json")


def get_desktops():
    return get("certifiedmakes/?format=json&desktops__gte=1")


def get_laptops():
    return get("certifiedmakes/?format=json&laptops__gte=1")


def get_socs():
    return get("certifiedmakes/?format=json&soc__gte=1")


def get_iot():
    return get("certifiedmakes/?format=json&smart_core__gte=1")


def get_servers():
    return get_releases_by_vendor()


def get_device_information_by_hardware_id(id):
    model_info = (
        get(f"certifiedmodels/?format=json&canonical_id={id}")
        .json()
        .get("objects")[0]
    )
    model_info["hardware_details"] = (
        get(
            "certifiedmodeldevices/"
            f"?format=json&canonical_id={id}&limit=1000"
        )
        .json()
        .get("objects")
    )

    return model_info
