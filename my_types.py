class ExportPreset:
    """
    DataType class - export preset
    """
    def __init__(self, side, length, quality):
        self.side = side
        self.length = int(length)
        self.quality = int(quality)

    def __repr__(self):
        return f"{self.side}:{self.length}:{self.quality}"
