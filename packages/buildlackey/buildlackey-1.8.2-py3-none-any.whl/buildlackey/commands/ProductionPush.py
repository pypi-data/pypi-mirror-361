
from logging import Logger
from logging import getLogger


from click import secho

from buildlackey.Environment import Environment

PYPI_PUSH: str = 'twine upload  dist/*'


class ProductionPush(Environment):
    def __init__(self):
        super().__init__()
        self.logger: Logger = getLogger(__name__)

    def execute(self):

        secho(f'{PYPI_PUSH}')
        status = self._runCommand(PYPI_PUSH)
        secho(f'{status=}')
