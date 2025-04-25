import xmlschema

class XsdParser:
    def __init__(self, filename):
        schema = xmlschema.XMLSchema(filename)

        # collect elements
        self.elements = {}
        for name, element in schema.elements.items():
            current = self.elements[name.lower()] = {}
            self._add_element(current, element)

    def _add_element(self, current, element):
        for e in element:
            if e.local_name is None:
                continue
            if len(e.findall('*')) < 1:
                # no childeren
                current[e.local_name.lower()] = e.local_name
            else:
                new = current[e.local_name.lower()] = {}
                self._add_element(new, e)

    def fieldName(self, layer_name, field_name):
        try:
            parts = field_name.split('_')
        except ValueError:
            return None

        try:
            element = self.elements[layer_name.split('_')[0]]['zaznamyobjektu']['zaznamobjektu']
            for p in parts:
                element = element[p]
            return element
        except KeyError:
            return None
