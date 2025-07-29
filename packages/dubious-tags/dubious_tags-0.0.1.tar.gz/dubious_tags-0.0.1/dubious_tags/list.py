import taginfo
import osm_bot_abstraction_layer.tag_knowledge as tag_knowledge
import dubious_tags.unclear_shop_values_with_no_specific_comment
import simple_cache
import rich

def dubious_tags_with_explanation(specified_cache_folder=""):
    returned = []

    returned.append({"key": "amenity", "value": "playground", "tag_specific_comment": "Maybe leisure=playground was supposed to be here? See https://wiki.openstreetmap.org/wiki/Tag:leisure%3Dplayground\n\nIf yes, then it would be likely beneficial to retag it to that standard value. If using amenity= is intentional - what was meant here?"})
    for value in tag_knowledge.valid_shop_values():
        entry = {
            "key": "shop",
            "value": value + "q",
            "tag_specific_comment": "shop=" + value + "q" + " ? Maybe intention was to use shop=" + value + " and then square area? (though, as aside, buildings and shops ideally would be mapped as a separate objects, not merged into one)",
        }
        returned.append(entry)
    for entry in cached_taginfo_for_what_id_project_uses(specified_cache_folder):
        key = entry["key"]
        value = entry["value"]
        if value != None:
            if key != "shop": # covered by above
                if key in ["building", "power", "leisure"]:
                    entry = {
                        "key": key,
                        "value": value + "q",
                        "tag_specific_comment": key + "=" + value + "q" + " ? Maybe intention was to use " + key + "=" + value + " and then square area?",
                    }
                    returned.append(entry)
    for barrier in ["g", "G", "g'", "g#"]:
        entry = {
            "key": "barrier",
            "value": barrier,
            "tag_specific_comment": "what this tag means? Is it maybe supposed to be barrier=gate? Or is maybe some other barrier?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:barrier%3Dgate",
        }
        returned.append(entry)
    for barrier in ["w", "wa"]:
        entry = {
            "key": "barrier",
            "value": barrier,
            "tag_specific_comment": "what this tag means? Is it maybe supposed to be barrier=wall? Or is maybe some other barrier?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:barrier%3Dwall",
        }
        returned.append(entry)
    for barrier in ["low"]:
        entry = {
            "key": "barrier",
            "value": barrier,
            "tag_specific_comment": "what this tag means? Is it maybe supposed to be barrier=log? Or is small unspecified barrier?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:barrier%3Dlog",
        }
        returned.append(entry)

    for case in [
        {"value": "church", "tag_specific_comment": "Is it a a Christian place of worship? (amenity=place_of_worship religion=christian - see https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dplace_of_worship)\nIs it a religious office?\nSomething else?"},
        {"value": "stationary", "tag_specific_comment": "Is it an attempt to map shop=stationery? ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dstationery )\nSomething else?"},
        {"value": "flag", "tag_specific_comment": "Is it an attempt to map flagpole with a flag? Or is it flag that is painted, hanging from something else etc?\n\n( man_made=flagpole would fit for flagpoles, see https://wiki.openstreetmap.org/wiki/Tag:man_made%3Dflagpole )"},
        {"value": "stationary shop", "tag_specific_comment": "Is it an attempt to map shop=stationery? ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dstationery )\nSomething else?"},
        {"value": "weather station", "tag_specific_comment": "Is it an attempt to map weather monitoring station?\n\nWould https://wiki.openstreetmap.org/wiki/Tag:man_made%3Dmonitoring_station fit? Probably tagging would be monitoring:weather=yes + man_made=monitoring_station"},
        {"value": "метеостанция", "tag_specific_comment": "Is it an attempt to map weather monitoring station?\n\nWould https://wiki.openstreetmap.org/wiki/Tag:man_made%3Dmonitoring_station fit? Probably tagging would be monitoring:weather=yes + man_made=monitoring_station"},
        {"value": "veterinary_pharmacy", "tag_specific_comment": "Would https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dveterinary_pharmacy fit well here?"},
        {"value": "fix", "tag_specific_comment": "what should be fixed here? do you need help with selecting better tags?"},
        {"value": "street lights", "tag_specific_comment": "Is it an attempt to map stret lamp, as described at https://wiki.openstreetmap.org/wiki/Tag:highway%3Dstreet_lamp )\nSomething else?"},
        {"value": "primary school", "tag_specific_comment": "Would it be amenity=school ( https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dschool )\nSomething else?"},
        {"value": "hotel", "tag_specific_comment": "Would it be tourism=hotel ( https://wiki.openstreetmap.org/wiki/Tag:tourism%3Dhotel )\nSomething else?"},
        {"value": "gate", "tag_specific_comment": "Would it be barrier=gate ( https://wiki.openstreetmap.org/wiki/Tag:barrier%3Dgate )\nSomething else?"},
        {"value": "Sweets=Indian", "tag_specific_comment": "Would it be shop=confectiory cuisine=indian ? ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconfectionery )\nSomething else?"},
        {"value": "railway station", "tag_specific_comment": "Would it be railway=station ( https://wiki.openstreetmap.org/wiki/Tag:railay%3Dstation )\nSomething else?"},
        {"value": "rescue=ladder?", "tag_specific_comment": "Maybe https://taginfo.openstreetmap.org/tags/emergency%3Drescue_ladder ? But probably would be a good idea to discuss good tag on https://community.openstreetmap.org/c/general/tagging/70 and document it on OSM Wiki"},
        {"value": "rescue=life_ladder?", "tag_specific_comment": "Maybe https://taginfo.openstreetmap.org/tags/emergency%3Drescue_ladder ? But probably would be a good idea to discuss good tag on https://community.openstreetmap.org/c/general/tagging/70 and document it on OSM Wiki"},
        {"value": "stairs", "tag_specific_comment": "It should be mapped as line with highway=steps ( https://wiki.openstreetmap.org/wiki/Tag:highway%3Dsteps ) - not as this weird fixme object"},
        {"value": "steps", "tag_specific_comment": "It should be mapped as line with highway=steps ( https://wiki.openstreetmap.org/wiki/Tag:highway%3Dsteps ) - not as this weird fixme object"},
        {"value": "school", "tag_specific_comment": "Would it be amenity=school ( https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dschool )\nSomething else?"},
        {"value": "School", "tag_specific_comment": "Would it be amenity=school ( https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dschool )\nSomething else?"},
        {"value": "parking", "tag_specific_comment": "Is it a parking for cars? (amenity=parking)\nfor bicycles? (amenity=bicycle_parking)\nSomething else?"},
        {"value": "parkplatz", "tag_specific_comment": "Is it a parking for cars? (amenity=parking)\nfor bicycles? (amenity=bicycle_parking)\nSomething else?"},
        {"value": "coach", "tag_specific_comment": "Is it an office of the coach? The it is probably some kind of office tag, see https://wiki.openstreetmap.org/wiki/Key:office\nSomething else?"},    
        {"value": "toilet", "tag_specific_comment": "Is it a public toilet?\nSomething else?"},
        {"value": "emergency", "tag_specific_comment": "What kind of emergency feature is here?\n\nSee https://wiki.openstreetmap.org/wiki/Emergency_facilities_and_amenities"},
        {"value": "office", "tag_specific_comment": "What kind of office is here?\n\nIf unclear, maybe office=yes would fit? Already more clear than hopeless amenity=fixme\n\nSee https://wiki.openstreetmap.org/wiki/Key:office"},
        {"value": "офисы", "tag_specific_comment": "What kind of office is here?\n\nIf unclear, maybe office=yes would fit? Already more clear than hopeless amenity=fixme\n\nSee https://wiki.openstreetmap.org/wiki/Key:office"},
        {"value": "pharmacy", "tag_specific_comment": "Is it simply a pharmacy? Would it be fine to mark it as amenity=pharmacy?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dpharmacy"},
        {"value": "empty", "tag_specific_comment": "Is it a vacant space? Would shop=vacant be a good tagging here?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop%3Dvacant"},
        {"value": "tree", "tag_specific_comment": "Have you tried to map a tree here? If yes, then natural=tree would fit\n\nSee https://wiki.openstreetmap.org/wiki/Tag:natural%3Dtree"},
        {"value": "park", "tag_specific_comment": "Have you tried to map a park here? If yes, then maybe leisure=park would fit?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:leisure%3Dpark"},
        {"value": "hospital", "tag_specific_comment": "is it a doctor office?\n\nor nurse office?\n\nor is it a full scale hospital?\n\nor maybe something else?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dhospital"},
        {"value": "construction", "tag_specific_comment": "What kind of construction is here? Are they preparing shop? Building a house? Building a road? Bridge? Something else?\n\nIs this construction ongoing or completed already?"},
        {"value": "shop", "tag_specific_comment": "What kind of shop is here?\n\nSee https://wiki.openstreetmap.org/wiki/Key:shop for common values - is any of them fitting?"},
        {"value": "sklep", "tag_specific_comment": "Jaki rodzaj sklepu tu jest?\n\nhttps://wiki.openstreetmap.org/wiki/Pl:Key:shop może pomóc"},
        {"value": "wejście", "tag_specific_comment": "Czy chodziło o coś z https://wiki.openstreetmap.org/wiki/Pl:Key:entrance ?"},
        {"value": "store", "tag_specific_comment": "What kind of shop is here?\n\nSee https://wiki.openstreetmap.org/wiki/Key:shop for common values - is any of them fitting?"},
        {"value": "tienda", "tag_specific_comment": "What kind of shop is here?\n\nSee https://wiki.openstreetmap.org/wiki/Key:shop for common values - is any of them fitting?"},
        {"value": "wellness", "tag_specific_comment": "What kind of POI is here?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop=beauty - is it fitting?"},
        {"value": "barrier", "tag_specific_comment": "What kind of barrier is here?\n\nSee https://wiki.openstreetmap.org/wiki/Key:barrier - is any fitting?"},
        {"value": "barriere", "tag_specific_comment": "What kind of barrier is here?\n\nSee https://wiki.openstreetmap.org/wiki/Key:barrier - is any fitting?"},
        {"value": "wastebucket", "tag_specific_comment": "Is it amenity=waste_basket ? See https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dwaste_basket"},
        {"value": "geoglyp", "tag_specific_comment": "Is it geoglyph ? See https://wiki.openstreetmap.org/wiki/Tag:man_made%3Dgeoglyph"},
        {"value": "door", "tag_specific_comment": "Is it entrance from outside into building? If yes, which of values at https://wiki.openstreetmap.org/wiki/Key:entrance fits?"},
        {"value": "entrance", "tag_specific_comment": "Is it entrance from outside into building? If yes, which of values at https://wiki.openstreetmap.org/wiki/Key:entrance fits?"},
        {"value": "znak drogowy", "tag_specific_comment": "Jaki znak drogowy tu jest? Która wartość z https://wiki.openstreetmap.org/wiki/Pl:Znaki_drogowe_w_Polsce będzie poprawna tu?"},
        {"value": "amenity= ATM stand", "tag_specific_comment": "Have you tried to map ATM here?"},
        {"value": "ベンチ", "tag_specific_comment": "Have you tried to map a bench here? Then amenity=bench would likely fit, see https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dbench"},
        {"value": "カフェ", "tag_specific_comment": "Have you tried to map a cafe here? Then amenity=cafe would likely fit, see https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dcafe"},
        {"value": "無人精米所", "tag_specific_comment": "Would amenity=vending_machine vending=rice_polishing fit here? See https://wiki.openstreetmap.org/wiki/Tag:vending%3Drice_polishing"},
        {"value": "お土産", "tag_specific_comment": "Would shop=gift fit here? See https://wiki.openstreetmap.org/wiki/Tag:shop=gift"},
        {"value": "唐揚げ", "tag_specific_comment": "Would amenity=fast_food fit here? See https://wiki.openstreetmap.org/wiki/Tag:amenity=fast_food"},
        {"value": "bank", "tag_specific_comment": "Would amenity=bank fit here? See https://wiki.openstreetmap.org/wiki/Tag:amenity=bank"},
        {"value": "banco", "tag_specific_comment": "Would amenity=bank fit here? See https://wiki.openstreetmap.org/wiki/Tag:amenity=bank"},
        {"value": "hazard - slip risk", "tag_specific_comment": "Have you tried to map a warning sign placed here? Personal opinion?"},
        {"value": "barber", "tag_specific_comment": "Is it an attempt to map a place specializing in masculine style hair cuts ( https://wiki.openstreetmap.org/wiki/Tag:hairdresser%253Dbarber )?\n\nThen likely shop=hairdresser + hairdresser=barber is a good tagging"},
        {"value": "house", "tag_specific_comment": "Is it an attempt to map a building not present in OSM data? Is it an attempt to add address info to an already mapped building? Something else?"},
        {"value": "building", "tag_specific_comment": "Is it an attempt to map a building not present in OSM data? Is it an attempt to add address info to an already mapped building? Something else?\n\nSee https://overpass-turbo.eu/s/21o2 for more objects with this problem"},
        {"value": "bridge", "tag_specific_comment": "Is it an attempt to map a bridge not present in OSM data? Then https://wiki.openstreetmap.org/wiki/Tag:man_made%3Dbridge has info how to do it properly"},
        {"value": "no hunting", "tag_specific_comment": "Is it mapping 'no hunting' sign? Is it mapping something else?"},
        {"value": "flight school", "tag_specific_comment": "Flight school is typically mapped as amenity=flight_school, see https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dflight_school"},
        {"value": "дезинфектор", "tag_specific_comment": "Is it an attempt to map hand disinfector? Something else?"},
        {"value": "hand ball court", "tag_specific_comment": "hand ball court - would it be leisure=pitch + sport=handball? See https://wiki.openstreetmap.org/wiki/Tag:sport%3Dhandball"},
        {"value": "statue", "tag_specific_comment": "see https://wiki.openstreetmap.org/wiki/Statue for info how statues should be marked"},
        {"value": "pond", "tag_specific_comment": "that would be natural=water water=pond - right? See https://wiki.openstreetmap.org/wiki/Tag:water%3Dpond"},
        {"value": "Academia de Inglés", "tag_specific_comment": "that would be amenity=language_school - right? See https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dlanguage_school"},
        {"value": "healthcare", "tag_specific_comment": "What kind of healthcare object it is? See https://wiki.openstreetmap.org/wiki/Healthcare"},
        {"value": "health care", "tag_specific_comment": "What kind of healthcare object it is? See https://wiki.openstreetmap.org/wiki/Healthcare"},
        {"value": "health centre", "tag_specific_comment": "What kind of healthcare object it is? See https://wiki.openstreetmap.org/wiki/Healthcare"},
        {"value": "health post", "tag_specific_comment": "What kind of healthcare object it is? See https://wiki.openstreetmap.org/wiki/Healthcare"},
        {"value": "psychologue", "tag_specific_comment": "Would healthcare=psychotherapist fit here? See https://wiki.openstreetmap.org/wiki/Tag:healthcare%3Dpsychotherapist"},
        
    ]:
        returned.append({"key": "fixme:type", "value": case['value'], "tag_specific_comment": case["tag_specific_comment"]})
        returned.append({"key": "fixme:type", "value": case['value'].capitalize(), "tag_specific_comment": case["tag_specific_comment"]})

    returned.append({"key": "landuse", "value": "pond", "tag_specific_comment": "that would be natural=water water=pond - right? See https://wiki.openstreetmap.org/wiki/Tag:water%3Dpond"})
    returned.append({"key": "shop", "value": "internet", "tag_specific_comment": """What is mapped as shop=internet here ?

Is it an internet cafe (amenity=internet_cafe)?

Office where you can sign up for internet service?

Something related to online shopping (pickup point that nowadays is marked as shop=outpost? company office marked as office=company?)"""})
    returned.append({"key": "shop", "value": "Internet", "tag_specific_comment": """What is mapped as shop=Internet here ?

Is it an internet cafe (amenity=internet_cafe)?

Office where you can sign up for internet service?

Something related to online shopping (pickup point that nowadays is marked as shop=outpost? company office marked as office=company?)"""})
    for value in ["online_shop", "onlineshop", "online", "e-commerce", 'Shop_online', 'Internet Shop', 'Online', 'digital_store', 'E-Commerce', 'Online_Gift', 'online_gaming', 'webshop', 'online_service', 'online:only', 'onlinehandel_mit_holzdeko', 'marketplace_online']:
        online_shop_description = """is it shop operating online without presence here? (in such case it should be deleted)

Is it office of such company? (in such case office=company would be valid)

Or is there actual shop there, selling things, where you can walk in?"""
        returned.append({"key": "shop", "value": value, "tag_specific_comment": online_shop_description})
    for specific_fruit_or_vegetable in ['apples', 'asparagus', 'beans', 'strawberries', 'berries', 'gourds', 'potatoes']:
        comment = "shop=" + specific_fruit_or_vegetable + " ? " + "Maybe shop=greengrocer greengrocer=" + specific_fruit_or_vegetable + " ( https://wiki.openstreetmap.org/wiki/Tag:shop=greengrocer ) shop=farm farm=" + specific_fruit_or_vegetable + " ( https://wiki.openstreetmap.org/wiki/Tag:shop=farm ) would be a better tagging? (or some other way to denote specific product being sold?)"
        returned.append({"key": "shop", "value": specific_fruit_or_vegetable, "tag_specific_comment": comment})
    for value in [
        'electricals', 'electricial',
        'electrogoods', 'electro', 'electrics', # as above?
        'electricity', 'electric', # white goods? electricity supply?
        'Electronics_and_white_goods',
        'Electrical_goods', 'Electric_shop', 'electric_shop',
        'eletronics', 'campground',
        'whiteware',
    ]:
        comment = "shop=" + value + " ? " + "What is being sold here? White goods/domestic appliances? Electrical supply contracts? Electronic elements?\n\nhttps://www.openstreetmap.org/changeset/36549076 reccomended shop=domestic_appliances / shop=white_goods for the first case: maybe retagging would be a good idea if it is this kind of shop to make it more clear?\n\n(yes, at time of creating this note neither is documented at wiki at its own page, see also https://wiki.openstreetmap.org/wiki/Key%3Ashop which may have some fitting values)"
        returned.append({"key": "shop", "value": value, "tag_specific_comment": comment})
    for entry in [
        ('Childrenswear', 'children'),
        ('Maternity_Wear', 'maternity'),
    ]:
        comment = "shop=" + entry[0] + " ? Is it intentional that shop=clothes clothes=" + entry[1] + " was not used instead? Such cascading tags have some benefits - for start, it is possible to have some general distinction/category/filtering without supporting 10 000 top level shop values.\n\nObviously, maybe other clothes= subtag would fit better.\n\nHaving separate top level shop values for every single thing seems to not be optimal."
        returned.append({"key": "shop", "value": entry[0], "tag_specific_comment": comment})
    for cuisine in ["asian", "african", "russian", "thai", "turkish", "japanese", "italian"]:
        for linker in [" ", "_"]:
            values = [
                cuisine + linker + "food",
                cuisine + linker + "food" + linker + "store",
                cuisine.capitalize() + linker + "Food",
                "specialty" + linker + "food" + linker + cuisine,
            ]
            for value in values:
                comment = "shop=" + value + " ? Maybe shop=food cuisine=" + cuisine + " would be acceptable and more likely to be handled by data consumers?"
                returned.append({"key": "shop", "value": value, "tag_specific_comment": comment})
    for value in ['workwear', 'gloves', 'fur', 'jeans', 'socks', 'tuxedo', 'beachwear', 'suits',
                    'stockings', 't-shirt', 'swimwear', 'hats', 'hat', 'fancy_dress']:
        comment = "shop=" + value + " ? Is it intentional that shop=clothes clothes=" + value + " was not used instead? Such cascading tags have some benefits - for start, it is possible to have some general distinction/category/filtering without supporting 10 000 top level shop values.\n\nObviously, maybe other clothes= subtag would fit better.\n\nHaving separate top level shop values for every single thing seems to not be optimal."
        returned.append({"key": "shop", "value": value, "tag_specific_comment": comment})
    for value in ["zero_waste", "zero_waste_shop", "Zero_waste_shop"]:
        comment = """shop tag should contain info what is sold there, not how it is sold there

You can have zero_waste shop (or at least ones trying to or branding themself in this way, zero waste is not really achievable) of various types

shop=greengrocer
shop=cosmetics
shop=grocery
shop=convenience
etc

are all possible. What kind of shop is this one?
"""
        returned.append({"key": "shop", "value": value, "tag_specific_comment": comment})
    returned.append({"key": "shop", "value": "bedroom", "tag_specific_comment": "Is it different from shop=bed ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dbed )"})
    returned.append({"key": "shop", "value": "audiologist", "tag_specific_comment": "shop=audiologist ? May refer to shop=hearing_aids or healthcare=audiologist and should be replaced by one of them after checking. As usual may be also something entirely different, especially if it got closed in meantime. In-place survey may be needed"})
    returned.append({"key": "amenity", "value": "audiologist", "tag_specific_comment": "amenity=audiologist ? May refer to shop=hearing_aids or healthcare=audiologist and should be replaced by one of them after checking. As usual may be also something entirely different, especially if it got closed in meantime. In-place survey may be needed"})
    returned.append({"key": "shop", "value": "drugstore", "tag_specific_comment": "Would it be pharmacy tagged as amenity=pharmacy ( https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dpharmacy )\n\nSomething else?"})
    returned.append({"key": "amenity", "value": "drugstore", "tag_specific_comment": "Would it be pharmacy tagged as amenity=pharmacy ( https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dpharmacy )\n\nSomething else?"})
    returned.append({"key": "guest_house", "value": "hotel", "tag_specific_comment": "Would it be hotel? ( tourism=hotel - https://wiki.openstreetmap.org/wiki/Tag:tourism%3Dhotel )\nGuest house? ( tourism=guest_house - https://wiki.openstreetmap.org/wiki/Tag:tourism%3Dguest_house )\n\nSomething else?"})
    returned.append({"key": "toilet:present", "value": "yes", "tag_specific_comment": "likely toilets=yes tag should be used See https://wiki.openstreetmap.org/wiki/Key:toilets"})
    returned.append({"key": "barrier", "value": "step_over", "tag_specific_comment": "What kind of barrier is here?\n\nSee https://wiki.openstreetmap.org/wiki/Key:barrier for a typical values\n\nIs it maybe a stepover stile? See https://wiki.openstreetmap.org/wiki/Tag:barrier%3Dstile"})
    returned.append({"key": "barrier", "value": "obstacle", "tag_specific_comment": "What kind of barrier is here?\n\nSee https://wiki.openstreetmap.org/wiki/Key:barrier for a typical values"})
    returned.append({"key": "barrier", "value": "roper", "tag_specific_comment": "Is there rope here acting as a barrier?\n\nif not - what barrier=roper actually means?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:barrier%3Drope"})
    returned.append({"key": "barrier", "value": "fencer", "tag_specific_comment": "Is there fence here?\n\nif not - what barrier=fencer actually means?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:barrier%3Dfence"})
    returned.append({"key": "barrier", "value": "f", "tag_specific_comment": "Is there fence here?\n\nif not - what barrier=f actually means?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:barrier%3Dfence"})
    returned.append({"key": "barrier", "value": "yesbl", "tag_specific_comment": "What kind of barrier is here?\n\nBlock?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:barrier%3Dblock"})
    returned.append({"key": "ship", "value": "instead", "tag_specific_comment": "What it is supposed to mean?"})
    returned.append({"key": "identifier", "tag_specific_comment": "What it is supposed to mean?"})
    returned.append({"key": "width", "value": "0", "tag_specific_comment": "how something exist and have width=0?"})
    returned.append({"key": "circumference", "value": "0", "tag_specific_comment": "how circumference=0 may be correctaccess%?"})
    returned.append({"key": "amenity", "value": "office", "tag_specific_comment": "It should be rather tagged with office=* tag, see https://wiki.openstreetmap.org/wiki/Key:office"})
    returned.append({"key": "underground", "value": "1", "tag_specific_comment": "What was meant by this?"})
    returned.append({"key": "underground", "value": "2", "tag_specific_comment": "What was meant by this?"})
    returned.append({"key": "underground", "value": "3", "tag_specific_comment": "What was meant by this?"})
    returned.append({"key": "underground", "value": "gravel", "tag_specific_comment": "What was meant by this?"})
    returned.append({"key": "underground", "value": "yes", "tag_specific_comment": "Would it be fine to use more usual location=underground?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:location%3Dunderground and https://wiki.openstreetmap.org/wiki/Key:underground"})
    
    
    returned.append({"key": "amenity", "value": "fixme", "tag_specific_comment": "What kind of object is here? Is it a shop? What kind of a shop? (see https://wiki.openstreetmap.org/wiki/Key:shop )"}) # https://github.com/Zverik/every_door/issues/880 - mostly Every Door induced
    returned.append({"key": "fixme", "value": "yes", "tag_specific_comment": "What requires fixing here? fixme=yes is not particularly clear, and maybe problem got fixed since then?"})
    returned.append({"key": "FIXME", "value": "yes", "tag_specific_comment": "What requires fixing here? fixme=yes is not particularly clear, and maybe problem got fixed since then?"})
    returned.append({"key": "roof:shape", "value": "pitched", "tag_specific_comment": "Maybe roof:shape=skillion was intended here? Or roof:shape=gabled? See https://wiki.openstreetmap.org/wiki/Tag:roof:shape=pitched"})
    returned.append({"key": "roof:shape", "value": "skilled", "tag_specific_comment": "Maybe roof:shape=gabled was intended here? See https://wiki.openstreetmap.org/wiki/Tag:roof:shape%3Dskillion"})
    returned.append({"key": "roof:shape", "value": "slanted", "tag_specific_comment": "Maybe roof:shape=skillion was intended here? Or some other value?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:roof:shape%3Dskillion and https://wiki.openstreetmap.org/wiki/Key:roof:shape for other documented values"})
    returned.append({"key": "building:roof:shape", "tag_specific_comment": "Maybe roof:shape was intended here?\n\nSee https://wiki.openstreetmap.org/wiki/Key:roof:shape\n\nSee also https://taginfo.openstreetmap.org/keys/building%3Aroof%3Ashape#overview and https://taginfo.openstreetmap.org/keys/roof%3Ashape"})

    for value in tag_knowledge.valid_roof_shape_values():
        returned.append({"key": "roof:levels", "value": value, "tag_specific_comment": "Maybe roof:shape=" + value + " was intended here?\n\nSee https://wiki.openstreetmap.org/wiki/Key:roof:shape"})
        returned.append({"key": "roof:type", "value": value, "tag_specific_comment": "Maybe roof:shape=" + value + " was intended here?\n\nSee https://wiki.openstreetmap.org/wiki/Key:roof:shape"})
        returned.append({"key": "roof_shape", "value": value, "tag_specific_comment": "Maybe roof:shape=" + value + " was intended here?\n\nSee https://wiki.openstreetmap.org/wiki/Key:roof:shape"})
        returned.append({"key": "roof", "value": value, "tag_specific_comment": "Maybe roof:shape=" + value + " was intended here?\n\nSee https://wiki.openstreetmap.org/wiki/Key:roof:shape and https://wiki.openstreetmap.org/wiki/Key:roof"})
    returned.append({"key": "name", "value": "Смерека срібляста", "tag_specific_comment": """"Смерека срібляста" is species name, not a given name of this specific tree, right?

In which language it is written? Ukrainian, with lang code uk?

Then it should go to species:uk - not name tag or name:uk tag"""})
    for mode in ["foot", "hgv", "bus", "bicycle", "psv", "motor_vehicle", "vehicle"]:
        # note that in case of retagging some maybe should be rather conditional
        # see https://www.openstreetmap.org/node/9097231451/history
        entry = {
            "key": "access:" + mode,
            "tag_specific_comment": "Would using " + mode + " access tag (see https://wiki.openstreetmap.org/wiki/Key:" + mode + " ) be fitting at least equally well?\n\nUsage statistics are sometimes wrong and should not be blindly followed, but are worth looking at - see http://taghistory.raifer.tech/#***/" + mode + "/&***/access%3A" + mode + "/",
        }
        returned.append(entry)
    cuisine_extra_trailing_character = {
        'chinese;面': 'chinese',
        'japanese;鰻': 'japanese',
        'japanese;회': 'japanese',
        'asian;麵': 'asian',
        'fish,魚': 'fish',
        'fish;鰻': 'fish',
        'japanese;酒': 'japanese',
    }
    for old, new in cuisine_extra_trailing_character.items():
        key = "cuisine"
        entry = {
        'key': key,
        'value': old,
        'tag_specific_comment': "Was it supposed to be cuisine = " + new + "\n?\n\nIf extra character at the end is intentional - would it be possible to express that cuisine as an English value so it would be understood more easily? See some already documented values in https://wiki.openstreetmap.org/wiki/Key:cuisine",
        }
        returned.append(entry)
    for key in ["PFM:comment", 'PFM:garmin_type', "PFM:garmin_road_class", "PFM:RoadID"]:
        returned.append({
            'key': key,
            'tag_specific_comment': 'Can you remove this tag or replace by more clear one? It looks like debris from GPS trace import and if there is some uyseful info in it retagging it may be useful (and if there is no useful info there then removing it would be a good idea)\n\nSorry for bothering about an ancient edit, but maybe you remember something.',
            'skipped_users': [
                "Beddhist", # https://www.openstreetmap.org/changeset/5105525
            ],
        })
    for key in short_suspect_values(specified_cache_folder):
        returned.append({
            'key': key,
            'tag_specific_comment': "What is the meaning of this unusual key? Is this tag needed?\nOr maybe can it be expressed in a more typical way that would be easier to understand?\nOr maybe this key can and should be documented as useful tagging schema?",
            'skipped_users': [
                'Russ McD', # https://www.openstreetmap.org/changeset/79075881
            ],
        })
    completely_unclear_shop_value_description = "What is the meaning of that shop value? What kind of services or products are sold here? Is anything from https://wiki.openstreetmap.org/wiki/Key:shop or https://wiki.openstreetmap.org/wiki/Category:Tag_descriptions_for_key_%22shop%22 fitting? Maybe new value needs to be invented? Maybe this data is wrong and there is no shop here? Maybe it is not a shop but something else?"
    for value in dubious_tags.unclear_shop_values_with_no_specific_comment.unclear_shop_values():
        returned.append({
            "key": "shop",
            "value": value,
            "tag_specific_comment": "shop=" + value + " ? " + completely_unclear_shop_value_description
            })
    medical_shop_description = """Current tag is not clear at all and can be made more specific... Is it place selling something medical-related?

or some place where alt-medicine practice is operating?

is it just a pharmacy? Then amenity=pharmacy should work

Or somehow differs from regular pharmacy?

If it is not a pharmacy - would https://wiki.openstreetmap.org/wiki/Tag:shop=medical_supply describe it well?

maybe it could be shop=herbalist ? ( https://wiki.openstreetmap.org/wiki/Tag:shop=herbalist )

maybe https://wiki.openstreetmap.org/wiki/Tag:shop=health_food or https://wiki.openstreetmap.org/wiki/Tag:shop=nutrition_supplements ?

Is it maybe a doctor office/clinic/etc? ( https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dclinic  https://wiki.openstreetmap.org/wiki/Tag:amenity%3Ddoctors)

or is it something else? Maybe it does not exist at all?
"""
    for value in ['medical_house', 'health & wellness', 'healthcare', 'health_care', 'health care', 'medicine', 'health', 'Health Products', 'Health_-_Naturista']:
        returned.append({
            'key': 'shop',
            'value': value, 
            'tag_specific_comment': "shop=" + value + " ? " + medical_shop_description,
        })

    for entry in [ # what kind of this things is available here? (for say shop=equipment)
        {'shop_value': 'bulk', 'what': 'products', 'examples': "Food? Textile? Chocolate? Pesticides? Windows? Tiles? Lumber?"},
        {'shop_value': 'Regional_Products', 'what': 'regional products', 'examples': "Small gifts? Souvenirs? Local food? Textile? Sculptures? Chocolate?"},
        {'shop_value': 'Local Products', 'what': 'local products', 'examples': "Small gifts? Souvenirs? Local food? Textile? Sculptures? Chocolate?"},
        {'shop_value': 'alterations', 'what': 'services', 'examples': "Clothing alterations? Car looks alterations? Hairstyle alterations?"},
        {'shop_value': "mobile_equipment", "what": "equipment", 'examples': "Industrial equipment? Sport equipment", "extra_info": "Is definition at https://wiki.openstreetmap.org/wiki/Talk:Tag:shop=mobile_equipment matching what is used here?"},
        {'shop_value': 'Showroom', 'what': 'showroom', 'examples': ""},
        {'shop_value': 'Service_Center', 'what': 'service', 'examples': ""},
        {'shop_value': 'Business', 'what': 'service', 'examples': ""},
        {'shop_value': 'Sales_and_Repair', 'what': 'sales and repair', 'examples': "Cars? Shoes? Planes? Industrial machinery? Phones? Bicycles? Electronics? Fridges?"},
        {'shop_value': 'factory_outlet', 'what': 'products', 'examples': "Cosmetics? Hammers? Fridges? Cars? Paint? Gloves?"},
        {'shop_value': 'Entertainment', 'what': 'entertainment', 'examples': "Selling balloons? Selling event organizing services? Escape room? Something else?"},
        {'shop_value': 'devices', 'what': 'devices', 'examples': "Electronics? Industrial equipment? Pyrotechnic devices?"},
        {'shop_value': 'Onsite Rentals', 'what': 'rentals', 'examples': "Of flats? Of cars? Of medical equipment? Of tourist accessories? Of costumes? Of power tools?"},
        {'shop_value': 'onsite rentals', 'what': 'rentals', 'examples': "Of flats? Of cars? Of medical equipment? Of tourist accessories? Of costumes? Of power tools?"},
        {'shop_value': 'onsite_rentals', 'what': 'rentals', 'examples': "Of flats? Of cars? Of medical equipment? Of tourist accessories? Of costumes? Of power tools?"},
        {'shop_value': 'equipment_rental', 'what': 'equipment_rental', 'examples': "What can be rented here? Skis? Skateboards? Industrial equipment? Something else?"},
        {'shop_value': 'Equipment', 'what': 'Equipment', 'examples': "Medical equipment? Power tools? Sport equipment? Industrial equipment?"},
        {'shop_value': 'equipment', 'what': 'equipment', 'examples': "Medical equipment? Power tools? Sport equipment? Industrial equipment?"},
        {'shop_value': 'Studio', 'what': 'Studio', 'examples': "Recording studio? Art studio? Beauty studio? Is it even a shop? See also https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dstudio"},
        {'shop_value': 'studio', 'what': 'studio', 'examples': "Recording studio? Art studio? Beauty studio? Is it even a shop? See also https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dstudio"},
    ]:
        comment = "shop=" + entry['shop_value'] + " ? What kind of " + entry['what'] + "? " + entry['examples'] + " (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)"
        if "extra_info" in entry:
            comment += " " + entry["extra_info"]
        returned.append({
            'key': 'shop',
            'value': entry['shop_value'], 
            'tag_specific_comment': comment,
        })
    for value in ["fair_trade", "fairtrade"]:
        returned.append({
            'key': 'shop',
            'value': value, 
            'tag_specific_comment': """What kind of products are sold there?

shop tag should contain shop type value - and """ + value + """ is not one

You can have fair trade shop of various types

shop=greengrocer
shop=cosmetics
shop=grocery
shop=convenience
etc

are all possible. What kind of shop is this one?

Fair trade status can be tagged with fair_trade=yes/fair_trade=only - see https://wiki.openstreetmap.org/wiki/Key:fair_trade""",
        })
    for value in ["duty_free", "duty-free", "Duty Free", "Duty_Free_Shop", "duty"]:
        returned.append({
            'key': 'shop',
            'value': value,
            'tag_specific_comment': "shop=" + value + "? What is actually sold here? Tobacco? Alcohol? Jewellery? Chocolate? migrating to shop=yes duty_free=yes sounds well, but there is also duty_free=refund... So it needs in-place survey to check to fix"
        })
    for value in ["organic", "Organic", "organic_food", "organic food", "Organic_Products"]:
        returned.append({
            'key': 'shop',
            'value': value, 
            'tag_specific_comment': "shop=" + value + " ? " + """What kind of products are sold there?

shop tag should contain shop type value - and """ + value + """ is not one

You can have organic shop of various types

shop=greengrocer
shop=cosmetics
shop=grocery
shop=convenience
etc

are all possible. What kind of shop is this one?

organic status can be tagged with organic=yes/organic=only - see https://wiki.openstreetmap.org/wiki/Key:organic"""
        })
    returned += [
        {
            'key': 'name:heb',
            'tag_specific_comment': 'Is it name in Hebrew? Note we use name:he for these, as ISO 639-1 code for Hebrew is he. See https://wiki.openstreetmap.org/wiki/Key:name:he',
        },
        {
            'key': 'na',
            'tag_specific_comment': 'Maybe that was supposed to be name= key?',
        },
        {
            'key': 'n',
            'tag_specific_comment': 'Maybe that was supposed to be name= key?',
        },
        {
            'key': 'app_operated',
            'value': "yes",
            'tag_specific_comment': 'What app_operated=yes means here? Have you wanted to mark that you can control it with app in some way but app may be necessary or not? For example shop where you can scan and pay with app, without going through a traditional line. Or is it for objects where you need an app to use them at all? Then maybe app_operated=only would be better?\n\nNote, this key seems undocumented on wiki, see https://wiki.openstreetmap.org/w/index.php?title=Key:app_operated and ',
        },
        {
            'key': 'support',
            'value': "pedestral",
            'tag_specific_comment': 'support=pedestral? Maybe support=pedestal was intended here? See https://wiki.openstreetmap.org/wiki/Key%3Asupport\n\nIf it was not supposed to be support=pedestral: what is "pedestral"?',
        },
        {
            'key': 'support',
            'value': "pedestrial",
            'tag_specific_comment': 'support=pedestral? Maybe support=pedestal was intended here? See https://wiki.openstreetmap.org/wiki/Key%3Asupport\n\nIf it was not supposed to be support=pedestral: what is "pedestral"?',
        },
        {
            'key': 'roof',
            'value': "f",
            'tag_specific_comment': 'Have you meant roof:shape=flat? Or something else? See https://wiki.openstreetmap.org/wiki/Key:roof:shape',
        },
        {
            'key': 'roof',
            'value': "grass",
            'tag_specific_comment': 'Have you meant roof:material=grass as it has grass on top? Or something else? See https://wiki.openstreetmap.org/wiki/Key:roof:materuial',
        },
        {
            'key': 'roof',
            'value': "7.2.7i",
            'tag_specific_comment': 'Have you meant anything by that value? If yes, what you wanted to express?',
        },
        {
            'key': 'roof',
            'value': "chapa",
            'tag_specific_comment': 'Have you meant anything by that value? If yes, what you wanted to express?',
        },
        {
            'key': 'roof',
            'value': "eave",
            'tag_specific_comment': 'Have you meant anything by that value? If yes, what you wanted to express?',
        },
        {
            'key': 'roof',
            'value': "giwa",
            'tag_specific_comment': 'Have you meant anything by that value? If yes, what you wanted to express?',
        },
        {
            'key': 'roof',
            'value': "N/A",
            'tag_specific_comment': 'Why it got added here?',
        },
        {
            'key': 'roof:type',
            'value': "romney",
            'tag_specific_comment': 'Have you meant anything by that value? If yes, what you wanted to express?',
        },
        {
            'key': 'roof:type',
            'value': "helm",
            'tag_specific_comment': 'Have you meant anything by that value? If yes, what you wanted to express?',
        },
        {
            'key': 'roof:type',
            'value': "tin",
            'tag_specific_comment': 'Have you meant anything by that value? If yes, what you wanted to express?',
        },
        {
            'key': 'roof:type',
            'value': "paravalanche",
            'tag_specific_comment': 'Have you meant anything by that value? If yes, what you wanted to express?',
        },
        {
            'key': 'building:name',
            'tag_specific_comment': 'Is building:name for building name? In such case it would be much better to put it into name tag. If this object merges builing and POI inside such as museum or shop, then having separate objects for point of interest and building would be better idea, museum may have own area or node (see also https://wiki.openstreetmap.org/wiki/One_feature,_one_OSM_element ).\n\nIf it is an inscription then it should use https://wiki.openstreetmap.org/wiki/Key:inscription\n\nIf that is not a building name - what was expressed by this tagging?',
            'skipped_users': [
                "archie", # https://www.openstreetmap.org/changeset/73223955 - I know how this user uses this key
            ],
        },
        {
            'key': 'building',
            'value': "foundation",
            'tag_specific_comment': """so well, it is not a building at all? Just foundations due to building being unfinished/destroyed?
If it is being contructed then building=construction may fit better
if it is not - then maybe man_made=foundation would be better so it will not get confused for a building?""",
        },
        {
            'key': 'building',
            'value': "foundations",
            'tag_specific_comment': """so well, it is not a building at all? Just foundations due to building being unfinished/destroyed?
If it is being contructed then building=construction may fit better
if it is not - then maybe man_made=foundation would be better so it will not get confused for a building?""",
        },
        {
            'key': 'building',
            'value': "base",
            'tag_specific_comment': """so well, it is not a building at all? Just foundations due to building being unfinished/destroyed?
If it is being contructed then building=construction may fit better
if it is not - then maybe man_made=foundation would be better so it will not get confused for a building?""",
        },
        {
            'key': 'building',
            'value': "proposed",
            'tag_specific_comment': 'Is this building existing now? Are there at least real plans for building it? If there are no serious plans for it - that should be entirely deleted. If construction started then building=construction is a better tag. If construction is upcoming then source for this claim should be tagged on the geometry itself (source tag, note tag) and different tagging should be used - we are mapping proposed features in OpenStreetMap very sparingly, not every promise or business plan should be mapped here.',
        },
        {
            'key': 'building',
            'value': "semi",
            'tag_specific_comment': 'would it be fine to move a bit unusual tagging of building=semi to building=semidetached_house ?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:building=semi and https://wiki.openstreetmap.org/wiki/Tag:building%3Dsemidetached_house',
        },
        {
            'key': 'building',
            'value': "ail",
            'tag_specific_comment': 'what does this tag mean? Does it mean anything?',
        },
        {
            'key': "amenity",
            'value': "church",
            'tag_specific_comment': "What was meant by amenity=church? It seem to be not documented value and it seems to be a duplicate of https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dplace_of_worship Note that christian church is taggable by amenity=place_of_worship religion=christian.\n\nIf you used it intentionally instead of amenity=place_of_worship - then what is the difference here?",
        },
        {
            'key': "amenity",
            'value': "temple",
            'tag_specific_comment': "What was meant by amenity=temple? It seem to be not documented value and it seems to be a duplicate of https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dplace_of_worship.\n\nIf it was used intentionally instead of amenity=place_of_worship - then what is the difference here?",
        },
        {
            'key': "shop",
            'value': "discount",
            'tag_specific_comment': "Is it shop=variety_store ? If not, how it differs from shop=variety_store? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dvariety_store And note, not all objects mapped as shop=discount are variety stores",
            # https://lists.openstreetmap.org/pipermail/talk-gb/2023-December/030943.html https://lists.openstreetmap.org/pipermail/talk-gb/2023-December/030947.html
            # looking at https://www.openstreetmap.org/way/61143920 it seems that mass edit is not so safe
            # bot edit proposal was:
            # Small ongoing automated edit proposal: shop=discount to shop=variety_store
            # I propose to replace all `shop=discount` in USA by `shop=variety_store` - including new ones in future.
            # See https://overpass-turbo.eu/s/1I1o for the list
            # See https://www.openstreetmap.org/note/3819307
            # See https://osmus.slack.com/archives/C2VJAJCS0/p1706219295884359
        },
        {
            'key': "shop",
            'value': "FIXME",
            'tag_specific_comment': "What kind of shop, if any is here?",
        },
        {
            'key': "shop",
            'value': "camping",
            'tag_specific_comment': "What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=outdoor ? If yes, what is the difference?\n\nShould we document this shop value as distinct, valid and useful?  Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?",
        },
        {
            'key': "amenity",
            'value': "convenience",
            'tag_specific_comment': "What was meant by amenity=convenience? Is it a convenience shop? Then shop=convenience is likely a better tagging, see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconvenience .",
        },
        {
            'key': "shop",
            'value': "convience",
            'tag_specific_comment': "Is it a convenience shop? Then shop=convenience is likely a better tagging, see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconvenience .",
        },
        {
            'key': "shop",
            'value': "coveni",
            'tag_specific_comment': "Is it a convenience shop? Then shop=convenience is likely a better tagging, see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconvenience .",
        },
        {
            'key': "shop",
            'value': "convince",
            'tag_specific_comment': "Is it a convenience shop? Then shop=convenience is likely a better tagging, see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconvenience .",
        },
        {
            'key': 'shop',
            'value': 'shopping_complex',
            'tag_specific_comment': 'shop=shopping_complex ? Is it intended to be shop=mall tag ?',
        },
        {
            'key': 'shop',
            'value': 'upholsterer',
            'tag_specific_comment': 'shop=upholsterer ? What kind of shop, if any is here? Or is it https://wiki.openstreetmap.org/wiki/Tag:craft=upholsterer ?',
        },
        {
            'key': 'shop',
            'value': 'public market',
            'tag_specific_comment': 'shop=public market ? Is it intetionally used instead of amenity=marketplace?',
        },
        {
            'key': 'shop',
            'value': 'Apache Trail Veterinary Services',
            'tag_specific_comment': 'shop=Apache Trail Veterinary Services ? What kind of shop, if any is here? Is it office of a veterinary doctor?',
        },
        {
            'key': 'shop',
            'value': 'landscaping',
            'tag_specific_comment': 'shop=landscaping ? What kind of shop, if any is here? Is it selling landscaping supplies? Or is it office of someone providing landscaping services? Or is it something else?',
        },
        {
            'key': 'shop',
            'value': 'hypermarket',
            'tag_specific_comment': 'shop=hypermarket ? Why not shop=supermarket? Is there some difference? See https://wiki.openstreetmap.org/wiki/Tag:shop=supermarket',
        },
        {
            'key': 'shop',
            'value': 'Hypermarket',
            'tag_specific_comment': 'shop=Hypermarket ? Why not shop=supermarket? Is there some difference? See https://wiki.openstreetmap.org/wiki/Tag:shop=supermarket',
        },
        {
            'key': 'shop',
            'value': 'plumbing',
            'tag_specific_comment': 'shop=plumbing ? Is it seling plumbing supplies? Or is it place where plumber may be contracted? Or is it company office that cannot be visited by general public?',
        },
        {
            'key': 'shop',
            'value': 'Dive_Center',
            'tag_specific_comment': 'shop=Dive_Center ? Are they selling some kind of service? Or are they selling equipment there?',
        },
        {
            'key': 'shop',
            'value': 'Plumbing',
            'tag_specific_comment': 'shop=Plumbing ? Is it seling plumbing supplies? Or is it place where plumber may be contracted? Or is it company office that cannot be visited by general public?',
        },
        {
            'key': 'shop',
            'value': 'plumber',
            'tag_specific_comment': 'shop=plumber ? Is it seling plumbing supplies? Or is it place where plumber may be contracted? Or is it company office that cannot be visited by general public?',
        },
        {
            'key': 'shop',
            'value': 'plumbers',
            'tag_specific_comment': 'shop=plumbers ? Is it seling plumbing supplies? Or is it place where plumber may be contracted? Or is it company office that cannot be visited by general public? Multiple plumber offices?',
        },
        {
            'key': 'shop',
            'value': 'Trailor',
            'tag_specific_comment': 'shop=Trailor ? Is it misspelling of tailor?',
        },
        {
            'key': 'shop',
            'value': 'multiple_shops',
            'tag_specific_comment': 'shop=multiple_shops ? Each shop should be mapped separately. Maybe this is landuse=retail or shop=mall?',
        },
        {
            'key': 'shop',
            'value': 'air_filling',
            'tag_specific_comment': 'shop=air_filling ? What kind of shop, if any is here? Should it be amenity=compressed_air?',
        },
        {
            'key': 'shop',
            'value': 'Grocery_and_vegetables',
            'tag_specific_comment': 'shop=Grocery_and_vegetables ? Is it just shop=convenience ?',
        },
        {
            'key': 'shop',
            'value': 'tobacconist',
            'tag_specific_comment': 'shop=tobacconist ? Is shop=tobacco intentionally not used here ( see https://wiki.openstreetmap.org/wiki/Tag:shop=tobacco ) - what is the difference? Should we document shop=tobacconist as a valid shop value?',
        },
        {
            'key': "shop",
            'value': "tienda_de_barrio",
            'tag_specific_comment': "Is it a convenience shop? Then shop=convenience is likely a better tagging, see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconvenience .\n\nSee https://www.openstreetmap.org/note/3848843",
        },
        {
            'key': "shop",
            'value': "BARRIO",
            'tag_specific_comment': "Is it a convenience shop? Then shop=convenience is likely a better tagging, see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconvenience .\n\nSee https://www.openstreetmap.org/note/3848843",
        },
        {
            'key': "shop",
            'value': "de_Barrio",
            'tag_specific_comment': "Is it a convenience shop? Then shop=convenience is likely a better tagging, see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconvenience .\n\nSee https://www.openstreetmap.org/note/3848843",
        },
        {
            'key': "shop",
            'value': "Tienda_de_barrio",
            'tag_specific_comment': "Is it a convenience shop? Then shop=convenience is likely a better tagging, see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconvenience .\n\nSee https://www.openstreetmap.org/note/3848843",
        },
        {
            'key': "shop",
            'value': "コンビニ",
            'tag_specific_comment': "Is it a convenience shop? Then shop=convenience is likely a better tagging, see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconvenience .\n\nSee https://www.openstreetmap.org/note/3823535",
        },
        {
            'key': "un",
            'value': "yes",
            'tag_specific_comment': "What was meant by un=yes? It seem to be not documented value and has no obvious meaning.",
        },
        {
            'key': "a",
            'value': "a",
            'tag_specific_comment': "What was meant by a=a? It seem to be not documented value and has no obvious meaning.",
        },
        {
            'key': "service",
            'value': "paved",
            'tag_specific_comment': "service=paved? Maybe surface=paved was intended here? If not this, then what it means?",
        },
        {
            'key': "paved",
            'value': "yes",
            'tag_specific_comment': "Why not surface=paved ? What is benefit of using unusual paved=yes rather than surface=paved ?",
        },
        {
            'key': "paved",
            'value': "no",
            'tag_specific_comment': "Why not surface=unpaved ? What is benefit of using unusual paved=no rather than surface=unpaved ?",
        },
        {
            'key': "amenity",
            'value': "water",
            'tag_specific_comment': """amenity=water? What is this?

If it is place with drinking water amenity=drinking_water is typically
used.

man_made=water_tap may be added if it is a water tap.

man_made=water_tap with drinking_water=no is typically used to indicate
tap without drinking water

see https://wiki.openstreetmap.org/wiki/Tag:amenity=water""",
        },
        {
            'key': "waterway",
            'value': "creek",
            'tag_specific_comment': "what was meant by waterway=creek? Is not using https://wiki.openstreetmap.org/wiki/Tag:waterway%3Dstream intentional and wanted here? How waterway=creek differs from waterway=stream in this case?",
        },
        {
            'key': "natural",
            'value': "stream",
            'tag_specific_comment': "what was meant by natural=stream? Is using it instead (or in addition to) https://wiki.openstreetmap.org/wiki/Tag:waterway%3Dstream intentional here?",
        },
        {
            'key': "waterway",
            'value': "brook",
            'tag_specific_comment': "what was meant by waterway=brook? Is not using https://wiki.openstreetmap.org/wiki/Tag:waterway%3Dstream intentional and wanted here? How waterway=brook differs from waterway=stream in this case?",
        },
        {
            'key': "vending",
            'value': "locker",
            'tag_specific_comment': "what it means? Maybe amenity=parcel_locker was meant to be tagged here? ( https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dparcel_locker ) Maybe amenity=luggage_locker ? ( https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dluggage_locker )",
        },
        {
            'key': "brand:wikidata",
            'value': "Q3751637",
            'tag_specific_comment': 'https://www.wikidata.org/wiki/Q3751637 from brand:wikidata=Q3751637 (brand:wikipedia=en:CajaSur) link company that does not exist anymore\n\nbrand:wikidata=Q20013689 and brand:wikipedia=es:CajaSur_Banco may be more fitting\nthey are linking https://es.wikipedia.org/wiki/CajaSur_Banco and https://www.wikidata.org/wiki/Q20013689',
        },
        {
            'key': "brand:wikipedia",
            'value': "en:CajaSur",
            'tag_specific_comment': 'brand:wikipedia=en:CajaSur ( and https://www.wikidata.org/wiki/Q3751637 from brand:wikidata=Q3751637 ) link company that does not exist anymore\n\nbrand:wikidata=Q20013689 and brand:wikipedia=es:CajaSur_Banco may be more fitting\nthey are linking https://es.wikipedia.org/wiki/CajaSur_Banco and https://www.wikidata.org/wiki/Q20013689',
        },
        {
            'key': "brand:wikidata",
            'value': "Q3568053",
            'tag_specific_comment': 'https://www.wikidata.org/wiki/Q3568053 link in brand:wikidata likely makes no sense ("Picard-language edition of Wikipedia")',
        },
        {
            'key': "name",
            'value': "Noname",
            'tag_specific_comment': "That is probably object without name, not object named \"Noname\". I think that https://wiki.openstreetmap.org/wiki/Tag:noname%3Dyes would work better here, should it be changed?",
        },
        {
            'key': "name",
            'value': "noname",
            'tag_specific_comment': "That is probably object without name, not object named \"noname\". I think that https://wiki.openstreetmap.org/wiki/Tag:noname%3Dyes would work better here, should it be changed?",
        },
        {
            'key': "name",
            'value': "no_name",
            'tag_specific_comment': "That is probably object without name, not object named \"no_name\". I think that https://wiki.openstreetmap.org/wiki/Tag:noname%3Dyes would work better here, should it be changed?",
        },
        {
            'key': "name",
            'value': "none",
            'tag_specific_comment': "That is probably object without name, not object named \"none\". I think that https://wiki.openstreetmap.org/wiki/Tag:noname%3Dyes would work better here, should it be changed?",
        },
        {
            'key': 'nature',
            'value': 'tree',
            'tag_specific_comment': 'Was it supposed to be natural=tree? See https://wiki.openstreetmap.org/wiki/Tag:natural%3Dtree (though maybe it is not a tree anymore?)',
        },
        {
            'key': 'store',
            'value': 'yes',
            'tag_specific_comment': 'Was it supposed to be shop= tag? And what kind of shop it is? https://wiki.openstreetmap.org/wiki/Key:shop may help to find a good value if you know this location',
        },
        {
            'key': 'crop',
            'value': 'no',
            'tag_specific_comment': 'What crop=no is supposed to mean in this context?',
        },
        {
            'key': 'shop',
            'value': 'diy',
            'tag_specific_comment': 'What kind of things are sold here? Maybe shop=doityourself or shop=trade is fitting here?',
        },
        {
            'key': 'shop',
            'value': 'fragrance',
            'tag_specific_comment': 'What kind of things are sold here? Maybe shop=perfumery is fitting here? (or shop=candles ?)',
        },
        {
            'key': 'shop',
            'value': 'press',
            'tag_specific_comment': 'What kind of shop=press ? Selling newspapers? Selling olive oil presses? Selling pressed fruit juice? Something else?',
        },
        {
            'key': 'shop',
            'value': 'white_goods',
            'tag_specific_comment': 'what was think nowadays about shop=white_goods and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dappliance ?\n\nWould it be fine to retag this object to shop=appliance or is shop=white_goods describing something else or is actually preferable?',
        },
        {
            'key': 'shop',
            'value': 'carpeter',
            'tag_specific_comment': 'Was it supposed to be shop=carpet? craft=carpenter? Something else?',
        },
        {
            'key': 'shop',
            'value': 'pet_care',
            'tag_specific_comment': 'Was it supposed to be shop=pet? amenity=veterinary? Something else?',
        },
        {
            'key': 'shop',
            'value': 'visa',
            'tag_specific_comment': 'What is sold here? Is it place selling help with getting visa abroad?',
        },
        {
            'key': 'shop',
            'value': 'Fertilizer',
            'tag_specific_comment': 'Maybe shop=agrarian agrarian=fertilizer would be better tagging? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dagrarian\n\nOr maybe this shop value should be documented at OSM Wiki?',
        },
        {
            'key': 'shop',
            'value': 'fertilizer',
            'tag_specific_comment': 'Maybe shop=agrarian agrarian=fertilizer would be better tagging? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dagrarian\n\nOr maybe this shop value should be documented at OSM Wiki?',
        },
        {
            'key': 'shop',
            'value': 'fertilisers',
            'tag_specific_comment': 'Maybe shop=agrarian agrarian=fertilizer would be better tagging? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dagrarian\n\nOr maybe this shop value should be documented at OSM Wiki?',
        },
        {
            'key': 'shop',
            'value': 'fertilizers',
            'tag_specific_comment': 'Maybe shop=agrarian agrarian=fertilizer would be better tagging? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dagrarian\n\nOr maybe this shop value should be documented at OSM Wiki?',
        },
        {
            'key': 'shop',
            'value': 'agricultural_machinery',
            'tag_specific_comment': 'Maybe shop=agrarian agrarian=agricultural_machinery would be better tagging? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dagrarian\n\nOr maybe this shop value should be documented at OSM Wiki?',
        },
        {
            'key': 'shop',
            'value': 'Agriculture_machines',
            'tag_specific_comment': 'Maybe shop=agrarian agrarian=agricultural_machinery would be better tagging? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dagrarian\n\nOr maybe this shop value should be documented at OSM Wiki?',
        },
        {
            'key': 'shop',
            'value': 'agricultural_machine',
            'tag_specific_comment': 'Maybe shop=agrarian agrarian=agricultural_machinery would be better tagging? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dagrarian\n\nOr maybe this shop value should be documented at OSM Wiki?',
        },
        {
            'key': 'shop',
            'value': 'agricultural_machines',
            'tag_specific_comment': 'Maybe shop=agrarian agrarian=agricultural_machinery would be better tagging? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dagrarian\n\nOr maybe this shop value should be documented at OSM Wiki?',
        },
        {
            'key': 'shop',
            'value': 'car_rental',
            'tag_specific_comment': 'shop=car_rental Maybe amenity=car_rental was meant here? See https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dcar_rental here?',
        },
        {
            'key': 'shop',
            'value': 'ironmonger',
            'tag_specific_comment': 'Was it supposed to be shop=hardware ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dhardware ) ? Something else? Or is this value making sense as a distinct value and should be documented?',
        },
        {
            'key': 'shop',
            'value': 'ironmongery',
            'tag_specific_comment': 'Was it supposed to be shop=hardware ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dhardware ) ? Something else? Or is this value making sense as a distinct value and should be documented?',
        },
        {
            'key': 'shop',
            'value': 'Ironmongery',
            'tag_specific_comment': 'Was it supposed to be shop=hardware ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dhardware ) ? Something else? Or is this value making sense as a distinct value and should be documented?',
        },
        {
            'key': 'shop',
            'value': 'General_Ironmongers',
            'tag_specific_comment': 'Was it supposed to be shop=hardware ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dhardware ) ? Something else? Or is this value making sense as a distinct value and should be documented?',
        },
        {
            'key': 'shop',
            'value': 'sklep_z_art._metalowymi',
            'tag_specific_comment': 'Was it supposed to be shop=hardware ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dhardware ) ? Something else? Or is this value making sense as a distinct value and should be documented?',
        },
        {
            'key': 'shop',
            'value': 'Iron',
            'tag_specific_comment': 'Was it supposed to be shop=hardware ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dhardware ) ? Something else? Or is this value making sense as a distinct value and should be documented?',
        },
        {
            'key': 'shop',
            'value': 'Iron_an_Steel_Shop',
            'tag_specific_comment': 'Was it supposed to be shop=hardware ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dhardware ) ? Something else? Or is this value making sense as a distinct value and should be documented?',
        },
        {
            'key': 'shop',
            'value': 'iron_and_steel_store',
            'tag_specific_comment': 'Was it supposed to be shop=hardware ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dhardware ) ? Something else? Or is this value making sense as a distinct value and should be documented?',
        },
        {
            'key': 'shop',
            'value': 'iron',
            'tag_specific_comment': 'Was it supposed to be shop=hardware ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dhardware ) ? Something else? Or is this value making sense as a distinct value and should be documented?',
        },
        {
            'key': 'shop',
            'value': 'steel',
            'tag_specific_comment': 'Was it supposed to be shop=hardware ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dhardware ) ? Something else? Or is this value making sense as a distinct value and should be documented?',
        },
        {
            'key': 'shop',
            'value': 'kios',
            'tag_specific_comment': 'Was it supposed to be shop=kiosk ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dkiosk ) ? Something else?',
        },
        {
            'key': 'shop',
            'value': 'travel',
            'tag_specific_comment': 'Was it supposed to be shop=travel_agency ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtravel_agency ) ? Something else?',
        },
        {
            'key': 'shop',
            'value': 'shopping_center',
            'tag_specific_comment': 'Was it supposed to be shop=mall ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dmall ) ? Something else?',
        },
        {
            'key': 'shop',
            'value': 'dentist',
            'tag_specific_comment': 'shop=dentist - Was it supposed to be amenity=dentist? ( https://wiki.openstreetmap.org/wiki/Tag:amenity%3Ddentist ). Or is it selling dentist supplies?',
        },
        {
            'key': 'shop',
            'value': 'dental_care',
            'tag_specific_comment': 'shop=dental_care - Was it supposed to be amenity=dentist? ( https://wiki.openstreetmap.org/wiki/Tag:amenity%3Ddentist ). Or is it selling dentist supplies?',
        },
        {
            'key': 'shop',
            'value': 'betting',
            'tag_specific_comment': 'Is shop=betting always replaceable by shop=bookmaker ? iD suggests such change right now, maybe it should be modified?\n\nMaybe here it is not shop=bookmaker but rather shop=lottery, amenity=casino, leisure=amusement_arcade, amenity=gambling or something else instead?',
        },
        {
            'key': 'shop',
            'value': 'bike_Repair_Shop',
            'tag_specific_comment': 'Is this place repairing bicycles? Or motorcycles? Or both? Note that "bike" may refer to bopth and capital letters are unlikely to be a good idea for shop=* values\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop%3Dmotorcycle and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dbicycle',
        },
        {
            'key': 'shop',
            'value': 'moto_repair',
            'tag_specific_comment': 'Is this place repairing cars? Or repairing motorcycles? Or both of them? Maybe one of existing shop values are fitting here and would be more clear?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop%3Dmotorcycle and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar',
        },
        {
            'key': 'shop',
            'value': 'motoculture',
            'tag_specific_comment': 'Is this place repairing cars? Or selling cars? Or selling/repairing motorcycles? Or car parts? Maybe one of existing shop values are fitting here and would be more clear?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop%3Dmotorcycle and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar_repair and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar_parts and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dmotorcycle_repair',
        },
        {
            'key': 'shop',
            'value': 'commercial_vehicle',
            'tag_specific_comment': 'Is this place repairing cars? Or selling cars? Or selling/repairing motorcycles? Or car parts? Maybe one of existing shop values are fitting here and would be more clear?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop%3Dmotorcycle and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar_repair and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar_parts and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dmotorcycle_repair',
        },
        {
            'key': 'shop',
            'value': 'automotive',
            'tag_specific_comment': 'Is this place repairing cars? Or selling cars? Or selling/repairing motorcycles? Or car parts? Maybe one of existing shop values are fitting here and would be more clear?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop%3Dmotorcycle and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar_repair and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar_parts and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dmotorcycle_repair',
        },
        {
            'key': 'shop',
            'value': 'Automotive',
            'tag_specific_comment': 'Is this place repairing cars? Or selling cars? Or selling/repairing motorcycles? Or car parts? Maybe one of existing shop values are fitting here and would be more clear?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop%3Dmotorcycle and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar_repair and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar_parts and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dmotorcycle_repair',
        },
        {
            'key': 'shop',
            'value': 'refurb',
            'tag_specific_comment': 'What is being refurbished here? Is it some repair shop?',
        },
        {
            'key': 'shop',
            'value': 'gold_dealer',
            'tag_specific_comment': 'shop=gold ? Is it a jeweller specializing in gold products? Place selling gold? Pawbroker? Place buying gold? (shop=gold_buyer)',
        },
        {
            'key': 'shop',
            'value': 'gold',
            'tag_specific_comment': 'shop=gold ? Is it a jeweller specializing in gold products? Place selling gold? Pawbroker? Place buying gold? (shop=gold_buyer)',
        },
        {
            'key': 'shop',
            'value': 'gold_trade',
            'tag_specific_comment': 'shop=gold_trade ? Is it shop=gold_buyer or is it intended to tag something distinct?',
        },
        {
            'key': 'shop',
            'value': 'vinery',
            'tag_specific_comment': 'shop=vinery ? Is it supposed to be shop=winery? Or is it valid shop value? In such case what it means - what they are selling here?',
        },
        {
            'key': 'shop',
            'value': 'vinothek',
            'tag_specific_comment': 'shop=vinothek ? Is it supposed to be shop=winery? Or is it valid shop value? In such case what it means - what they are selling here?',
        },
        {
            'key': 'shop',
            'value': 'skincare',
            'tag_specific_comment': 'shop=skincare ? How it differs from shop=cosmetics ? Should we document this tag as a new shop value?',
        },
        {
            'key': 'shop',
            'value': 'beauty_supplies',
            'tag_specific_comment': 'shop=beauty_supplies ? How it differs from shop=cosmetics and shop=hairdresser_supply? Should we document this tag as a new shop value?',
        },
        {
            'key': 'shop',
            'value': 'beauty_Supply',
            'tag_specific_comment': 'shop=beauty_Supply ? How it differs from shop=cosmetics and shop=hairdresser_supply? Should we document this tag as a new shop value?',
        },
        {
            'key': 'shop',
            'value': 'news',
            'tag_specific_comment': 'shop=news ? That is https://wiki.openstreetmap.org/wiki/Tag:shop=newsagent - right? (if they still are active at all)',
        },
        {
            'key': 'shop',
            'value': 'newsstand',
            'tag_specific_comment': 'shop=newsstand ? That is https://wiki.openstreetmap.org/wiki/Tag:shop=newsagent - right? (if they still are active at all)',
        },
        {
            'key': 'shop',
            'value': 'newspaper_agent',
            'tag_specific_comment': 'shop=newspaper_agent ? That is https://wiki.openstreetmap.org/wiki/Tag:shop=newsagent - right? (if they still are active at all)',
        },
        {
            'key': 'shop',
            'value': 'newsagency',
            'tag_specific_comment': 'shop=newsagency ? That is https://wiki.openstreetmap.org/wiki/Tag:shop=newsagent - right? (if they still are active at all)',
        },
        {
            'key': 'shop',
            'value': 'storage',
            'tag_specific_comment': 'shop=storage ? Is it simply a shop=storage_rental? See https://wiki.openstreetmap.org/wiki/Tag:shop=storage_rental Or is it selling boxes/packaging? Or for storing luggage?',
        },
        {
            'key': 'amenity',
            'value': 'storage',
            'tag_specific_comment': 'amenity=storage ? Is it simply a shop=storage_rental? See https://wiki.openstreetmap.org/wiki/Tag:shop=storage_rental Or is it selling boxes/packaging? Or for storing luggage?',
        },
        {
            'key': 'shop',
            'value': 'Storage Buildings',
            'tag_specific_comment': 'shop=Storage Buildings ? Is it simply a shop=storage_rental? See https://wiki.openstreetmap.org/wiki/Tag:shop=storage_rental Or is it selling boxes/packaging?',
        },
        {
            'key': 'shop',
            'value': 'storage_units',
            'tag_specific_comment': 'shop=storage_units ? Is it simply a shop=storage_rental? See https://wiki.openstreetmap.org/wiki/Tag:shop=storage_rental Or is it selling boxes/packaging?\n\nIf it is certainly shop=storage_rental - would it be safe to mass-retag it without inspecting individual cases for all objects tagged this way?',
        },
        {
            'key': 'amenity',
            'value': 'self_storage',
            'tag_specific_comment': 'amenity=self_storage ? Is it simply a shop=storage_rental? See https://wiki.openstreetmap.org/wiki/Tag:shop=storage_rental Or is it selling boxes/packaging?\n\nIf it is certainly shop=storage_rental - would it be safe to mass-retag it without inspecting individual cases for all objects tagged this way?',
        },
        {
            'key': 'shop',
            'value': 'self_storage',
            'tag_specific_comment': 'shop=self_storage ? Is it simply a shop=storage_rental? See https://wiki.openstreetmap.org/wiki/Tag:shop=storage_rental Or is it selling boxes/packaging?\n\nIf it is certainly shop=storage_rental - would it be safe to mass-retag it without inspecting individual cases for all objects tagged this way?',
        },
        {
            'key': 'amenity',
            'value': 'storage_rental',
            'tag_specific_comment': 'amenity=storage_rental ? Is it simply a shop=storage_rental? See https://wiki.openstreetmap.org/wiki/Tag:shop=storage_rental Or is it selling boxes/packaging?\n\nIf it is certainly shop=storage_rental - would it be safe to mass-retag it without inspecting individual cases for all objects tagged this way?',
        },
        {
            'key': 'shop',
            'value': 'Sandwich_bar',
            'tag_specific_comment': 'shop=Sandwich_bar ? Is it amenity=fast_food cuisine=sandwich? Or is it something else?',
        },
        {
            'key': 'shop',
            'value': 'dance',
            'tag_specific_comment': 'shop=dance ? What kind of shop, if any is here? Are they selling dance supplies (shop=dance_supplies)? Is it dancing venue rather than shop? Office of dancing school? Something else?',
        },
        {
            'key': 'shop',
            'value': 'beauty_salon',
            'tag_specific_comment': 'shop=beauty_salon ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=beauty ? If yes, what is the difference?\n\nShould we document this shop value as distinct, valid and useful?  Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?',
        },
        {
            'key': 'shop',
            'value': 'Fruits and Vegetable Section',
            'tag_specific_comment': 'shop=Fruits and Vegetable Section ? What kind of shop, if any is here? Judging by value it does not seem to be an actual shop',
        },
        {
            'key': 'shop',
            'value': 'surfing',
            'tag_specific_comment': 'shop=surfing ? What kind of shop, if any is here? Sport shop selling surfing equipment? (shop=sports sport=surfing would be better tagging in such case, there is also shop=surf)',
        },
        {
            'key': 'shop',
            'value': 'surfware',
            'tag_specific_comment': 'shop=surfware ? What kind of shop, if any is here? Sport shop selling surfing equipment? (shop=sports sport=surfing would be better tagging in such case, there is also shop=surf)',
        },
        {
            'key': 'shop',
            'value': 'garage',
            'tag_specific_comment': 'shop=garage ? What kind of shop, if any is here? Is it https://wiki.openstreetmap.org/wiki/Tag:shop=car_repair ? Or maybe it is fuel station? Or selling car parts? Or something else car adjacent? Maybe even building=garage was intended and it is just place to store a car? Or place where they sell prefabricated garages?',
        },
        {
            'key': 'shop',
            'value': 'drinks',
            'tag_specific_comment': 'shop=drinks ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=beverages ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'handmade',
            'tag_specific_comment': 'shop=handmade ? What kind of shop, if any is here? Is it selling handmade toys? handmade food? handmade gift products?',
        },
        {
            'key': 'shop',
            'value': 'wood_shop',
            'tag_specific_comment': 'shop=wood_shop ? What kind of shop, if any is here? Is it selling lumber? Wood as fuel? Wooden toys? All of that?',
        },
        {
            'key': 'shop',
            'value': 'gas_station',
            'tag_specific_comment': 'shop=gas_station ? What kind of shop, if any is here? shop=convenience shop of gas station? amenity=fuel mapped as shop? Both?',
        },
        {
            'key': 'shop',
            'value': 'leasing',
            'tag_specific_comment': 'shop=leasing ? What kind of shop, if any is here? Is it leasing cars, industrial equipment, costumes, planes, wedding decorations or something else? Is it even a shop? Can clients walk in here at will?',
        },
        {
            'key': 'shop',
            'value': 'apple_retailer',
            'tag_specific_comment': 'shop=apple_retailer ? What kind of shop, if any is here? Is it a greengrocer or electronics retailer related to iPhone maker?',
        },
        {
            'key': 'shop',
            'value': 'stationery_store',
            'tag_specific_comment': 'shop=stationery_store ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=stationery ?',
        },
        {
            'key': 'shop',
            'value': 'horse_abattoir',
            'tag_specific_comment': 'shop=horse_abattoir ? What kind of shop, if any is here? That is man_made=works, not a shop, right?',
        },
        {
            'key': 'shop',
            'value': 'marble',
            'tag_specific_comment': 'shop=marble ? What kind of shop, if any is here? Is it selling marble slabs? Marble products? Is it maybe man_made=works, rather than actual shop? Or internal company office?',
        },
        {
            'key': 'shop',
            'value': 'zoo',
            'tag_specific_comment': 'shop=zoo ? What kind of shop, if any is here? Is it shop=pet by any chance?',
        },
        {
            'key': 'shop',
            'value': 'outdoor_equipment',
            'tag_specific_comment': 'shop=outdoor_equipment ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=outdoor ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'farmers_market',
            'tag_specific_comment': 'shop=farmers_market ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=farm and https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dmarketplace ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'cobbler',
            'tag_specific_comment': 'shop=cobbler? Is it intentionally used instead of shop=shoe_repair ( https://wiki.openstreetmap.org/wiki/Tag:shop=shoe_repair ) or shop=shoes (there is also craft=shoemaker...',
        },
        {
            'key': 'shop',
            'value': 'vineyard',
            'tag_specific_comment': 'shop=vineyard ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=alcohol ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'general_stores',
            'tag_specific_comment': 'shop=general_stores ? What kind of shop, if any is here? Is it shop=general? Multiple shop=general? Is any of values from https://wiki.openstreetmap.org/wiki/Key:shop matching well?',
        },
        {
            'key': 'shop',
            'value': 'tailors shop',
            'tag_specific_comment': 'shop=tailors shop ? Is it shop providing supplies for tailors? Or is it craft=tailor?',
        },
        {
            'key': 'shop',
            'value': 'riding_accessory',
            'tag_specific_comment': 'shop=riding_accessory ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=equestrian ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'Horse_Products',
            'tag_specific_comment': 'shop=Horse_Products ? Is it selling equestrian products for caring for horses? The maybe shop=equestrian would be better? (see https://wiki.openstreetmap.org/wiki/Tag:shop=equestrian ) Is it selling products made out of horses ?',
        },
        {
            'key': 'shop',
            'value': 'kennel',
            'tag_specific_comment': 'shop=kennel ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=pet ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'fishes',
            'tag_specific_comment': 'shop=fishes ? Is it about selling fish as food? In such case why not shop=seafood? Is it about selling pet fish? Then why not shop=pet ?',
        },
        {
            'key': 'shop',
            'value': 'pet_services',
            'tag_specific_comment': 'shop=pet_services ? What kind of shop, if any is here? Is it shop=pet_grooming or is it a veterinary? See https://wiki.openstreetmap.org/wiki/Tag:shop=pet_grooming',
        },
        {
            'key': 'shop',
            'value': 'dog_care',
            'tag_specific_comment': 'shop=dog_care ? What kind of shop, if any is here? Is it shop=pet_grooming pet=dog or is it a place selling dogs? See https://wiki.openstreetmap.org/wiki/Tag:shop=pet_grooming',
        },
        {
            'key': 'shop',
            'value': 'dog_salon',
            'tag_specific_comment': 'shop=dog_salon ? What kind of shop, if any is here? Is it shop=pet_grooming pet=dog or is it a place selling dogs? See https://wiki.openstreetmap.org/wiki/Tag:shop=pet_grooming',
        },
        {
            'key': 'shop',
            'value': 'dog parlour',
            'tag_specific_comment': 'shop=dog parlour ? What kind of shop, if any is here? Is it shop=pet_grooming pet=dog or is it a place selling dogs? See https://wiki.openstreetmap.org/wiki/Tag:shop=pet_grooming',
        },
        {
            'key': 'shop',
            'value': 'dog_trimming',
            'tag_specific_comment': 'shop=dog_trimming ? What kind of shop, if any is here? It is probably object typically tagged as shop=pet_grooming pet=dog  See https://wiki.openstreetmap.org/wiki/Tag:shop=pet_grooming',
        },
        {
            'key': 'shop',
            'value': 'Bespoke_Rugs',
            'tag_specific_comment': 'shop=Bespoke_Rugs ? What kind of shop, if any is here? How it differs from rugs in general? Why not shop=rugs or shop=carpet? See https://wiki.openstreetmap.org/wiki/Tag:shop=carpet',
        },
        {
            'key': 'shop',
            'value': 'suntan',
            'tag_specific_comment': 'shop=suntan ? Is it attempt to mark solarium ? If yes, then we have https://wiki.openstreetmap.org/wiki/Tag:leisure%3Dtanning_salon ',
        },
        {
            'key': 'shop',
            'value': 'solarium',
            'tag_specific_comment': 'shop=solarium ? Is it attempt to mark solarium ? If yes, then we have https://wiki.openstreetmap.org/wiki/Tag:leisure%3Dtanning_salon ',
        },
        {
            'key': 'shop',
            'value': 'horse_supplies',
            'tag_specific_comment': 'shop=horse_supplies ? Why not shop=equestrian, see https://wiki.openstreetmap.org/wiki/Tag:shop=equestrian ?',
        },
        {
            'key': 'shop',
            'value': 'equine_supplies',
            'tag_specific_comment': 'shop=equine_supplies ? Why not shop=equestrian, see https://wiki.openstreetmap.org/wiki/Tag:shop=equestrian ?',
        },
        {
            'key': 'shop',
            'value': 'cigarettes',
            'tag_specific_comment': 'Why not shop=tobacco, see https://wiki.openstreetmap.org/wiki/Tag:shop=tobacco ?\n\nDo we need both shop=tobacco and shop=cigarettes? How these shop values differ?\n\nIf shop=cigarettes should exist, documenting it at https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcigarettes would be useful (see https://wiki.openstreetmap.org/wiki/Creating_a_page_describing_key_or_value )',
        },
        {
            'key': 'shop',
            'value': 'cigars',
            'tag_specific_comment': 'Why not shop=tobacco (with tobacco=cigars), see https://wiki.openstreetmap.org/wiki/Tag:shop=tobacco ?\n\nDo we really need both shop=tobacco and shop=cigars as top level values? Having separate top level values for minor variations makes using OSM data harder.\n\nIf shop=cigars should exist, documenting it at https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcigarettes would be useful (see https://wiki.openstreetmap.org/wiki/Creating_a_page_describing_key_or_value )',
        },
        {
            'key': 'shop',
            'value': 'sourvey',
            'tag_specific_comment': 'shop=sourvey ? Is it intended to be source=survey tag ?',
        },
        {
            'key': 'surface',
            'value': 'BD Ortho IGN',
            'tag_specific_comment': 'surface=BD Ortho IGN ? Is it intended to be source=BD Ortho IGN tag ?',
        },
        {
            'key': 'lanes',
            'value': '0',
            'tag_specific_comment': 'what lanes=0 tag is expressing? That there are no lane markings here? Then use lane_markings=no\n\nThat there is no road here? Something else?',
        },
        {
            'key': 'lanes',
            'value': '-1',
            'tag_specific_comment': 'what lanes=-1 tag is expressing?',
        },
        {
            'key': 'amenity',
            'value': 'burial_ground',
            'tag_specific_comment': 'Is it simply graveyard/cemetery? Is amenity=burial_ground useful or needed for something?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:landuse%3Dcemetery and https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dgrave_yard',
        },
        {
            'key': 'amenity',
            'value': 'cemetery',
            'tag_specific_comment': 'Is it simply graveyard/cemetery? Is amenity=burial_ground useful or needed for something?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:landuse%3Dcemetery and https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dgrave_yard',
        },
        {
            'key': 'ccc',
            'value': 'cyclinglane',
            'tag_specific_comment': 'What ccc=cyclinglane means here?',
        },
        {
            'key': 'ccc',
            'value': 'cyclingpath',
            'tag_specific_comment': 'What ccc=cyclingpath means here?',
        },
        {
            'key': 'ccc',
            'value': 'cyclingroute',
            'tag_specific_comment': 'What ccc=cyclingpath means here?',
        },
        {
            'key': 'ccc',
            'value': 'cylinglane',
            'tag_specific_comment': 'What ccc=cyclingpath means here?',
        },
        {
            'key': 'ccc',
            'value': 'cyclingtrack',
            'tag_specific_comment': 'What ccc=cyclingpath means here?',
        },
        {
            'key': 'ccc',
            'value': 'cyclingcrossing',
            'tag_specific_comment': 'What ccc=cyclingpath means here?',
        },
        {
            'key': 'ccc',
            'value': 'cyclinggreenway',
            'tag_specific_comment': 'What ccc=cyclingpath means here?',
        },
        {
            'key': 'ccc',
            'value': 'cyclnglane',
            'tag_specific_comment': 'What ccc=cyclingpath means here?',
        },
        {
            'key': 'ccc',
            'value': 'cylclinglane',
            'tag_specific_comment': 'What ccc=cyclingpath means here?',
        },
        {
            'key': 'ccc',
            'value': 'cylingpath',
            'tag_specific_comment': 'What ccc=cyclingpath means here?',
        },
        {
            'key': 'ccc',
            'value': 'cycletrack',
            'tag_specific_comment': 'What ccc=cyclingpath means here?',
        },
        {
            'key': 'ccc',
            'value': 'cyclingtunnel',
            'tag_specific_comment': 'What ccc=cyclingpath means here?',
        },
        {
            'key': 'ccc',
            'value': 'cyclingppath',
            'tag_specific_comment': 'What ccc=cyclingpath means here?',
        },        
        {
            'key': 'shop',
            'value': 'Athletic_Club',
            'tag_specific_comment': 'Is it sport club or is it a shop?',
        },
        {
            'key': 'access:hvg',
            'tag_specific_comment': 'Was it supposed to be access:hgv? Would using hgv access tag (see https://wiki.openstreetmap.org/wiki/Key:hgv ) be fitting at least equally well?',
        },
        {
            'key': 'pedestrian',
            'value': 'crossing',
            'tag_specific_comment': 'Was it supposed to mark this way as a pedestrian crossing? Then proper tag is footway=crossing',
        },
        {
            'key': 'pedestrian',
            'value': 'sidewalk',
            'tag_specific_comment': 'Was it supposed to mark this way as a sidewalk? Then proper tag is footway=sidewalk',
        },
        {
            'key': 'pedestrian',
            'value': 'yes',
            'tag_specific_comment': 'Was it supposed to mark legal pedestrian access? In such case - foot=yes is the normal tag for it, see https://wiki.openstreetmap.org/wiki/Key:foot',
        },
        {
            'key': 'horse',
            'value': 'noC',
            'tag_specific_comment': 'horse = noC looks like a typo. It seems that it should be horse = no\n\nBut I was not sure enough to make a remote replacement. Is it safe to change it?',
        },
        {
            'key': 'horse',
            'value': 'nov',
            'tag_specific_comment': 'horse = noC looks like a typo. It seems that it should be horse = no\n\nBut I was not sure enough to make a remote replacement. Is it safe to change it?',
        },
        {
            'key': 'horse',
            'value': 'now',
            'tag_specific_comment': 'horse = now looks like a typo. It seems that it should be horse = no\n\nBut I was not sure enough to make a remote replacement. Is it safe to change it?',
        },
        {
            'key': 'horse',
            'value': 'nor',
            'tag_specific_comment': 'horse = nor looks like a typo. It seems that it should be horse = no\n\nBut I was not sure enough to make a remote replacement. Is it safe to change it?',
        },
        {
            'key': 'private',
            'value': 'yes',
            'tag_specific_comment': 'Is it feature with restricted access where no better access tag applies? (access=private, see https://wiki.openstreetmap.org/wiki/Tag:access%3Dprivate ) Or is it just privately owned? And operator:type=private would fit? (see https://wiki.openstreetmap.org/wiki/Key:operator:type )',
        },
        { # often immediate cleanup based on aerial is possible (waterway=culvert on nodes)
            'key': 'waterway',
            'value': 'culvert',
            'tag_specific_comment': 'Maybe tagging other than waterway=culvert would be better?\n\nTypical tagging for drain/stream/river in culvert is to use tunnel=culvert + waterway=stream (or waterway=drain or waterway=ditch or waterway=river as appropriate) for waterway type.\n\nJust waterway=culvert makes impossible to tag properly what is in this culvert.\n\nSee https://wiki.openstreetmap.org/wiki/Tag:tunnel%3Dculvert',
            'skipped_users': [],
        },
        {
            'key': 'ref',
            'value': 'BRAK W WYKAZIE',
            'tag_specific_comment': 'No to nie jest prawdziwy ref. Lepiej skasować czy wymyślamy jakiś sposób na zapisanie tego bez podawania fikcyjnej wartości ref?',
        },
        {
            'key': 'ref',
            'value': 'Proposed',
            'tag_specific_comment': '(1) is it even existing at all? In OSM we should not map proposed things, and in extreme cases of being mapped they should be clearly marked as proposed\n(2) this is not a real ref value',
        },
        {
            'key': 'ref',
            'value': 'proposed',
            'tag_specific_comment': '(1) is it even existing at all? In OSM we should not map proposed things, and in extreme cases of being mapped they should be clearly marked as proposed\n(2) this is not a real ref value',
        },
        {
            'key': 'proposed',
            'value': 'yes',
            'tag_specific_comment': 'is it even existing at all? In OSM we should not map proposed things, and in extreme cases of being mapped they should be clearly marked as proposed',
        },
        {
            'key': 'power',
            'value': 'abandoned:tower',
            'tag_specific_comment': 'This should be abandoned:power-tower, right?',
        },
        {
            'key': 'sport',
            'value': 'football',
            'tag_specific_comment': 'What kind of football you meant?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:sport%3Dfootball and https://wiki.openstreetmap.org/wiki/Football\n\nsport=soccer, sport=american_football, sport=australian_football, sport=canadian_football, sport=ruby_union, sport=rugby_league, sport=gaelic_games gaelic_games:football=yes are among possible correct tags here',
        },
        {
            'key': 'sidewalk:right',
            'value': 'left',
            'tag_specific_comment': 'so left or right?',
        },
        {
            'key': 'sidewalk:left',
            'value': 'right',
            'tag_specific_comment': 'so left or right?',
        },
        {
            'key': 'sidewalk:right',
            'value': 'both',
            'tag_specific_comment': 'so left or right or both?',
        },
        {
            'key': 'sidewalk:left',
            'value': 'both',
            'tag_specific_comment': 'so left or right or both?',
        },
        {
            'key': 'sidewalk:both',
            'value': 'left',
            'tag_specific_comment': 'so left or right or both?',
        },
        {
            'key': 'sidewalk:both',
            'value': 'right',
            'tag_specific_comment': 'so left or right or both?',
        },
        {
            'key': 'sport',
            'value': 'team_handball',
            'tag_specific_comment': 'Would sport=handball (see https://wiki.openstreetmap.org/wiki/Tag:sport%3Dhandball ) be fitting at least equally well? It seems that sport=team_handball and sport=handball refer to the same thing and second is used more widely while not being worse.',
        },
        {
            'key': 'shop',
            'value': 'Fish_shop',
            'tag_specific_comment': 'is it shop=seafood (fish for eating) or shop=pet (fish as pets)?',
        },
        {
            'key': 'shop',
            'value': 'petrol',
            'tag_specific_comment': 'is it a fuel station? See https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dfuel\n\nOr is it a shop selling botled petrol? Maybe as a fuel?',
        },
        {
            'key': 'shop',
            'value': 'materiales_de_construccion',
            'tag_specific_comment': 'shop=materiales_de_construccion ? shop=building_materials ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dbuilding_materials ) or shop=trade + trade=building_supplies ( https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ) was likely meant',
        },
        {
            'key': 'shop',
            'value': 'building_materials_store',
            'tag_specific_comment': 'shop=building_materials_store ? shop=building_materials ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dbuilding_materials ) or shop=trade + trade=building_supplies ( https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ) was likely meant.\n\nOr is it worth keeping as a separate value? How it differs from them?',
        },
        {
            'key': 'shop',
            'value': 'build',
            'tag_specific_comment': 'shop=build ? shop=building_materials ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dbuilding_materials ) or shop=trade + trade=building_supplies ( https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ) was likely meant.\n\nOr is it worth keeping as a separate value? How it differs from them?',
        },
        {
            'key': 'shop',
            'value': 'building_parts',
            'tag_specific_comment': 'shop=building_parts ? shop=building_materials ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dbuilding_materials ) or shop=trade + trade=building_supplies ( https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ) was likely meant.\n\nOr is it worth keeping as a separate value? How it differs from them?',
        },


        {
            'key': 'shop',
            'value': 'hotel',
            'tag_specific_comment': 'shop=hotel ? Is it a mistagged hotel? Maybe it should be https://wiki.openstreetmap.org/wiki/Tag:tourism%3Dhotel ? Is it a place selling hotel equipment (in such case shop=trade trade=hotel_equipment would be likely better and more clear) ? Something else?',
        }, # create_notes_based_on_some_complex_filters.py in my script bundle creates notes for shop=hotel tourism=hotel
        {
            'key': 'shop',
            'value': 'Hotel',
            'tag_specific_comment': 'shop=Hotel ? Is it a mistagged hotel? Maybe it should be https://wiki.openstreetmap.org/wiki/Tag:tourism%3Dhotel ? Is it a place selling hotel equipment (in such case shop=trade trade=hotel_equipment would be likely better and more clear) ? Something else?', # create_notes_based_on_some_complex_filters.py in my script bundle creates notes for shop=Hotel tourism=hotel (see handle_shop_tag_duplicating_real_one)
        }, 
        {
            'key': 'shop',
            'value': 'restaurant',
            'tag_specific_comment': 'shop=restaurant ? Is it a mistagged restaurant? Maybe it should be https://wiki.openstreetmap.org/wiki/Tag:amenity%3Drestaurant ? Is it a place selling restaurant equipment (in such case shop=trade trade=restaurant_equipment would be likely better and more clear) ? Something else?',# create_notes_based_on_some_complex_filters.py in my script bundle creates notes for shop=Restaurant amenity=restaurant (see handle_shop_tag_duplicating_real_one)
        }, 
        {
            'key': 'shop',
            'value': 'Restaurant',
            'tag_specific_comment': 'shop=Restaurant ? Is it a mistagged restaurant? Maybe it should be https://wiki.openstreetmap.org/wiki/Tag:amenity%3Drestaurant ? Is it a place selling restaurant equipment (in such case shop=trade trade=restaurant_equipment would be likely better and more clear) ? Something else?',
        },  # create_notes_based_on_some_complex_filters.py in my script bundle creates notes for shop=Restaurant amenity=restaurant (see handle_shop_tag_duplicating_real_one)
        {
            'key': 'shop',
            'value': 'restaurante',
            'tag_specific_comment': 'shop=restaurante ? Is it a mistagged restaurant? Maybe it should be https://wiki.openstreetmap.org/wiki/Tag:amenity%3Drestaurant ? Is it a place selling restaurant equipment (in such case shop=trade trade=restaurant_equipment would be likely better and more clear) ? Something else?',
        },  # create_notes_based_on_some_complex_filters.py in my script bundle creates notes for shop=restaurante amenity=restaurant (see handle_shop_tag_duplicating_real_one)
        {
            'key': 'shop',
            'value': 'pub',
            'tag_specific_comment': 'shop=pub ? Is it a mistagged pub? Maybe it should be https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dpub ? Is it a place selling pub equipment (in such case shop=trade trade=pub_equipment would be likely better and more clear) ? Something else?',
        },  # create_notes_based_on_some_complex_filters.py in my script bundle creates notes for shop=pub amenity=pub (see handle_shop_tag_duplicating_real_one)
        {
            'key': 'shop',
            'value': 'Cafe',
            'tag_specific_comment': 'shop=Cafe ? Is it a mistagged cafe? Maybe it should be https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dcafe ? Is it a place selling cafe equipment (in such case shop=trade trade=cafe_equipment would be likely better and more clear) ? Something else?', # create_notes_based_on_some_complex_filters.py in my script bundle creates notes for shop=Cafe amenity=cafe (see handle_shop_tag_duplicating_real_one)
        }, 
        {
            'key': 'shop',
            'value': 'cafe',
            'tag_specific_comment': 'shop=cafe ? Is it a mistagged cafe? Maybe it should be https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dcafe ? Is it a place selling cafe equipment (in such case shop=trade trade=cafe_equipment would be likely better and more clear) ? Something else?', # create_notes_based_on_some_complex_filters.py in my script bundle creates notes for shop=cafe amenity=cafe (see handle_shop_tag_duplicating_real_one)
        },
        {
            'key': 'shop',
            'value': 'theatre',
            'tag_specific_comment': 'shop=theatre ? Is it a mistagged amenity=theatre? Is it a gift shop in a theatre ( https://wiki.openstreetmap.org/wiki/Tag:shop=gift ) ? Place selling theatre tickets? ( https://wiki.openstreetmap.org/wiki/Tag:shop=ticket or https://wiki.openstreetmap.org/wiki/Tag:vending%3Dadmission_tickets ) Is it a something else? It almost certainly is mistagged',
        }, # create_notes_based_on_some_complex_filters.py detects it (in my automation scripts)
        {
            'key': 'shop',
            'value': 'marketplace',
            'tag_specific_comment': 'shop=marketplace ? Is it an entire marketplace? ( https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dmarketplace ) Specific shop (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values) ? Something else? ',
        }, # create_notes_based_on_some_complex_filters.py detects it (in my automation scripts)
        {
            'key': 'shop',
            'value': 'market',
            'tag_specific_comment': 'shop=market ? Is it an entire marketplace? ( https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dmarketplace ) Specific shop (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values) ? Something else? ',
        }, # create_notes_based_on_some_complex_filters.py detects it (in my automation scripts)
        {
            'key': 'shop',
            'value': 'bank',
            'tag_specific_comment': 'shop=bank ? Is it a mistagged bank? Maybe it should be https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dbank ? Is it a place selling bank equipment (in such case shop=trade trade=bank_equipment would be likely better and more clear) ? Something else?',
        }, # create_notes_based_on_some_complex_filters.py detects it (in my automation scripts)
        {
            'key': 'shop',
            'value': 'museum',
            'tag_specific_comment': 'shop=museum ? Is it a mistagged tourism=museum? Is it a gift shop in a museum ( https://wiki.openstreetmap.org/wiki/Tag:shop=gift ) ? Place selling museum tickets? ( https://wiki.openstreetmap.org/wiki/Tag:shop=ticket or https://wiki.openstreetmap.org/wiki/Tag:vending%3Dadmission_tickets ) Is it a something else? It almost certainly is mistagged',
        }, # create_notes_based_on_some_complex_filters.py detects it (in my automation scripts)
        {
            'key': 'shop',
            'value': 'library',
            'tag_specific_comment': 'shop=library is quite unusual and surprising\n\nIs it bookstore or library? Or something else? If shop=library is correct - what it means here?',
        },
        {
            'key': 'shop',
            'value': 'Library',
            'tag_specific_comment': 'shop=Library is quite unusual and surprising\n\nIs it bookstore or library? Or something else? If shop=library is correct - what it means here?',
        },
        {
            'key': 'shop',
            'value': 'boutique',
            'tag_specific_comment': 'shop=boutique? Is it shop selling clothes? Then maybe shop=clothes would fit well, see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dclothes\n\nOr maybe shop=fashion_accessories ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dfashion_accessories ) would fit better? Or shop=bag ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dbag ) ?\n\nOr is it some completely different type of shop, with tag used as "boutique" is French word for shop? In such case see https://wiki.openstreetmap.org/wiki/Key:shop for some documented values.\n\nFor shop=boutique info see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dboutique page',
        },
        {
            'key': 'shop',
            'value': 'botique',
            'tag_specific_comment': 'shop=botique? Is it shop selling clothes? Then maybe shop=clothes would fit well, see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dclothes\n\nOr maybe shop=fashion_accessories ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dfashion_accessories ) would fit better? Or shop=bag ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dbag ) ?\n\nOr is it some completely different type of shop, with tag used as "boutique" is French word for shop? In such case see https://wiki.openstreetmap.org/wiki/Key:shop for some documented values.\n\nFor shop=boutique info see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dboutique page (botique here is likely mispelling of boutique, at least I guess so)',
        },
        {
            'key': 'shop',
            'value': 'tourism',
            'tag_specific_comment': "shop=tourism ? " + """Is it a shop for tourists, unused by local people? Are they selling tourist equipment? Selling tours?

Would maybe https://wiki.openstreetmap.org/wiki/Tag:shop=gift or https://wiki.openstreetmap.org/wiki/Tag:shop=travel_agency or https://wiki.openstreetmap.org/wiki/Tag:shop=outdoor would fit better?

Or something else from https://wiki.openstreetmap.org/wiki/Key:shop""",
        },
        {
            'key': 'shop',
            'value': 'tourist',
            'tag_specific_comment': "shop=tourist ? " + """Is it a shop for tourists, unused by local people? Are they selling tourist equipment? Selling tours?

Would maybe https://wiki.openstreetmap.org/wiki/Tag:shop=gift or https://wiki.openstreetmap.org/wiki/Tag:shop=travel_agency or https://wiki.openstreetmap.org/wiki/Tag:shop=outdoor would fit better?

Or something else from https://wiki.openstreetmap.org/wiki/Key:shop""",
        },
        {
            'key': 'shop',
            'value': 'trcuk',
            'tag_specific_comment': 'shop=trcuk? Maybe shop=truck was intended? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtruck',
        },
        {
            'key': 'shop',
            'value': 'trucks',
            'tag_specific_comment': 'Maybe shop=truck was intended? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtruck',
        },
        {
            'key': 'shop',
            'value': 'bowed_ice',
            'tag_specific_comment': 'shop=bowed_ice? Is it some type of ice cream? Maybe shop=ice_cream would work well here? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dice_cream',
        },
        {
            'key': 'shop',
            'value': 'shaved_ice',
            'tag_specific_comment': 'shop=shaved_ice? Is it some type of ice cream? Maybe shop=ice_cream would work well here? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dice_cream',
        },
        {
            'key': 'shop',
            'value': 'cartridge',
            'tag_specific_comment': 'shop=cartridge? Maybe shop=printer_ink would work well? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dprinter_ink\n\nOr is it for a different type of catridge, maybe ammunition-related?',
        },
        {
            'key': 'shop',
            'value': 'bar',
            'tag_specific_comment': 'shop=bar? Is it even a shop? Maybe https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dbar was meant here?',
        },
        {
            'key': 'shop',
            'value': 'Bar',
            'tag_specific_comment': 'shop=Bar? Is it even a shop? Maybe https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dbar was meant here?',
        },
        {
            'key': 'shop',
            'value': 'Chocolade winkel',
            'tag_specific_comment': 'Is it shop=chocolate? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dchocolate',
        },
        {
            'key': 'shop',
            'value': 'sweets_shop',
            'tag_specific_comment': 'shop=sweets_shop? Is it shop=confectionery ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconfectionery ) ? If not, how it differs from shop=confectionery ? Maybe it is https://wiki.openstreetmap.org/wiki/Tag:shop%3Dpastry or https://wiki.openstreetmap.org/wiki/Tag:shop%3Dchocolate ?',
        },
        {
            'key': 'shop',
            'value': 'desserts',
            'tag_specific_comment': 'shop=sweets_shop? Is it shop=confectionery ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconfectionery ) ? If not, how it differs from shop=confectionery ? Maybe it is https://wiki.openstreetmap.org/wiki/Tag:shop%3Dpastry or https://wiki.openstreetmap.org/wiki/Tag:shop%3Dchocolate ?',
        },
        {
            'key': 'shop',
            'value': 'Sweet_Shop',
            'tag_specific_comment': 'shop=Sweet_Shop ? Is it shop=confectionery ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconfectionery ) ? If not, how it differs from shop=confectionery ? Maybe it is https://wiki.openstreetmap.org/wiki/Tag:shop%3Dpastry or https://wiki.openstreetmap.org/wiki/Tag:shop%3Dchocolate ?',
        },
        {
            'key': 'shop',
            'value': 'Food_vender',
            'tag_specific_comment': 'shop=Food_vender ? Is it amenity=fast_food ? Maybe with street_vendor=yes ? If not, what this tag is intended to mean? See https://wiki.openstreetmap.org/wiki/Tag:street_vendor%3Dyes and https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dfast_food',
        },
        {
            'key': 'shop',
            'value': 'fast_food',
            'tag_specific_comment': 'shop=fast_food ? Is it amenity=fast_food ? If not, what this tag is intended to mean? See https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dfast_food',
        },
        {
            'key': 'shop',
            'value': 'fast food',
            'tag_specific_comment': 'shop=fast food ? Is it amenity=fast_food ? If not, what this tag is intended to mean? See https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dfast_food',
        },
        {
            'key': 'shop',
            'value': 'takeaway',
            'tag_specific_comment': 'shop=take_away ? Is it amenity=fast_food ? If not, what this tag is intended to mean? See https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dfast_food',
        },
        {
            'key': 'shop',
            'value': 'take_away',
            'tag_specific_comment': 'shop=take_away ? Is it amenity=fast_food ? If not, what this tag is intended to mean? See https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dfast_food',
        },
        {
            'key': 'shop',
            'value': 'takeout',
            'tag_specific_comment': 'shop=takeout ? Is it amenity=fast_food ? If not, what this tag is intended to mean? See https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dfast_food',
        },
        {
            'key': 'shop',
            'value': 'take away',
            'tag_specific_comment': 'shop=take away ? Is it amenity=fast_food ? If not, what this tag is intended to mean? See https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dfast_food',
        },
        {
            'key': 'shop',
            'value': 'Take Away',
            'tag_specific_comment': 'shop=take away ? Is it amenity=fast_food ? If not, what this tag is intended to mean? See https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dfast_food',
        },
        {
            'key': 'shop',
            'value': 'shop=restaurant',
            'tag_specific_comment': 'shop= shop=restaurant? Is it even a shop? Maybe https://wiki.openstreetmap.org/wiki/Tag:amenity%3Drestaurant was meant here?',
        },
        {
            'key': 'shop',
            'value': 'pizza',
            'tag_specific_comment': 'shop=pizza ? Is it amenity=fast_food cuisine=pizza or amenity=restaurant cuisine=pizza by any chance? Or are they selling pizza not ready to eat? Or ingredients for pizza?',
        },
        {
            'key': 'shop',
            'value': 'Italian Pasta & Pizza',
            'tag_specific_comment': 'shop=Italian Pasta & Pizza ? Is it amenity=fast_food cuisine=italian;pizza or amenity=restaurant cuisine=italian;pizza by any chance? Or are they selling pizza not ready to eat? Or ingredients for pizza?',
        },
        {
            'key': 'shop',
            'value': 'fish_&_chips',
            'tag_specific_comment': 'shop=fish_&_chips ? Is it amenity=fast_food or amenity=restaurant by any chance? Or are they selling ingredients for that type of food?',
        },
        {
            'key': 'shop',
            'value': 'pizzeria',
            'tag_specific_comment': 'shop=pizzeria ? Is it amenity=fast_food cuisine=pizza or amenity=restaurant cuisine=pizza by any chance? Or are they selling pizza not ready to eat? Or ingredients for pizza?',
        },
        {
            'key': 'shop',
            'value': 'Pizzeria',
            'tag_specific_comment': 'shop=Pizzeria ? Is it amenity=fast_food cuisine=pizza or amenity=restaurant cuisine=pizza by any chance? Or are they selling pizza not ready to eat? Or ingredients for pizza?',
        },
        {
            'key': 'shop',
            'value': 'kebab',
            'tag_specific_comment': 'shop=kebab ? Is it amenity=fast_food cuisine=kebab?  Or are they selling barbecue ingredients? Or is it a restaurant? Or is kabab not a type for kebab?',
        },
        {
            'key': 'shop',
            'value': 'kabab',
            'tag_specific_comment': 'shop=kabab ? Is it amenity=fast_food cuisine=kebab?  Or are they selling barbecue ingredients? Or is it a restaurant? Or is kabab not a type for kebab?',
        },
        {
            'key': 'shop',
            'value': 'sandwich',
            'tag_specific_comment': 'shop=sandwich ? Is it amenity=fast_food cuisine=sandwich ? Or are they selling sandwiches not ready to eat? Or ingredients for sandwiches?',
        },
        {
            'key': 'shop',
            'value': 'sandwiches',
            'tag_specific_comment': 'shop=sandwiches ? Is it amenity=fast_food cuisine=sandwich ? Or are they selling sandwiches not ready to eat? Or ingredients for sandwiches?',
        },
        {
            'key': 'shop',
            'value': 'breakfast',
            'tag_specific_comment': 'shop=breakfast ? Is it amenity=fast_food ? Or are they selling food usable only for breakfeasts? Or is it something else entirely?',
        },
        {
            'key': 'shop',
            'value': 'off_licence',
            'tag_specific_comment': 'shop=off_licence ? Is it simply an alcohol shop? Is it OK to retag it remotely rather than opening notes?',
        },
        {
            'key': 'shop',
            'value': 'off_license',
            'tag_specific_comment': 'shop=off_license ? Is it simply an alcohol shop? Is it OK to retag it remotely rather than opening notes?',
        },
        {
            'key': 'shop',
            'value': 'off-license',
            'tag_specific_comment': 'shop=off_license ? Is it simply an alcohol shop? Is it OK to retag it remotely rather than opening notes?',
        },
        {
            'key': 'shop',
            'value': 'car_wash',
            'tag_specific_comment': 'shop=car_wash ? Is it simply https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dcar_wash ? Or are they selling some producs for washing car and you cannot wash car there?',
        },
        {
            'key': 'shop',
            'value': 'market',
            'tag_specific_comment': 'What kind of shop is that? Is it shop=convenience? shop=supermarket? amenity=marketplace?',
        },
        {
            'key': 'shop',
            'value': 'minimarket',
            'tag_specific_comment': 'What kind of shop is that? Can it be assumed to be shop=convenience ( see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconvenience and https://www.openstreetmap.org/note/3822336 ) and changed remotely without verification? Or is it better to open a note and wait for a local check?',
        },
        {
            'key': 'shop',
            'value': 'MiniMarket',
            'tag_specific_comment': 'What kind of shop is that? Can it be assumed to be shop=convenience ( see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconvenience and https://www.openstreetmap.org/note/3822336 ) and changed remotely without verification? Or is it better to open a note and wait for a local check?',
        },
        {
            'key': 'shop',
            'value': 'мини_маркет',
            'tag_specific_comment': 'What kind of shop is that? Can it be assumed to be shop=convenience ( see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dconvenience ) and changed remotely without verification? Or is it better to open a note and wait for a local check?',
        },
        {
            'key': 'shop',
            'value': 'fruit',
            'tag_specific_comment': 'shop=fruit ? Maybe shop=greengrocer was intended? If they truly sell solely only fruit then maybe extra tag like greengrocer=fruit would be better? If they sell also vegetables then https://wiki.openstreetmap.org/wiki/Tag:shop=greengrocer is definitely better.\n\nshop=greengrocer is far more widely used and supported and does fit even if only variety of fruits is sold.\n\nBut maybe another shop tag would fit better? Maybe shop=farm? ( https://wiki.openstreetmap.org/wiki/Tag:shop=farm )',
        },
        {
            'key': 'shop',
            'value': 'fruits',
            'tag_specific_comment': 'shop=fruits ? Maybe shop=greengrocer was intended? If they truly sell solely only fruit then maybe extra tag like greengrocer=fruit would be better? If they sell also vegetables then https://wiki.openstreetmap.org/wiki/Tag:shop=greengrocer is definitely better.\n\nshop=greengrocer is far more widely used and supported and does fit even if only variety of fruits is sold.\n\nBut maybe another shop tag would fit better? Maybe shop=farm? ( https://wiki.openstreetmap.org/wiki/Tag:shop=farm )',
        },
        {
            'key': 'shop',
            'value': 'Fruits',
            'tag_specific_comment': 'shop=Fruits ? Maybe shop=greengrocer was intended? If they truly sell solely only fruit then maybe extra tag like greengrocer=fruit would be better? If they sell also vegetables then https://wiki.openstreetmap.org/wiki/Tag:shop=greengrocer is definitely better.\n\nshop=greengrocer is far more widely used and supported and does fit even if only variety of fruits is sold.\n\nBut maybe another shop tag would fit better? Maybe shop=farm? ( https://wiki.openstreetmap.org/wiki/Tag:shop=farm )',
        },
        {
            'key': 'shop',
            'value': 'vegetables',
            'tag_specific_comment': 'shop=vegetables ? Maybe shop=greengrocer was intended? If they truly sell solely only vegetables then maybe extra tag like greengrocer=vegetables would be better? If they sell also fruits then https://wiki.openstreetmap.org/wiki/Tag:shop=greengrocer is definitely better.\n\nshop=greengrocer is far more widely used and supported and does fit even if only variety of vegetables is sold.\n\nBut maybe another shop tag would fit better? Maybe shop=farm? ( https://wiki.openstreetmap.org/wiki/Tag:shop=farm )',
        },
        {
            'key': 'shop',
            'value': 'vegetagles',
            'tag_specific_comment': 'shop=vegetagles ? Maybe shop=greengrocer was intended? If they truly sell solely only vegetables then maybe extra tag like greengrocer=vegetables would be better? If they sell also fruits then https://wiki.openstreetmap.org/wiki/Tag:shop=greengrocer is definitely better.\n\nshop=greengrocer is far more widely used and supported and does fit even if only variety of vegetables is sold.\n\nBut maybe another shop tag would fit better? Maybe shop=farm? ( https://wiki.openstreetmap.org/wiki/Tag:shop=farm )',
        },
        {
            'key': 'shop',
            'value': 'vegetable_store',
            'tag_specific_comment': 'shop=vegetable_store ? Maybe shop=greengrocer was intended? If they truly sell solely only vegetables then maybe extra tag like greengrocer=vegetables would be better? If they sell also fruits then https://wiki.openstreetmap.org/wiki/Tag:shop=greengrocer is definitely better.\n\nshop=greengrocer is far more widely used and supported and does fit even if only variety of vegetables is sold.\n\nBut maybe another shop tag would fit better? Maybe shop=farm? ( https://wiki.openstreetmap.org/wiki/Tag:shop=farm )',
        },
        {
            'key': 'shop',
            'value': 'vegetable_shop',
            'tag_specific_comment': 'shop=vegetable_shop ? Maybe shop=greengrocer was intended? If they truly sell solely only vegetables then maybe extra tag like greengrocer=vegetables would be better? If they sell also fruits then https://wiki.openstreetmap.org/wiki/Tag:shop=greengrocer is definitely better.\n\nshop=greengrocer is far more widely used and supported and does fit even if only variety of vegetables is sold.\n\nBut maybe another shop tag would fit better? Maybe shop=farm? ( https://wiki.openstreetmap.org/wiki/Tag:shop=farm )',
        },
        {
            'key': 'shop',
            'value': 'vegetable',
            'tag_specific_comment': 'shop=vegetable ? Maybe shop=greengrocer was intended? If they truly sell solely only vegetables then maybe extra tag like greengrocer=vegetable would be better? If they sell also fruits then https://wiki.openstreetmap.org/wiki/Tag:shop=greengrocer is definitely better.\n\nshop=greengrocer is far more widely used and supported and does fit even if only variety of vegetables is sold.\n\nBut maybe another shop tag would fit better? Maybe shop=farm? ( https://wiki.openstreetmap.org/wiki/Tag:shop=farm )',
        },
        {
            'key': 'shop',
            'value': 'vegitable_shop',
            'tag_specific_comment': 'shop=vegitable_shop ? Maybe shop=greengrocer was intended? If they truly sell solely only vegetables then maybe extra tag like greengrocer=vegetable would be better? If they sell also fruits then https://wiki.openstreetmap.org/wiki/Tag:shop=greengrocer is definitely better.\n\nshop=greengrocer is far more widely used and supported and does fit even if only variety of vegetables is sold.\n\nBut maybe another shop tag would fit better? Maybe shop=farm? ( https://wiki.openstreetmap.org/wiki/Tag:shop=farm )',
        },
        {
            'key': 'shop',
            'value': 'vegitables',
            'tag_specific_comment': 'shop=vegitables ? Maybe shop=greengrocer was intended? If they truly sell solely only vegetables then maybe extra tag like greengrocer=vegetable would be better? If they sell also fruits then https://wiki.openstreetmap.org/wiki/Tag:shop=greengrocer is definitely better.\n\nshop=greengrocer is far more widely used and supported and does fit even if only variety of vegetables is sold.\n\nBut maybe another shop tag would fit better? Maybe shop=farm? ( https://wiki.openstreetmap.org/wiki/Tag:shop=farm )',
        },
        {
            'key': 'shop',
            'value': 'vegetable market',
            'tag_specific_comment': 'shop=vegetable market ? Maybe shop=greengrocer was intended? Or multiple such objects? If they truly sell solely only vegetables then maybe extra tag like greengrocer=vegetable would be better? If they sell also fruits then https://wiki.openstreetmap.org/wiki/Tag:shop=greengrocer is definitely better.\n\nshop=greengrocer is far more widely used and supported and does fit even if only variety of vegetables is sold.\n\nBut maybe another shop tag would fit better? Maybe shop=farm? ( https://wiki.openstreetmap.org/wiki/Tag:shop=farm )',
        },
        {
            'key': 'shop',
            'value': 'salon',
            'tag_specific_comment': 'shop=salon ? Is it shop=beauty or shop=hairdresser by any chance? If shop=salon is intentional - what it means?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop%3Dhairdresser and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dbeauty',
        },
        {
            'key': 'shop',
            'value': 'Beauty Salon',
            'tag_specific_comment': 'shop=Beauty Salon ? Is it shop=beauty or shop=hairdresser by any chance? If shop=Beauty Salon is intentional - what it means?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop%3Dhairdresser and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dbeauty',
        },
        {
            'key': 'shop',
            'value': 'Hair Salon',
            'tag_specific_comment': 'shop=Hair Salon ? Is it shop=hairdresser or shop=beauty by any chance? If shop=Hair Salon is intentional - what it means?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop%3Dhairdresser and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dbeauty',
        },
        {
            'key': 'shop',
            'value': 'machine',
            'tag_specific_comment': 'shop=machine ? What kind of machines? Industrial machines? Washing machines? Computers? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed). Or is it not actually a place where you can walk in and buy stuff? But rather internal company office tagged as office=company?',
        },
        {
            'key': 'shop',
            'value': 'machines',
            'tag_specific_comment': 'shop=machines ? What kind of machines? Industrial machines? Washing machines? Computers? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed). Or is it not actually a place where you can walk in and buy stuff? But rather internal company office tagged as office=company?',
        },
        {
            'key': 'shop',
            'value': 'Machines',
            'tag_specific_comment': 'shop=Machines ? What kind of machines? Industrial machines? Washing machines? Computers? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed). Or is it not actually a place where you can walk in and buy stuff? But rather internal company office tagged as office=company?',
        },
        {
            'key': 'shop',
            'value': 'machinery',
            'tag_specific_comment': 'shop=machinery ? What kind of machines? Industrial machines? Washing machines? Computers? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed). Or is it not actually a place where you can walk in and buy stuff? But rather internal company office tagged as office=company?',
        },
        {
            'key': 'shop',
            'value': 'Machinery',
            'tag_specific_comment': 'shop=Machinery ? What kind of machines? Industrial machines? Washing machines? Computers? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed). Or is it not actually a place where you can walk in and buy stuff? But rather internal company office tagged as office=company?',
        },
        {
            'key': 'shop',
            'value': 'specialty',
            'tag_specific_comment': 'shop=specialty ? What kind of specialty? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'Specialty',
            'tag_specific_comment': 'shop=Specialty ? What kind of specialty? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'materials',
            'tag_specific_comment': 'shop=materials ? What kind of materials? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'hire',
            'tag_specific_comment': 'shop=hire ? What kind of hiring can be done here? Can you look for job here? Hire a guide? Something else?',
        },
        {
            'key': 'shop',
            'value': 'Hire_Shop',
            'tag_specific_comment': 'shop=Hire_Shop ? What kind of hiring can be done here? Can you look for job here? Hire a guide? Something else?',
        },
        {
            'key': 'shop',
            'value': 'chicken_shop',
            'tag_specific_comment': 'shop=chicken_shop ? is it seling living chickens, raw chicken meat as food, products for chickens like animal feed? Something else?',
        },
        {
            'key': 'shop',
            'value': 'chicken shop',
            'tag_specific_comment': 'shop=chicken shop ? is it seling living chickens, raw chicken meat as food, products for chickens like animal feed? Something else?',
        },
        {
            'key': 'shop',
            'value': 'chicken',
            'tag_specific_comment': 'shop=chicken ? is it seling living chickens, raw chicken meat as food, products for chickens like animal feed? Something else?',
        },
        {
            'key': 'shop',
            'value': 'Chicken',
            'tag_specific_comment': 'shop=Chicken ? is it seling living chickens, raw chicken meat as food, products for chickens like animal feed? Something else?',
        },
        {
            'key': 'shop',
            'value': 'poultry',
            'tag_specific_comment': 'shop=poultry ? is it seling living poultry, raw poultry meat as food, products for poultry like animal feed? Something else?',
        },
        {
            'key': 'shop',
            'value': 'chicken_only',
            'tag_specific_comment': 'shop=chicken_only ? is it seling living chickens, raw chicken meat as food, products for chicken like animal feed? Something else?',
        },
        {
            'key': 'shop',
            'value': 'Chicken Store',
            'tag_specific_comment': 'shop=Chicken Store ? is it seling living chickens, raw chicken meat as food, products for chickens like animal feed? Something else?',
        },
        {
            'key': 'shop',
            'value': 'house',
            'tag_specific_comment': 'shop=house ? Are they selling houses? Products for furnishing house? Something else? ( shop=prefabricated_house for say prefabricated houses being sold there? )',
        },
        {
            'key': 'shop',
            'value': 'building',
            'tag_specific_comment': 'shop=building ? Are they selling houses? Products for furnishing house? Something else?',
        },
        {
            'key': 'shop',
            'value': 'Home',
            'tag_specific_comment': 'shop=Home ? Are they selling houses? Products for furnishing house? Something else?',
        },
        {
            'key': 'shop',
            'value': 'interiors',
            'tag_specific_comment': 'shop=interiors ? What kind of shop, if any is here? Is it intentionally used instead of shop=interior_decoration / shop=furniture ? (see https://wiki.openstreetmap.org/wiki/Tag:shop=interior_decoration and https://wiki.openstreetmap.org/wiki/Tag:shop=furniture ) ?\n\nIf yes, what is the difference? Should we document this shop value as distinct, valid and useful? Or maybe this shop=home is about selling real estate?',
        },
        {
            'key': 'shop',
            'value': 'home_decor',
            'tag_specific_comment': 'shop=home_decor ? What kind of shop, if any is here? Is it intentionally used instead of shop=interior_decoration ? (see https://wiki.openstreetmap.org/wiki/Tag:shop=interior_decoration ) ?\n\nIf yes, what is the difference? Should we document this shop value as distinct, valid and useful? Or maybe this shop=home is about selling real estate?',
        },
        {
            'key': 'shop',
            'value': 'grossery',
            'tag_specific_comment': 'shop=grossery ? is it shop=grocery by any chance? Or something else? If shop=grossery is intentional - what it means?',
        },
        {
            'key': 'shop',
            'value': 'asian',
            'tag_specific_comment': 'shop=asian ? What kind of products is sold here? Food? Cars? Cutlery? Electronics?\n\nIf it is selling food - maybe focus can be expressed by cuisine=asian tag?',
        },
        {
            'key': 'shop',
            'value': 'asian grocery',
            'tag_specific_comment': 'shop=asian grocery ? is it shop=grocery by any chance? Maybe focus can be expressed by cuisine=asian tag?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop=grocery',
        },
        {
            'key': 'shop',
            'value': 'herbs',
            'tag_specific_comment': 'shop=herbs ? is it shop=spices or shop=herbalist ? Or something else? See https://wiki.openstreetmap.org/wiki/Tag:shop=spices and https://wiki.openstreetmap.org/wiki/Tag:shop=herbalist',
        },
        {
            'key': 'shop',
            'value': 'herb',
            'tag_specific_comment': 'shop=herb ? is it shop=spices or shop=herbalist Or something else? ? See https://wiki.openstreetmap.org/wiki/Tag:shop=spices and https://wiki.openstreetmap.org/wiki/Tag:shop=herbalist',
        },
        {
            'key': 'shop',
            'value': 'beauty_products',
            'tag_specific_comment': 'shop=beauty_products ? Is it intentionally used instead of more typical shop=cosmetics ? How it differs from it? Maybe retagging to shop=cosmetics would be a reasonable idea?',
        },
        {
            'key': 'shop',
            'value': '便利店',
            'tag_specific_comment': 'shop=便利店 ? What kind of shop is that? Can it be assumed to be shop=convenience ( see https://www.openstreetmap.org/note/3822609 ) and changed remotely without verification? Or is it better to open a note and wait for a local check?',
        },
        {
            'key': 'shop',
            'value': 'abarrotes',
            'tag_specific_comment': 'shop=abarrotes ? What kind of shop is that? Can it be assumed to be shop=convenience ( see https://www.openstreetmap.org/note/3805281 ) and changed remotely without verification? Or is it better to open a note and wait for a local check?',
        },
        {
            'key': 'shop',
            'value': 'vision',
            'tag_specific_comment': 'shop=vision ? Is it optician ( https://wiki.openstreetmap.org/wiki/Tag:shop=optician ) or something else?',
        },
        {
            'key': 'shop',
            'value': 'opticial',
            'tag_specific_comment': 'shop=opticial ? Is it optician ( https://wiki.openstreetmap.org/wiki/Tag:shop=optician ) or something else?',
        },
        {
            'key': 'shop',
            'value': 'optic',
            'tag_specific_comment': 'shop=optic ? Is it optician ( https://wiki.openstreetmap.org/wiki/Tag:shop=optician ) or something else?',
        },
        {
            'key': 'shop',
            'value': 'optical',
            'tag_specific_comment': 'shop=optical ? Is it optician ( https://wiki.openstreetmap.org/wiki/Tag:shop=optician ) or something else?',
        },
        {
            'key': 'shop',
            'value': 'Optical_Shop',
            'tag_specific_comment': 'shop=Optical_Shop ? Is it optician ( https://wiki.openstreetmap.org/wiki/Tag:shop=optician ) or something else?',
        },
        {
            'key': 'shop',
            'value': 'spectacles',
            'tag_specific_comment': 'shop=spectacles ? Is it optician ( https://wiki.openstreetmap.org/wiki/Tag:shop=optician ) or something else?',
        },
        {
            'key': 'shop',
            'value': 'Traditional Broom factory',
            'tag_specific_comment': 'shop=Traditional Broom factory ? Is it shop selling brooms? Or just place producing them? (man_made=works?)',
        },
        {
            'key': 'shop',
            'value': 'producent',
            'tag_specific_comment': 'shop=producent ? Is it shop selling something? Or just place producing something and where you cannot walk in and buy that? In the second case it is rather man_made=works than a shop.',
        },
        {
            'key': 'shop',
            'value': 'fabrication',
            'tag_specific_comment': 'shop=fabrication ? Is it shop selling something? Or just place producing something and where you cannot walk in and buy that? In the second case it is rather man_made=works than a shop.',
        },
        {
            'key': 'shop',
            'value': 'noodle_production',
            'tag_specific_comment': 'shop=noodle_production ? Is it shop selling noodles? Or just place producing them and where you cannot walk in and buy them? In the second case it is rather man_made=works than a shop.',
        },
        {
            'key': 'shop',
            'value': 'tyre_manufacture',
            'tag_specific_comment': 'shop=tyre_manufacture ? Is it shop selling tyres? Or just place producing them and where you cannot walk in and buy them? In the second case it is rather man_made=works than a shop.',
        },
        {
            'key': 'shop',
            'value': 'cookie_factory',
            'tag_specific_comment': 'shop=cookie_factory ? Is it shop selling cookies? Or just place producing them? (man_made=works?)',
        },
        {
            'key': 'shop',
            'value': 'tortilla_factory',
            'tag_specific_comment': 'shop=tortilla_factory ? Is it shop selling tortillas? Or just place producing them? (man_made=works?)',
        },
        {
            'key': 'shop',
            'value': 'Jewelry Factory',
            'tag_specific_comment': 'shop=Jewelry Factory ? Is it shop selling jewelry? Or just place producing it? (man_made=works?)',
        },
        {
            'key': 'shop',
            'value': 'cheese_factory',
            'tag_specific_comment': 'shop=cheese_factory ? Is it shop selling cheese? Or just place producing them? (man_made=works?)',
        },
        {
            'key': 'shop',
            'value': 'Cheese_factory',
            'tag_specific_comment': 'shop=Cheese_factory ? Is it shop selling cheese? Or just place producing them? (man_made=works?)',
        },
        {
            'key': 'shop',
            'value': '米廠',
            'tag_specific_comment': 'shop=米廠 ? Is it rice processing facility as mentioned in https://www.openstreetmap.org/note/3806264 ? (man_made=works?)',
        },
        {
            'key': 'shop',
            'value': '米工廠',
            'tag_specific_comment': 'shop=米工廠 ? Is it rice processing facility as mentioned in https://www.openstreetmap.org/note/3806264 ? (man_made=works?)',
        },
        {
            'key': 'shop',
            'value': 'cider factory',
            'tag_specific_comment': 'shop=cider factory ? What kind of shop, if any is here? Is it selling cider? Other alcohol? Is it maybe man_made=works, rather than actual shop? Or internal company office?',
        },
        {
            'key': 'shop',
            'value': 'Samurai_doll_factory',
            'tag_specific_comment': 'shop=Samurai_doll_factory ? What kind of shop, if any is here? Is it selling samurai dolls? Other dolls? Is it maybe man_made=works, rather than actual shop? Or internal company office?',
        },
        {
            'key': 'shop',
            'value': 'manufacturing',
            'tag_specific_comment': 'shop=manufacturing ? What kind of shop, if any is here? Is it selling anything on side? Is it maybe man_made=works, rather than actual shop? Or internal company office?',
        },
        {
            'key': 'shop',
            'value': 'Garden_Machinery',
            'tag_specific_comment': 'shop=Garden_Machinery ? What kind of shop, if any is here?\n\nIs it office of company and no clients can enter here? Is it point where client can walk in and arrange selling of product? Is it shop selling these? Factory making them?',
        },
        {
            'key': 'shop',
            'value': 'Lubricants',
            'tag_specific_comment': 'shop=Lubricants ? What kind of shop, if any is here?\n\nIs it office of company and no clients can enter here? Is it point where client can walk in and arrange selling of product? Is it shop selling these? Factory making them?',
        },
        {
            'key': 'shop',
            'value': 'Helmet',
            'tag_specific_comment': 'shop=Helmet ? What kind of shop, if any is here?\n\nIs it office of company and no clients can enter here? Is it point where client can walk in and arrange selling of product? Is it shop selling these? Factory making them?',
        },
        {
            'key': 'shop',
            'value': 'Brick_cement_shop',
            'tag_specific_comment': 'shop=Brick_cement_shop ? What kind of shop, if any is here?\n\nIs it office of company and no clients can enter here? Is it point where client can walk in and arrange selling of product? Is it shop selling these? Factory making them?',
        },
        {
            'key': 'shop',
            'value': 'Custom_Seismic_Processing',
            'tag_specific_comment': 'shop=Custom_Seismic_Processing ? What kind of shop, if any is here?\n\nIs it office of company and no clients can enter here? Is it point where client can walk in and arrange visit? Is it workshop/laboratory?',
        },
        {
            'key': 'shop',
            'value': 'Air_Conditioning_Contractor',
            'tag_specific_comment': 'shop=Air_Conditioning_Contractor ? What kind of shop, if any is here?\n\nAre they selling air conditioners? Repairing them here? Is it office of repair company and no clients can enter here? Is it point where client can walk in and arrange visit? Is it workshop?',
        },
        {
            'key': 'shop',
            'value': 'chemical',
            'tag_specific_comment': 'shop=chemical ? What kind of shop, if any is here? Is it maybe something like  shop=cleaning_supplies ? Or maybe shop=chemist? (see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcleaning_supplies and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dchemist ). Is it selling household chemicals or industrial supplies?\n\nShould we document this shop=chemical value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'chemistry',
            'tag_specific_comment': 'shop=chemistry ? What kind of shop, if any is here? Is it maybe something like  shop=cleaning_supplies ? Or maybe shop=chemist? (see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcleaning_supplies and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dchemist )\n\nShould we document this shop=chemistry value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'Fertilizantes',
            'tag_specific_comment': 'shop=Fertilizantes ? What kind of shop, if any is here?\n\nif it sells solely fertilizer then shop=fertilizer or shop=fertilizers may make sense (in English)\nmaybe shop=agrarian makes sense? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dagrarian\nThere is also proposed tagging shop=agrarian agrarian=fertilizer',
        },
        {
            'key': 'shop',
            'value': 'Fertiliser_Store',
            'tag_specific_comment': 'shop=Fertiliser_Store ? What kind of shop, if any is here?\n\nif it sells solely fertilizer then shop=fertilizer or shop=fertilizers may make sense\nmaybe shop=agrarian makes sense? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dagrarian\nThere is also proposed tagging shop=agrarian agrarian=fertilizer',
        },
        {
            'key': 'shop',
            'value': 'Design Agency',
            'tag_specific_comment': 'shop=Design Agency? That is an office of some design agency? Is it even allowing walk in of potential customers? If it is an office not allowing clients to just appear then office=company company=design_agency may be better. If that place allows clients to just walk in then shop=design_agency seems better (value with a standard formatting)',
        },
        {
            'key': 'shop',
            'value': 'delivery_service',
            'tag_specific_comment': 'shop=delivery_service ? Is it actually shop/office selling delivery service? Or is it internal point from which couriers are operating?',
        },
        {
            'key': 'shop',
            'value': 'Phone Charging',
            'tag_specific_comment': 'shop=Phone Charging ? What kind of shop, if any is here? What you can charge here? Battery in mobile device? Mobile bank account? Is it about some financial services? Seling phone chargers? Something else?',
        },
        {
            'key': 'shop',
            'value': 'charging shop',
            'tag_specific_comment': 'shop=charging shop ? What kind of shop, if any is here? What you can charge here? Battery in mobile device? Battery in a car? Charge mobile bank account? Is it about some financial services? Something else?',
        },
        {
            'key': 'shop',
            'value': 'gym',
            'tag_specific_comment': 'shop=gym ? What kind of shop, if any is here?\nIs it a gym (in either of its meaning, see https://wiki.openstreetmap.org/wiki/Gym ) - or is it actually a shop? If it is a shop - what they are selling there? Gym equipment?',
        },
        {
            'key': 'shop',
            'value': 'mower_repair',
            'tag_specific_comment': 'shop=mower_repair ? Is it about lawnmower repair? Then maybe shop=lawn_mower_repair or shop=lawnmower_repair would be better as more specific? Or shop=repair with some subtag?',
        },
        {
            'key': 'shop',
            'value': 'hgv_repair',
            'tag_specific_comment': 'shop=hgv_repair ? How it differs from shop=truck_repair ? Should it be maybe used instead it and also documented, like https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtruck_repair is?',
        },
        {
            'key': 'shop',
            'value': 'auto_repair',
            'tag_specific_comment': 'shop=auto_repair ? How it differs from shop=car_repair ? Should it be maybe used instead it and also documented, like https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar_repair is?',
        },
        {
            'key': 'shop',
            'value': 'vehicle',
            'tag_specific_comment': 'shop=vehicle ? What kind of shop, if any is here? Is it possible to specify what kind of vehicles is handled here?\n\ncars? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar\nbicycles? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dbicycle\nTrucks? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtruck\nMotorcycles? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dmotorcycle\nCaravans? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcaravan\nCar rental? See https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dcar_rental\nQuads/All-terrain vehicles/ATV? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Datv\nCar repair? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar_repair\nCar parts? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcar_parts\nOr maybe it sells boats/rockets/trains/etc?',
        },
        {
            'key': 'shop',
            'value': 'Kosher supermarket',
            'tag_specific_comment': 'shop=Kosher supermarket ?\n\nMaybe shop=supermarket with diet:kosher would be a better tagging? But is it diet:kosher=only or diet:kosher=yes ?\n\nSee https://wiki.openstreetmap.org/wiki/Key:diet:kosher',
        },
        {
            'key': 'shop',
            'value': 'pet_supply',
            'tag_specific_comment': 'shop=pet_supply ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=pet ? If yes, what is the difference?\n\nShould we document this shop value as distinct, valid and useful?  Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?',
        },
        {
            'key': 'shop',
            'value': 'animal',
            'tag_specific_comment': 'shop=animal ? What kind of shop, if any is here? Is it selling pets or supplies for them (in such casem, why not use https://wiki.openstreetmap.org/wiki/Tag:shop=pet ?)\n\nIs it selling livestock?\n\nIs it selling butchered animals?',
        },
        {
            'key': 'shop',
            'value': 'pet_supplies',
            'tag_specific_comment': 'shop=pet_supplies ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=pet ? If yes, what is the difference?\n\nShould we document this shop value as distinct, valid and useful?  Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?',
        },
        {
            'key': 'shop',
            'value': 'à_venda',
            'tag_specific_comment': 'shop=à_venda ? What kind of shop, if any is here? Is it maybe an empty shop, typically mapped as disused:shop=yes or shop=vacant? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dvacant and https://wiki.openstreetmap.org/wiki/Key:disused:shop',
        },
        {
            'key': 'shop',
            'value': 'vacanto',
            'tag_specific_comment': 'shop=vacanto ? What kind of shop, if any is here? Is it maybe an empty shop, typically mapped as disused:shop=yes or shop=vacant? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dvacant and https://wiki.openstreetmap.org/wiki/Key:disused:shop',
        },
        {
            'key': 'shop',
            'value': 'remnant',
            'tag_specific_comment': 'shop=remnant ? What kind of shop, if any is here? Is it maybe an empty shop, typically mapped as disused:shop=yes or shop=vacant? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dvacant and https://wiki.openstreetmap.org/wiki/Key:disused:shop',
        },
        {
            'key': 'shop',
            'value': 'burmese supermarket',
            'tag_specific_comment': 'shop=burmese supermarket ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=supermarket ? If yes, what is the difference?\n\nShould we document this shop value as distinct, valid and useful?  Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?\n\nMaybe shop=supermarket cuisine=burmese would work well here?',
        },
        {
            'key': 'shop',
            'value': 'garment_exporting',
            'tag_specific_comment': 'shop=garment_exporting ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=clothes ? If yes, what is the difference?\n\nShould we document this shop value as distinct, valid and useful?  Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?',
        },
        {
            'key': 'shop',
            'value': 'Ladies Fashion and Accessories',
            'tag_specific_comment': 'shop=Ladies Fashion and Accessories ? Is it intentionally used instead of shop=clothes clothes=women ( see https://wiki.openstreetmap.org/wiki/Tag:shop=clothes and https://wiki.openstreetmap.org/wiki/Key:clothes )? If yes, what is the difference?\n\nShould we document this shop value as distinct, valid and useful?  Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?',
        },
        {
            'key': 'shop',
            'value': 'buddhist_supplies',
            'tag_specific_comment': 'shop=buddhist_supplies ? Would shop=religion religion=buddhist tagging fit well? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dreligion',
        },
        {
            'key': 'shop',
            'value': 'soapery',
            'tag_specific_comment': 'shop=soapery ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=cosmetics ? If yes, what is the difference?\n\nShould we document this shop value as distinct, valid and useful?  Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?\n\nIs it man_made=works making shop? How it differs from shop=soap?',
        },
        {
            'key': 'shop',
            'value': 'veterinary',
            'tag_specific_comment': 'shop=veterinary ? What kind of shop, if any is here? Is it office of a veterinary doctor where you can come with animal for health services? Or is it a place selling veterinary supplies?',
        },
        {
            'key': 'shop',
            'value': 'hunter',
            'tag_specific_comment': 'shop=hunter ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=hunting ?\n\nIf yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'hunters',
            'tag_specific_comment': 'shop=hunters ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=hunting ?\n\nIf yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'funeral_service',
            'tag_specific_comment': 'shop=funeral_service ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=funeral_directors ? If yes, what is the difference?\n\nShould we document this shop value as distinct, valid and useful?  Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?',
        },
        {
            'key': 'shop',
            'value': 'funeral_home',
            'tag_specific_comment': 'shop=funeral_home ? Is it intentionally used instead of shop=funeral_directors ( see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dfuneral_directors ). If it was deliberately used instead - how it differs from it in meaning?',
        },
        {
            'key': 'shop',
            'value': 'funerary_services',
            'tag_specific_comment': 'shop=funerary_services ? Is it intentionally used instead of shop=funeral_directors ( see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dfuneral_directors ). If it was deliberately used instead - how it differs from it in meaning?',
        },
        {
            'key': 'shop',
            'value': 'funeral',
            'tag_specific_comment': 'shop=funeral ? Is it intentionally used instead of shop=funeral_directors ( see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dfuneral_directors ). If it was deliberately used instead - how it differs from it in meaning?',
        },
        {
            'key': 'shop',
            'value': 'bicycle_repair_station',
            'tag_specific_comment': 'shop=bicycle_repair_station ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dbicycle_repair_station?\n\nShould we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'bicycle_repair_station',
            'tag_specific_comment': 'shop=bicycle_repair_station ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dbicycle_repair_station?\n\nShould we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'vehicle_repair',
            'tag_specific_comment': 'shop=vehicle_repair ? what can be repaired here? Planes? Cars? Motorcycles? Tractors? Maybe more sopecific value can be used?',
        },
        {
            'key': 'shop',
            'value': 'Emissions Testing',
            'tag_specific_comment': 'Maybe amenity=vehicle_inspection would be better fitting? If not - why not?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dvehicle_inspection', # TODO - is it found by https://wiki.openstreetmap.org/w/index.php?search=Emissions+Testing&title=Special%3ASearch&go=Go
        },
        {
            'key': 'shop',
            'value': 'entertainment_agency',
            'tag_specific_comment': 'shop=entertainment_agency ? What kind of shop, if any is here? Can it be tagged more specifically?\n\nIs it some euphemism for amenity=brothel ?',
        },
        {
            'key': 'shop',
            'value': 'electric_supplies',
            'tag_specific_comment': 'shop=electric_supplies ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=electrical ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'Electrical_Supply_Store',
            'tag_specific_comment': 'shop=Electrical_Supply_Store ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=electrical ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'local_food',
            'tag_specific_comment': 'shop=local_food ? Maybe shop=food cuisine=regional (or other cuisine value) would fit? That would have better chance to be be supported...',
        },
        {
            'key': 'shop',
            'value': 'regional_food',
            'tag_specific_comment': 'shop=regional_food ? Maybe shop=food cuisine=regional (or other cuisine value) would fit? That would have better chance to be be supported...',
        },
        {
            'key': 'shop',
            'value': 'local food',
            'tag_specific_comment': 'shop=local food ? Maybe shop=food cuisine=regional (or other cuisine value) would fit? That would have better chance to be be supported...',
        },
        {
            'key': 'shop',
            'value': 'Power_Plant_Equipment_Supplier',
            'tag_specific_comment': 'shop=Power_Plant_Equipment_Supplier ? What kind of shop, if any is here? is it company office by any chance? Or is it shop where you can go in and buy such things or service on the spot?',
        },
        {
            'key': 'shop',
            'value': 'japanese tea',
            'tag_specific_comment': 'shop=japanese tea ? What kind of shop, if any is here? Maybe shop=tea cuisine=japanese tagging would be better? That would give the same info, I think - and be properly recognised as shop selling tea. Unless it is place selling prepared tea?',
        },
        {
            'key': 'shop',
            'value': 'Clinic',
            'tag_specific_comment': 'shop=Clinic ? What kind of shop, if any is here? Is it maybe amenity=clinic, see https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dclinic ',
        },
        {
            'key': 'shop',
            'value': 'tea_traders',
            'tag_specific_comment': 'shop=tea_traders ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=tea ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'Foot_wear',
            'tag_specific_comment': 'shop=Foot_wear ? Is it intentional that shop=shoes was not used? How it differs from it?',
        },
        {
            'key': 'shop',
            'value': 'shisha',
            'tag_specific_comment': 'shop=shisha ? Is it selling shisha equipment? Then maybe https://wiki.openstreetmap.org/wiki/Tag:shop=hookah would work? Or is it a https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dhookah_lounge ? Or is it something else? ',
        },
        {
            'key': 'shop',
            'value': 'Shisha',
            'tag_specific_comment': 'shop=Shisha ? Is it selling shisha equipment? Then maybe https://wiki.openstreetmap.org/wiki/Tag:shop=hookah would work? Or is it a https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dhookah_lounge ? Or is it something else? ',
        },
        {
            'key': 'shop',
            'value': 'supermarket+organic',
            'tag_specific_comment': 'shop=supermarket+organic ? It should be shop=supermarket... The main question is - is that organic=yes or organic=only... Are they selling only "organic" products?',
        },
        {
            'key': 'shop',
            'value': 'organic_vegetables_and_fruit',
            'tag_specific_comment': 'shop=organic_vegetables_and_fruit ? It should be shop=greengrocer or shop=farm... The question is - is that organic=yes or organic=only... Are they selling only "organic" products?',
        },
        {
            'key': 'shop',
            'value': 'FIXME',
            'tag_specific_comment': 'shop=FIXME ? What kind of shop, if any is here?',
        },
        {
            'key': 'shop',
            'value': 'fixme',
            'tag_specific_comment': 'shop=fixme ? What kind of shop, if any is here?',
        },
        {
            'key': 'shop',
            'value': 'Office',
            'tag_specific_comment': 'shop=Office ? What kind of shop, if any is here? Is it just office of some kind (office=*)? Or are they selling office equipment here?',
        },
        {
            'key': 'shop',
            'value': 'office',
            'tag_specific_comment': 'shop=office ? What kind of shop, if any is here? Is it just office of some kind (office=*)? Or are they selling office equipment here?',
        },
        {
            'key': 'shop',
            'value': 'plumping_materials',
            'tag_specific_comment': 'shop=plumping_materials ? That is plumbing_supplies, right?',
        },
        {
            'key': 'shop',
            'value': '10pin',
            'tag_specific_comment': 'shop=10pin ? What kind of shop, if any is here? Are they selling billard equipment?',
        },
        {
            'key': 'shop',
            'value': '10 pin',
            'tag_specific_comment': 'shop=10 pin ? What kind of shop, if any is here? Are they selling billard equipment?',
        },
        {
            'key': 'shop',
            'value': 'Independent_Shop_selling Norfolk wares',
            'tag_specific_comment': 'shop=Independent_Shop_selling Norfolk wares ? What kind of shop is that? What is that "Norfolk wares"?',
        },
        {
            'key': 'shop',
            'value': 'warehouse',
            'tag_specific_comment': 'shop=warehouse ? Is it place renting small space for people to store their stuff? If yes then it is shop=storage_rental - or is it some other kind of place? Are they selling large areas or entire warehouse to companies? If yes then shop=* is a poor tagging. Or are they selling warehousing equipment?',
        },
        {
            'key': 'shop',
            'value': 'Warehouse',
            'tag_specific_comment': 'shop=Warehouse ? Is it place renting small space for people to store their stuff? If yes then it is shop=storage_rental - or is it some other kind of place? Are they selling large areas or entire warehouse to companies? If yes then shop=* is a poor tagging. Or are they selling warehousing equipment?',
        },
        {
            'key': 'shop',
            'value': 'parking',
            'tag_specific_comment': 'shop=parking ? Is it selling parking construction materials? Parking tickets? Is it maybe parking tickets vending machine?',
        },
        {
            'key': 'shop',
            'value': 'Friends photo studio',
            'tag_specific_comment': 'shop=Friends photo studio ? It is safe to retag it to shop=photo_studio, right? https://wiki.openstreetmap.org/wiki/Tag:shop=photo_studio',
        },
        {
            'key': 'shop',
            'value': 'Small_grocerry_shop',
            'tag_specific_comment': 'shop=Small_grocerry_shop ? It is safe to retag it to shop=grocery, right? https://wiki.openstreetmap.org/wiki/Tag:shop=grocery',
        },
        {
            'key': 'shop',
            'value': 'pawn',
            'tag_specific_comment': 'shop=pawn ? Is it a pawnshop? ( https://wiki.openstreetmap.org/wiki/Tag:shop=pawnbroker )',
        },
        {
            'key': 'shop',
            'value': 'Pawn',
            'tag_specific_comment': 'shop=pawn ? Is it a pawnshop? ( https://wiki.openstreetmap.org/wiki/Tag:shop=pawnbroker )',
        },
        {
            'key': 'shop',
            'value': 'Bleach',
            'tag_specific_comment': 'shop=Bleach ? Is it really shop selling only/primarily bleach and not cleaning products in general?',
        },
        {
            'key': 'shop',
            'value': 'Mystery_Room',
            'tag_specific_comment': 'shop=Mystery_Room ? What kind of shop, if any is here? Is it rather https://wiki.openstreetmap.org/wiki/Tag:leisure%3Descape_game ?',
        },
        {
            'key': 'shop',
            'value': 'coffee_machines',
            'tag_specific_comment': 'shop=coffee_machines ? Is it a vending machine? Or is it shop selling coffee machines? Should this shop value be documented as new shop value, or maybe some of existing would fir with some additional subtag?',
        },
        {
            'key': 'shop',
            'value': 'vending_machine',
            'tag_specific_comment': 'shop=vending_machine ? Is it a vending machine? Or is it shop selling vending machines?',
        },
        {
            'key': 'shop',
            'value': 'office_supply',
            'tag_specific_comment': 'shop=office_supply ? Is it just shop=stationery ? How it differs from it?',
        },
        {
            'key': 'shop',
            'value': 'material',
            'tag_specific_comment': 'shop=material ? What kind of materials are sold here? Cloth? Wood? Paper?',
        },
        {
            'key': 'shop',
            'value': 'Fashion',
            'tag_specific_comment': 'shop=Fashion ? Is it just shop=clothes ?',
        },
        {
            'key': 'shop',
            'value': 'apparel',
            'tag_specific_comment': 'shop=apparel ? Is it just shop=clothes ?',
        },
        {
            'key': 'shop',
            'value': 'conceptstore',
            'tag_specific_comment': 'What is sold in this "concept store" ? Clothes? Cars? Mobile phones? Shoes? Alcohol? Guns? Perfumes? Food? Something else?',
        },
        {
            'key': 'shop',
            'value': 'Gun_dealers',
            'tag_specific_comment': 'shop=Gun_dealers ? Should it be shop=gun https://wiki.openstreetmap.org/wiki/Tag:shop%3Dgun (or is it group of shop=gun POIs)?',
        },
        {
            'key': 'shop',
            'value': 'firearms',
            'tag_specific_comment': 'shop=firearms ? Should it be shop=gun https://wiki.openstreetmap.org/wiki/Tag:shop%3Dgun (or is it intentionally not using shop=gun)?',
        },
        {
            'key': 'shop',
            'value': 'pharmacy Shops',
            'tag_specific_comment': 'shop=pharmacy Shops ? Is it just amenity=pharmacy ? (or multiple pharmacies?)',
        },
        {
            'key': 'shop',
            'value': 'Vetshop',
            'tag_specific_comment': 'shop=Vetshop ? What kind of shop, if any is here? Is it office of a veterinary doctor?',
        },
        {
            'key': 'shop',
            'value': 'Weather Station',
            'tag_specific_comment': 'shop=Weather Station ? What kind of shop, if any is here? Is it maybe rather weather station mistagged as a shop?',
        },
        {
            'key': 'shop',
            'value': 'Dildo_Singapore',
            'tag_specific_comment': 'shop=Dildo_Singapore ? What kind of shop, if any is here? Is it shop=erotic ?',
        },
        {
            'key': 'shop',
            'value': 'METALS',
            'tag_specific_comment': 'shop=METALS ? What kind of shop, if any is here? Is it buying scrap metal? Selling metal for industrial purposes? Selling metal music-related stuff? Selling hardware? Something else?',
        },
        {
            'key': 'shop',
            'value': 'trumpet',
            'tag_specific_comment': 'shop=trumpet ? It seems that shop=musical_instrument musical_instrument=trumpet would be better tagging, see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dmusical_instrument\n\nIn this way data consumers can support musical instrument shops without listing dedicated shop type for every single musical instrument in general AND they can, if they want, support more detail\n\nOr maybe this shop is gone or about different kind of trumpets?',
        },
        {
            'key': 'shop',
            'value': 'Diary',
            'tag_specific_comment': 'shop=Diary ? What kind of shop, if any is here? Is it shop=diary selling diaries? Or is it typoed shop=dairy ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Ddairy )?',
        },
        {
            'key': 'shop',
            'value': 'diary',
            'tag_specific_comment': 'shop=diary ? What kind of shop, if any is here? Is it really shop=diary selling diaries? Or is it typoed shop=dairy ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Ddairy )?',
        },
        {
            'key': 'shop',
            'value': 'Meat_Products',
            'tag_specific_comment': 'shop=Meat_Products ? What kind of shop, if any is here? Is it shop=butcher ? If no, how it differs from it?',
        },
        {
            'key': 'shop',
            'value': 'Heavy_equipment_Supplier',
            'tag_specific_comment': 'shop=Heavy_equipment_Supplier ? What kind of shop, if any is here? Is it maybe a company office? Can anyone walk in here without appoitment to buy that heavy machinery?',
        },
        {
            'key': 'shop',
            'value': 'casino',
            'tag_specific_comment': 'shop=casino ? What kind of shop, if any is here? Is it casino by any chance? Is it selling caino equipment? Maybe https://wiki.openstreetmap.org/wiki/Tag:leisure=adult_gaming_centre or https://wiki.openstreetmap.org/wiki/Tag:amenity=casino would fit?',
        },
        {
            'key': 'shop',
            'value': 'Spa',
            'tag_specific_comment': 'shop=Spa ? What kind of shop, if any is here? Is it selling spa equipment? Spa services? Cosmetics? Furniture to set up spa?',
        },
        {
            'key': 'shop',
            'value': 'eyewear',
            'tag_specific_comment': 'shop=eyewear ? What kind of shop, if any is here? Is it maybe shop=optician ? https://wiki.openstreetmap.org/wiki/Tag:shop=optician Or maybe we need to document shop=eyewear as distinct from shop=optician?',
        },
        {
            'key': 'shop',
            'value': 'eyeglasses',
            'tag_specific_comment': 'shop=eyeglasses ? What kind of shop, if any is here? Is it maybe shop=optician ? https://wiki.openstreetmap.org/wiki/Tag:shop=optician Maybe shop=sunglasses if it sell nothing correcting eye deformities?',
        },
        {
            'key': 'shop',
            'value': 'eyeglass',
            'tag_specific_comment': 'shop=eyeglass ? What kind of shop, if any is here? Is it maybe shop=optician ? https://wiki.openstreetmap.org/wiki/Tag:shop=optician Maybe shop=sunglasses if it sell nothing correcting eye deformities?',
        },
        {
            'key': 'shop',
            'value': 'eye_glasses',
            'tag_specific_comment': 'shop=eye_glasses ? What kind of shop, if any is here? Is it maybe shop=optician ? https://wiki.openstreetmap.org/wiki/Tag:shop=optician Maybe shop=sunglasses if it sell nothing correcting eye deformities?',
        },
        {
            'key': 'shop',
            'value': 'Eyeglasses',
            'tag_specific_comment': 'shop=Eyeglasses ? What kind of shop, if any is here? Is it maybe shop=optician ? https://wiki.openstreetmap.org/wiki/Tag:shop=optician Maybe shop=sunglasses if it sell nothing correcting eye deformities?',
        },
        {
            'key': 'shop',
            'value': 'herbal_medicine',
            'tag_specific_comment': 'shop=herbal_medicine ? Is it the same as shop=herbalist ? If no, how it differs? ',
        },
        {
            'key': 'shop',
            'value': 'manicurist',
            'tag_specific_comment': 'shop=manicurist ? Maybe shop=beauty beauty= (for example beauty=nails) would be better tagging?',
        },
        {
            'key': 'shop',
            'value': 'manicure',
            'tag_specific_comment': 'shop=manicure ? Maybe shop=beauty beauty= (for example beauty=nails) would be better tagging?',
        },
        {
            'key': 'shop',
            'value': 'outlet',
            'tag_specific_comment': 'shop=outlet ? Is it outlet for home electronics like fridges? For clothes? For cars? For something else?',
        },
        {
            'key': 'shop',
            'value': 'retail_shop',
            'tag_specific_comment': 'shop=retail_shop ? Is it selling for home electronics like fridges? Clothes? Cars? Food? Shop type should be specified, see https://wiki.openstreetmap.org/wiki/Key:shop for possible values',
        },
        
        {
            'key': 'shop',
            'value': 'reseller',
            'tag_specific_comment': 'shop=reseller ? Is it reseller for home electronics like fridges? For clothes? For cars? For food? For pets? For something else?',
        },
        {
            'key': 'shop',
            'value': 'distributor',
            'tag_specific_comment': 'shop=distributor ? Is it distributor for home electronics like fridges? For clothes? For cars? For food? For pets? For something else?',
        },
        {
            'key': 'shop',
            'value': 'Rural_supermarket',
            'tag_specific_comment': 'shop=Rural_supermarket ? Why not shop=supermarket? How it differs from one - if it actually differs?',
        },
        {
            'key': 'shop',
            'value': 'Reliance_supermarket',
            'tag_specific_comment': 'shop=Reliance_supermarket ? Why not shop=supermarket? How it differs from one - if it actually differs?',
        },
        {
            'key': 'shop',
            'value': 'Dehydrated',
            'tag_specific_comment': 'shop=Dehydrated ? Is it selling dehydrated food or dry herbs or something else?',
        },
        {
            'key': 'shop',
            'value': 'Nonmetallic_material',
            'tag_specific_comment': 'shop=Nonmetallic_material ? What it is actually selling? Gravel? Food?',
        },
        {
            'key': 'shop',
            'value': 'School_Supply_Store',
            'tag_specific_comment': 'shop=School_Supply_Store ? Is it shop=stationery If no, how it differs from it? See https://wiki.openstreetmap.org/wiki/Tag:shop=stationery',
        },
        {
            'key': 'shop',
            'value': 'small super market',
            'tag_specific_comment': 'shop=small super market ? What kind of shop, if any is here? Is it shop=convenience?\n\n(see https://wiki.openstreetmap.org/wiki/Tag:shop=convenience )',
        },
        {
            'key': 'shop',
            'value': 'convenient shop',
            'tag_specific_comment': 'shop=convenient shop ? What kind of shop, if any is here? Is it shop=convenience?\n\n(see https://wiki.openstreetmap.org/wiki/Tag:shop=convenience )',
        },
        {
            'key': 'shop',
            'value': 'Convenient',
            'tag_specific_comment': 'shop=Convenient ? What kind of shop, if any is here? Is it shop=convenience?\n\n(see https://wiki.openstreetmap.org/wiki/Tag:shop=convenience )',
        },
        {
            'key': 'shop',
            'value': 'mini_markert',
            'tag_specific_comment': 'shop=mini_markert ? What kind of shop, if any is here? Is it shop=convenience?\n\n(see https://wiki.openstreetmap.org/wiki/Tag:shop=convenience )',
        },
        {
            'key': 'shop',
            'value': 'mini-supermarket',
            'tag_specific_comment': 'shop=mini-supermarket ? What kind of shop, if any is here? Is it shop=convenience?\n\n(see https://wiki.openstreetmap.org/wiki/Tag:shop=convenience )',
        },
        {
            'key': 'shop',
            'value': 'mini_supermarket',
            'tag_specific_comment': 'shop=mini_supermarket ? What kind of shop, if any is here? Is it shop=convenience?\n\n(see https://wiki.openstreetmap.org/wiki/Tag:shop=convenience )',
        },
        {
            'key': 'shop',
            'value': 'Minimart',
            'tag_specific_comment': 'shop=Minimart ? What kind of shop, if any is here? Is it shop=convenience?\n\n(see https://wiki.openstreetmap.org/wiki/Tag:shop=convenience )',
        },
        {
            'key': 'shop',
            'value': 'Mini-Supermarket',
            'tag_specific_comment': 'shop=Mini-Supermarket ? What kind of shop, if any is here? Is it shop=convenience?\n\n(see https://wiki.openstreetmap.org/wiki/Tag:shop=convenience )',
        },
        {
            'key': 'shop',
            'value': 'Fried chicken',
            'tag_specific_comment': 'shop=Fried chicken ? Would it be better tagged as amenity=fast_food with fried chicken mentioned in cuisine or product tag or somewhere else?',
        },
        {
            'key': 'shop',
            'value': 'Meat Market',
            'tag_specific_comment': 'shop=Meat Market ? Is it shop=butcher? If not, how it differs from it? Or is it for entire are with shop=butcher locations? In that case mapping at least some of them would be nice.',
        },
        {
            'key': 'shop',
            'value': 'Mini_market',
            'tag_specific_comment': 'shop=Mini_market ? Is it shop=convenience? If not, how it differs from it?',
        },
        {
            'key': 'shop',
            'value': 'For Sale',
            'tag_specific_comment': 'shop=For Sale ? Is shop itself for sale (shop=vacant)? Or is it shop=variety_store? Or something else?',
        },
        {
            'key': 'shop',
            'value': 'newsagent,_tobacco,_beverages,_post_office=yes',
            'tag_specific_comment': 'shop=newsagent,_tobacco,_beverages,_post_office=yes ? Would shop=kiosk post_office=yes would be a good tagging here?',
        },
        {
            'key': 'shop',
            'value': 'Airport Terminal Building',
            'tag_specific_comment': 'shop=Airport Terminal Building ? Is it unusual mapping of terminal, or is it mapping of shop inside terminal without specifying its type?',
        },
        {
            'key': 'shop',
            'value': 'painter',
            'tag_specific_comment': 'shop=painter ? Is it mistagged https://wiki.openstreetmap.org/wiki/Tag:shop=paint ? Or is it office of someone offering paiting services? (https://wiki.openstreetmap.org/wiki/Tag:craft%3Dpainter or office=painter I guess?)',
        },
        {
            'key': 'shop',
            'value': 'electrotools',
            'tag_specific_comment': 'shop=electrotools ? What kind of shop, if any is here? Is shop=electrotools used intentionally instead of https://wiki.openstreetmap.org/wiki/Tag:shop=power_tools ? If yes, what is the difference?',
        },
        {
            'key': 'shop',
            'value': 'carto',
            'tag_specific_comment': 'shop=carto ? What kind of shop, if any is here? Is it maybe shop selling maps?',
        },
        {
            'key': 'shop',
            'value': 'opportunity',
            'tag_specific_comment': 'shop=opportunity ? https://www.openstreetmap.org/note/3806441 mentions that it is likely alias of shop=charity - maybe it would be better to tag it this way?',
        },
        {
            'key': 'shop',
            'value': 'op',
            'tag_specific_comment': 'shop=op ? https://www.openstreetmap.org/note/3806441 mentions that it is likely alias of shop=charity - maybe it would be better to tag it this way?',
        },
        {
            'key': 'shop',
            'value': 'opshop',
            'tag_specific_comment': 'shop=opshop ? https://www.openstreetmap.org/note/3806441 mentions that it is likely alias of shop=charity - maybe it would be better to tag it this way?',
        },
        {
            'key': 'shop',
            'value': 'op_shop',
            'tag_specific_comment': 'shop=op_shop ? https://www.openstreetmap.org/note/3806441 mentions that such values are likely alias of shop=charity - maybe it would be better to tag it this way?',
        },
        {
            'key': 'shop',
            'value': 'cannery',
            'tag_specific_comment': 'shop=cannery ? What kind of shop, if any is here? cannery means "a factory where food is canned" from what I found. So is it man_made=works rather than shop? Or is it shop selling canned food? Both?',
        },
        {
            'key': 'shop',
            'value': 'paper',
            'tag_specific_comment': 'shop=paper ? Is it shop=stationery If no, how it differs from it? See https://wiki.openstreetmap.org/wiki/Tag:shop=stationery',
        },
        {
            'key': 'shop',
            'value': 'Community Hall',
            'tag_specific_comment': 'shop=Community Hall ? That is not a shop, right?',
        },
        {
            'key': 'shop',
            'value': 'vintage',
            'tag_specific_comment': 'shop=vintage ? What kind of shop, if any is here? Is it simply shop=second_hand ? See good discussion in https://www.openstreetmap.org/note/3865985',
        },
        {
            'key': 'shop',
            'value': 'angling',
            'tag_specific_comment': 'shop=angling ? What kind of shop, if any is here? Is it simply shop=fishing ? Is it intentional that different value was used? Maybe shop=angling should be documented as distinct from shop=fishing?\nMaybe shop=fishing fishing=angling would work to provide detail? See https://wiki.openstreetmap.org/wiki/Tag:shop=fishing\n\nAlso, maybe this shop value is unrelated to fishing.',
        },
        {
            'key': 'shop',
            'value': 'Niharika mobile gallery',
            'tag_specific_comment': 'shop=Niharika mobile gallery ? What kind of shop, if any is here? Is it even mappable in OSM if it is mobile?',
        },
        {
            'key': 'shop',
            'value': 'mobile_bakery',
            'tag_specific_comment': 'shop=mobile_bakery ? What kind of shop, if any is here? Is it even mappable in OSM if it is mobile? Is it maybe simply shop=bakery?',
        },
        {
            'key': 'shop',
            'value': 'bureau de poste',
            'tag_specific_comment': 'shop=bureau de poste ? Is it post office?',
        },
        {
            'key': 'shop',
            'value': 'butcher Bioland',
            'tag_specific_comment': 'shop=butcher Bioland ? butcher part is clear, what is meant by "Bioland" here?',
        },
        {
            'key': 'shop',
            'value': 'safety',
            'tag_specific_comment': 'shop=safety ? What kind of shop, if any is here?  is https://wiki.openstreetmap.org/wiki/Tag:shop=safety_equipment fitting?',
        },
        {
            'key': 'shop',
            'value': 'grocer',
            'tag_specific_comment': 'shop=grocer ? Is it maybe better tagged as https://wiki.openstreetmap.org/wiki/Tag:shop=grocery ?',
        },
        {
            'key': 'amenity',
            'value': 'grocer',
            'tag_specific_comment': 'amenity=grocer ? Is it maybe better tagged as https://wiki.openstreetmap.org/wiki/Tag:shop=grocery ?',
        },
        {
            'key': 'shop',
            'value': 'Marine Cargo Container',
            'tag_specific_comment': 'shop=Marine Cargo Container ? can anyone walk in and buy containers? Or is it B2B company office? Or at least shop=trade trade= ?',
        },
        {
            'key': 'shop',
            'value': 'halal_food',
            'tag_specific_comment': 'shop=halal_food ? Would it better tagged as shop=food + halal=only? (or halal=yes, if some non-halal food is sold there)',
        },
        {
            'key': 'shop',
            'value': 'JM photo studio',
            'tag_specific_comment': 'shop=JM photo studio ? What JM means here? What about shop=photo_studio? Where meaning of JM would go?',
        },
        {
            'key': 'shop',
            'value': 'JM Bakery',
            'tag_specific_comment': 'shop=JM Bakery ? What JM means here? What about tagging it as shop=bakery? Where meaning of JM would go?',
        },
        {
            'key': 'shop',
            'value': 'Syon Liquor Shop',
            'tag_specific_comment': 'shop=Syon Liquor Shop ? What Syon means here? What about tagging it as shop=alcohol? Where meaning of Syon would go?',
        },
        {
            'key': 'shop',
            'value': 'grocer_&_coal_merchant',
            'tag_specific_comment': 'shop=grocer_&_coal_merchant ? Maybe shop=grocerr;fuel fuel=coal would be better?',
        },
        {
            'key': 'shop',
            'value': 'speciality',
            'tag_specific_comment': 'shop=speciality ? But what kind of specialist shop? Is it specializing in fruit and vegetables? Dog collars? Herbs? Shoe repair? Something else? Is any of values from https://wiki.openstreetmap.org/wiki/Key:shop matching well?',
        },
        {
            'key': 'shop',
            'value': 'specialist',
            'tag_specific_comment': 'shop=specialist ? But what kind of specialist shop? Is it specializing in fruit and vegetables? Dog collars? Herbs? Shoe repair? Something else? Is any of values from https://wiki.openstreetmap.org/wiki/Key:shop matching well?',
        },
        {
            'key': 'shop',
            'value': 'specialized_products',
            'tag_specific_comment': 'shop=specialized_products ? But what kind of specialist shop? Is it specializing in fruit and vegetables? Dog collars? Herbs? Shoe repair? Something else? Is any of values from https://wiki.openstreetmap.org/wiki/Key:shop matching well?',
        },
        {
            'key': 'shop',
            'value': 'specialist_shop',
            'tag_specific_comment': 'shop=specialist_shop ? But what kind of specialist shop? Is it specializing in fruit and vegetables? Dog collars? Herbs? Shoe repair? Something else? Is any of values from https://wiki.openstreetmap.org/wiki/Key:shop matching well?',
        },
        {
            'key': 'shop',
            'value': 'Aircraft',
            'tag_specific_comment': 'shop=Aircraft ? Is it shop where you can go in and buy aeroplane? Or is it about aircraft models?',
        },
        {
            'key': 'shop',
            'value': 'Gaming',
            'tag_specific_comment': 'shop=Gaming ? Is it selling board games? Computer for gaming? Something else? Is any of values from https://wiki.openstreetmap.org/wiki/Key:shop matching well?',
        },
        {
            'key': 'shop',
            'value': 'clearance',
            'tag_specific_comment': 'shop=clearance ? Is it shop=variety_store ? If not, how it differs from shop=variety_store? See https://wiki.openstreetmap.org/wiki/Tag:shop=variety_store',
        },
        {
            'key': 'shop',
            'value': 'random_crap',
            'tag_specific_comment': 'Is sounds like shop=variety_store - is it matching? If not, how it differs from shop=variety_store? See https://wiki.openstreetmap.org/wiki/Tag:shop=variety_store',
        },
        {
            'key': 'shop',
            'value': 'variety',
            'tag_specific_comment': 'shop=variety ? Is it shop=variety_store ? If not, how it differs from shop=variety_store? See https://wiki.openstreetmap.org/wiki/Tag:shop=variety_store',
        },
        {
            'key': 'shop',
            'value': 'Low_prices_shop',
            'tag_specific_comment': 'shop=Low_prices_shop ? Is it shop=variety_store ? If not, how it differs from shop=variety_store? See https://wiki.openstreetmap.org/wiki/Tag:shop=variety_store',
        },
        {
            'key': 'shop',
            'value': 'thrift_store',
            'tag_specific_comment': 'shop=thrift_store ? Is it shop=variety_store ? If not, how it differs from shop=variety_store? See https://wiki.openstreetmap.org/wiki/Tag:shop=variety_store',
        },
        {
            'key': 'shop',
            'value': 'Thrift Store',
            'tag_specific_comment': 'shop=Thrift Store ? Is it shop=variety_store ? If not, how it differs from shop=variety_store? See https://wiki.openstreetmap.org/wiki/Tag:shop=variety_store',
        },
        {
            'key': 'shop',
            'value': 'Tea_stall',
            'tag_specific_comment': 'shop=Tea_stall ? Is it selling ready-to drink tea or dry tea? In either case there is a better tagging for that....',
        },
        {
            'key': 'shop',
            'value': 'drink',
            'tag_specific_comment': 'shop=drink ? Should it be shop=beverages ( https://wiki.openstreetmap.org/wiki/Tag:shop=beverages ) Maybe with drink= with value describing dominating beverage? Or is it rather an alcohol shop?',
        },
        {
            'key': 'shop',
            'value': 'Soft Drinks',
            'tag_specific_comment': 'shop=Soft Drinks ? Should it be shop=beverages ( https://wiki.openstreetmap.org/wiki/Tag:shop=beverages ) Maybe with drink= with value describing dominating beverage?',
        },
        {
            'key': 'shop',
            'value': 'Soft drinks',
            'tag_specific_comment': 'shop=Soft drinks ? Should it be shop=beverages ( https://wiki.openstreetmap.org/wiki/Tag:shop=beverages ) Maybe with drink= with value describing dominating beverage?',
        },
        {
            'key': 'shop',
            'value': 'Juice_shop',
            'tag_specific_comment': 'shop=Juice_shop ? Should it be shop=beverages ( https://wiki.openstreetmap.org/wiki/Tag:shop=beverages ) Maybe with drink=fruit_juice or similar?',
        },
        {
            'key': 'shop',
            'value': 'Fresh_drinks_from_fruits',
            'tag_specific_comment': 'shop=Fresh_drinks_from_fruits ? Should it be shop=beverages ( https://wiki.openstreetmap.org/wiki/Tag:shop=beverages ) Maybe with drink=fruit_juice or similar?',
        },
        {
            'key': 'shop',
            'value': 'Halfway_House',
            'tag_specific_comment': 'shop=Halfway_House ? That is a social facility, not a shop, right?',
        },
        {
            'key': 'shop',
            'value': 'Civic amenity site',
            'tag_specific_comment': 'shop=Civic amenity site ? That is not a shop, right? What kind of civic amenity site is here? Townhall? Social facility of some kind? Government office?',
        },
        {
            'key': 'shop',
            'value': 'Sofa',
            'tag_specific_comment': 'shop=Sofa ? Would it be fine to use shop=furniture furniture=sofa ? Or is it nonexisting now/other type of shop?',
        },
        {
            'key': 'shop',
            'value': 'shoe Hub',
            'tag_specific_comment': 'shop=shoes ? Should it be shop=shoe (or is it group of shop=shoes POIs)?',
        },
        {
            'key': 'shop',
            'value': 'Phone repair',
            'tag_specific_comment': 'shop=Phone repair ? What kind of shop, if any is here? should it be shop=repair + mobile_phone:repair=yes ? Or at least shop=mobilephone_repair ? https://wiki.openstreetmap.org/wiki/Key:mobile_phone:repair',
        },
        {
            'key': 'shop',
            'value': 'Mobile_repair',
            'tag_specific_comment': 'shop=Mobile_repair ? What kind of shop, if any is here? should it be shop=repair + mobile_phone:repair=yes ? Or at least shop=mobilephone_repair ? https://wiki.openstreetmap.org/wiki/Key:mobile_phone:repair',
        },
        {
            'key': 'shop',
            'value': 'spicy',
            'tag_specific_comment': 'shop=spicy ? What kind of shop, if any is here? Is it shop=spices? See https://wiki.openstreetmap.org/wiki/Tag:shop=spices',
        },
        {
            'key': 'shop',
            'value': 'seasoning',
            'tag_specific_comment': 'shop=seasoning ? What kind of shop, if any is here? Is it shop=spices? See https://wiki.openstreetmap.org/wiki/Tag:shop=spices',
        },
        {
            'key': 'shop',
            'value': 'Seasoning',
            'tag_specific_comment': 'shop=Seasoning ? What kind of shop, if any is here? Is it shop=spices? See https://wiki.openstreetmap.org/wiki/Tag:shop=spices',
        },
        {
            'key': 'shop',
            'value': 'Osiedlowy',
            'tag_specific_comment': 'shop=Osiedlowy ? To jest shop=convenience czy coś innego?',
        },
        {
            'key': 'shop',
            'value': 'repair_centre',
            'tag_specific_comment': 'shop=repair_centre ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=repair ? If yes, what is the difference?\n\nShould we document this shop value as distinct, valid and useful?  Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?',
        },
        {
            'key': 'shop',
            'value': 'astrology',
            'tag_specific_comment': 'shop=astrology ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=esoteric or https://wiki.openstreetmap.org/wiki/Tag:shop=new_age ? If yes, what is the difference?\n\nSee also shop=astrologer (not documented, presumably selling astrology services rather than astrology products...)\n\nShould we document this shop value as distinct, valid and useful?  Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?',
        },
        {
            'key': 'shop',
            'value': 'metaphysical',
            'tag_specific_comment': 'shop=metaphysical ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=esoteric or https://wiki.openstreetmap.org/wiki/Tag:shop=new_age ? If yes, what is the difference?\n\nShould we document this shop value as distinct, valid and useful?  Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?',
        },
        {
            'key': 'shop',
            'value': 'occult',
            'tag_specific_comment': 'shop=occult ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=esoteric or https://wiki.openstreetmap.org/wiki/Tag:shop=new_age ? If yes, what is the difference?\n\nShould we document this shop value as distinct, valid and useful?  Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?',
        },
        {
            'key': 'shop',
            'value': 'spiritual',
            'tag_specific_comment': 'shop=spiritual ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=esoteric or https://wiki.openstreetmap.org/wiki/Tag:shop=new_age ? If yes, what is the difference?\n\nShould we document this shop value as distinct, valid and useful?  Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?',
        },
        {
            'key': 'shop',
            'value': 'award',
            'tag_specific_comment': 'shop=award ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=trophy ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful? Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?',
        },
        {
            'key': 'shop',
            'value': 'awards',
            'tag_specific_comment': 'shop=awards ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=trophy ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful? Or maybe it is so obvious duplicate that I should have replaced it with an automatic edit rather than making a note?',
        },
        {
            'key': 'shop',
            'value': 'car_showroom',
            'tag_specific_comment': 'shop=car_showroom ? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=car ? If yes, what is the difference? You can probably order car here, right? Or is it rather like museum rather shop selling cars?',
        },
        {
            'key': 'shop',
            'value': 'foto',
            'tag_specific_comment': 'shop=foto ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=photo ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'photograph',
            'tag_specific_comment': 'shop=photograph ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=photo ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'photographic',
            'tag_specific_comment': 'shop=photograph ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=photo ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'philately',
            'tag_specific_comment': 'shop=philately ? Maybe it can be better tagged as shop=collector collector=stamps as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcollector suggests?\n\nOr maybe shop=philately should be documented on OSM Wiki as preferable?',
        },
        {
            'key': 'shop',
            'value': 'Philately',
            'tag_specific_comment': 'shop=Philately ? Maybe it can be better tagged as shop=collector collector=stamps as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcollector suggests?\n\nOr maybe shop=philately should be documented on OSM Wiki as preferable? (shop=philately is definitely better than shop=Philately)',
        },
        {
            'key': 'shop',
            'value': 'coin',
            'tag_specific_comment': 'shop=coin ? Maybe it can be better tagged as shop=collector collector=coins as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcollector suggests?\n\nOr maybe shop=coin should be documented on OSM Wiki as preferable?',
        },
        {
            'key': 'shop',
            'value': 'coins',
            'tag_specific_comment': 'shop=coins ? Maybe it can be better tagged as shop=collector collector=coins as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcollector suggests?\n\nOr maybe shop=coins should be documented on OSM Wiki as preferable?',
        },
        {
            'key': 'shop',
            'value': 'stamps',
            'tag_specific_comment': 'shop=coin ? Maybe it can be better tagged as shop=collector collector=stamps as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcollector suggests?\n\nOr maybe shop=stamps should be documented on OSM Wiki as preferable?',
        },
        {
            'key': 'shop',
            'value': 'copier',
            'tag_specific_comment': 'shop=copier ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=copyshop ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'copies',
            'tag_specific_comment': 'shop=copies ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=copyshop ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'copy',
            'tag_specific_comment': 'shop=copy ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=copyshop ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'xerox',
            'tag_specific_comment': 'shop=xerox ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=copyshop ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'bath',
            'tag_specific_comment': 'shop=bath ? What kind of shop, if any is here? Is it shop=bathroom_furnishing ? ( https://wiki.openstreetmap.org/wiki/Tag:shop=bathroom%20furnishing ) Is it maybe public toilet/shower marked as a shop?',
        },
        {
            'key': 'shop',
            'value': 'bathroom',
            'tag_specific_comment': 'shop=bathroom ? What kind of shop, if any is here? Is it shop=bathroom_furnishing ? ( https://wiki.openstreetmap.org/wiki/Tag:shop=bathroom%20furnishing ) Is it maybe public toilet/shower marked as a shop?',
        },
        {
            'key': 'shop',
            'value': 'vaping',
            'tag_specific_comment': 'shop=vaping ? Could it be tagged as https://wiki.openstreetmap.org/wiki/Tag:shop=e-cigarette (if shop=vape / shop=vaping / shop=vape_store is needed - how it differs or is better than shop=e-cigarette ?)',
        },
        {
            'key': 'shop',
            'value': 'vape_store',
            'tag_specific_comment': 'shop=vape_store ? Could it be tagged as https://wiki.openstreetmap.org/wiki/Tag:shop=e-cigarette (if shop=vape / shop=vaping / shop=vape_store is needed - how it differs or is better than shop=e-cigarette ?)',
        },
        {
            'key': 'shop',
            'value': 'vape',
            'tag_specific_comment': 'shop=vape ? Could it be tagged as https://wiki.openstreetmap.org/wiki/Tag:shop=e-cigarette (if shop=vape / shop=vaping / shop=vape_store is needed - how it differs or is better than shop=e-cigarette ?)',
        },
        {
            'key': 'shop',
            'value': 'Vape_Shop',
            'tag_specific_comment': 'shop=Vape_Shop ? Could it be tagged as https://wiki.openstreetmap.org/wiki/Tag:shop=e-cigarette (if shop=vape / shop=vaping / shop=vape_store is needed - how it differs or is better than shop=e-cigarette ?)',
        },
        {
            'key': 'shop',
            'value': 'vape_shop',
            'tag_specific_comment': 'shop=vape_shop ? Could it be tagged as https://wiki.openstreetmap.org/wiki/Tag:shop=e-cigarette (if shop=vape / shop=vaping / shop=vape_store is needed - how it differs or is better than shop=e-cigarette ?)',
        },
        {
            'key': 'shop',
            'value': 'Vape_Store',
            'tag_specific_comment': 'shop=Vape_Store ? Could it be tagged as https://wiki.openstreetmap.org/wiki/Tag:shop=e-cigarette (if shop=vape / shop=vaping / shop=vape_store is needed - how it differs or is better than shop=e-cigarette ?)',
        },
        {
            'key': 'shop',
            'value': 'gaz',
            'tag_specific_comment': 'shop=gaz ? Should it be shop=fuel fuel=gas ? Or shop=gas ? Or office=company?',
        },
        {
            'key': 'shop',
            'value': 'Textile_shop',
            'tag_specific_comment': 'shop=Textile_shop ? Is https://wiki.openstreetmap.org/wiki/Tag:shop=fabric describing this shop well? Is it intentional that shop=Textile_shop, was used not shop=fabric? How it differs from it?',
        },
        {
            'key': 'shop',
            'value': 'textiles',
            'tag_specific_comment': 'shop=textiles ? Is https://wiki.openstreetmap.org/wiki/Tag:shop=fabric describing this shop well? Is it intentional that shop=textiles, was used not shop=fabric? How it differs from it?',
        },
        {
            'key': 'shop',
            'value': 'textile_shop',
            'tag_specific_comment': 'shop=textile_shop ? Is https://wiki.openstreetmap.org/wiki/Tag:shop=fabric describing this shop well? Is it intentional that shop=textiles, was used not shop=fabric? How it differs from it?',
        },
        {
            'key': 'shop',
            'value': 'hometextile',
            'tag_specific_comment': 'shop=hometextile ? Is https://wiki.openstreetmap.org/wiki/Tag:shop=fabric describing this shop well? Is it intentional that shop=hometextile, was used not shop=fabric? How it differs from it?',
        },
        {
            'key': 'shop',
            'value': 'Stationary',
            'tag_specific_comment': 'shop=Stationary ? So is it supposed to be shop=stationery ?',
        },
        {
            'key': 'shop',
            'value': 'stationery??',
            'tag_specific_comment': 'shop=stationery?? ? So is it stationery shop?',
        },
        {
            'key': 'shop',
            'value': 'head',
            'tag_specific_comment': 'shop=head ? Is it the same as shop=headshop - see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dheadshop ? (or maybe shop=headshop should be tagged as shop=head ?). If it is not the same - what is the difference?',
        },
        {
            'key': 'shop',
            'value': 'head_shop',
            'tag_specific_comment': 'shop=head_shop ? Is it the same as shop=headshop - see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dheadshop ? (or maybe shop=headshop should be tagged as shop=head_shop ?). If it is not the same - what is the difference?',
        },
        {
            'key': 'shop',
            'value': 'soft_drugs',
            'tag_specific_comment': 'shop=soft_drugs ? Is it the same as shop=headshop - see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dheadshop ? Or the same as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dsmartshop ? Or it is a pharmacy ( https://wiki.openstreetmap.org/wiki/Tag:amenity=pharmacy ) ? Or is it a separate shop category that should be documented as valid?',
        },
        {
            'key': 'shop',
            'value': 'Drug Shop',
            'tag_specific_comment': 'shop=Drug Shop ? Is it the same as shop=headshop - see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dheadshop ? Or the same as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dsmartshop ? Or it is a pharmacy ( https://wiki.openstreetmap.org/wiki/Tag:amenity=pharmacy ) ? Or is it a separate shop category that should be documented as valid?',
        },
        {
            'key': 'shop',
            'value': 'Smoke_Shop',
            'tag_specific_comment': 'Is it the same as shop=headshop - see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dheadshop ? Or the same as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dsmartshop ?\n\nOr maybe it sells e-cigarettes and is shop=e-cigarette ( https://wiki.openstreetmap.org/wiki/Tag:shop%3De-cigarette )?\n\nOr maybe shop=tobacco is the best fit ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtobacco )?\n\nOr is it a separate shop category that should be documented as valid?',
        },
        {
            'key': 'shop',
            'value': 'smoke',
            'tag_specific_comment': 'Is it the same as shop=headshop - see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dheadshop ? Or the same as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dsmartshop ?\n\nOr maybe it sells e-cigarettes and is shop=e-cigarette ( https://wiki.openstreetmap.org/wiki/Tag:shop%3De-cigarette )?\n\nOr maybe shop=tobacco is the best fit ( https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtobacco )?\n\nOr is it a separate shop category that should be documented as valid?',
        },
        {
            'key': 'shop',
            'value': 'pro_shop',
            'tag_specific_comment': 'shop=pro_shop ? Is it the same as shop=headshop - see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dheadshop ? Or the same as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dsmartshop ? Or is it a separate shop category that should be documented as valid?',
        },
        {
            'key': 'shop',
            'value': 'mushroom',
            'tag_specific_comment': 'shop=mushroom ? Is it the same as shop=headshop - see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dheadshop ? Or the same as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dsmartshop ? Or is it a separate shop category that should be documented as valid?\n\nIs it maybe selling regular mushrooms for cooking, not narcotic ones?',
        },
        {
            'key': 'shop',
            'value': 'magic_mushroom',
            'tag_specific_comment': 'shop=magic_mushroom ? Is it the same as shop=headshop - see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dheadshop ? Or the same as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dsmartshop ? Or is it a separate shop category that should be documented as valid?\n\nIs it maybe selling regular mushrooms for cooking, not narcotic ones?',
        },
        {
            'key': 'shop',
            'value': 'Drugs',
            'tag_specific_comment': 'shop=Drug Shop ? Is it the same as shop=headshop - see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dheadshop ? Or the same as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dsmartshop ? Or it is a pharmacy ( https://wiki.openstreetmap.org/wiki/Tag:amenity=pharmacy ) ? Or is it a separate shop category that should be documented as valid?',
        },
        {
            'key': 'shop',
            'value': 'softdrugs',
            'tag_specific_comment': 'shop=softdrugs? Is it the same as shop=headshop - see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dheadshop ? Or the same as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dsmartshop ? Or it is a pharmacy ( https://wiki.openstreetmap.org/wiki/Tag:amenity=pharmacy ) ? Or is it a separate shop category that should be documented as valid?',
        },
        {
            'key': 'shop',
            'value': 'drug shop',
            'tag_specific_comment': 'shop=drug shop ? Is it the same as shop=headshop - see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dheadshop ? Or the same as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dsmartshop ? Or it is a pharmacy ( https://wiki.openstreetmap.org/wiki/Tag:amenity=pharmacy ) ? Or is it a separate shop category that should be documented as valid?',
        },
        {
            'key': 'shop',
            'value': 'soft_drugs',
            'tag_specific_comment': 'shop=soft_drugs? Is it the same as shop=headshop - see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dheadshop ? Or the same as https://wiki.openstreetmap.org/wiki/Tag:shop%3Dsmartshop ? Or it is a pharmacy ( https://wiki.openstreetmap.org/wiki/Tag:amenity=pharmacy ) ? Or is it a separate shop category that should be documented as valid?',
        },
        {
            'key': 'shop',
            'value': 'publisher of Science, the scientific journal',
            'tag_specific_comment': 'shop=publisher of Science, the scientific journal ? That is office, not shop, right?',
        },
        {
            'key': 'shop',
            'value': 'farm_produce',
            'tag_specific_comment': 'shop=farm_produce ? What kind of shop, if any is here? Is shop=farm_produce used intentionally instead of https://wiki.openstreetmap.org/wiki/Tag:shop=farm ? If yes, what is the difference?',
        },
        {
            'key': 'shop',
            'value': 'orchard',
            'tag_specific_comment': 'shop=orchard ? What kind of shop, if any is here? Is shop=orchard used intentionally instead of https://wiki.openstreetmap.org/wiki/Tag:shop=farm ? If yes, what is the difference?',
        },
        {
            'key': 'shop',
            'value': 'produce_stand',
            'tag_specific_comment': 'shop=produce_stand ? What kind of shop, if any is here? Is shop=produce_stand used intentionally instead of https://wiki.openstreetmap.org/wiki/Tag:shop=farm ? If yes, what is the difference?',
        },
        {
            'key': 'shop',
            'value': 'electric_tool',
            'tag_specific_comment': 'shop=electric_tool ? What kind of shop, if any is here? Is shop=electric_tool used intentionally instead of https://wiki.openstreetmap.org/wiki/Tag:shop=power_tools ? If yes, what is the difference?',
        },
        {
            'key': 'shop',
            'value': 'power_equipment',
            'tag_specific_comment': 'shop=power_equipment ? What kind of shop, if any is here? Is shop=power_equipment used intentionally instead of https://wiki.openstreetmap.org/wiki/Tag:shop=power_tools ? If yes, what is the difference?',
        },
        {
            'key': 'shop',
            'value': 'boots',
            'tag_specific_comment': 'shop=boots ? What kind of shop, if any is here? Is it intentional that it is used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=shoes ?',
        },
        {
            'key': 'shop',
            'value': 'FOOTWEAR',
            'tag_specific_comment': 'shop=FOOTWEAR ? What kind of shop, if any is here? Is it intentional that it is used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=shoes ?',
        },
        {
            'key': 'shop',
            'value': 'footwear',
            'tag_specific_comment': 'shop=footwear ? What kind of shop, if any is here? Is it intentional that it is used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=shoes ?',
        },
        {
            'key': 'shop',
            'value': 'Footwear_Shop',
            'tag_specific_comment': 'shop=Footwear_Shop ? What kind of shop, if any is here? Is it intentional that it is used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=shoes ?',
        },
        {
            'key': 'shop',
            'value': 'footwears',
            'tag_specific_comment': 'shop=footwears ? What kind of shop, if any is here? Is it intentional that it is used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=shoes ?',
        },
        {
            'key': 'shop',
            'value': 'foot_wear',
            'tag_specific_comment': 'shop=foot_wear ? What kind of shop, if any is here? Is it intentional that it is used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=shoes ?',
        },
        {
            'key': 'shop',
            'value': 'footware',
            'tag_specific_comment': 'shop=footware ? What kind of shop, if any is here? Is it intentional that it is used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=shoes ?',
        },
        {
            'key': 'shop',
            'value': 'footware',
            'tag_specific_comment': 'shop=shoemaker ? What kind of shop, if any is here? Is it intentional that it is used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=shoes ? And instead of https://wiki.openstreetmap.org/wiki/Tag:craft%3Dshoemaker ?',
        },
        
        {
            'key': 'shop',
            'value': 'home_supplies',
            'tag_specific_comment': 'shop=home_supplies ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'House_Decoration',
            'tag_specific_comment': 'shop=House_Decoration ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'homeware_&_household_goods',
            'tag_specific_comment': 'shop=homeware_&_household_goods ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'household_goods',
            'tag_specific_comment': 'shop=household_goods ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'homegoods',
            'tag_specific_comment': 'shop=homegoods ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'Household Items',
            'tag_specific_comment': 'shop=Household Items ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'home_good_store',
            'tag_specific_comment': 'shop=home_good_store ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'household',
            'tag_specific_comment': 'shop=household ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'homeware',
            'tag_specific_comment': 'shop=homeware ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'homewares',
            'tag_specific_comment': 'shop=homewares ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'household_items_shop',
            'tag_specific_comment': 'shop=household_items_shop ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'home_goods',
            'tag_specific_comment': 'shop=home_goods ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'home_goods_store',
            'tag_specific_comment': 'shop=home_goods_store ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'home_goods_stores',
            'tag_specific_comment': 'shop=home_goods_stores ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'home goods',
            'tag_specific_comment': 'shop=home goods ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'Home_goods_stores',
            'tag_specific_comment': 'shop=Home_goods_stores ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'Home_Goods',
            'tag_specific_comment': 'shop=Home_Goods ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'Home_Goods_Store',
            'tag_specific_comment': 'shop=Home_Goods_Store ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'Home goods',
            'tag_specific_comment': 'shop=Home goods ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'Home_goods_store',
            'tag_specific_comment': 'shop=Home_goods_store ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'home',
            'tag_specific_comment': 'shop=home ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=houseware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful? Or maybe this shop=home is about selling real estate?',
        },
        {
            'key': 'shop',
            'value': 'kitchen_supply',
            'tag_specific_comment': 'shop=kitchen_supply ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=kitchenware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?\n\nOr maybe this shop is selling food?',
        },
        {
            'key': 'shop',
            'value': 'cookery',
            'tag_specific_comment': 'shop=cookery ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=kitchenware ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?\n\nOr maybe this shop is selling food?',
        },
        {
            'key': 'shop',
            'value': 'dressmaker',
            'tag_specific_comment': 'shop=dressmaker ? If it selling ready dresses then maybe shop=clothes would work fine? (see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dclothes ) If it is making dresses on request then maybe craft=dressmaker or craft=tailor would work well? See https://wiki.openstreetmap.org/wiki/Tag:craft%3Ddressmaker and  https://wiki.openstreetmap.org/wiki/Tag:craft%3Dtailor',
        },
        {
            'key': 'shop',
            'value': 'Tortillería',
            'tag_specific_comment': 'shop=Tortillería ? Should it be shop=tortilla proposed at https://wiki.openstreetmap.org/wiki/Proposal:shop=tortilla ?\n\nIs it amenity=fast_food or amenity=restaurant by any chance? Or are they selling pieces not ready to eat? Or ingredients? Maybe some https://wiki.openstreetmap.org/wiki/Key:cuisine would be a good idea?',
        },
        {
            'key': 'shop',
            'value': 'tortillería',
            'tag_specific_comment': 'shop=tortillería ? Should it be shop=tortilla proposed at https://wiki.openstreetmap.org/wiki/Proposal:shop=tortilla ?\n\nIs it amenity=fast_food or amenity=restaurant by any chance? Or are they selling pieces not ready to eat? Or ingredients? Maybe some https://wiki.openstreetmap.org/wiki/Key:cuisine would be a good idea?',
        },
        {
            'key': 'shop',
            'value': 'tortilleria',
            'tag_specific_comment': 'shop=tortilleria ? Should it be shop=tortilla proposed at https://wiki.openstreetmap.org/wiki/Proposal:shop=tortilla ?\n\nIs it amenity=fast_food or amenity=restaurant by any chance? Or are they selling pieces not ready to eat? Or ingredients? Maybe some https://wiki.openstreetmap.org/wiki/Key:cuisine would be a good idea?',
        },
        {
            'key': 'shop',
            'value': 'Tortilleria',
            'tag_specific_comment': 'shop=Tortilleria ? Should it be shop=tortilla proposed at https://wiki.openstreetmap.org/wiki/Proposal:shop=tortilla ?\n\nIs it amenity=fast_food or amenity=restaurant by any chance? Or are they selling pieces not ready to eat? Or ingredients? Maybe some https://wiki.openstreetmap.org/wiki/Key:cuisine would be a good idea?',
        },
        {
            'key': 'shop',
            'value': 'tortilliería',
            'tag_specific_comment': 'shop=tortilliería ? Should it be shop=tortilla proposed at https://wiki.openstreetmap.org/wiki/Proposal:shop=tortilla ?\n\nIs it amenity=fast_food or amenity=restaurant by any chance? Or are they selling pieces not ready to eat? Or ingredients? Maybe some https://wiki.openstreetmap.org/wiki/Key:cuisine would be a good idea?',
        },
        {
            'key': 'shop',
            'value': 'gocery',
            'tag_specific_comment': 'shop=gocery ? Is it typo of https://wiki.openstreetmap.org/wiki/Tag:shop=grocery ?',
        },
        {
            'key': 'shop',
            'value': 'cookies',
            'tag_specific_comment': 'shop=cookies ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=pastry ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'buildings',
            'tag_specific_comment': 'shop=buildings ? Is someone selling real estate (build houses)? Ready-to-build wooden houses on your property?',
        },
        {
            'key': 'shop',
            'value': 'timberhouses',
            'tag_specific_comment': 'shop=timberhouses ? Is someone selling real estate (build houses)? Ready-to-build wooden houses on your property?',
        },
        {
            'key': 'shop',
            'value': 'Rękodzieło,_artykuły_dekoracyjne,_meble.',
            'tag_specific_comment': 'shop=Rękodzieło,_artykuły_dekoracyjne,_meble. ?\n\nMoże\nshop furniture\ndescription=Rękodzieło,_artykuły_dekoracyjne,_meble.\n\nby było lepsze?',
        },
        {
            'key': 'shop',
            'value': 'building materials',
            'tag_specific_comment': 'shop=building materials ? Is it https://wiki.openstreetmap.org/wiki/Tag:shop=doityourself or https://wiki.openstreetmap.org/wiki/Tag:shop=trade + https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ? If not, how it differs?',
        },
        {
            'key': 'shop',
            'value': 'Tienda_de_suministros_de_materiales_de_construccion',
            'tag_specific_comment': 'shop=Tienda_de_suministros_de_materiales_de_construccion ? Is it https://wiki.openstreetmap.org/wiki/Tag:shop=doityourself or https://wiki.openstreetmap.org/wiki/Tag:shop=trade + https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ? If not, how it differs?',
        },
        {
            'key': 'shop',
            'value': 'Material_Construção',
            'tag_specific_comment': 'shop=Material_Construção ? Is it https://wiki.openstreetmap.org/wiki/Tag:shop=doityourself or https://wiki.openstreetmap.org/wiki/Tag:shop=trade + https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ? If not, how it differs?',
        },
        {
            'key': 'shop',
            'value': 'Construtora',
            'tag_specific_comment': 'shop=Construtora ? Is it https://wiki.openstreetmap.org/wiki/Tag:shop=doityourself or https://wiki.openstreetmap.org/wiki/Tag:shop=trade + https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ? If not, how it differs?',
        },
        {
            'key': 'shop',
            'value': 'BUILIDNG_MATERIAL_STORE',
            'tag_specific_comment': 'shop=BUILIDNG_MATERIAL_STORE ? Is it https://wiki.openstreetmap.org/wiki/Tag:shop=doityourself or https://wiki.openstreetmap.org/wiki/Tag:shop=trade + https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ? If not, how it differs?',
        },
        {
            'key': 'shop',
            'value': 'Building Materials',
            'tag_specific_comment': 'shop=Building Materials ? Is it https://wiki.openstreetmap.org/wiki/Tag:shop=doityourself or https://wiki.openstreetmap.org/wiki/Tag:shop=trade + https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ? If not, how it differs?',
        },
        {
            'key': 'shop',
            'value': 'Builders_Merchants',
            'tag_specific_comment': 'shop=Builders_Merchants ? Is it https://wiki.openstreetmap.org/wiki/Tag:shop=doityourself or https://wiki.openstreetmap.org/wiki/Tag:shop=trade + https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ? If not, how it differs?',
        },
        {
            'key': 'shop',
            'value': 'matériaux_de_construction',
            'tag_specific_comment': 'shop=matériaux_de_construction ? Is it https://wiki.openstreetmap.org/wiki/Tag:shop=doityourself or https://wiki.openstreetmap.org/wiki/Tag:shop=trade + https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ? If not, how it differs?',
        },
        {
            'key': 'shop',
            'value': 'building_material',
            'tag_specific_comment': 'shop=building_material ? Is it https://wiki.openstreetmap.org/wiki/Tag:shop=doityourself or https://wiki.openstreetmap.org/wiki/Tag:shop=trade + https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ? If not, how it differs?',
        },
        {
            'key': 'shop',
            'value': 'construction_shop',
            'tag_specific_comment': 'shop=construction_shop ? Is it https://wiki.openstreetmap.org/wiki/Tag:shop=doityourself or https://wiki.openstreetmap.org/wiki/Tag:shop=trade + https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ? If not, how it differs?',
        },
        {
            'key': 'shop',
            'value': 'construction_material',
            'tag_specific_comment': 'shop=construction_material ? Is it https://wiki.openstreetmap.org/wiki/Tag:shop=doityourself or https://wiki.openstreetmap.org/wiki/Tag:shop=trade + https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ? If not, how it differs?',
        },
        {
            'key': 'shop',
            'value': 'builders_merchant',
            'tag_specific_comment': 'shop=builders_merchant ? Is it https://wiki.openstreetmap.org/wiki/Tag:shop=doityourself or https://wiki.openstreetmap.org/wiki/Tag:shop=trade + https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ? If not, how it differs?',
        },
        {
            'key': 'shop',
            'value': 'skład_budowlany',
            'tag_specific_comment': 'shop=skład_budowlany ? Czy to https://wiki.openstreetmap.org/wiki/Pl:Tag:shop=doityourself ? Lub https://wiki.openstreetmap.org/wiki/Tag:shop=trade + https://wiki.openstreetmap.org/wiki/Tag:trade%3Dbuilding_supplies ? Czy coś innego?',
        },
        {
            'key': 'shop',
            'value': 'Skateboard_shop',
            'tag_specific_comment': 'shop=Skateboard_shop ? What kind of shop, if any is here? Would shop=sports + sport=skateboard would be maybe a better tagging? See https://wiki.openstreetmap.org/wiki/Tag:shop=sports and https://wiki.openstreetmap.org/wiki/Tag:sport%3Dskateboard\n\nNote that splitting categorisation into more general (shop=sports) and more detailed (sport=skateboard) makes easier to use OSM data.',
        },
        {
            'key': 'shop',
            'value': 'skateboard',
            'tag_specific_comment': 'shop=skateboard ? What kind of shop, if any is here? Would shop=sports + sport=skateboard would be maybe a better tagging? See https://wiki.openstreetmap.org/wiki/Tag:shop=sports and https://wiki.openstreetmap.org/wiki/Tag:sport%3Dskateboard\n\nNote that splitting categorisation into more general (shop=sports) and more detailed (sport=skateboard) makes easier to use OSM data.',
        },
        {
            'key': 'shop',
            'value': 'skateboards',
            'tag_specific_comment': 'shop=skateboards ? What kind of shop, if any is here? Would shop=sports + sport=skateboard would be maybe a better tagging? See https://wiki.openstreetmap.org/wiki/Tag:shop=sports and https://wiki.openstreetmap.org/wiki/Tag:sport%3Dskateboard\n\nNote that splitting categorisation into more general (shop=sports) and more detailed (sport=skateboard) makes easier to use OSM data.',
        },
        {
            'key': 'shop',
            'value': 'hockey',
            'tag_specific_comment': 'shop=hockey ? What kind of shop, if any is here? Would shop=sports + sport=hockey would be maybe a better tagging? See https://wiki.openstreetmap.org/wiki/Tag:shop=sports and https://wiki.openstreetmap.org/wiki/Tag:sport%3Dhockey\n\nNote that splitting categorisation into more general (shop=sports) and more detailed (sport=hockey) makes easier to use OSM data.',
        },
        {
            'key': 'shop',
            'value': 'Celebration supplies store',
            'tag_specific_comment': 'shop=Celebration supplies store ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=party ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'italian_specialties',
            'tag_specific_comment': 'shop=italian_specialties ? What kind of shop, if any is here? Is it selling food?',
        },
        {
            'key': 'shop',
            'value': 'pool_maintenance',
            'tag_specific_comment': 'shop=pool_maintenance ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=swimming_pool ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'photographer',
            'tag_specific_comment': 'shop=photographer ? What kind of shop, if any is here? Maybe https://wiki.openstreetmap.org/wiki/Tag:shop=photo or https://wiki.openstreetmap.org/wiki/Tag:craft%3Dphotographer would be better tag?',
        },
        {
            'key': 'shop',
            'value': 'Best Barber Shop',
            'tag_specific_comment': 'shop=Best Barber Shop ? Maybe following https://wiki.openstreetmap.org/wiki/Tag:hairdresser%3Dbarber would be a good idea and shop=hairdresser hairdresser=barber would be a better tagging?',
        },
        {
            'key': 'shop',
            'value': 'barber',
            'tag_specific_comment': 'shop=barber ? Maybe following https://wiki.openstreetmap.org/wiki/Tag:hairdresser%3Dbarber would be a good idea and shop=hairdresser hairdresser=barber would be a better tagging?',
        },
        {
            'key': 'shop',
            'value': 'barbershop',
            'tag_specific_comment': 'shop=barbershop ? Maybe following https://wiki.openstreetmap.org/wiki/Tag:hairdresser%3Dbarber would be a good idea and shop=hairdresser hairdresser=barber would be a better tagging?',
        },
        {
            'key': 'shop',
            'value': 'cafefurniture',
            'tag_specific_comment': 'shop=cafefurniture ? What kind of shop, if any is here? Is it typo or is it mix of furniture shop and cafe (in such case amenity=cafe + shop=furniture should work)',
        },
        {
            'key': 'shop',
            'value': 'for_rent',
            'tag_specific_comment': 'shop=for_rent ? Is it an empty shop space for rent (shop=vacant would be more standard)? Or is ir place where something can be rented? If yes, what can be rented here?',
        },
        {
            'key': 'shop',
            'value': 'chocolatier',
            'tag_specific_comment': 'shop=chocolatier ? What kind of shop, if any is here? Is it office=company ? shop=chocolate ? craft= ? https://wiki.openstreetmap.org/wiki/Tag:shop=chocolate https://wiki.openstreetmap.org/wiki/Tag:office%3Dcompany',
        },
        {
            'key': 'shop',
            'value': 'hairdressers',
            'tag_specific_comment': 'shop=hairdressers ? Is it single shop=hairdresser business or multiple ones?',
        },
        {
            'key': 'amenity',
            'value': 'hairdresser',
            'tag_specific_comment': 'Can it be changed to more standard shop=hairdresser ? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dhairdresser',
        },
        {
            'key': 'shop',
            'value': 'plumming_supplies',
            'tag_specific_comment': 'shop=plumming_supplies ? Is it intended to be shop=plumbing_supplies tag ?',
        },
        {
            'key': 'shop',
            'value': 'oil',
            'tag_specific_comment': 'shop=oil ? Is it a shop selling edible oil? Engine oil? Fuel oil? Something else?\n\nIs this shop even existing?',
        },
        {
            'key': 'shop',
            'value': 'tennis',
            'tag_specific_comment': 'shop=tennis ? What kind of shop, if any is here? Sport shop selling tennis equipment? (shop=sports sport=tennis would be better tagging in such case)',
        },
        {
            'key': 'shop',
            'value': 'canoe',
            'tag_specific_comment': 'shop=canoe ? What kind of shop, if any is here? Is it selling canoe trips? Sport shop selling canoe equipment? (shop=sports sport=canoe would be better tagging)',
        },
        {
            'key': 'shop',
            'value': 'running_specialty',
            'tag_specific_comment': 'shop=running_specialty ? What kind of shop, if any is here? Is it running club? Running sport shop? (shop=sports sport=running would be better tagging)',
        },
        {
            'key': 'shop',
            'value': 'general shops',
            'tag_specific_comment': 'shop=general_stores ? What kind of shop, if any is here? Is it shop=general? Multiple shop=general? Is any of values from https://wiki.openstreetmap.org/wiki/Key:shop matching well?',
        },
        {
            'key': 'shop',
            'value': 'dojo',
            'tag_specific_comment': 'shop=dojo ? Was it supposed to be amenity=dojo or shop=sports?',
        },
        {
            'key': 'shop',
            'value': 'centrum_handlowe',
            'tag_specific_comment': 'shop=centrum_handlowe ? shop=mall jak coś',
        },
        {
            'key': 'shop',
            'value': 'distilled_spirits_shop',
            'tag_specific_comment': 'shop=distilled_spirits_shop ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=alcohol ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'cider',
            'tag_specific_comment': 'shop=cider ? Maybe shop=alcohol alcohol=cider would work well, indicating that shop sells primarily this alcohol? Having separate shop types for sake, whisky, cider, beer, wine, red wine etc etc seems a poor idea while cascading tagging still provides full info for anyone interested while providing also top-level basic info for someone wanting 100 shop types rather than 10 000.\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop=alcohol',
        },
        {
            'key': 'shop',
            'value': 'sake',
            'tag_specific_comment': 'shop=sake ? Maybe shop=alcohol alcohol=sake would work well, indicating that shop sells primarily this alcohol? Having separate shop types for sake, whisky, cider, beer, wine, red wine etc etc seems a poor idea while cascading tagging still provides full info for anyone interested while providing also top-level basic info for someone wanting 100 shop types rather than 10 000.\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop=alcohol',
        },
        {
            'key': 'shop',
            'value': 'Sake',
            'tag_specific_comment': 'shop=Sake ? Maybe shop=alcohol alcohol=sake would work well, indicating that shop sells primarily this alcohol? Having separate shop types for sake, whisky, cider, beer, wine, red wine etc etc seems a poor idea while cascading tagging still provides full info for anyone interested while providing also top-level basic info for someone wanting 100 shop types rather than 10 000.\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop=alcohol',
        },
        {
            'key': 'shop',
            'value': 'whiskey',
            'tag_specific_comment': 'shop=whiskey ? Maybe shop=alcohol alcohol=whiskey would work well, indicating that shop sells primarily this alcohol? Having separate shop types for sake, whisky, cider, beer, wine, red wine etc etc seems a poor idea while cascading tagging still provides full info for anyone interested while providing also top-level basic info for someone wanting 100 shop types rather than 10 000.\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop=alcohol',
        },
        {
            'key': 'shop',
            'value': 'whisky',
            'tag_specific_comment': 'shop=whisky ? Maybe shop=alcohol alcohol=whisky would work well, indicating that shop sells primarily this alcohol? Having separate shop types for sake, whisky, cider, beer, wine, red wine etc etc seems a poor idea while cascading tagging still provides full info for anyone interested while providing also top-level basic info for someone wanting 100 shop types rather than 10 000.\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop=alcohol',
        },
        {
            'key': 'shop',
            'value': 'champagne',
            'tag_specific_comment': 'shop=champagne ? Maybe shop=alcohol alcohol=champagne would work well, indicating that shop sells primarily this alcohol? Having separate shop types for sake, whisky, cider, beer, wine, red wine etc etc seems a poor idea while cascading tagging still provides full info for anyone interested while providing also top-level basic info for someone wanting 100 shop types rather than 10 000.\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop=alcohol',
        },
        {
            'key': 'shop',
            'value': 'beer',
            'tag_specific_comment': 'shop=beer ? Maybe shop=alcohol alcohol=beer would work well, indicating that shop sells primarily this alcohol? Having separate shop types for sake, whisky, cider, beer, wine, red wine etc etc seems a poor idea while cascading tagging still provides full info for anyone interested while providing also top-level basic info for someone wanting 100 shop types rather than 10 000.\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop=alcohol',
        },
        {
            'key': 'shop',
            'value': 'ounpost',
            'tag_specific_comment': 'shop=ounpost ? Is it typo for shop=outpost (primarily pickup of ordered items) ?',
        },
        {
            'key': 'shop',
            'value': 'hairdresser_accessories',
            'tag_specific_comment': 'shop=hairdresser_accessories ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=hairdresser_supply ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'accessories',
            'tag_specific_comment': 'shop=accessories ? What kind of accwessories are sold here? Fashion accessories? Car parts? Gun accessories?\n\nMaybe use shop=fashion_accessories for clothing accessories, shop=car_parts for car accessories or other shop=* instead - see https://wiki.openstreetmap.org/wiki/Tag:shop%3Daccessories',
        },
        {
            'key': 'shop',
            'value': 'clothing_accessories',
            'tag_specific_comment': 'shop=clothing_accessories ? Is maybe shop=fashion_accessories fitting equally well? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dfashion_accessories',
        },
        {
            'key': 'shop',
            'value': 'toffe',
            'tag_specific_comment': 'shop=toffe ? What kind of shop, if any is here? Is it shop selling toffee (note an extra e). In such case maybe shop=confectionery confectionery=toffee or othe cascading tagging would work well?',
        },
        {
            'key': 'shop',
            'value': 'cosmetic_procedures',
            'tag_specific_comment': 'shop=cosmetic_procedures ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=beauty ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'beauty_center',
            'tag_specific_comment': 'shop=beauty_center ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=beauty ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'horseriding',
            'tag_specific_comment': 'shop=horseriding ? What kind of shop, if any is here? Or is it place where you may ride horse as a tourism attraction? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=equestrian ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'horseback',
            'tag_specific_comment': 'shop=horseback ? What kind of shop, if any is here? Or is it place where you may ride horse as a tourism attraction? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=equestrian ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'Carpet Cleaning',
            'tag_specific_comment': 'shop=Carpet Cleaning ? Is it an internal company office (office=company)? Place selling supplies and machines to clear carpets? Place where you can walk in arrange carpet cleaning?',
        },
        {
            'key': 'shop',
            'value': 'Masking_tape',
            'tag_specific_comment': 'shop=Masking_tape ? What kind of shop, if any is here? Is it really selling primarily/only masking tape? Is any of values from https://wiki.openstreetmap.org/wiki/Key:shop matching well?',
        },
        {
            'key': 'shop',
            'value': 'motor_bikes',
            'tag_specific_comment': 'shop=motor_bikes ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=motorcycle ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'bike',
            'tag_specific_comment': 'shop=bike ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=motorcycle ? Or is it about bicycles?\n\nShould we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'bike_parts',
            'tag_specific_comment': 'shop=bike_parts ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=motorcycle_parts ? Or is it about bicycles?\n\nShould we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': '2_wheeler',
            'tag_specific_comment': 'shop=2_wheeler ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=motorcycle ? Or is it about bicycles?\n\nShould we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'spożywczo-przemysłowy',
            'tag_specific_comment': 'shop=spożywczo-przemysłowy ? Czy to na pewno shop=convenience czy może coś innego?',
        },
        {
            'key': 'shop',
            'value': 'bakery_and_vegetables',
            'tag_specific_comment': 'shop=bakery_and_vegetables ? Maybe shop=bakery;greengrocer would work well? Or maybe it is shop=convenience?',
        },
        {
            'key': 'shop',
            'value': 'electronic_recycling',
            'tag_specific_comment': 'shop=electronic_recycling ? Are they selling used electronics? Buying it? Both? Is it even shop or just waste bin collecting electronics?',
        },
        {
            'key': 'shop',
            'value': 'Woodcraft',
            'tag_specific_comment': 'shop=Woodcraft ? Is it selling supplies for wood carving? Ready products? Something else?',
        },
        {
            'key': 'shop',
            'value': 'pastry_chef',
            'tag_specific_comment': 'shop=pastry_chef ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=pastry ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'it',
            'tag_specific_comment': 'shop=it ? Is it computer repair shop? Office of an IT company (office=company) ? Place selling computers? Something else??',
        },
        {
            'key': 'shop',
            'value': 'kids',
            'tag_specific_comment': 'shop=kids ? What kind of shop, if any is here? Is it intentionally used instead of shop=toys and shop=baby_goods ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop%3Dbaby_goods and https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtoys',
        },
        {
            'key': 'shop',
            'value': 'baby',
            'tag_specific_comment': 'shop=kids ? What kind of shop, if any is here? Is it intentionally used instead of shop=baby_goods ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:shop%3Dbaby_goods',
        },
        {
            'key': 'shop',
            'value': 'handbags',
            'tag_specific_comment': 'shop=handbags ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=bag ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'cardomom_drier',
            'tag_specific_comment': 'shop=cardomom_drier ? is it providing some service to general public ? Or is it man_made=works? Or is it company office (office=company)?\n\nSee https://wiki.openstreetmap.org/wiki/Tag:man_made%3Dworks and https://wiki.openstreetmap.org/wiki/Tag:office=company',
        },
        {
            'key': 'shop',
            'value': 'mill',
            'tag_specific_comment': 'shop=mill ? is it providing some service to general public ? Or is it man_made=works? Or is it company office (office=company)?',
        },
        {
            'key': 'shop',
            'value': 'Processing Plant',
            'tag_specific_comment': 'shop=Processing Plant? is it providing some service to general public ? Or is it man_made=works? Or is it company office (office=company)?',
        },
        {
            'key': 'shop',
            'value': 'factory',
            'tag_specific_comment': 'shop=factory? is it providing some service or selling products to general public ? Or is it man_made=works? Or is it company office (office=company)?\n\nIf it is shop, which of https://wiki.openstreetmap.org/wiki/Key:shop would fit? Or is it selling something else?',
        },
        {
            'key': 'shop',
            'value': 'manufacturer',
            'tag_specific_comment': 'shop=manufacturer? is it providing some service or selling products to general public ? Or is it man_made=works? Or is it company office (office=company)?',
        },
        {
            'key': 'shop',
            'value': 'floors',
            'tag_specific_comment': 'shop=floors ? What kind of shop, if any is here? Is it intentional that it is used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=flooring ? ( https://wiki.openstreetmap.org/wiki/Tag:craft=floorer may be also useful) Maybe all shop=floors should be replaced by shop=flooring in blind mechanical edit?',
        },
        {
            'key': 'shop',
            'value': 'floortiles',
            'tag_specific_comment': 'shop=floortiles ? What kind of shop, if any is here? Is it intentional that it is used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=flooring ? ( https://wiki.openstreetmap.org/wiki/Tag:craft=floorer may be also useful) Maybe all shop=floortiles should be replaced by shop=flooring in blind mechanical edit?',
        },
        {
            'key': 'shop',
            'value': 'tiled_floor',
            'tag_specific_comment': 'shop=tiled_floor?\n\nThere are several tagging for various tile-related things. Is it really distinct from them? How it differs from:\n- shop=tiles https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtiles\n- shop=trade trade=tiles https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtrade\n- craft=tiler https://wiki.openstreetmap.org/wiki/Tag:craft%3Dtiler\n- shop=flooring https://wiki.openstreetmap.org/wiki/Tag:shop%3Dflooring\n- craft=floorer https://wiki.openstreetmap.org/wiki/Tag:craft%3Dfloorer\n\nMaybe one of this options fits well and can be used?\nAlso, is it really solely floor tiles that cannot be put on walls?',
        },
        {
            'key': 'shop',
            'value': 'floortile',
            'tag_specific_comment': 'shop=floortile?\n\nThere are several tagging for various tile-related things. Is it really distinct from them? How it differs from:\n- shop=tiles https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtiles\n- shop=trade trade=tiles https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtrade\n- craft=tiler https://wiki.openstreetmap.org/wiki/Tag:craft%3Dtiler\n- shop=flooring https://wiki.openstreetmap.org/wiki/Tag:shop%3Dflooring\n- craft=floorer https://wiki.openstreetmap.org/wiki/Tag:craft%3Dfloorer\n\nMaybe one of this options fits well and can be used?\nAlso, is it really solely floor tiles that cannot be put on walls?',
        },
        {
            'key': 'shop',
            'value': 'floorer',
            'tag_specific_comment': 'shop=floorer?\n\nThere are several tagging for various tile-related things. Is it really distinct from them? How it differs from:\n- shop=tiles https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtiles\n- shop=trade trade=tiles https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtrade\n- craft=tiler https://wiki.openstreetmap.org/wiki/Tag:craft%3Dtiler\n- shop=flooring https://wiki.openstreetmap.org/wiki/Tag:shop%3Dflooring\n- craft=floorer https://wiki.openstreetmap.org/wiki/Tag:craft%3Dfloorer\n\nMaybe one of this options fits well and can be used?',
        },
        {
            'key': 'shop',
            'value': 'tiling',
            'tag_specific_comment': 'shop=tiling?\n\nThere are several tagging for various tile-related things. Is it really distinct from them? How it differs from:\n- shop=tiles https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtiles\n- shop=trade trade=tiles https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtrade\n- craft=tiler https://wiki.openstreetmap.org/wiki/Tag:craft%3Dtiler\n- shop=flooring https://wiki.openstreetmap.org/wiki/Tag:shop%3Dflooring\n- craft=floorer https://wiki.openstreetmap.org/wiki/Tag:craft%3Dfloorer\n\nMaybe one of this options fits well and can be used?',
        },
        {
            'key': 'shop',
            'value': 'tiler',
            'tag_specific_comment': 'shop=tiler?\n\nThere are several tagging for various tile-related things. Is it really distinct from them? How it differs from:\n- shop=tiles https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtiles\n- shop=trade trade=tiles https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtrade\n- craft=tiler https://wiki.openstreetmap.org/wiki/Tag:craft%3Dtiler\n- shop=flooring https://wiki.openstreetmap.org/wiki/Tag:shop%3Dflooring\n- craft=floorer https://wiki.openstreetmap.org/wiki/Tag:craft%3Dfloorer\n\nMaybe one of this options fits well and can be used?',
        },
        {
            'key': 'shop',
            'value': 'aluminum_Supplier',
            'tag_specific_comment': 'shop=aluminum_Supplier ? can anyone walk in and buy x kg of alluminium? Or is it company office of business having B2B on long term contracts? Is it even a shop at all? Or is it taggable as shop=trade trade=aluminium_supplier or something similar?',
        },
        {
            'key': 'shop',
            'value': 'Grocery_Store',
            'tag_specific_comment': 'shop=Grocery_Store ? Is it maybe better tagged as https://wiki.openstreetmap.org/wiki/Tag:shop=grocery ? Is it safe to blindly retag this remotely?',
        },
        {
            'key': 'shop',
            'value': 'Cafe_and_Gift_Shop',
            'tag_specific_comment': 'shop=Cafe_and_Gift_Shop ?  is it one object (and then can be actually tagged as gift shop and as a cafe on one object)?\n\nOr has someone mapped two separate POIs as one?',
        },        
        {
            'key': 'shop',
            'value': 'glass_art',
            'tag_specific_comment': 'shop=glass_art ? What kind of shop, if any is here?\n\nIs it selling produced glass art pieces? Or materials for making glass art? Maybe shop=gift gift=glass_art works well for it?\n\nMaybe shop=craft if it is selling materials to make craft art, see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcraft',
        },
        {
            'key': 'shop',
            'value': 'crafting',
            'tag_specific_comment': 'shop=crafting ? What kind of shop, if any is here?\n\nIs it selling produced craft art pieces? Or materials for making crafts? Maybe shop=gift gift=crafts works well for it?\n\nMaybe shop=craft if it is selling materials to make craft art, see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcraft',
        },
        {
            'key': 'shop',
            'value': 'handcrafts',
            'tag_specific_comment': 'shop=handcrafts ? What kind of shop, if any is here?\n\nIs it selling produced craft art pieces? Or materials for making crafts? Maybe shop=gift gift=handcrafts works well for it?\n\nMaybe shop=craft if it is selling materials to make craft art, see https://wiki.openstreetmap.org/wiki/Tag:shop%3Dcraft',
        },        
        {
            'key': 'shop',
            'value': 'Flyfishing Outfitter',
            'tag_specific_comment': 'shop=Flyfishing Outfitter ? What kind of shop, if any is here? See also https://wiki.openstreetmap.org/wiki/Tag:shop=fishing - is shop=fishing a good idea as a shop value? (some extra tags may convey extra detail)',
        },
        {
            'key': 'shop',
            'value': 'Fishing_Tackel',
            'tag_specific_comment': 'shop=Fishing_Tackle_and_Bait ? What kind of shop, if any is here? See also https://wiki.openstreetmap.org/wiki/Tag:shop=fishing - is shop=fishing a good idea as a shop value? (some extra tags may convey extra detail)',
        },
        {
            'key': 'shop',
            'value': 'fishing_bait',
            'tag_specific_comment': 'shop=fishing_bait ? What kind of shop, if any is here? See also https://wiki.openstreetmap.org/wiki/Tag:shop=fishing - is shop=fishing a good idea as a shop value? (some extra tags may convey extra detail)',
        },
        {
            'key': 'shop',
            'value': 'Fishing_Tackle_and_Bait',
            'tag_specific_comment': 'shop=Fishing_Tackle_and_Bait ? What kind of shop, if any is here? See also https://wiki.openstreetmap.org/wiki/Tag:shop=fishing - is shop=fishing a good idea as a shop value? (some extra tags may convey extra detail)',
        },
        {
            'key': 'shop',
            'value': 'fishing_supply',
            'tag_specific_comment': 'shop=fishing_supply ? What kind of shop, if any is here? See also https://wiki.openstreetmap.org/wiki/Tag:shop=fishing - is shop=fishing intentionally not used here?',
        },
        {
            'key': 'shop',
            'value': 'fishing_tackle_store',
            'tag_specific_comment': 'shop=fishing_supply ? What kind of shop, if any is here? See also https://wiki.openstreetmap.org/wiki/Tag:shop=fishing - is shop=fishing intentionally not used here?\n\nAnd maybe shop=fishing fishing=tackle or similar tagging can be used?',
        },
        {
            'key': 'shop',
            'value': 'fishing_supplies',
            'tag_specific_comment': 'shop=fishing_supplies - is it just simply shop=fishing ? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dfishing',
        },
        {
            'key': 'shop',
            'value': 'dairy_kitchen',
            'tag_specific_comment': 'shop=dairy_kitchen ? Is it amenity=fast_food or amenity=restaurant? If not, how it differs from it? Maybe cuisine= with some value would fit? Or is it about having vegetarian food?',
        },
        {
            'key': 'shop',
            'value': 'cafeteria',
            'tag_specific_comment': 'shop=cafeteria ? Is it amenity=fast_food or amenity=restaurant? If not, how it differs from them?',
        },
        {
            'key': 'shop',
            'value': 'cooking',
            'tag_specific_comment': 'shop=cooking ? Is it amenity=fast_food or amenity=restaurant? If not, how it differs from it? Is it mabe prepraring materials for cooking? Or cooking utensils? Or something else?',
        },
        {
            'key': 'shop',
            'value': 'barbeque',
            'tag_specific_comment': 'shop=barbeque ? Is it amenity=fast_food or amenity=restaurant? If not, how it differs from it? Maybe cuisine=barbeque would work?\n\nmaybe shop=bbq if it sells grills? See https://wiki.openstreetmap.org/wiki/Tag:shop=bbq',
        },
        {
            'key': 'shop',
            'value': 'grill',
            'tag_specific_comment': 'shop=grill ? Is it amenity=fast_food or amenity=restaurant? If not, how it differs from it? Maybe cuisine=barbeque would work?\n\nmaybe shop=bbq if it sells grills? See https://wiki.openstreetmap.org/wiki/Tag:shop=bbq',
        },
        {
            'key': 'shop',
            'value': 'Eatery',
            'tag_specific_comment': 'shop=Eatery ? Is it amenity=fast_food or amenity=restaurant? If not, how it differs from it?',
        },
        {
            'key': 'shop',
            'value': 'eatery',
            'tag_specific_comment': 'shop=Eetery ? Is it amenity=fast_food or amenity=restaurant? If not, how it differs from it?',
        },
        {
            'key': 'shop',
            'value': 'cantina',
            'tag_specific_comment': 'shop=cantina ? Is it amenity=fast_food or amenity=restaurant? If not, how it differs from it?',
        },
        {
            'key': 'shop',
            'value': 'Canteen',
            'tag_specific_comment': 'shop=Canteen ? Is it amenity=fast_food or amenity=restaurant? If not, how it differs from it?',
        },
        {
            'key': 'shop',
            'value': 'canteen',
            'tag_specific_comment': 'shop=canteen ? Is it amenity=fast_food or amenity=restaurant? If not, how it differs from it?',
        },
        {
            'key': 'shop',
            'value': 'Secondhand bookshop',
            'tag_specific_comment': 'shop=Secondhand bookshop ? Is it shop=books second_hand=only or is it shop=books second_hand=yes (if they sell also new books)?',
        },
        {
            'key': 'shop',
            'value': 'used_furniture_store',
            'tag_specific_comment': 'shop=used_furniture_store ? Is it shop=furniture second_hand=only or is it shop=furniture second_hand=yes (if they sell also new furniture)?',
        },
        {
            'key': 'shop',
            'value': 'furntiure_reuse',
            'tag_specific_comment': 'shop=furntiure_reuse ? Is it shop=furniture second_hand=only or is it shop=furniture second_hand=yes (if they sell also new furniture)?',
        },
        {
            'key': 'shop',
            'value': '2nd Hand Motors',
            'tag_specific_comment': 'shop=2nd Hand Motors ? Is it about motorcycles? Is it second_hand=only or is it second_hand=yes (if they sell also new stuff)?',
        },
        {
            'key': 'shop',
            'value': 'fruit_and_vegitable_store',
            'tag_specific_comment': 'shop=fruit_and_vegitable_store ? What kind of shop, if any is here? Is it maybe shop=greengrocer ? or shop=farm? ( https://wiki.openstreetmap.org/wiki/Tag:shop=farm )',
        },
        {
            'key': 'shop',
            'value': 'produce',
            'tag_specific_comment': 'shop=produce ? What kind of shop, if any is here? Is it maybe shop=greengrocer ?',
        },
        {
            'key': 'shop',
            'value': 'School',
            'tag_specific_comment': 'shop=School ? What kind of shop, if any is here? Is it maybe rather school than shop?',
        },
        {
            'key': 'shop',
            'value': 'school',
            'tag_specific_comment': 'shop=school ? What kind of shop, if any is here? Is it maybe rather school than shop?',
        },
        {
            'key': 'shop',
            'value': 'matress',
            'tag_specific_comment': 'shop=matress ? Is it typo of shop=mattress ? If not, what this tag is intended to mean?',
        },
        {
            'key': 'shop',
            'value': 'Oxygen',
            'tag_specific_comment': 'shop=Oxygen ? Is it shop name put as its type? Is it some place actually selling oxygen gas?',
        },
        {
            'key': 'shop',
            'value': 'oxygen',
            'tag_specific_comment': 'shop=oxygen ? Is it shop name put as its type? Is it some place actually selling oxygen gas?',
        },
        {
            'key': 'shop',
            'value': 'medical technology',
            'tag_specific_comment': 'shop=medical technology ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=medical_supply ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'medical_shop',
            'tag_specific_comment': 'shop=medical_shop ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=medical_supply ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful? Is it simply a pharmacy (amenity=pharmacy)?',
        },
        {
            'key': 'shop',
            'value': 'health_equipment',
            'tag_specific_comment': 'shop=health_equipment ? What kind of shop, if any is here? Is it intentionally used instead of https://wiki.openstreetmap.org/wiki/Tag:shop=medical_supply ? If yes, what is the difference? Should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'prosthetics',
            'tag_specific_comment': 'shop=prosthetics ? Maybe it would be better to tag it as subtag of shop=medical_supply (say medical_supply=prosthetics) ? https://wiki.openstreetmap.org/wiki/Tag:shop=medical_supply ? Having separate top level value for every type of medical equipment seems a bit too much...\n\nOr should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'prothesis',
            'tag_specific_comment': 'shop=prothesis ? Maybe it would be better to tag it as subtag of shop=medical_supply (say medical_supply=prothesis) ? https://wiki.openstreetmap.org/wiki/Tag:shop=medical_supply ? Having separate top level value for every type of medical equipment seems a bit too much...\n\nOr should we document this shop value as distinct, valid and useful?',
        },
        {
            'key': 'shop',
            'value': 'tabacco',
            'tag_specific_comment': 'shop=tabacco - is it supposed to be shop=tobacco ? See https://wiki.openstreetmap.org/wiki/Tag:shop%3Dtobacco',
        },
        {
            'key': 'shop',
            'value': 'kiosk:conditional=yes @ 06:00-22:00',
            'tag_specific_comment': 'shop=kiosk:conditional=yes @ 06:00-22:00 ? So it is open in this hours? Or is its structure removed?',
        },
        {
            'key': 'shop',
            'value': 'spares',
            'tag_specific_comment': 'shop=spares ? What kind of spare parts? Of car parts? specialized machinery? sailing boats? train models? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'spare_parts',
            'tag_specific_comment': 'shop=spare_parts ? What kind of spare parts? Of car parts? specialized machinery? sailing boats? train models? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'Spares_parts_shop',
            'tag_specific_comment': 'shop=Spares_parts_shop ? What kind of spare parts? Of car parts? specialized machinery? sailing boats? train models? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'Spare parts shop',
            'tag_specific_comment': 'shop=Spare parts shop ? What kind of spare parts? Of car parts? specialized machinery? sailing boats? train models? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'service',
            'tag_specific_comment': 'shop=service ? What kind of service? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'entertainment',
            'tag_specific_comment': 'shop=entertainment ? What kind of entertainment? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'services',
            'tag_specific_comment': 'shop=services ? What kind of service? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'Services',
            'tag_specific_comment': 'shop=Services ? What kind of service? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'Records',
            'tag_specific_comment': 'shop=Records ? What kind of records? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'surplus',
            'tag_specific_comment': 'shop=surplus ? What kind of surplus? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'Surplus Warehouse',
            'tag_specific_comment': 'shop=Surplus Warehouse ? What kind of surplus? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'Surplus',
            'tag_specific_comment': 'shop=Surplus ? What kind of surplus? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'Appliances',
            'tag_specific_comment': 'shop=Appliances ? What kind of appliances? (see https://wiki.openstreetmap.org/wiki/Key:shop for possible values - though maybe new one is needed)',
        },
        {
            'key': 'shop',
            'value': 'pharmacist',
            'tag_specific_comment': 'shop=pharmacist ? Is it simply a pharmacy (amenity=pharmacy) or something else? Should I have changed it remotely, without survey rathen than making a note?',
        },
        {
            'key': 'shop',
            'value': 'apothecary',
            'tag_specific_comment': 'shop=apothecary ? Is it simply a pharmacy (amenity=pharmacy) or something else? Should I have changed it remotely, without survey rathen than making a note?',
        },
        {
            'key': 'shop',
            'value': 'post_office',
            'tag_specific_comment': 'shop=post_office ? Is it simply post office (amenity=post_office, see https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dpost_office ) or was it intentionally mapped not as a post office?',
        },
        {
            'key': 'shop',
            'value': 'postal',
            'tag_specific_comment': 'shop=postal ? Is it simply post office (amenity=post_office, see https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dpost_office ) or was it intentionally mapped not as a post office?',
        },
        {
            'key': 'shop',
            'value': 'sari-sari',
            'tag_specific_comment': 'shop=sari-sari ? What kind of shop is that? Can it be assumed to be shop=convenience ( see https://www.openstreetmap.org/note/3805130 ) and changed remotely without verification? Or is it better to open a note and wait for a local check?',
        },
        {
            'key': 'shop',
            'value': 'Manufacture_of_ICT_Infrastructure Equipment',
            'tag_specific_comment': 'shop=Manufacture_of_ICT_Infrastructure Equipment ? Is it shop selling this product? Or just place producing it? (man_made=works?) Or maybe both?',
        },
        {
            'key': 'shop',
            'value': 'Water_Filtration_Equipment_Manufacturer',
            'tag_specific_comment': 'shop=Water_Filtration_Equipment_Manufacturer ? Is it shop selling this product? Or just place producing it? (man_made=works?) Or maybe both?',
        },
        {
            'key': 'shop',
            'value': 'brewery',
            'tag_specific_comment': 'shop=brewery ? Is it shop selling alcohol? Or just place producing it? (man_made=works?) Or maybe both? See https://wiki.openstreetmap.org/wiki/Tag:shop=alcohol',
        },
        {
            'key': 'shop',
            'value': 'cbd',
            'tag_specific_comment': 'shop=cbd ? What kind of shop, if any is here? See also https://wiki.openstreetmap.org/wiki/Tag:shop=cannabis - is shop=cannabis intentionally not used here?',
        },
        {
            'key': 'office',
            'value': 'graphic_designer',
            'tag_specific_comment': 'office = graphic_designer looks like a typo. It seems that it should be office = graphic_design\n\nBut I was not sure enough to make a remote replacement. Is it safe to change it?',
        },
        {
            'key': 'office',
            'value': 'Company 2',
            'tag_specific_comment': 'office = Company 2 looks like a typo. It seems that it should be office = company\n\nBut I was not sure enough to make a remote replacement. Is it safe to change it?',
        },
        {
            'key': 'surface',
            'value': 'bare_ground',
            'tag_specific_comment': 'Is surface=bare_ground in any way at all distict from surface=dirt ? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Ddirt',
        },
        {
            'key': 'surface',
            'value': 'stairs',
            'tag_specific_comment': 'It should have highway=steps, right? With surface tag for actual surface...\n\nUnless it is not steps at all then surface=stairs should be removed',
        },
        {
            'key': 'surface',
            'value': 'steps',
            'tag_specific_comment': 'It should have highway=steps, right? With surface tag for actual surface...\n\nUnless it is not steps at all then surface=steps should be removed',
        },
        {
            # https://www.openstreetmap.org/note/3977911
            'key': 'surface',
            'value': 'tarmac',
            'tag_specific_comment': 'is it an actual tarmacadan? In such case surface=tarmacadan may be a better less confused term (tarmac is widely used for asphalt and concrete surfaces)\n\nOr is it just a regular asphalt surface? Then surface=asphalt would be better\n\nsee https://wiki.openstreetmap.org/wiki/Tag:surface=tarmac for some documentation',
        },
        {
            'key': 'surface',
            'value': 'pa',
            'tag_specific_comment': 'surface = pa looks like it was supposed to be surface=paved.\n\nBut I was not sure enough to make a remote replacement. Have I guessed correctly?',
        },
        {
            'key': 'surface',
            'value': 'com',
            'tag_specific_comment': 'surface = com looks like it was supposed to be surface=compacted.\n\nBut I was not sure enough to make a remote replacement. Have I guessed correctly?',
        },
        {
            'key': 'surface',
            'value': "a'",
            'tag_specific_comment': "What was meant by surface=a' ?",
        },
        {
            'key': 'surface',
            'value': "tared",
            'tag_specific_comment': "What was meant by surface=tared ?",
        },
        {
            'key': 'surface',
            'value': "plates",
            'tag_specific_comment': "What was meant by surface=plates ? Is any value from https://wiki.openstreetmap.org/wiki/Key:surface#Values fitting?\n\nAre these large prefabricated concrete plates? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dconcrete:plates\n\nAre these small concrete plates (also known as paving stones) See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dpaving_stones",
        },
        {
            'key': 'surface',
            'value': "concrete_slabs",
            'tag_specific_comment': "What was meant by surface=concrete_slabs ? Is any value from https://wiki.openstreetmap.org/wiki/Key:surface#Values fitting?\n\nAre these large prefabricated concrete plates? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dconcrete:plates\n\nAre these small concrete plates (also known as paving stones) See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dpaving_stones",
        },
        {
            'key': 'surface',
            'value': "concrete:slabs",
            'tag_specific_comment': "What was meant by surface=concrete:slabs ? Is any value from https://wiki.openstreetmap.org/wiki/Key:surface#Values fitting?\n\nAre these large prefabricated concrete plates? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dconcrete:plates\n\nAre these small concrete plates (also known as paving stones) See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dpaving_stones",
        },
        {
            'key': 'surface',
            'value': "concrete:tiles",
            'tag_specific_comment': "What was meant by surface=concrete:tiles ? Is any value from https://wiki.openstreetmap.org/wiki/Key:surface#Values fitting?\n\nAre these small concrete plates (also known as paving tiles)? That would be tagged surface=paving_stones See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dpaving_stones",
        },
        {
            'key': 'surface',
            'value': "loose_sand",
            'tag_specific_comment': "Is there any kind of sand except loose sand? Why not use https://wiki.openstreetmap.org/wiki/Tag:surface%3Dsand ? Note that for earth (that tends to stick more than sand) we have surface=dirt",
        },
        {
            'key': 'surface',
            'value': "Turf",
            'tag_specific_comment': "What is this? surface=artificial_turf or surface=grass? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dturf",
        },
        {
            'key': 'surface',
            'value': "turf",
            'tag_specific_comment': "What is this? surface=artificial_turf or surface=grass? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dturf",
        },
        {
            'key': 'surface',
            'value': "all_weather",
            'tag_specific_comment': "nWhich value from https://wiki.openstreetmap.org/wiki/Key:surface fits? Is it safe to assume and remotely retag with no verification that it is surface=paved?",
        },
        {
            'key': 'surface',
            'value': "conc",
            'tag_specific_comment': "Which value from https://wiki.openstreetmap.org/wiki/Key:surface fits? Is it safe to assume and remotely retag with no verification that it is surface=concrete?",
        },
        {
            'key': 'surface',
            'value': "sans_revêtement",
            'tag_specific_comment': "Which value from https://wiki.openstreetmap.org/wiki/Key:surface fits? Is it safe to assume and remotely retag with no verification that it is surface=unpaved?",
        },
        {
            'key': 'surface',
            'value': "klinkers",
            'tag_specific_comment': "Which value from https://wiki.openstreetmap.org/wiki/Key:surface fits? Is it safe to assume and remotely retag with no verification that it is surface=sett? Or can it be also surface=paving_stones or surface=unhewn_cobblestone?",
        },
        {
            'key': 'surface',
            'value': "straatstenenc",
            'tag_specific_comment': "Which value from https://wiki.openstreetmap.org/wiki/Key:surface fits? Is it safe to assume and remotely retag with no verification that it is surface=paving_stones? Or can it be also surface=sett or surface=unhewn_cobblestone?",
        },
        {
            'key': 'surface',
            'value': "плитка",
            'tag_specific_comment': "Which value from https://wiki.openstreetmap.org/wiki/Key:surface fits? Is it safe to assume and remotely retag with no verification that it is surface=paving_stones? Or can it be also surface=sett or surface=unhewn_cobblestone or surface=tiles?",
        },
        {
            'key': 'surface',
            'value': "bestraat",
            'tag_specific_comment': "Which value from https://wiki.openstreetmap.org/wiki/Key:surface fits? Is it safe to assume and remotely retag with no verification that it is surface=paving_stones? Or can it be also surface=sett or surface=unhewn_cobblestone?",
        },
        {
            'key': 'surface',
            'value': "Bosbodem",
            'tag_specific_comment': "Which value from https://wiki.openstreetmap.org/wiki/Key:surface fits? Is it safe to assume and remotely retag with no verification that it is surface=dirt? Or maybe some other value can fit better?",
        },
        {
            'key': 'surface',
            'value': "грунт",
            'tag_specific_comment': "Which value from https://wiki.openstreetmap.org/wiki/Key:surface fits? Is it safe to assume and remotely retag with no verification that it is surface=dirt? Or maybe some other value can fit better?",
        },
        {
            'key': 'surface',
            'value': "boue",
            'tag_specific_comment': "Would it be better tag it as surface=mud ? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dmud",# https://www.openstreetmap.org/note/3845166
        },
        {
            'key': 'surface',
            'value': "pierres",
            'tag_specific_comment': "Is it surface=gravel? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dgravel",
        },
        {
            'key': 'surface',
            'value': "gazon_ras",
            'tag_specific_comment': 'Seems to mean "short grass" but maybe surface=grass would work? Or at least surface=short_grass... Or maybe some subtag, like surface=grass height=?? or surface=grass grass=short_grass ?',
        },
        {
            'key': 'surface',
            'value': "gazon_tres_ras",
            'tag_specific_comment': 'Seems to mean "very short grass" but maybe surface=grass would work? Or at least surface=short_grass... Or maybe some subtag, like surface=grass height=?? or surface=grass grass=very_short_grass ?',
        },
        {
            'key': 'surface',
            'value': "synthétique",
            'tag_specific_comment': "is it surface=artificial_turf ? Or maybe surface=tartan ? Or maybe something else? \n\nSee https://wiki.openstreetmap.org/wiki/Tag:surface%3Dartificial_turf and https://wiki.openstreetmap.org/wiki/Key:surface",
        },
        {
            'key': 'surface',
            'value': "synthétique",
            'tag_specific_comment': "is it surface=artificial_turf ? Or maybe surface=tartan ? Or maybe something else? \n\nSee https://wiki.openstreetmap.org/wiki/Tag:surface%3Dartificial_turf and https://wiki.openstreetmap.org/wiki/Key:surface",
        },
        {
            'key': 'surface',
            'value': "terrain_synthétique",
            'tag_specific_comment': "is it surface=artificial_turf ? Or maybe surface=tartan ? Or maybe something else? \n\nSee https://wiki.openstreetmap.org/wiki/Tag:surface%3Dartificial_turf and https://wiki.openstreetmap.org/wiki/Key:surface",
        },
        {
            'key': 'surface',
            'value': "pierres",
            'tag_specific_comment': "Is it surface=gravel? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dgravel",
        },
        {
            'key': 'surface',
            'value': "rochers",
            'tag_specific_comment': "Would it be better tag it as surface=rock ? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Drock",
        },
        {
            'key': 'surface',
            'value': "rocher",
            'tag_specific_comment': "Would it be better tag it as surface=rock ? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Drock",
        },
        {
            'key': 'surface',
            'value': "blocs_de_roche",
            'tag_specific_comment': "Would it be better tag it as surface=rock ? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Drock",
        },
        {
            'key': 'surface',
            'value': "pierres_sèches",
            'tag_specific_comment': "Would it be better tag it as surface=rock ? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Drock",
        },
        {
            'key': 'surface',
            'value': "rocheux/felsig",
            'tag_specific_comment': "Would it be better tag it as surface=rock ? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Drock",
        },
        { # see https://community.openstreetmap.org/t/proposed-bot-edit-automatic-replacement-of-surface-values-where-it-is-safe/105361/3
            'key': 'surface',
            'value': "pflastersteine",
            'tag_specific_comment': "Is it surface=sett or is it surface=paving_stones in this case? Or maybe surface=unhewn_cobblestone? Or maybe something else?",
        },
        { # see https://community.openstreetmap.org/t/proposed-bot-edit-automatic-replacement-of-surface-values-where-it-is-safe/105361/3
            'key': 'surface',
            'value': "pflasterstein",
            'tag_specific_comment': "Is it surface=sett or is it surface=paving_stones in this case? Or maybe surface=unhewn_cobblestone? Or maybe something else?",
        },
        {
            'key': 'surface',
            'value': "dirty",
            'tag_specific_comment': "Should it be surface=dirt ? Is it safe to blindly replace in bot edit or is it requiring better review? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Ddirt",
        },
        {
            'key': 'surface',
            'value': "erde",
            'tag_specific_comment': "Should it be surface=dirt ? Is it safe to blindly replace in bot edit or is it requiring better review? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Ddirt",
        },
        {
            'key': 'surface',
            'value': "muddy",
            'tag_specific_comment': "Should it be surface=mud or surface=dirt or be split into parts? Or maybe we need a yet another surface value, this time surface=muddy? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dmud",
        },
        {
            'key': 'surface',
            'value': "iron",
            'tag_specific_comment': "Is it really iron rather than steel? Maybe surface=metal would be better tagging? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dmetal",
        },
        {
            'key': 'surface',
            'value': "steel",
            'tag_specific_comment': "Maybe surface=metal material=steel would be better tagging? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dmetal",
        },
        {
            'key': 'surface',
            'value': "aluminium",
            'tag_specific_comment': "Maybe surface=metal material=aluminium would be better tagging here? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dmetal",
        },
        {
            'key': 'surface',
            'value': "앿",
            'tag_specific_comment': "Can it be safely retagged to surface=dirt? Or maybe surface=unpaved? See https://wiki.openstreetmap.org/wiki/Key:surface - maybe it should be assumed to be safe for automatic retagging, see comment about keyboard mode in https://www.openstreetmap.org/note/3976830",
        },
        {
            'key': 'surface',
            'value': "Waldboden",
            'tag_specific_comment': "Which value from https://wiki.openstreetmap.org/wiki/Key:surface fits? Is it safe to assume and remotely retag with no verification that it is surface=ground? Or maybe some other value can fit better?",
        },
        {
            'key': 'surface',
            'value': "щебеночное_покрытие",
            'tag_specific_comment': "Which value from https://wiki.openstreetmap.org/wiki/Key:surface fits? Is it safe to assume and remotely retag with no verification that it is surface=gravel?",
        },
        {
            'key': 'surface',
            'value': "kies",
            'tag_specific_comment': "is it surface=gravel ? surface=fine_gravel ? surface=pebblestone ? Something else? See https://wiki.openstreetmap.org/wiki/Key:surface and https://wiki.openstreetmap.org/wiki/DE:Key:surface  and https://community.openstreetmap.org/t/surface-kies-is-it-surface-gravel/102927",
        },
        {
            'key': 'surface',
            'value': "hardcore",
            # see https://www.openstreetmap.org/note/3977357
            'tag_specific_comment': "What is this? Equivalent of surface=compacted (as smashed up rubble)? Or maybe it is closed to surface=gravel?\n\nOr maybe it should be tagged as a different entry from standard surface values?\n\nIf not and it is a distinct surface - can you document it at OSM Wiki?\n\nSee https://overpass-turbo.eu/s/1CM3 to detect more unusual surface values (move to your preferred map location and press run button)",
        },
        {
            'key': 'surface',
            'value': "Gras_Laub",
            'tag_specific_comment': "Should it be surface=grass ? Is it safe to blindly replace in bot edit or is it requiring better review? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dgrass",
        },
        {
            'key': 'surface',
            'value': "comp",
            'tag_specific_comment': "Should it be surface=compacted ? Is it safe to blindly replace in bot edit or is it requiring better review? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dcompacted",
        },
        {
            'key': 'surface',
            'value': "bark",
            'tag_specific_comment': "I expect it to be woodchips made out of bark. Maybe it should be tagged " + key + "=woodchips, see https://wiki.openstreetmap.org/wiki/Tag:surface%3Dwoodchips\n\n(with optional woodchips=bark)\n\nmaybe if surface=bark is valid and should not be changed to surface=woodchips - consider posting about it on tagging mailing list, https://community.openstreetmap.org/ and/or editing that wiki page",
        },
        {
            'key': 'surface',
            'value': "champs,_herbe",
            'tag_specific_comment': "what is the actual situation here?\n\nIs it where grass is cultivated?",
        },
#        {
#            'key': 'surface',
#            'value': "aaaaaaaaaa",
#            'tag_specific_comment': "",
#        },
        {
            'key': 'surface',
            'value': 'green',
            'tag_specific_comment': 'What surface=green means? Is maybe surface=grass correct here? See https://wiki.openstreetmap.org/wiki/Tag:surface=grass\n\nOr maybe surface=artificial_turf ? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dartificial_turf',
        },
        {
            'key': 'surface',
            'value': 'graveled',
            'tag_specific_comment': 'surface = graveled looks like a typo. It seems that it should be surface = gravel\n\nBut I was not sure enough to make a remote replacement. Is it safe to change it?',
        },
        {
            'key': "surface:pt",
            'tag_specific_comment': "is surface:pt really wanted or a good idea? It seems a pointless duplication of surface tag to me - in which case surface:pt would be useful and wanted? Note that editors may have support for translating/presenting tag value in local language.\n\nSee https://overpass-turbo.eu/s/1lAT",
        },
        {
            'key': 'surface:note',
            'value': 'cemento',
            'tag_specific_comment': 'surface:note=cemento ? Is it simply surface=concrete? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dconcrete',
        },
        {
            'key': 'surface:note',
            'value': 'sandy',
            'tag_specific_comment': 'surface:note=sandy ? Is it simply surface=sand? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dsand',
        },
        {
            'key': 'surface:note',
            'value': 'Sandweg',
            'tag_specific_comment': 'surface:note=Sandweg ? Is it simply surface=sand? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dsand',
        },
        {
            'key': 'surface:note',
            'value': 'compacted gravel',
            'tag_specific_comment': 'surface:note=compacted gravel ? Is it simply surface=compacted? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Dcompacted',
        },
        {
            'key': 'surface:note',
            'value': 'not sure if asphalt',
            'tag_specific_comment': 'surface:note=not sure if asphalt\n\nIs it surface=asphalt? If unsure - can you attach a photo?',
        },
        {
            'key': 'surface:note',
            'value': 'Trampelpfad',
            'tag_specific_comment': 'surface:note=Trampelpfad ? Is it simply surface=dirt? See https://wiki.openstreetmap.org/wiki/Tag:surface%3Ddirt\n\nWould surface=dirt replace it fully?',
        },
        {
            'key': 'surface:note',
            'value': 'Holzstufen',
            'tag_specific_comment': 'surface:note=Holzstufen ? Maybe surface=wood on highway=steps would be better?\n\nOr highway=steps + material=wood + surface=dirt (or gravel or something else) if steps are built from wood, but surface between them is dirt or similar.',
        },
        {
            'key': 'surface:note',
            'value': 'Kies',
            'tag_specific_comment': 'surface:note=Kies\n\nIs it surface=gravel? Or surface=pebblestone? Or something else?\n\nSee https://community.openstreetmap.org/t/surface-kies-is-it-surface-gravel/102927/2',
        },
        {
            'key': 'surface:note',
            'value': 'kies',
            'tag_specific_comment': 'surface:note=Kies\n\nIs it surface=gravel? Or surface=pebblestone? Or something else?\n\nSee https://community.openstreetmap.org/t/surface-kies-is-it-surface-gravel/102927/2',
        },
        {
            'key': 'operator',
            'value': 'n/a',
            'tag_specific_comment': 'operator=n/a ? is it an attempt to tag that operator is not applicable or unknown or missing?\n\nEither way, operator=n/a is wrong unless operator is actually named "n/a"',
        },
        {
            'key': 'website',
            'value': 'n/a',
            'tag_specific_comment': 'website=n/a ? is it an attempt to tag that website is not applicable or unknown or missing?\n\nEither way, website=n/a is wrong as there is no such website',
        },
        {
            'key': 'addr:city',
            'value': 'n/a',
            'tag_specific_comment': 'Why you added this tag? If address has no associated city, just do not add addr:city\n\naddr:city=n/a means that that this address in a city called "n/a" which does not apply here, right?',
        },
        {
            'key': 'addr:housenumber',
            'value': 'b/n',
            'tag_specific_comment': 'czy chodzi tutaj że numeru domu tutaj nie ma? To lepiej nie dodawać wcale, addr:housenumber=b/n raczek powinien być skasowany\n\nChyba że coś przegapiłem?', #'b/n expands to "bez numeru", which means "without number", so far every case is a bad inport in Poland',
        },
        {
            'key': 'addr:housenumber',
            'value': 'House',
            'tag_specific_comment': 'info that something is built as house goes to building=house, not into address field. Please, help with this cleanup. See https://overpass-turbo.eu/s/24J2 for more objects with this problem',
        },
        {
            'key': 'addr:housenumber',
            'value': 'house',
            'tag_specific_comment': 'info that something is built as house goes to building=house, not into address field. Please, help with this cleanup',
        },
        {
            'key': 'addr:housename',
            'value': 'House',
            'tag_specific_comment': 'info that something is built as house goes to building=house, not into address field. Please, help with this cleanup',
        },
        {
            'key': 'addr:housename',
            'value': 'house',
            'tag_specific_comment': 'info that something is built as house goes to building=house, not into address field. Please, help with this cleanup',
        },
        {
            'key': 'addr:flats',
            'value': 'House',
            'tag_specific_comment': 'info that something is built as house goes to building=house, not into address field. Please, help with this cleanup',
        },
        {
            'key': 'addr:flats',
            'value': 'house',
            'tag_specific_comment': 'info that something is built as house goes to building=house, not into address field. Please, help with this cleanup',
        },
        {
            'key': 'maxspeed:source',
            'value': 'sign',
            'tag_specific_comment': 'is it intentionally used instead of source:maxspeed=sign ? See https://wiki.openstreetmap.org/wiki/Tag%3Asource%3Amaxspeed%3Dsign\n\nmaxspeed:type is also sometimes used as a key for such data, see https://wiki.openstreetmap.org/wiki/Key:maxspeed:type',
        },
        {
            'key': 'maxspeed:source',
            'value': 'DE:urban',
            'tag_specific_comment': 'is maxspeed:source intentionally used instead of source:maxspeed ? See https://wiki.openstreetmap.org/wiki/Key:source:maxspeed\n\nmaxspeed:type is also sometimes used as a key for such data, see https://wiki.openstreetmap.org/wiki/Key:maxspeed:type',
        },
        {
            'key': 'maxspeed:source',
            'value': 'DE:rural',
            'tag_specific_comment': 'is maxspeed:source intentionally used instead of source:maxspeed ? See https://wiki.openstreetmap.org/wiki/Key:source:maxspeed\n\nmaxspeed:type is also sometimes used as a key for such data, see https://wiki.openstreetmap.org/wiki/Key:maxspeed:type',
        },
        {
            'key': 'maxspeed:source',
            'value': 'PL:urban',
            'tag_specific_comment': 'is maxspeed:source intentionally used instead of source:maxspeed ? See https://wiki.openstreetmap.org/wiki/Key:source:maxspeed\n\nmaxspeed:type is also sometimes used as a key for such data, see https://wiki.openstreetmap.org/wiki/Key:maxspeed:type',
        },
        {
            'key': 'maxspeed:source',
            'value': 'PL:rural',
            'tag_specific_comment': 'is maxspeed:source intentionally used instead of source:maxspeed ? See https://wiki.openstreetmap.org/wiki/Key:source:maxspeed\n\nmaxspeed:type is also sometimes used as a key for such data, see https://wiki.openstreetmap.org/wiki/Key:maxspeed:type',
        },
        {
            'key': 'maxspeed:source',
            'value': 'FR:urban',
            'tag_specific_comment': 'is maxspeed:source intentionally used instead of source:maxspeed ? See https://wiki.openstreetmap.org/wiki/Key:source:maxspeed\n\nmaxspeed:type is also sometimes used as a key for such data, see https://wiki.openstreetmap.org/wiki/Key:maxspeed:type',
        },
        {
            'key': 'maxspeed:source',
            'value': 'FR:rural',
            'tag_specific_comment': 'is maxspeed:source intentionally used instead of source:maxspeed ? See https://wiki.openstreetmap.org/wiki/Key:source:maxspeed\n\nmaxspeed:type is also sometimes used as a key for such data, see https://wiki.openstreetmap.org/wiki/Key:maxspeed:type',
        },
        {
            'key': 'maxspeed:source',
            'value': 'CZ:urban',
            'tag_specific_comment': 'is maxspeed:source intentionally used instead of source:maxspeed ? See https://wiki.openstreetmap.org/wiki/Key:source:maxspeed\n\nmaxspeed:type is also sometimes used as a key for such data, see https://wiki.openstreetmap.org/wiki/Key:maxspeed:type',
        },
        {
            'key': 'maxspeed:source',
            'value': 'CZ:rural',
            'tag_specific_comment': 'is maxspeed:source intentionally used instead of source:maxspeed ? See https://wiki.openstreetmap.org/wiki/Key:source:maxspeed\n\nmaxspeed:type is also sometimes used as a key for such data, see https://wiki.openstreetmap.org/wiki/Key:maxspeed:type',
        },
        {
            'key': 'maxspeed:source',
            'value': 'CH:urban',
            'tag_specific_comment': 'is maxspeed:source intentionally used instead of source:maxspeed ? See https://wiki.openstreetmap.org/wiki/Key:source:maxspeed\n\nmaxspeed:type is also sometimes used as a key for such data, see https://wiki.openstreetmap.org/wiki/Key:maxspeed:type',
        },
        {
            'key': 'maxspeed:source',
            'value': 'CH:rural',
            'tag_specific_comment': 'is maxspeed:source intentionally used instead of source:maxspeed ? See https://wiki.openstreetmap.org/wiki/Key:source:maxspeed\n\nmaxspeed:type is also sometimes used as a key for such data, see https://wiki.openstreetmap.org/wiki/Key:maxspeed:type',
        },
        {
            'key': 'bicycle_parking',
            'value': 'stand',
            'tag_specific_comment': 'bicycle_parking=stands was probably intended here, right? See https://wiki.openstreetmap.org/wiki/Key:bicycle_parking\n\nnote that if we have a single stand it is still bicycle_parking=stands',
        },
        {
            'key': 'bicycle_parking',
            'value': 'high_capacity',
            'tag_specific_comment': 'what bicycle_parking=high_capacity means? See https://wiki.openstreetmap.org/wiki/Key:bicycle_parking - is this parking matching any value described there?',
        },
        {
            'key': 'bicycle_parking',
            'value': 'v',
            'tag_specific_comment': 'what bicycle_parking=v means? See https://wiki.openstreetmap.org/wiki/Key:bicycle_parking - is this parking matching any value described there?',
        },
        {
            'key': 'bicycle_parking',
            'value': 'arceaux',
            'tag_specific_comment': 'what bicycle_parking=arceaux means? See https://wiki.openstreetmap.org/wiki/Key:bicycle_parking - is this parking matching any value described there?',
        },
        {
            'key': 'bicycle_parking',
            'value': 'Bügel',
            'tag_specific_comment': 'what bicycle_parking=Bügel means? See https://wiki.openstreetmap.org/wiki/Key:bicycle_parking - is this parking matching any value described there?',
        },
        {
            'key': 'bicycle_parking',
            'value': 'use_sidepath',
            'tag_specific_comment': 'what bicycle_parking=use_sidepath means?\n\nIs it maybe supposed to be bicycle=use_sidepath?\n\nIf it is bicycle parking... See https://wiki.openstreetmap.org/wiki/Key:bicycle_parking - is this parking matching any value described there?',
        },
        {
            'key': 'bicycle:repair',
            'tag_specific_comment': 'service:bicycle:repair is much more common way of expressing the same info as one from bicycle:repair key. Would you be fine with changing this tagging to a more popular version?\n\nI think that in this case difference in key names are minimal, and benefit from easier use of data would be greater\n\nSee https://wiki.openstreetmap.org/wiki/Key:bicycle:repair and https://wiki.openstreetmap.org/wiki/Key:service:bicycle:repair',
        },
        {
            'key': 'bicycle:sales',
            'tag_specific_comment': 'service:bicycle:retail',
            'tag_specific_comment': 'service:bicycle:retail is much more common way of expressing the same info as one from bicycle:sales key. Would you be fine with changing this tagging to a more popular version?\n\nI think that in this case difference in key names are minimal, and benefit from easier use of data would be greater\n\nSee https://wiki.openstreetmap.org/wiki/Key:bicycle:sales and https://wiki.openstreetmap.org/wiki/Key:service:bicycle:retail',
        },
    ]
    returned += unexpected_number_valued_data_from_taginfo(specified_cache_folder)
    returned += unexpectedly_long_tags_from_taginfo(specified_cache_folder)
    return returned

