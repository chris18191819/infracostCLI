import sqlite3
import json


def flatten_pricing():
    conn = sqlite3.connect("pricing.db")
    conn.row_factory = sqlite3.Row
    print("Connecting to table")
    c = conn.cursor()

    # Create the new flattened table with extended primary key
    c.execute("""
    CREATE TABLE IF NOT EXISTS pricing_flat (
        service_code TEXT,
        region TEXT,
        sku TEXT,
        product_family TEXT,
        deploymentModel TEXT,
        regionCode TEXT,
        servicecode TEXT,
        usagetype TEXT,
        locationType TEXT,
        location TEXT,
        servicename TEXT,
        operation TEXT,
        deploymentModelDescription TEXT,
        term_type TEXT,
        offerTermCode TEXT,
        unit TEXT,
        endRange TEXT,
        price_description TEXT,
        beginRange TEXT,
        pricePerUnitUSD TEXT,
        effectiveDate TEXT,
        currency TEXT,
        PRIMARY KEY(
            service_code, region, sku, term_type, offerTermCode, unit, beginRange
        )
    )
    """)

    rows = c.execute("SELECT * FROM pricing").fetchall()

    for i, row in enumerate(rows):
        print(
            f"Processing row {i + 1}: sku={row['sku']}, service_code={row['service_code']}"
        )

        try:
            attributes = json.loads(row["attributes"]) if row["attributes"] else {}
        except Exception as e:
            print(f"Error parsing attributes for sku {row['sku']}: {e}")
            attributes = {}

        try:
            price_terms = (
                json.loads(row["price_dimensions"]) if row["price_dimensions"] else {}
            )
        except Exception as e:
            print(f"Error parsing price_dimensions for sku {row['sku']}: {e}")
            price_terms = {}

        # Loop through all term types (OnDemand, Reserved, etc.)
        for term_type, term_dict in price_terms.items():
            if not isinstance(term_dict, dict):
                continue
            for term_key, term_detail in term_dict.items():
                effectiveDate = term_detail.get("effectiveDate")
                offerTermCode = term_detail.get("offerTermCode")

                priceDimensions = term_detail.get("priceDimensions", {})
                # Insert one row per price dimension (if any)
                for pd_key, pd in priceDimensions.items():
                    unit = pd.get("unit")
                    endRange = pd.get("endRange")
                    price_description = pd.get("description")
                    beginRange = pd.get("beginRange")
                    pricePerUnit = pd.get("pricePerUnit", {})
                    pricePerUnitUSD = pricePerUnit.get("USD") or (
                        list(pricePerUnit.values())[0] if pricePerUnit else None
                    )

                    c.execute(
                        """
                        INSERT OR REPLACE INTO pricing_flat (
                            service_code, region, sku, product_family,
                            deploymentModel, regionCode, servicecode, usagetype,
                            locationType, location, servicename, operation,
                            deploymentModelDescription, term_type, offerTermCode,
                            unit, endRange, price_description, beginRange,
                            pricePerUnitUSD, effectiveDate, currency
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            row["service_code"],
                            row["region"],
                            row["sku"],
                            row["product_family"],
                            attributes.get("deploymentModel"),
                            attributes.get("regionCode"),
                            attributes.get("servicecode"),
                            attributes.get("usagetype"),
                            attributes.get("locationType"),
                            attributes.get("location"),
                            attributes.get("servicename"),
                            attributes.get("operation"),
                            attributes.get("deploymentModelDescription"),
                            term_type,
                            offerTermCode,
                            unit,
                            endRange,
                            price_description,
                            beginRange,
                            pricePerUnitUSD,
                            effectiveDate,
                            row["currency"],
                        ),
                    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    flatten_pricing()
