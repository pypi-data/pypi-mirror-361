import copy
import click

import os
import sys
import pathlib
from types import ModuleType

from archtool.dependency_injector import DependencyInjector


CONFIG_FODER = pathlib.Path("/var/dpod")
# initial_folder = pathlib.Path("/var/dpod")


# TODO: отладочное значение
# DIRECTORY_PATH = pathlib.Path(__file__).parents[2]
# TODO: решение при сдорке
DIRECTORY_PATH = pathlib.Path(__file__).parent.parent
if not DIRECTORY_PATH.exists():
    DIRECTORY_PATH.mkdir(parents=True, exist_ok=True)



os.chdir(DIRECTORY_PATH.as_posix())
sys.path.insert(1, DIRECTORY_PATH.as_posix())
sys.path.append(pathlib.Path(__file__).parents[2].as_posix())


from dpod.archtool_conf.bundle_project import bundle
from dpod.core.deps import USER_PATH_LOCATION


def create_app() -> tuple[DependencyInjector]:
    injector = bundle(DIRECTORY_PATH, CONFIG_FODER)
    return injector


# if __name__ == "__main__":
injector = create_app()
cli = injector.get_dependency(click.Group)
cli()
