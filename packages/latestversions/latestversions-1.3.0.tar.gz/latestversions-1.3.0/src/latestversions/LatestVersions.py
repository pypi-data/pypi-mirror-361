
from typing import NewType
from typing import Tuple

from logging import Logger
from logging import getLogger

import logging.config

from os import sep as osSep

from json import load as jsonLoad

from subprocess import CompletedProcess
from subprocess import run as subProcessRun

from platform import platform as osPlatform

from click import command
from click import ClickException

from click import version_option
from click import option

from click import secho as clickSEcho
from click import open_file

from codeallybasic.ResourceManager import ResourceManager

from latestversions import __version__


THE_GREAT_MAC_PLATFORM: str = 'macOS'

# noinspection SpellCheckingInspection
PACKAGE_NAME:                 str = 'latestversions'
DEBUG_LOGGER_NAME:            str = 'PackageVersions'
JSON_LOGGING_CONFIG_FILENAME: str = "loggingConfiguration.json"
RESOURCES_PATH:               str = f'{PACKAGE_NAME}{osSep}resources'
RESOURCES_PACKAGE_NAME:       str = f'{PACKAGE_NAME}.resources'

CURL_CMD:         str = 'curl'
JQ_CMD:           str = 'jq'
MAC_OS_JQ_PATH:   str = f'/opt/homebrew/bin/{JQ_CMD} --version'
LINUX_OS_JQ_PATH: str = f'/usr/bin/{JQ_CMD} --version'

NON_MAC_OS_LS_PATH: str = '/usr/bin/ls'

MAC_OS_CURL_PATH:   str = f'/usr/bin/{CURL_CMD} --help'
LINUX_OS_CURL_PATH: str = f'/usr/bin/{CURL_CMD} --help'

JQ_FILTER_CMD:     str = "jq -r '.info.version'"

DEFAULT_OUTPUT_FILE_NAME: str = 'latestVersions.txt'
CLICK_STDOUT_INDICATOR:   str = '-'

PackageNames = NewType('PackageNames', Tuple[str])


class LatestVersions:
    """
    Let's us check the latest version of a package

    curl -s https://pypi.org/pypi/buildlackey/json | jq -r '.info.version'
    """
    def __init__(self):
        self.logger: Logger = getLogger(DEBUG_LOGGER_NAME)

    def report(self, packageNames: PackageNames, outputFileName: str):

        self.logger.info(f'I am reporting you to the IRS')

        if not self._checkJQInstalled():
            raise ClickException(f'{JQ_CMD} is not installed')
        if not self._checkCurlInstalled():
            raise ClickException(f'{CURL_CMD} not installed')

        clickSEcho('Dependencies are present')
        if outputFileName is None:
            outputFileName = CLICK_STDOUT_INDICATOR
        with open_file(outputFileName, 'w') as outputFile:

            for packageName in packageNames:
                self.logger.info(f'{packageName=}')
                checkCmd: str = (
                    f"curl -s https://pypi.org/pypi/{packageName}/json | jq -r '.info.version'"
                )
                completedProcess: CompletedProcess = subProcessRun([checkCmd], shell=True, capture_output=True, text=True, check=False)
                if completedProcess.returncode == 0:
                    versionDescription: str = f'{packageName}=={completedProcess.stdout}'
                    self.logger.debug(versionDescription)
                    outputFile.write(versionDescription)

        if outputFileName != CLICK_STDOUT_INDICATOR:
            clickSEcho(f'')
            clickSEcho(f'Output written to {outputFileName}', italic=True)

    def _checkJQInstalled(self) -> bool:
        """
        Returns: `True` if the JSON processor is installed else `False`
        """
        platform: str = osPlatform(terse=True)
        if platform.startswith(THE_GREAT_MAC_PLATFORM):
            return self._checkInstallation(MAC_OS_JQ_PATH)
        else:
            return self._checkInstallation(NON_MAC_OS_LS_PATH)

    def _checkCurlInstalled(self) -> bool:
        return self._checkInstallation(MAC_OS_CURL_PATH)

    def _checkInstallation(self, commandToCheck) -> bool:
        ans:    bool = False
        status: int  = LatestVersions.runCommand(commandToCheck)
        if status == 0:
            ans = True
        return ans

    @classmethod
    def runCommand(cls, programToRun: str) -> int:
        """

        Args:
            programToRun:  What must be executed

        Returns:  The status return of the executed program
        """
        completedProcess: CompletedProcess = subProcessRun([programToRun], shell=True, capture_output=True, text=True, check=False)
        return completedProcess.returncode

    @classmethod
    def setupSystemLogging(cls):

        configFilePath: str = ResourceManager.retrieveResourcePath(bareFileName=JSON_LOGGING_CONFIG_FILENAME,
                                                                   resourcePath=RESOURCES_PATH,
                                                                   packageName=RESOURCES_PACKAGE_NAME)
        with open(configFilePath, 'r') as loggingConfigurationFile:
            configurationDictionary = jsonLoad(loggingConfigurationFile)

        logging.config.dictConfig(configurationDictionary)
        logging.logProcesses = False
        logging.logThreads   = False


@command()
@version_option(version=f'{__version__}', message='%(version)s')
@option('--package-name', '-p', multiple=True, required=True, help='Specify package names')
@option('-o', '--output-file', required=False, help='The optional file.')
def commandHandler(package_name: PackageNames, output_file: str):
    """
    \b
    This command reports the latest package versions of the specified input packages
    \b
    By default output is written to stdout

    """
    LatestVersions.setupSystemLogging()

    packageVersions: LatestVersions = LatestVersions()
    packageVersions.report(packageNames=package_name, outputFileName=output_file)


if __name__ == "__main__":

    commandHandler(['--package-name', 'setuptools', '--package-name', 'twine'])
