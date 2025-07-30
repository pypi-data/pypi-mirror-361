# Constellation Enum

A Python enum for astronomical constellations with standard abbreviations.

This package provides a comprehensive enum of all 88 modern constellations recognized by the International Astronomical Union (IAU), along with their standard 3-letter abbreviations.

## Features

- ✨ All 88 IAU-recognized constellations
- 🔤 Standard 3-letter abbreviations
- 🐍 Pure Python, no dependencies
- 📝 Full type hints support

## Installation

```bash
pip install constellation-enum
```

## Usage

```python
from constellation import Constellation

# Example usage
print(Constellation.Andromeda)  # Directly access the enum member
print(Constellation['Andromeda'])  # Access by name
print(Constellation['And'])  # Access by abbreviation

# Accessing name, abbreviation, and value
print(Constellation.Andromeda.name)  # 'Andromeda'
print(Constellation.Andromeda.abbr)  # 'And'
print(Constellation.Andromeda.value)  # 1 (auto-assigned value)

# Comparing enum members
print(Constellation.Andromeda == Constellation['And'])  # True

# Iterate through all constellations
for constellation in Constellation:
    print(f"{constellation.name} ({constellation.abbr})")
```

## All Constellations

The enum includes all 88 modern constellations:

- Andromeda (And), Antlia (Ant), Apus (Aps), Aquarius (Aqr), Aquila (Aql)
- Ara (Ara), Aries (Ari), Auriga (Aur), Boötes (Boo), Caelum (Cae)
- And 78 more...

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
```