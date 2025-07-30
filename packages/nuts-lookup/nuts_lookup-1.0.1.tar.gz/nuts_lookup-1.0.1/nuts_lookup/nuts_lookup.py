import sqlite3
import importlib.resources

class NutsLookup:
    def __init__(self):
        with importlib.resources.path("nuts_lookup.data", "nuts.db") as db_path:
            disk_conn = sqlite3.connect(str(db_path))
            self._conn = sqlite3.connect(":memory:")
            disk_conn.backup(self._conn)
            disk_conn.close()

    def get_nuts_code(self, country_alpha2, zip_code):
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT nuts_3 FROM nuts WHERE alpha_2 = ? AND zip = ?",
            (country_alpha2.upper(), zip_code)
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def get_nuts0_code(self, country_alpha2, zip_code):
        nuts3 = self.get_nuts_code(country_alpha2, zip_code)
        return nuts3[:2] if nuts3 else None

    def get_nuts1_code(self, country_alpha2, zip_code):
        nuts3 = self.get_nuts_code(country_alpha2, zip_code)
        return nuts3[:3] if nuts3 else None

    def get_nuts2_code(self, country_alpha2, zip_code):
        nuts3 = self.get_nuts_code(country_alpha2, zip_code)
        return nuts3[:4] if nuts3 else None
