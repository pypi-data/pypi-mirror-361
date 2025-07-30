from pluggy import HookimplMarker
from pluggy import HookspecMarker


hookspec = HookspecMarker("winzy")
hookimpl = HookimplMarker("winzy")


class winzySpec:
    @hookspec
    def register_commands(subparser):
        """Register additional CLI sub commands, e.g. 'winzy mycommand ...'"""
