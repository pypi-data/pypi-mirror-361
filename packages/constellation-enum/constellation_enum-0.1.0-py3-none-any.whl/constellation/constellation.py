from enum import Enum, auto

class Constellation(Enum):
    Andromeda = auto()
    Antlia = auto()
    Apus = auto()
    Aquarius = auto()
    Aquila = auto()
    Ara = auto()
    Aries = auto()
    Auriga = auto()
    Bootes = auto()
    Caelum = auto()
    Camelopardalis = auto()
    Cancer = auto()
    CanesVenatici = auto()
    CanisMajor = auto()
    CanisMinor = auto()
    Capricornus = auto()
    Carina = auto()
    Cassiopeia = auto()
    Centaurus = auto()
    Cepheus = auto()
    Cetus = auto()
    Chamaeleon = auto()
    Circinus = auto()
    Columba = auto()
    ComaBerenices = auto()
    CoronaAustralis = auto()
    CoronaBorealis = auto()
    Corvus = auto()
    Crater = auto()
    Crux = auto()
    Cygnus = auto()
    Delphinus = auto()
    Dorado = auto()
    Draco = auto()
    Equuleus = auto()
    Eridanus = auto()
    Fornax = auto()
    Gemini = auto()
    Grus = auto()
    Hercules = auto()
    Horologium = auto()
    Hydra = auto()
    Hydrus = auto()
    Indus = auto()
    Lacerta = auto()
    Leo = auto()
    LeoMinor = auto()
    Lepus = auto()
    Libra = auto()
    Lupus = auto()
    Lynx = auto()
    Lyra = auto()
    Mensa = auto()
    Microscopium = auto()
    Monoceros = auto()
    Musca = auto()
    Norma = auto()
    Octans = auto()
    Ophiuchus = auto()
    Orion = auto()
    Pavo = auto()
    Pegasus = auto()
    Perseus = auto()
    Phoenix = auto()
    Pictor = auto()
    Pisces = auto()
    PiscisAustrinus = auto()
    Puppis = auto()
    Pyxis = auto()
    Reticulum = auto()
    Sagitta = auto()
    Sagittarius = auto()
    Scorpius = auto()
    Sculptor = auto()
    Scutum = auto()
    Serpens = auto()
    Sextans = auto()
    Taurus = auto()
    Telescopium = auto()
    Triangulum = auto()
    TriangulumAustrale = auto()
    Tucana = auto()
    UrsaMajor = auto()
    UrsaMinor = auto()
    Vela = auto()
    Virgo = auto()
    Volans = auto()
    Vulpecula = auto()

    # Aliases for convenience
    And = Andromeda
    Ant = Antlia
    Aps = Apus
    Aqr = Aquarius
    Aql = Aquila
    # Ara = Ara
    Ari = Aries
    Aur = Auriga
    Boo = Bootes
    Cae = Caelum
    Cam = Camelopardalis
    Cnc = Cancer
    CVn = CanesVenatici
    CMa = CanisMajor
    CMi = CanisMinor
    Cap = Capricornus
    Car = Carina
    Cas = Cassiopeia
    Cen = Centaurus
    Cep = Cepheus
    Cet = Cetus
    Cha = Chamaeleon
    Cir = Circinus
    Col = Columba
    Com = ComaBerenices
    CrA = CoronaAustralis
    CrB = CoronaBorealis
    Crv = Corvus
    Crt = Crater
    Cru = Crux
    Cyg = Cygnus
    Del = Delphinus
    Dor = Dorado
    Dra = Draco
    Equ = Equuleus
    Eri = Eridanus
    For = Fornax
    Gem = Gemini
    Gru = Grus
    Her = Hercules
    Hor = Horologium
    Hya = Hydra
    Hyi = Hydrus
    Ind = Indus
    Lac = Lacerta
    # Leo = Leo
    LMi = LeoMinor
    Lep = Lepus
    Lib = Libra
    Lup = Lupus
    Lyn = Lynx
    Lyr = Lyra
    Men = Mensa
    Mic = Microscopium
    Mon = Monoceros
    Mus = Musca
    Nor = Norma
    Oct = Octans
    Oph = Ophiuchus
    Ori = Orion
    Pav = Pavo
    Peg = Pegasus
    Per = Perseus
    Phe = Phoenix
    Pic = Pictor
    Psc = Pisces
    PsA = PiscisAustrinus
    Pup = Puppis
    Pyx = Pyxis
    Ret = Reticulum
    Sge = Sagitta
    Sgr = Sagittarius
    Sco = Scorpius
    Scl = Sculptor
    Sct = Scutum
    Ser = Serpens
    Sex = Sextans
    Tau = Taurus
    Tel = Telescopium
    Tri = Triangulum
    TrA = TriangulumAustrale
    Tuc = Tucana
    UMa = UrsaMajor
    UMi = UrsaMinor
    Vel = Vela
    Vir = Virgo
    Vol = Volans
    Vul = Vulpecula

    @classmethod
    def _initialize_abbreviations(cls):
        """Initialize abbreviations after all enum members are created."""
        # Create abbreviation mapping
        # abbreviations = {}
        # for name, member in cls.__members__.items():
        #     if len(name) == 3:
        #         # Find the full constellation that this abbreviation refers to
        #         for full_name, full_member in cls.__members__.items():
        #             if member == full_member and len(full_name) > 3:
        #                 abbreviations[full_member] = name
        #                 break
        #         # If it's a 3-letter name itself and has no longer equivalent, use itself
        #         if member not in abbreviations:
        #             abbreviations[member] = name
        # cls._abbreviations = abbreviations
        cls._abbreviations_ = {}
        for member in cls:
            for _name, _member in cls.__members__.items():
                if _member == member and len(_name) == 3:
                    cls._abbreviations_[member] = _name
                    break

    @property
    def abbr(self):
        """Return the 3-letter abbreviation for the constellation."""
        return getattr(self.__class__, '_abbreviations_', {}).get(self)


# Initialize abbreviations after class is fully created
Constellation._initialize_abbreviations()