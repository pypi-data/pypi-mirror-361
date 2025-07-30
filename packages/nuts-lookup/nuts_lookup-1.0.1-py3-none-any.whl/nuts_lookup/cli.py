import argparse
from nuts_lookup import NutsLookup

def main():
    parser = argparse.ArgumentParser(
        description="Lookup NUTS codes by country and postal code."
    )
    parser.add_argument("country_code", help="Country code (Alpha-2)")
    parser.add_argument("postal_code", help="Postal code")
    parser.add_argument(
        "--level",
        type=int,
        choices=[0, 1, 2, 3],
        default=3,
        help="NUTS level (0, 1, 2, or 3). Default is 3 (NUTS-3)."
    )

    args = parser.parse_args()
    lookup = NutsLookup()

    if args.level == 0:
        code = lookup.get_nuts0_code(args.country_code, args.postal_code)
    elif args.level == 1:
        code = lookup.get_nuts1_code(args.country_code, args.postal_code)
    elif args.level == 2:
        code = lookup.get_nuts2_code(args.country_code, args.postal_code)
    else:
        code = lookup.get_nuts_code(args.country_code, args.postal_code)

    if code:
        print(code)
    else:
        print("No NUTS code found.", flush=True)

if __name__ == "__main__":
    main()
