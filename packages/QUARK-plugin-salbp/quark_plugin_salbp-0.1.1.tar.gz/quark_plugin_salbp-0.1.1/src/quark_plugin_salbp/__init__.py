from quark.plugin_manager import factory

from quark_plugin_salbp.salbp_instance_provider import SalbpInstanceProvider
from quark_plugin_salbp.salbp_mip_mapping import SalbpMipMapping


def register() -> None:
    """
    Register all modules exposed to quark by this plugin.
    For each module, add a line of the form:
        factory.register("module_name", Module)

    The "module_name" will later be used to refer to the module in the configuration file.
    """
    factory.register("salbp_instance_provider", SalbpInstanceProvider)
    factory.register("salbp_mip_mapping", SalbpMipMapping)
