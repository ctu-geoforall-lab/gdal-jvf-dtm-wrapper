import xmlschema

class XsdParser:
    def __init__(self, filename: str):
        """Initialize XSD parser.

        :param str filename: path to main XSD file
        """
        schema = xmlschema.XMLSchema(filename)

        # collect elements
        self.elements = {}
        for name, element in schema.elements.items():
            current = self.elements[name] = {}
            self._add_element(current, element)

    def _add_element(self, current: dict, element: xmlschema.validators.elements.XsdElement):
        """Add element to the tree.
        """
        for e in element:
            if e.local_name is None:
                continue
            if len(e.findall('*')) < 1:
                # no childeren
                current[e.local_name] = e.local_name
            else:
                new = current[e.local_name] = {}
                self._add_element(new, e)

    def fieldName(self, layer_name: str, field_name: str) -> str:
        """Print get field name.

        :param str layer_name: layer name
        :param str field_name: GDAL field name
        """
        try:
            parts = field_name.split('_')
        except ValueError:
            return None

        try:
            element = self.elements[layer_name.split('_')[0]]['ZaznamyObjektu']['ZaznamObjektu']
            for p in parts:
                element = element[p]
            return element
        except KeyError:
            return None
