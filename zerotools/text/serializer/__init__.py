import enum


class LocalizationSerializerFormat(enum.Enum):
    FS = "FS"
    JSON = "JSON"
    XML = "XML"

    def __eq__(self, other):
        if id(other) == id(self):
            return True

        if isinstance(other, str):
            return self.value == other.upper()

        return False


LOCALIZATION_SERIALIZERS = tuple(s.value for s in LocalizationSerializerFormat)

TABLE_NAME_MIN_DIGIT = 4
