import click
from lxml import etree


def get_row_values(elem):
    for n, child in enumerate(elem.getchildren()):
        if n != 2:  # 去除第3列：Structure
            text = '|'.join(t.strip().replace('\n', ';') for n, t in enumerate(child.itertext()) if t.strip())
            yield text


def extract_text_from_rows(file_path, chunk_size=1024*1024):
    with open(file_path, 'r', encoding='utf-8') as file:
        # 创建一个 XMLPullParser 实例，监听 'end' 事件，针对 'row' 标签
        namespace = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
        row_tag = f"{{{namespace}}}row"

        xml_parser = etree.XMLPullParser(events=('end',), tag=row_tag)
        
        while True:
            # 读取文件的一块数据
            chunk = file.read(chunk_size)
            if not chunk:
                break
            # 将数据块传递给解析器
            # print(chunk)
            xml_parser.feed(chunk)

            # 处理解析器中已完成的事件
            for event, elem in xml_parser.read_events():
                values = '\t'.join(list(get_row_values(elem)))
                print(values)
                elem.clear()  # 清理已处理的元素以释放内存

            # break

        # 处理文件结束后任何剩余的缓冲区内容
        for event, elem in xml_parser.read_events():
            values = '\t'.join(list(get_row_values(elem)))
            print(values)
            elem.clear()
            

@click.command(
    no_args_is_help=True,
)
@click.option('-i', '--infile', help='the input file', type=click.Path(exists=True))
@click.option('-o', '--outfile', help='the output file', type=click.Path())
def main(infile, outfile):
    extract_text_from_rows(infile)


if __name__ == '__main__':
    main()
