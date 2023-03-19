import enum

from zerotools.zero.names import IG_MSG, M_EVENTS
from zerotools.text.message.locale import Locale


class MessageNames(enum.Enum):
    IG_MSG = IG_MSG
    M0_EVENT = M_EVENTS[0]
    M1_EVENT = M_EVENTS[1]
    M2_EVENT = M_EVENTS[2]
    M3_EVENT = M_EVENTS[3]
    M4_EVENT = M_EVENTS[4]

    def to_locale_file_name(self, locale: Locale):
        if locale in (Locale.US, Locale.JP):
            return f"{self.name}.OBJ"

        elif locale == Locale.EN:
            return f"{self.name}_E.OBJ"

        elif locale == Locale.FR:
            return f"{self.name}_F.OBJ"

        elif locale == Locale.GE:
            return f"{self.name}_G.OBJ"

        elif locale == Locale.SP:
            return f"{self.name}_S.OBJ"

        elif locale == Locale.IT:
            return f"{self.name}_I.OBJ"
