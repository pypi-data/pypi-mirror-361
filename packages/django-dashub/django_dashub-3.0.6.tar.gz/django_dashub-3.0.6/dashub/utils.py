import datetime
import importlib
import inspect
import logging
from typing import Any, Callable, Dict, List, Set, Union, Optional
from urllib.parse import urlencode

from django.apps import apps
from django.conf import settings
from django.contrib.admin import ListFilter
from django.contrib.admin.helpers import AdminForm
from django.contrib.auth.models import AbstractUser
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.base import Model, ModelBase
from django.db.models.options import Options
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext

from .compat import NoReverseMatch, reverse

logger = logging.getLogger(__name__)


def order_with_respect_to(original: List, reference: List, getter: Callable = lambda x: x) -> List:
    """
    Order a list based on the location of items in the reference list, optionally, use a getter to pull values out of
    the first list
    """
    ranking = []
    max_num = len(original)
    for item in original:
        try:
            pos = reference.index(getter(item))
        except ValueError:
            pos = max_num

        ranking.append(pos)

    return [y for x, y in sorted(zip(ranking, original), key=lambda x: x[0])]


def order_menus_with_order(original: List[Dict[str, Any]], order_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for item in original:
        item["order"] = item.get("item", 0)
        app_label = item.get("app_label") or item.get("app")
        order_entry = next((entry for entry in order_list if entry["app"] == app_label), None)
        if order_entry:
            item["order"] = order_entry["order"]

        if "models" in item and isinstance(item["models"], list):
            model_order_list = order_entry.get("models", []) if order_entry else []

            for model in item["models"]:
                model["order"] = model.get("order", 0)
                model_entry = next((m for m in model_order_list if m["model"] == model.get("object_name")), None)
                if model_entry:
                    model["order"] = model_entry["order"]

                # Also order submenus if they exists
                if "submenus" in model and isinstance(model["submenus"], list):
                    model["submenus"] = [submenu.get("order", 0) for submenu in model["submenus"]]
                    model["submenus"] = model["submenus"].sort(key=lambda x: x["order"], reverse=True)

            item["models"].sort(key=lambda x: x["order"], reverse=True)
    original.sort(key=lambda x: x["order"], reverse=True)
    return original


def get_admin_url(instance: Any, admin_site: str = "admin", from_app: bool = False, **kwargs: str) -> str:
    """
    Return the admin URL for the given instance, model class or <app>.<model> string
    """
    url = "#"
    try:
        if isinstance(instance, str):
            app_label, model_name = instance.split(".")
            model_name = model_name.lower()
            url = reverse(
                "admin:{app_label}_{model_name}_changelist".format(app_label=app_label, model_name=model_name),
                current_app=admin_site,
            )

        # Model class
        elif instance.__class__ == ModelBase:
            app_label, model_name = instance._meta.app_label, instance._meta.model_name
            url = reverse(
                "admin:{app_label}_{model_name}_changelist".format(app_label=app_label, model_name=model_name),
                current_app=admin_site,
            )

        # Model instance
        elif instance.__class__.__class__ == ModelBase and isinstance(instance, instance.__class__):
            app_label, model_name = instance._meta.app_label, instance._meta.model_name
            url = reverse(
                "admin:{app_label}_{model_name}_change".format(app_label=app_label, model_name=model_name),
                args=(instance.pk,),
                current_app=admin_site,
            )

    except (NoReverseMatch, ValueError):
        # If we are not walking through the models within an app, let the user know this url cant be reversed
        if not from_app:
            logger.warning(gettext("Could not reverse url from {instance}".format(instance=instance)))

    if kwargs:
        url += "?{params}".format(params=urlencode(kwargs))

    return url


def get_filter_id(spec: ListFilter) -> str:
    return getattr(spec, "field_path", getattr(spec, "parameter_name", spec.title))


def get_custom_url(url: str, admin_site: str = "admin") -> str:
    """
    Take in a custom url, and try to reverse it
    """
    if not url:
        logger.warning("No url supplied in custom link")
        return "#"

    if "/" in url:
        return url
    try:
        url = reverse(url.lower(), current_app=admin_site)
    except NoReverseMatch:
        logger.warning("Couldnt reverse {url}".format(url=url))
        url = "#" + url

    return url


def get_model_meta(model_str: str) -> Union[None, Options]:
    """
    Get model meta class
    """
    try:
        app, model = model_str.split(".")
        model_klass: Model = apps.get_registered_model(app, model)
        return model_klass._meta
    except (ValueError, LookupError):
        return None


def get_app_admin_urls(app: str, admin_site: str = "admin") -> List[Dict]:
    """
    For the given app string, get links to all the app models admin views
    """
    if app not in apps.app_configs:
        logger.warning("{app} not found when generating links".format(app=app))
        return []

    models = []
    for model in apps.app_configs[app].get_models():
        url = get_admin_url(model, admin_site=admin_site, from_app=True)

        # We have no admin class
        if url == "#":
            continue

        models.append(
            {
                "url": url,
                "model": "{app}.{model}".format(app=model._meta.app_label, model=model._meta.model_name),
                "name": model._meta.verbose_name_plural.title(),
            }
        )

    return models


def get_view_permissions(user: AbstractUser) -> Set[str]:
    """
    Get model names based on a users view/change permissions
    """
    perms = user.get_all_permissions()
    # the perm codenames should always be lower case
    lower_perms = []
    for perm in perms:
        app, perm_codename = perm.split(".")
        lower_perms.append("{app}.{perm_codename}".format(app=app, perm_codename=perm_codename.lower()))
    return {x.replace("view_", "") for x in lower_perms if "view" in x or "change" in x}


def manage_submenu(submenus: List[Dict], options: Dict) -> List[Dict]:
    output = []
    for submenu in submenus:
        if not submenu:
            continue

        if "model" in submenu:
            model = get_model_meta(submenu["model"])
            if model:
                output.append(
                    {
                        "name": model.verbose_name_plural.title(),
                        "url": get_admin_url(submenu["model"]),
                        "icon": submenu.get("icon", options["default_icon_children"]),
                        "order": submenu.get("order", 0),
                    }
                )
        elif "url" in submenu:
            output.append(
                {
                    "name": submenu.get("name", "unspecified"),
                    "url": get_custom_url(submenu["url"]),
                    "icon": submenu.get("icon", options["default_icon_children"]),
                    "order": submenu.get("order", 0),
                }
            )
    return output


def make_single_menu(model_permissions: set[str], user: AbstractUser, link: Dict, options: Dict, app_name: Union[str, None],
                     allow_appmenus: bool = True, admin_site: str = "admin") -> List[Dict]:

    menu = []
    if isinstance(link, str):
        return menu

    perm_matches = []
    link_permissions = link.get("permissions", [])
    for perm in link_permissions:
        perm_matches.append(user.has_perm(perm))

    if not all(perm_matches):
        return menu

    # Url links
    if "url" in link:
        identifier_name = slugify(link.get("name", "unspecified"))
        menu.append(
            {
                "object_name": identifier_name,
                "name": link.get("name", "unspecified"),
                "url": get_custom_url(link["url"], admin_site=admin_site),
                "children": [],
                "new_window": link.get("new_window", False),
                "icon": link.get("icon", options["default_icon_children"]),
                "submenu": manage_submenu(link.get("submenu", []), options),
                "order": link.get("order", 0),
            }
        )
    # Model links
    elif "model" in link:
        model_label = link["model"].lower()
        app_permission = model_label
        if app_name and "." not in model_label:
            app_permission = f"{app_name}.{model_label}"
        if model_label not in model_permissions and app_permission not in model_permissions:
            return []

        _meta = get_model_meta(link["model"])

        name = _meta.verbose_name_plural.title() if _meta else link["model"]
        menu.append(
            {
                "object_name": model_label,
                "name": name,
                "url": get_admin_url(link["model"], admin_site=admin_site),
                "children": [],
                "new_window": link.get("new_window", False),
                "icon": options["icons"].get(link["model"], options["default_icon_children"]),
                "submenu": manage_submenu(link.get("submenu", []), options),
                "order": link.get("order", 0),
            }
        )

    # App links
    elif "app" in link and allow_appmenus:
        children = [
            {"name": child.get("verbose_name", child["name"]), "url": child["url"], "children": None}
            for child in get_app_admin_urls(link["app"], admin_site=admin_site)
            if child["model"] in model_permissions
        ]
        if len(children) == 0:
            return []

        menu.append({
            "object_name": link["app"],
            "name": getattr(apps.app_configs[link["app"]], "verbose_name", link["app"]).title(),
            "url": "#",
            "children": children,
            "icon": options["icons"].get(link["app"], options["default_icon_children"]),
            "order": link.get("order", 0),
        })
    return menu


def make_menu(
        user: AbstractUser, links: List[Dict], options: Dict, app_name: Union[str, None], allow_appmenus: bool = True,
        admin_site: str = "admin"
) -> List[Dict]:
    """
    Make a menu from a list of user supplied links
    """
    if not user:
        return []

    model_permissions = get_view_permissions(user)

    menu = []
    if isinstance(links, list):
        for link in links:
            menu.extend(make_single_menu(model_permissions, user, link, options, app_name, allow_appmenus, admin_site))
    elif isinstance(links, dict):
        menu.extend(make_single_menu(model_permissions, user, links, options, app_name, allow_appmenus, admin_site))

    return menu


def has_fieldsets_check(adminform: AdminForm) -> bool:
    fieldsets = adminform.fieldsets
    if not fieldsets or (len(fieldsets) == 1 and fieldsets[0][0] is None):
        return False
    return True


def attr(**kwargs) -> Callable:
    def decorator(func: Callable):
        for key, value in kwargs.items():
            setattr(func, key, value)
        return func

    return decorator


def get_installed_apps() -> List[str]:
    return [app_config.label for app_config in apps.get_app_configs()]


def hex_to_rgb(hex_color):
    """
    Convert a hex color string to an RGB string in the format "r, g, b".

    :param hex_color: str, hex color code (e.g., "#FF5733" or "FF5733")
    :return: str, "r, g, b"
    """

    # Check for valid hex color format
    try:
        if not isinstance(hex_color, str):
            raise ValueError("Hex color must be a string")

        if not hex_color.startswith('#'):
            hex_color = '#' + hex_color

        hex_color = hex_color.lstrip('#')  # Remove '#' if present
        if len(hex_color) != 6:
            raise ValueError("Invalid hex color format")

        r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        return f"{r}, {g}, {b}"
    except Exception:
        return f"0, 0, 0"



def parse_date_str(value: str) -> Optional[datetime.date]:
    for date_format in settings.DATE_INPUT_FORMATS:
        try:
            return datetime.datetime.strptime(value, date_format).date()
        except (ValueError, TypeError):
            continue
    return None


def parse_datetime_str(value: str) -> Optional[datetime.datetime]:
    for date_format in settings.DATETIME_INPUT_FORMATS:
        try:
            return datetime.datetime.strptime(value, date_format)
        except (ValueError, TypeError):
            continue
    return None


def resolve_dynamic_value(value: Any, request: WSGIRequest = None, **kwargs) -> Any:
    """
    Resolve a value that can be either static or a callable function.

    Args:
        value: The value to resolve (can be static value or callable)
        request: Django request object to pass to callable
        **kwargs: Additional keyword arguments to pass to callable

    Returns:
        The resolved value
    """
    if callable(value):
        try:
            if request is not None:
                try:
                    return value(request, **kwargs)
                except TypeError as e:
                    print(f"Error calling dynamic value with request: {e}")
                    return value(**kwargs)
            else:
                return value(**kwargs)
        except Exception as e:
            print(f"Error resolving dynamic value: {e}")
            return value
    return value


def import_from_string(path: str) -> Callable:
    """
    Import a function from a dotted path string (e.g., 'myapp.utils.func')
    """
    module_path, func_name = path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, func_name)


def evaluate_dynamic_value(
    value: Union[str, Callable],
    *args,
    **kwargs
) -> Any:
    """
    Try to resolve a value:
    - If it's a callable, call it
    - If it's a string path to function, import and call it
    - If import/call fails, return the string as-is (assumed to be path)
    """
    if isinstance(value, (dict, list, tuple, set)):
        return value

    if callable(value):
        try:
            return value(*args, **kwargs)
        except Exception:
            ...

    if isinstance(value, str):
        try:
            func = import_from_string(value)
            return func(*args, **kwargs)
        except (ImportError, AttributeError, ValueError) as e:
            ...

    return value






