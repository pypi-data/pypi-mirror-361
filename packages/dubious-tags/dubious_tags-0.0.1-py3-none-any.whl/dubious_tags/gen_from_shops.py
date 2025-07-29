"""
for importing from similar list embedded in part of my other repository
I intend to move its contents over but it will take some time
"""
for entry in [
        ("shop", "library", """shop=library is quite unusual and surprising

Is it bookstore or library? Or something else? If shop=library is correct - what it means here?"""),
        ("shop", "Library", """shop=Library is quite unusual and surprising

Is it bookstore or library? Or something else? If shop=library is correct - what it means here?"""),

        ("shop", "theatre", "shop=theatre ? Is it a mistagged amenity=theatre? Is it a gift shop in a theatre ( https://wiki.openstreetmap.org/wiki/Tag:shop=gift ) ? Place selling theatre tickets? ( https://wiki.openstreetmap.org/wiki/Tag:shop=ticket or https://wiki.openstreetmap.org/wiki/Tag:vending%3Dadmission_tickets ) Is it a something else? It almost certainly is mistagged"), # create_notes_based_on_some_complex_filters.py detects it (in my automation scripts)
        ("shop", "marketplace", "shop=marketplace ? Is it an entire marketplace? ( https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dmarketplace ) Specific shop (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values) ? Something else? "),  # create_notes_based_on_some_complex_filters.py detects it (in my automation scripts)
        ("shop", "market", "shop=market ? Is it an entire marketplace? ( https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dmarketplace ) Specific shop (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values) ? Something else? "),  # create_notes_based_on_some_complex_filters.py detects it (in my automation scripts)
        ("shop", "bank", "shop=bank ? Is it a mistagged bank? Maybe it should be https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dbank ? Is it a place selling bank equipment (in such case shop=trade trade=bank_equipment would be likely better and more clear) ? Something else?"), # create_notes_based_on_some_complex_filters.py detects it (in my automation scripts)
        ("shop", "museum", "shop=museum ? Is it a mistagged tourism=museum? Is it a gift shop in a museum ( https://wiki.openstreetmap.org/wiki/Tag:shop=gift ) ? Place selling museum tickets? ( https://wiki.openstreetmap.org/wiki/Tag:shop=ticket or https://wiki.openstreetmap.org/wiki/Tag:vending%3Dadmission_tickets ) Is it a something else? It almost certainly is mistagged"),  # create_notes_based_on_some_complex_filters.py detects it (in my automation scripts)
]:
        if "'" in entry[0]:
            print(entry)
            raise
        if "'" in entry[1]:
            print(entry)
            raise
        if "'" in entry[2]:
            print(entry)
            raise
        print("""        {
            'key': '""" + entry[0] + """',
            'value': '""" + entry[1] + """',
            'tag_specific_comment': '""" + entry[2].replace("\n", "\\n") + """',
        },""")
