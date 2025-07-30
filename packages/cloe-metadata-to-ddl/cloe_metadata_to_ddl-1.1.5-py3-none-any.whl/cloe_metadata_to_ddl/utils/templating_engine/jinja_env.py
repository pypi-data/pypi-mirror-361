import os

from jinja2 import Environment, PackageLoader


def get_jinja_env(loader: PackageLoader | None = None) -> Environment:
    build_variables = {
        name: val for name, val in os.environ.items() if "CLOE_BUILD_" in name
    }
    template_env = Environment(loader=loader)
    template_env.globals |= build_variables

    return template_env


def load_package(sql_system: str) -> Environment:
    package_loader = PackageLoader("cloe_metadata_to_ddl.utils.templates", sql_system)
    return get_jinja_env(package_loader)
