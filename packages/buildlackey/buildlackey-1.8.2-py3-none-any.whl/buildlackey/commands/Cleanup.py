
from logging import Logger
from logging import getLogger

from os import sep as osSep

from click import secho

from buildlackey.Environment import Environment

DELETE_DIST_BUILD:       str = 'rm -rfv dist build'
DELETE_GENERAL_EGG_INFO: str = "find . -type d -name '*'.egg-info -delete"
DELETE_LOG_FILES:        str = 'find . -type f -name "*.log"      -delete'
DELETE_EGGS:             str = 'rm -rfv .eggs'


class Cleanup(Environment):

    def __init__(self, packageName: str, applicationName: str):

        super().__init__()

        self.logger:           Logger = getLogger(__name__)
        self._packageName:     str    = packageName
        self._applicationName: str    = applicationName

    def execute(self):

        self._changeToProjectRoot()

        secho(f'{DELETE_DIST_BUILD}')
        status: int = self._runCommand(DELETE_DIST_BUILD)
        secho(f'{status=}')

        secho(f'{DELETE_GENERAL_EGG_INFO}')
        status = self._runCommand(DELETE_GENERAL_EGG_INFO)
        secho(f'{status=}')

        secho(f'{DELETE_LOG_FILES}')
        status = self._runCommand(DELETE_LOG_FILES)
        secho(f'{status=}')

        secho(f'{DELETE_EGGS}')
        status = self._runCommand(DELETE_EGGS)
        secho(f'{status=}')

        if self._packageName is None:
            packageName: str = self._projectDirectory
        else:
            packageName = self._packageName
        #
        # Works for setup.py.OLD projects
        #
        if self._applicationName is not None:
            PROJECT_EGG_INFO: str = f'rm -rfv {self._applicationName}.egg-info'
        else:
            PROJECT_EGG_INFO = f'rm -rfv {packageName}.egg-info'

        secho(f'{PROJECT_EGG_INFO}')
        status = self._runCommand(PROJECT_EGG_INFO)
        secho(f'{status=}')
        #
        # works for pyproject.toml projects; (https://packaging.python.org/en/latest/specifications/pyproject-toml/)
        #
        SRC_EGG_INFO: str = f'rm -rfv src{osSep}{packageName}.egg-info'
        secho(f'{SRC_EGG_INFO}')
        status = self._runCommand(SRC_EGG_INFO)
        secho(f'{status=}')
