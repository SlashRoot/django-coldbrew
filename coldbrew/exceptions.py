class ColdBrewCompileError(SyntaxError):
    def __init__(self, location, error):
        self.coffee_error_location = location
        self.error = error
        super(ColdBrewCompileError, self).__init__('Compiling %s \n\n %s' % (location, error))