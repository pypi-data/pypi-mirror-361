from pkgutil import ModuleInfo
from types import ModuleType


def import_module_from_info(module_info: ModuleInfo) -> ModuleType:
    """Import a module from a ModuleInfo object."""
    finder = module_info.module_finder
    spec = finder.find_spec(module_info.name)  # type: ignore[call-arg]
    module = spec.loader.load_module(module_info.name)  # type: ignore[union-attr]
    return module  # noqa: RET504
