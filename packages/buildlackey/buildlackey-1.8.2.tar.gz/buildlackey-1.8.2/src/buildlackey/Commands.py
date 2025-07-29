
import logging
import logging.config

from importlib.resources import files

from importlib.resources.abc import Traversable

from json import load as jsonLoad

import click
from click import Option
from click import UNPROCESSED
from click import clear
from click import command
from click import option
from click import secho
from click import version_option
from click import Context

from buildlackey import __version__ as version
from buildlackey.PythonWarnings import PythonWarnings

from buildlackey.commands.Cleanup import Cleanup
from buildlackey.commands.Package import Package
from buildlackey.commands.RunMypy import RunMypy
from buildlackey.commands.UnitTests import UnitTests
from buildlackey.commands.ProductionPush import ProductionPush
from buildlackey.commands.UnitTestVerbosity import UnitTestVerbosity

RESOURCES_PACKAGE_NAME:       str = 'buildlackey.resources'
JSON_LOGGING_CONFIG_FILENAME: str = "loggingConfiguration.json"

EPILOG: str = 'Written by Humberto A. Sanchez II (humberto.a.sanchez.ii@gmail.com)'


"""
Put in type ignore because of strange error on that appeared on 8.1.4

buildlackey/Commands.py:80: error: Argument 1 has incompatible type "Callable[[], Any]"; expected <nothing>  [arg-type]
    @command
"""


def setUpLogging():
    """
    """
    traversable: Traversable = files(RESOURCES_PACKAGE_NAME) / JSON_LOGGING_CONFIG_FILENAME

    loggingConfigFilename: str = str(traversable)

    with open(loggingConfigFilename, 'r') as loggingConfigurationFile:
        configurationDictionary = jsonLoad(loggingConfigurationFile)

    logging.config.dictConfig(configurationDictionary)
    logging.logProcesses = False
    logging.logThreads = False


# noinspection PyUnusedLocal
def validateWarning(ctx: Context, param: Option, value: str) -> PythonWarnings:
    if value is None or value == '':
        enumValue: PythonWarnings = PythonWarnings.IGNORE
    else:
        enumValue = PythonWarnings(value)

    return enumValue


# noinspection PyUnusedLocal
def validateVerbosity(ctx: Context, param: Option, value: str) -> UnitTestVerbosity:
    """
    The enumeration conversion may fail with a BadParameter exception;

    Args:
        ctx:  Click Context
        param: The type of parameter
        value: The string value that was input

    Returns:  The original input value

    """
    if value is None or value == '':
        enumValue: UnitTestVerbosity = UnitTestVerbosity.DEFAULT
    else:
        enumValue = UnitTestVerbosity.toEnum(value)

    return enumValue


@command(epilog=EPILOG)
@version_option(version=f'{version}', message='%(prog)s version %(version)s')
@option('--warning',     '-w', default='ignore',   type=UNPROCESSED, callback=validateWarning, help='Use this option to control Python warnings')
@option('--verbosity',   '-v', default='default',  type=UNPROCESSED, callback=validateVerbosity, help='How verbose to be')
@option('--pattern',     '-p', default='Test*.py', help='Test files that match pattern will be loaded')
@option('--html',        '-h', default=False,      is_flag=True, help='Run the HTML rest runner')
@option('--report-name', '-r', default='Unit Test Report',       help='The HTML test report name')
@option('--source',      '-s', default='src',                    help='The project subdirectory where the source code resides')
def unittests(warning: PythonWarnings, verbosity: UnitTestVerbosity, pattern: str, html: bool, report_name: str, source: str):
    """
    \b
    Runs the unit tests for the project specified by the environment variables listed below.
    This command differs from the 'runtests' command in that it uses the unit test TestLoader
    discovery mechanism

    Environment Variables

        PROJECTS_BASE -  The local directory where the python projects are based
        PROJECT       -  The name of the project;  It should be a directory name

    \b
    However, if one or the other is not defined the command assumes it is executing in a CI
    environment and thus the current working directory is the project base directory.
    \b
    Legal values for -w/--warning are:

    \b
        default
        error
        always
        module
        once
        ignore      This is the default
    \b
    The default pattern is 'Test*.py'
    \b
    Legal values for -v/--verbosity are:
        quiet
        default     This is the default 🧐
        verbose
        loud

    The -h/--html flag runs the HTMLTestRunner and places the reports in the 'html_unit_test_reports' directory

    The -r/--report-name options names the HTML Test report

    The -s/--source option specifies the project subdirectory where the Python source code resides. The source
    default value is 'src'
    \b
    """
    setUpLogging()
    unitTests: UnitTests = UnitTests(warning=warning, pattern=pattern, verbosity=verbosity, html=html, reportName=report_name, sourceSubDirectory=source)

    unitTests.execute()
    ctx: Context = click.get_current_context()
    ctx.exit(unitTests.executionStatus)


