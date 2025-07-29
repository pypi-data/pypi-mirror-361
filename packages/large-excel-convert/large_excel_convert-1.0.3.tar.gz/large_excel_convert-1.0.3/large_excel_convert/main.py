import sys
import time
import zipfile

import click
import loguru
from lxml import etree


class ExcelParser(object):
    def __init__(self, file, tag='row', sheet=1, chunksize=1024*1024):
        self.sheet = sheet
        self.chunksize = chunksize
        self.zip_handle = zipfile.ZipFile(file)
        self.namespace = self.get_namespace()
        self.tag = f'{{{self.namespace}}}{tag}' if self.namespace else tag

    def get_namespace(self):
        tree = etree.parse(self.zip_handle.open('xl/workbook.xml'))
        return list(tree.getroot().nsmap.values())[0]

    def rows(self):
        xml_parser = etree.XMLPullParser(events=('end',), tag=self.tag)

        with self.zip_handle.open(f'xl/worksheets/sheet{self.sheet}.xml') as xml:
            for chunk in iter(lambda: xml.read(self.chunksize), b''):
                xml_parser.feed(chunk)
                yield from self.read_events(xml_parser)
        yield from self.read_events(xml_parser)

    def read_events(self, xml_parser):
        for action, elem in xml_parser.read_events():
            yield list(self.get_row_values(elem))
            elem.clear()


    @staticmethod
    def get_row_values(elem):
        for child in elem.getchildren():
            text = '|'.join(t.strip().replace('\n', ';') for n, t in enumerate(child.itertext()) if t.strip())
            yield text

CONTEXT_SETTINGS = dict(help_option_names=['-?', '-h', '--help'])


@click.command(
    no_args_is_help=True,
    context_settings=CONTEXT_SETTINGS,
)
@click.option('-i', '--input_file', help='The input Excel file path', type=click.Path(exists=True), required=True)
@click.option('-o', '--output_file', help='The output CSV file path [default: stdout]')
@click.option('-t', '--tag', help='the tag to extract', default='row', show_default=True)
@click.option('-f', '--output-format', help='the format of the output file', type=click.Choice(['csv', 'tsv']), default='csv', show_default=True)
@click.option('-s', '--sheet', help='the sheet to extract', type=int, default=1, show_default=True)
def main(input_file, output_file, tag, output_format):

    start_time = time.time()

    loguru.logger.debug(f'input_file: {input_file}')
    loguru.logger.debug(f'output_file: {output_file}')
    loguru.logger.debug(f'tag: {tag}')
    loguru.logger.debug(f'output_format: {output_format}')

    out = open(output_file, 'w') if output_file else sys.stdout
    if output_format == 'tsv':
        sep = '\t'
    else:
        sep = ','

    excel = ExcelParser(input_file)
    loguru.logger.debug(f'namespace: {excel.namespace}')
    with out:
        for n, row in enumerate(excel.rows(), 1):
            line = sep.join(row)
            out.write(line + '\n')

            if n % 10000 == 0:
                loguru.logger.debug(f'processed {n} rows')

    loguru.logger.debug(f'processed {n} rows')
    loguru.logger.debug(f'save file to: {output_file}')
    time_taken = time.time() - start_time
    loguru.logger.debug(f'time taken: {time_taken:.2f} seconds')


if __name__ == '__main__':
    main()
