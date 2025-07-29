
from logging import Logger
from logging import getLogger

from pathlib import Path

from click import ClickException
from click import secho

from buildlackey.Environment import Environment

# noinspection SpellCheckingInspection
BUILD_WHEEL:   str = 'python -m build --sdist --wheel'


class Package(Environment):
    def __init__(self, inputFile: str):

        super().__init__()
        self.logger: Logger = getLogger(__name__)

        self._inputFile: str = inputFile

    def execute(self):

        self._changeToProjectRoot()

        if self._inputFile is None:
            secho(f'{BUILD_WHEEL}')
            status: int = self._runCommand(BUILD_WHEEL)
            secho(f'{status=}')

            CHECK_PACKAGE: str = 'twine check dist/*'
            secho(f'{CHECK_PACKAGE}')
            status = self._runCommand(CHECK_PACKAGE)
            secho(f'{status=}')
        else:
            path: Path = Path(self._inputFile)
            if path.exists() is True:
                with path.open(mode='r') as fd:
                    cmd: str = fd.readline()
                    while cmd != '':
                        secho(f'{cmd}')
                        status = self._runCommand(f'{cmd}')
                        if status != 0:
                            exit(status)
                        cmd = fd.readline()
            else:
                raise ClickException(f'No such file: {self._inputFile}')