def caching_time():
    day_in_seconds = 60 * 60 * 24
    return 30 * day_in_seconds

def cached_taginfo_for_what_id_project_uses(cache_location):
    @simple_cache.cache_it(filename=cache_location + "taginfo_for_what_id_project_uses_for_dubious_tags_library.cache", ttl=caching_time())
    def cached():
        print('taginfo_for_what_id_project_uses - fetching from taginfo')
        project = "id_editor"
        returned = []
        for entry in taginfo.query.tagging_used_by_project(project):
            returned.append(entry)
        return returned
    return cached()

# cached to avoid hitting taginfo and to avoid drudgery of handling tags
# that keep appearing and disappearing
def short_keys_from_taginfo_cached_list(cache_location):
    @simple_cache.cache_it(filename=cache_location + "taginfo_for_short_keys_for_dubious_tags_library.cache", ttl=caching_time())
    def cached():
        print('taginfo_for_short_keys_for_dubious_tags_library - fetching from taginfo')
        returned_key_list = []
        for entry in taginfo.query.get_short_key_info():
            if entry['count_all'] == 0:
                continue # has wiki pages and no uses
            if entry['key'].lower() in [ # smarter message may be needed
                's', # source/surface?
                'n', "na", # name? Has dedicated entry in that list
                'b', # building?
                'cd', # got reply on that topic
                'it', # not completely weird
                'to', # https://taginfo.openstreetmap.org/keys/to#overview
                'ip', # https://wiki.openstreetmap.org/wiki/Key%3Aip - still a bad idea (TODO: have a dedicated entry)
                'pk', # https://wiki.openstreetmap.org/wiki/Key%3Apk - has a known meaning
                'ev', # electric vehicle access, no clear tagging for that yet, see https://wiki.openstreetmap.org/wiki/Key:access
                '3d', # seems to be in use to link 3d model
                'km', # used for distance based addressing/markings (see also addr:milestone)
                'pk', # https://www.openstreetmap.org/changeset/148062106
                'tc', # https://wiki.openstreetmap.org/wiki/Key:tc
            ]:
                continue
            if len(entry['key']) > 2:
                if entry.get('in_wiki') == True:
                    # skip ref and similar
                    continue
                #print(entry['key'], "is not super small - exiting")
                break
            returned_key_list.append(entry['key'])
        return returned_key_list
    return cached()

