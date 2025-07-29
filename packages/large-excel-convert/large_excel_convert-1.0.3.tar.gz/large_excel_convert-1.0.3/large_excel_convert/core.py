import zipfile

from lxml import etree


class ExcelParser(object):
    def __init__(self, file, tag='row', sheet=1, chunksize=4096):
        self.sheet = sheet
        self.chunksize = chunksize
        self.zip_handle = zipfile.ZipFile(file)

        self.namespace = self.get_namespace()
        self.namespaces = {None: self.namespace}

        self.shared_strings = self.get_shared_strings()

        self.tag = f'{{{self.namespace}}}{tag}' if self.namespace else tag

    def get_namespace(self):
        tree = etree.parse(self.zip_handle.open('xl/workbook.xml'))
        return list(tree.getroot().nsmap.values())[0]
    
    def get_shared_strings(self):
        if 'xl/sharedStrings.xml' not in self.zip_handle.namelist():
            return {}
        tree = etree.parse(self.zip_handle.open('xl/sharedStrings.xml'))
        elements = tree.findall('si/t', namespaces=self.namespaces)
        return dict((enumerate((e.text or '').strip() for e in elements)))

    def rows(self):
        xml_parser = etree.XMLPullParser(events=('end',), tag=self.tag)

        with self.zip_handle.open(f'xl/worksheets/sheet{self.sheet}.xml') as xml:
            for chunk in iter(lambda: xml.read(self.chunksize), b''):
                xml_parser.feed(chunk)
                yield from self.read_events(xml_parser)
        yield from self.read_events(xml_parser)

    def read_events(self, xml_parser):
        for action, row_element in xml_parser.read_events():
            values = list(self.get_row_values(row_element))
            yield values
            row_element.clear()

    def get_row_values(self, row_element):
        for cell in row_element.findall('c', namespaces=self.namespaces):
            cell_type = cell.get('t')
            v = cell.find('v', namespaces=self.namespaces)

            if cell_type == 's':
                value = self.shared_strings[int(v.text)]
            elif cell_type == 'inlineStr':
                value = ''.join(cell.itertext())
            else:
                value = v.text if v is not None else ''

            value = value.strip().replace('\n', ';')
            value = value.replace('\t', ' ')

            yield value
