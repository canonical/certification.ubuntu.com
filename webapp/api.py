from canonicalwebteam.http import CachedSession


api_session = CachedSession(
    fallback_cache_duration=300, file_cache_directory=".webcache"
)

base_url = "https://certification.ubuntu.com/api/v1"


def get(endpoint):
    return api_session.get(f"{base_url}/{endpoint}")


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

    model_info["release_details"] = (
        get(f"certifiedmodeldetails/?format=json&canonical_id={id}")
        .json()
        .get("objects")
    )

    return model_info