# cached to avoid hitting taginfo and to avoid drudgery of handling tags
# that keep appearing and disappearing
def unexpected_number_valued_data_from_taginfo(cache_location):
    cache = cache_location + "unexpected_number_valued_data_from_taginfo.cache"
    @simple_cache.cache_it(cache, ttl=caching_time())
    def cached():
        print("unexpected_number_valued_data_from_taginfo - fetching from taginfo, cache was set to", cache)
        returned = []
        for key in tag_knowledge.typical_main_keys() + ["roof:type", "roof_shape", "roof"]:
            for taginfo_entry in taginfo.query.values_of_key_with_data(key):
                if taginfo_entry['value'].replace('.','',1).isdigit():
                    returned.append({
                            'key': key,
                            'value': taginfo_entry['value'],
                            'tag_specific_comment': 'What this tag means? Numeric value is unexpected here and it is unclear what it means',
                        })
        return returned
    return cached()

# cached to avoid hitting taginfo and to avoid drudgery of handling tags
# that keep appearing and disappearing
def unexpectedly_long_tags_from_taginfo(cache_location):
    @simple_cache.cache_it(cache_location + "unexpectedly_long_tags_from_taginfo_v6.cache", ttl=caching_time())
    def cached():
        print('unexpectedly_long_tags_from_taginfo - fetching from taginfo')
        returned = []
        for key in ['maxheight', 'maxweight']:
            for taginfo_entry in taginfo.query.values_of_key_with_data(key):
                if '@' in taginfo_entry['value']:
                    # conditional restrictions are not supposed to go here, but...
                    continue
                if len(taginfo_entry['value']) > 30: # TODO maybe shorter are also bad?
                    # maxweight=14.5 t
                    # maxweight=88000 lbs
                    # maxweight=10000lbs
                    # maxweight=70 lbs/person
                    # maxweight=11000 Pounds
                    # maybe not exactly correct but should get different error message
                    # maxweight=5,000 lbs vehicle load limit
                    returned.append({
                            'key': key,
                            'value': taginfo_entry['value'],
                            'tag_specific_comment': 'this value is unexpectedly long - is it really correct?',
                        })
                elif "." in taginfo_entry['value']:
                    # maxheight=9.25 feet
                    after_dot = taginfo_entry['value'].split('.')[-1]
                    if len(after_dot) >= 4 and after_dot.isdigit():
                        returned.append({
                                'key': key,
                                'value': taginfo_entry['value'],
                                'tag_specific_comment': 'this value is unexpectedly long and detailed - is it really correct?',
                            })
        return returned
    return cached()


def short_suspect_values(cache_location):
    short_manually_listed_dubious_ones = [
        "2.5",
        "---",
    ]
    for entry in short_manually_listed_dubious_ones:
        yield entry
    for key in short_keys_from_taginfo_cached_list(cache_location):
        if key in short_manually_listed_dubious_ones:
            continue
        yield key
