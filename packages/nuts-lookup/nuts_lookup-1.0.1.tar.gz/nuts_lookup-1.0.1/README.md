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

### Examples

```bash
nuts-lookup DE 10115           # Outputs NUTS-3 code (e.g. DE300)
nuts-lookup DE 10115 --level 2 # Outputs NUTS-2 code (e.g. DE30)
nuts-lookup DE 10115 --level 1 # Outputs NUTS-1 code (e.g. DE3)
nuts-lookup DE 10115 --level 0 # Outputs NUTS-0 code (e.g. DE)
```

## License

MIT

---

## Eurostat Copyright Notice

Please note that nuts-lookup is not developed, maintained, or affiliated with Eurostat. The following copyright notice from Eurostat regards their data, which underpins nuts-lookup:

> In addition to the general copyright and licence policy applicable to the whole Eurostat website, the following specific provisions apply to the datasets you are downloading. The download and usage of these data is subject to the acceptance of the following clauses:
>
> The Commission agrees to grant the non-exclusive and not transferable right to use and process the Eurostat/GISCO geographical data downloaded from this page (the "data").
>
> The permission to use the data is granted on condition that:
>
> - the data will not be used for commercial purposes;
> - the source will be acknowledged. A copyright notice, as specified below, will have to be visible on any printed or electronic publication using the data downloaded from this page.

### Copyright Notice

When data downloaded from this page is used in any printed or electronic publication, in addition to any other provisions applicable to the whole Eurostat website, the data source will have to be acknowledged in the legend of the map and in the introductory page of the publication with the following copyright notice:

- EN: © EuroGeographics for the administrative boundaries
- FR: © EuroGeographics pour les limites administratives
- DE: © EuroGeographics bezüglich der Verwaltungsgrenzen

For publications in languages other than English, French, or German, the translation of the copyright notice in the language of the publication shall be used.

If you intend to use the data commercially, please contact EuroGeographics for information regarding their licence agreements.
