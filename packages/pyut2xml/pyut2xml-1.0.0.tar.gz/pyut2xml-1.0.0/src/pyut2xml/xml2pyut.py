
from zlib import compress
from zlib import ZLIB_VERSION

from click import ClickException
from click import command
from click import option
from click import version_option
from click import echo as clickEcho
from click import secho as clickSEcho

from pyut2xml import __version__ as pyut2xmlVersion

INPUT_SUFFIX:  str = '.xml'
OUTPUT_SUFFIX: str = '.put'


class Xml2Pyut:

    def __init__(self, inputFileName: str, outputFileName: str):

        if INPUT_SUFFIX in inputFileName:
            self._inputFileName: str = inputFileName
        else:
            self._inputFileName = f'{inputFileName}{INPUT_SUFFIX}'

        if outputFileName is None:
            clickSEcho('Using input file name as base for output file name', bold=True)
            baseName: str = inputFileName.replace(INPUT_SUFFIX, '')
            self._outputFileName: str = f'{baseName}{OUTPUT_SUFFIX}'
        elif OUTPUT_SUFFIX in outputFileName:
            self._outputFileName = outputFileName
        else:
            self._outputFileName = f'{outputFileName}{OUTPUT_SUFFIX}'

    def compress(self):
        try:
            clickSEcho(f'{ZLIB_VERSION=}', bold=True)
            rawXml:   str   = self.getRawXml(fqFileName=self._inputFileName)
            byteText: bytes = rawXml.encode()
            compressedBytes: bytes = compress(byteText)

            with open(self._outputFileName, "wb") as binaryIO:
                binaryIO.write(compressedBytes)

        except (ValueError, Exception) as e:
            clickEcho(f'Error:  {e}')

    def getRawXml(self, fqFileName: str) -> str:
        """
        method to read a file.  Assumes the file has XML.
        No check is done to verify this
        Args:
            fqFileName: The file to read

        Returns:  The contents of the file
        """
        try:
            with open(fqFileName, "r") as xmlFile:
                xmlString: str = xmlFile.read()
        except (ValueError, Exception) as e:
            raise ClickException(f'xml open:  {e}')

        return xmlString


@command()
@version_option(version=f'{pyut2xmlVersion}', message='%(version)s')
@option('-i', '--input-file',  required=True,  help='The input .xml file to compress.')
@option('-o', '--output-file', required=False, help='The output .put file.')
def commandHandler(input_file: str, output_file: str):

    xml2pyut: Xml2Pyut = Xml2Pyut(inputFileName=input_file, outputFileName=output_file)

    xml2pyut.compress()


if __name__ == "__main__":

    commandHandler()
