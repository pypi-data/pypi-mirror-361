import pluggy
from .hookspecs import winzySpec

import sys
from runpy import run_module

pm = pluggy.PluginManager("winzy")
pm.add_hookspecs(winzySpec)


def load_plugins():
    if not getattr(sys, "_called_from_test", False):
        # Only load plugins if not running tests
        pm.load_setuptools_entrypoints("winzy.plugins")


def get_plugins(args):
    plugins = []
    if not getattr(sys, "_called_from_test", False):
        plugin_to_distinfo = dict(pm.list_plugin_distinfo())
        for plugin in pm.get_plugins():
            plugin_info = {
                "name": plugin.__name__,
                "hooks": [h.name for h in pm.get_hookcallers(plugin)],
            }
            distinfo = plugin_to_distinfo.get(plugin)
            if distinfo:
                plugin_info["version"] = distinfo.version
                plugin_info["name"] = distinfo.project_name
            plugins.append(plugin_info)

    if plugins:
        print("Installed Plugins:")
        for p in plugins:
            print(p["name"])
    else:
        print("No external plugins in env.")
    return plugins


def install_plugin(packages, upgrade, editable, force_reinstall, no_cache_dir):
    """Install packages from PyPI into the same environment as winzy"""
    args = ["pip", "install"]
    if upgrade:
        args += ["--upgrade"]
    if editable:
        args += ["--editable", editable]
    if force_reinstall:
        args += ["--force-reinstall"]
    if no_cache_dir:
        args += ["--no-cache-dir"]
    args += list(packages)
    sys.argv = args
    run_module("pip", run_name="__main__")
