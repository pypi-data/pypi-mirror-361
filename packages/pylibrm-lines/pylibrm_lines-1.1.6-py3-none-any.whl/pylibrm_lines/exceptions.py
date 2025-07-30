
class LibMissing(Exception):
    def __init__(self):
        super().__init__("LIB rm_lines was not loaded properly")

class FailedToBuildTree(Exception):
    def __init__(self):
        super().__init__("A major issue occurred reading the LINES file and building the scene tree")

class FailedToConvertToJson(Exception):
    def __init__(self):
        super().__init__("An issue occurred while converting scene tree to json")

class FailedToConvertToMd(Exception):
    def __init__(self):
        super().__init__("An issue occurred while rendering to md")

class FailedToConvertToTxt(Exception):
    def __init__(self):
        super().__init__("An issue occurred while rendering to txt")

class NoSceneInfo(Exception):
    def __init__(self):
        super().__init__("The scene tree has no scene info.")
