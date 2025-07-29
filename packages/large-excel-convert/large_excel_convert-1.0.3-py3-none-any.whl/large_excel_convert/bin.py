import sys
import time

import click
import loguru
from humanfriendly import parse_size, format_timespan

from large_excel_convert import version_info
from large_excel_convert.core import ExcelParser


CONTEXT_SETTINGS = dict(help_option_names=['-?', '-h', '--help'])

epilog = '''
\b
\x1b[33m
example:
    {prog} -i input.xlsx
    {prog} -i input.xlsx -o output.csv
    {prog} -i input.xlsx -o output.csv -enc gb18030
    {prog} -i input.xlsx -o output.tsv -f tsv
    {prog} -i input.xlsx -o sheet2.csv -s 2

\x1b[3;39m
contact: {author} <{author_email}>
'''.format(**version_info)



@click.command(
    name=version_info['prog'],
    help=click.style(version_info['desc'], fg='cyan'),
    epilog=epilog,
    no_args_is_help=True,
    context_settings=CONTEXT_SETTINGS,
)
@click.option('-i', '--input_file', help='The input Excel file path', type=click.Path(exists=True), required=True)
@click.option('-o', '--output_file', help='The output CSV file path [default: stdout]')
@click.option('-t', '--tag', help='the tag to extract', default='row', show_default=True)
@click.option('-f', '--output-format', help='the format of the output file', type=click.Choice(['csv', 'tsv']), default='csv', show_default=True)
@click.option('-s', '--sheet', help='the sheet to extract', type=int, default=1, show_default=True)
@click.option('-enc', '--encoding', help='the encoding of the output file', default='utf-8', show_default=True)
@click.option('--chunksize', help='the chunk size of the input file', default='4096', show_default=True)
@click.version_option(prog_name=version_info['prog'], version=version_info['version'])
def cli(input_file, output_file, tag, output_format, sheet, encoding, chunksize):

    start_time = time.time()

    loguru.logger.debug(f'input_file: {input_file}')
    loguru.logger.debug(f'output_file: {output_file}')
    loguru.logger.debug(f'tag: {tag}')
    loguru.logger.debug(f'output_format: {output_format}')
    loguru.logger.debug(f'sheet: {sheet}')
    loguru.logger.debug(f'encoding: {encoding}')
    loguru.logger.debug(f'chunksize: {chunksize}')

    out = open(output_file, 'w', encoding=encoding) if output_file else sys.stdout
    if output_format == 'tsv':
        sep = '\t'
    else:
        sep = ','

    chunksize = parse_size(chunksize, binary=True)

    excel = ExcelParser(input_file, tag=tag, sheet=sheet, chunksize=chunksize)
    loguru.logger.debug(f'namespace: {excel.namespace}')
    with out:
        for n, row in enumerate(excel.rows(), 1):
            line = sep.join(row)
            out.write(line + '\n')

            if n % 10000 == 0:
                loguru.logger.debug(f'processed {n} rows')

    loguru.logger.debug(f'processed {n} rows')
    loguru.logger.debug(f'save file to: {output_file}')
    time_taken = format_timespan(time.time() - start_time)
    loguru.logger.debug(f'time taken: {time_taken}')


def main():
    cli()


if __name__ == '__main__':
    main()
