from django.conf import settings


def clean_app_name(app_name) -> str:
    split = str(app_name).split(".")
    end_index = len(split)

    for index, element in enumerate(split):
        if index == 0:
            continue

        if element == "apps":
            end_index = index
            break

    return ".".join(split[0:end_index])


def get_modules_list() -> list[str]:
    if hasattr(settings, "AUTO_ROUTER_MODULES"):
        return getattr(settings, "AUTO_ROUTER_MODULES")

    return ["views"]
