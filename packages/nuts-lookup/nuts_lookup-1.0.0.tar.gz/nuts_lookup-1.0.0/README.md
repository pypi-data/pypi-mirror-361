# nuts-lookup

Quick lookup of NUTS codes (NUTS-0, NUTS-1, NUTS-2, NUTS-3) by country (Alpha-2) and postal code using a compact in-memory SQLite database.

## Installation
```bash
pip install nuts-lookup
```

## Python API

```python
from nuts_lookup import NutsLookup

lookup = NutsLookup()
print(lookup.get_nuts_code("DE", "10115"))    # Example: 'DE300' (NUTS-3)
print(lookup.get_nuts2_code("DE", "10115"))   # Example: 'DE30'  (NUTS-2)
print(lookup.get_nuts1_code("DE", "10115"))   # Example: 'DE3'   (NUTS-1)
print(lookup.get_nuts0_code("DE", "10115"))   # Example: 'DE'    (NUTS-0)
```

## CLI

After installation, the `nuts-lookup` command is available:

```bash
nuts-lookup <COUNTRY_CODE> <POSTAL_CODE> [--level 0|1|2|3]
```

- `--level` specifies the desired NUTS level (0, 1, 2, or 3). Default is 3 (NUTS-3).

**Examples:**
```bash
nuts-lookup DE 10115           # Outputs NUTS-3 code (e.g. DE300)
nuts-lookup DE 10115 --level 2 # Outputs NUTS-2 code (e.g. DE30)
nuts-lookup DE 10115 --level 1 # Outputs NUTS-1 code (e.g. DE3)
nuts-lookup DE 10115 --level 0 # Outputs NUTS-0 code (e.g. DE)
```

## License
MIT