@command(epilog=EPILOG)
@version_option(version=f'{version}', message='%(prog)s version %(version)s')
@option('--package-name', '-p', required=False, help='Use this option when the package name does not match the project name')
@option('--source',       '-s', default='src',   help='The project subdirectory where the source code resides')
def runmypy(package_name: str, source: str):
    """
    \b
    Runs the mypy checks for the project specified by the following environment variables
    \b
        PROJECTS_BASE -  The local directory where the python projects are based
        PROJECT       -  The name of the project;  It should be a directory name

    PROJECT is overridden if the developer specifies a package name

    The -s/--source option specifies the project subdirectory where the Python source code resides. The source
    default value is 'src'

    """
    runMyPy: RunMypy = RunMypy(packageName=package_name, sourceSubDirectory=source)
    runMyPy.execute()


@command(epilog=EPILOG)
@version_option(version=f'{version}', message='%(prog)s version %(version)s')
@option('--package-name', '-p', required=False, help='Use this option when the package name does not match the project name')
@option('--application-name', '-a', required=False, help='Use this option when the generated application name does not match the project name')
def cleanup(package_name: str, application_name: str):
    """
    \b
    Clean the build artifacts for the project specified by the following environment variables
    \b
        PROJECTS_BASE -  The local directory where the python projects are based
        PROJECT       -  The name of the project;  It should be a directory name

    PROJECT is overridden if the developer specifies a package name
    """
    setUpLogging()
    clean: Cleanup = Cleanup(packageName=package_name, applicationName=application_name)

    clean.execute()


@command(epilog=EPILOG)
@version_option(version=f'{version}', message='%(prog)s version %(version)s')
@option('--input-file', '-i', required=False,   help='Use input file to specify a set of commands to execute')
def package(input_file: str):
    """
    \b
    Creates the deployable for the project specified by the environment variables listed below
    \b
    Use the -i/--input-file option to specify a set of custom commands to execute to build
    your deployable

    Environment Variables
    \b
        PROJECTS_BASE -  The local directory where the python projects are based
        PROJECT       -  The name of the project;  It should be a directory name

    """
    setUpLogging()
    pkg: Package = Package(inputFile=input_file)

    pkg.execute()


@command(epilog=EPILOG)
@version_option(version=f'{version}', message='%(prog)s version %(version)s')
def prodpush():
    """
    \b
    Pushes the deployable to pypi.  The project is specified by the following environment variables
    \b
        PROJECTS_BASE -  The local directory where the python projects are based
        PROJECT       -  The name of the project;  It should be a directory name
    """
    productionPush: ProductionPush = ProductionPush()
    productionPush.execute()


@command()
@version_option(version=f'{version}', message='%(prog)s version %(version)s')
def buildlackey():
    clear()
    secho('Commands are:')
    secho('\tunittests')
    secho('\tcleanup:')
    secho('\trunmypy')
    secho('\tpackage')
    secho('\tprodpush')


if __name__ == "__main__":
    # unittests(['-w', 'ignore'])
    # runtests(['-w', 'default'])
    # noinspection SpellCheckingInspection
    # runmypy([])
    # cleanup(['--application-name', 'Pyut'])
    # deploy(['--help'])
    # unittests(['-s', '.'])
    unittests(['--version'])
