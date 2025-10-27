class Package:
    def __init__(self,name,parent_package):
        self.name = name
        self.paren_package:Package|None = parent_package
        self.package_list:list[Package] = []
        self.function_list:list[Function] = []

    def reg_package(self,package):
        self.package_list.append(package)

    def reg_function(self,function):
        self.function_list.append(function)

class Function:
    def __init__(self,name,args:list):
        self.name = name
        self.args = args

    def execute(self):
        return self.args