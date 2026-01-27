from ij.gui import GenericDialog



class OptionsDialog(GenericDialog):


    def __init__(self, options):
        super(OptionsDialog, self).__init__(options.optionsName)
        self.options = options
        self.addFields()
        
        
    def addFields(self):
        for name, item in self.options.items.items():
            if item['type'] == 'int':
                self.addNumericField(name, float(item['value']), 0)
            if item['type'] == 'float':
                self.addNumericField(name, item['value'])
            if item['type'] == 'bool':
                self.addCheckbox(name, item['value'])
        
        
    def transferValues(self):
        for name, item in self.options.items.items():
             if item['type'] == 'int':
                item['value'] = int(self.getNextNumber())
             if item['type'] == 'float':
                item['value'] = self.getNextNumber()
             if item['type'] == 'bool':
                item['value'] = self.getNextBoolean()
             
            