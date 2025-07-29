def unclear_shop_values():
    # thre is .split("\n") at the function end
    return """
Mpesa
Moda
noleggio bus
Toko_Perlengkapan_Rumah
atelier couture
limpieza general
Distributor
Counter HP
Chiropodist
Sport Chek
Toko_Alat_Tulis_Kantor
Barer
Holzhandlung
Call shop
Kalinag Furniture and Kath Udhyog
Distributor Minuman dan Makana
Polirubro
Waren_und_Wohnkultur_aus_fernen_Ländern
cosmetics et vetements
Merceria
Hilos_e_hilazas
Fruver
home glory
fours et panneaux solaires
MERCADO MUNICIPAL
Reinigung
Pulidor de Metales
Venda_de_artigos_de_casa
sound image
SALA_DE_ESTUDO
FERRETERIA,_ABARROTERIA_Y_VENTA_DE_ROPA
Shag Shop
Centro Comercial
Sisfo
9848879110,9851141983
زريبة_فحم
万犬吠
décoration_événementielle
είδη_γάμου_-_βάπτισης
محل تبغ
yapı_malzemeleri
aquarium1
販売店
είδη_συσκευασίας,_πλαστικά_κλπ
Blumen_und_Gemüse
γκραβούρες
Aesthetic_Bar_&_Spa_Retreat', "station d'essence", 'rações
كهرباء
သငကနဆင
Интегро
استیل
Artículos_desechables
пчеларски
9851058590
bdivers (femme anango)
mariscos_vivos_e_congelados
siding
rarity
thiruvananthapuram
ascensores
productos_de_limpieza
luminary
tissus
english
reparacion de muebles
lechon_manok
cajero
kiranam_shop
local_shops
talabarteria
tienda_que_en_realidad_es_un_bar
moda
consultant
produits_artisanaux_du_nepal_et_d'inde
avondwinkel
undef
AURA
chennapara
loja_de_malas
tabacchi edicola
شهید‌ رضا‌ خدارحمی
ČÚZK
batik
de_barrio
Remodelação_de_interiores
armature
tteok
zwembag
piojos y liendres
jajee
baja
clima
tatami
conv
assorted
emas
comercial
пиццерия
colmado
teppanyaki_grillgeräte
microenterprise
Yemci
CEVP
Строительный магазин
bulcanisadora
technically
automatically
aggregates
chaveiro
assicurance
cartoleria
nudle
alimentari
ourivesaria
platrerie
byggvaruhandel
negozio_di_abbigliamento_per_neonati_e_bambini
scooptram
viewpoint
kerala_vision
stores
local_market
pasta_fresca
refrescos
fornitore_di_uova
traktorverleih
byke
amenity
facials
maveli_store
container
mixed
selhoz_parts
granete
cancha_de_tejo
punto_vendita
lyrics
herboristery
expo
alat_rumah_tangga
hkb77
detached
residential
agropecuaria
agropecuario
meubelstofferen
hopfen
pyres
marquetry
carne_pui
maquillaje_y_accesorios
flohmarkt
gbodour
sundries
designer
som_automotivo
cacharreria
magazin_alimentar
canchas_de_tejo
family_plastics
funreal
registry
kirana_store
piensos y abonos
tienda_de_cuadros_y_canceleria_de_aluminio
comida_para_animales
شهرک صنعتی کارا
2024-03-30
meuble
freight fowarding
pneumatic
copystery
wholesenate
complementary_health
utilidades
edelsteine
worshop
poulterer
chef
kawara
wagasgi
cacha
produits_derives
ve
joogakauppa
reciclados
chatpat
helados
convite
limon
maxcolchon
lavomatic
dieselvarmere_og_varmepumper
joieria
無人販売
vacantΤο ποδόσφαιρο φτιάχνεται από κάτω προς τα πάνω όχι έτσι γνώμη μου
زجاج سيارات
vacantauth.defense.gouv.frauth.defense.gouv.fr
Acadèmia Valenciana de la Llengua
desconhecido
Nachtwinkel
Fliesenausstellung
colchones
arreglo_ropa
frutas
aceros_aluminios_y_vidrios
Agence immobilière
Kaminholz
location_of_stuff
de_todo
hosiery
membership
glocery
multi_tienda
tienda_rural
articulos_de_la_canasta_familiar
sony studio de beaute
hoses
bois
tecido
design_e_publicidade
P2P
orange_money
artkraft
tamales
herrajes
dry_shop
sartoria
electrodomésticos
quincaillerie
metaphysical_shop
alimentation_animale
audicien
giornali_tabacchi_libri
Dishes
contabilidade
airway
pintura
pariuri_sportive
etc_shop
store vintage
kiryana_store
colourman""".split("\n") + [
        'bijoux', # jewelry? verify TODO
        'bijouterie', # jewelry? verify TODO
        'patisserie', # pastry? verify TODO
        "point_of_sale", # https://www.openstreetmap.org/changeset/129236580 this import added almost all of them, see https://taginfo.openstreetmap.org/tags/shop=point_of_sale
        'salvage', 'dishes', 'sells disks', 'motor_show', 'earthworks', 'naturopath', 'fairy_lights', 'power_billing',
        'leisure_club', 'magazin', 'emergency', 'solar_energy_comapany', 'agent', 'assurance',
        'お土産', 'ambulance', 'seal', 'media', 'business_center', 'auctioneers', 'Kios', 'jogos', 'paraphenalia_palace',
        'bamboo', 'contractor', 'installation', 'ladies_store', 'chinaware', 'tent', 'saw',
        'New Enrich Place', 'multimedia', 'Network_-_Marketing', 'sun_protection,_Sonnenschutz', 'wash', 'dragstore',
        'industry', 'gate', 'typography', 'feed', 'canal', 'servis', 'mobile-store', 'garageservices',
        'elderly', 'audio', 'Njane metal cracking and welding', 'cookshop',
        'technical', 'armorariaspot_market', 'export', 'community mart', 'labor', 'Meubelhuis Comfort',
        'armoraria', 'spot_market', 'natural', 'wet_market', 'accessory', 'najari_va_naghshi_choob', 'provisions',
        'tienda_de_accesorios_para_automoviles_y_papel_ahumado', 'architectural layout',
        'driveway', 'coolbar', 'comar', 'everything', 'varies', 'publicist', 'laser', 'local market', 'farmland',
        'playground', 'sun_shade', 'supermercado_veredal', 'minimercado', 'alles', 'ag_eqpt_repair', 'venta_de_pollo',
        'venta_de_frutas_verduras_y_carne', 'diskont', 'aiguisage', 'maill', 'mosthaus', 'chucherias',
        'multitienda', 'national_trust', 'supplies', 'manege', 'date', 'cell', 'homecenter',
        'small_shop', 'small_store', 'african', 'green market', 'papeleria', 'millinery', 'conservatories',
        'pilot', 'forestry', 'asesoria', 'loja_de_surf', 'vaporizor_store', 'venta_de_instrumentos_electronicos',
        'cartonage', 'ebonist', 'center', 'coutellerie', 'krippenbau', 'mini-barns', 'alimentos_para_animales',
        'all_sal_shop', 'stock', 'dedetizadora', 'piensos', 'entrance', 'varghese', 'kitajci', 'testing_centre',
        'delicatessent', 'trading_post', 'samoobsluha', 'nanma_store', 'bodega', 'targo',
        'bebidas', 'distribution', 'mix_tovar', 'vignette', 'kmetijska_zadruga', 'werksverkauf', 'small wares',
        'kiln', 'fioul', 'materials_handling', 'ground', 'quilter', 'maybe', 'fairy', 'dismond', 'spring', 'bric_a_brac',
        'academia', 'various', 'economic', 'Airtime', 'specialized', 'lifestyle', 'taxi',
        'Watercolor Workout', 'Regalvermietung', 'Miscelanea Chavez', 'Maquilhagem,_Loja_feminina', 'Nhung Style', 'Buvette',
        'Building Society', 'Mini co-op city', 'Transmission Shop', 'Alimentación', 'Resturent',
        'Feuerwehr-,_Rettungsdienst-_und_Brandschutzbedarf', 'El_Pinero', 'Safilo', 'Various', 'Venta_de_juegos_de_mesa',
        'Bengkel_dan_Jual_Suku_Cadang_Motor', 'pepiniere', 'doping', 'Presentes_personalizados', 'Alat_Rumah_Tangga',
        'Arte_y_Ocio', 'Pap Electronic', 'Banco_del_Barrio_de_Guayaquil', 'Water Station', 'CPC', 'Agro_Insumos',
        'Table market', 'Shopping_Complex_Building', 'Sellos_de_Hule', 'Achat_de_bouteille_de_vin', 'Product_Marker',
        'Regionales', 'Artes_e_Oficinas', 'Composite Panel Head', 'Madina shopping centre', "women's accessories",
        'Kaffee und Kurse', 'Olshop', 'Local Shop', 'Agencias de cobranza', 'COMERCIAL', 'Feira', 'Loja_Desporto',
        'Toko_Makanan_Laut_Kering', 'Especializada', 'น้ำดื่มเย็นเย็น', 'Makochi', 'Mountain Warehouse', 'Tienda_electronica',
        'Savonnerie', 'စတိတ်ခုံငှား', 'Tau sports', 'Loja_de_Decoração', 'Loja_de_Importados', 'MDI', 'Green_Energy',
        'Tienda_de_lanas', 'Mix', 'Puja Samagri Pasal', 'Brand', 'Crema VET', 'General Contractor', 'Al Kifaf',
        'COMMERCIAL', 'Shadman', 'Importadora', 'Malharia', 'Pashmina', 'Toko Kanaan', 'Akis Express',
        'Mafagio shop', 'Taller', 'Rajput Sweet', 'equipo Neumatico servicio', 'Assistenza_Caldaie', 'Ammus bakery',
        'Teures Billig', 'Niagara Swalayan', 'IZASKUN', 'Company_Store_-_entree:_On_Invitation', 'Bing',
        'Puutavaraliike', 'Tienda_de_Manualidades', 'Super Wawa', 'Vinee_Ash', 'http://www.lesgourmets.es', 'Bata',
        'Esabi', 'www.facebook.com/vlxdtamthao', 'Toserba', 'VLXD', 'Magasin de carreaux', 'Asesoria', 'Spur', 'UHPA',
        'মেসার্স_মৃদুলা_ট্রেডার্স', 'OGIA, PAN', 'Santary', 'Mount Plymouth IGA', 'BOLT Manufacture', 'ASCI',
        'Revistas,_panaderia,_quiosco', 'Charcuterie', 'Ncell Recharge', 'Loja_de_Material_de_Pesca', 'Menuiserie',
        'Repuestos,_accesorios_para_maquina_de_coser,_Hilos_e_hilazas', 'Impianti_idraulici_e_termoidraulici', 'Menaje', 'Local',
        'Pyoke_Par_Store', 'Parador', 'Drucksachen, Stempel, Telekommunikation, Hardware, Software',
        'Mini_Mercado_-_Drogaria_-_Racoes', 'Auto puncture', 'Decorders', 'Empresa_de_Topografia', 'Accessoires_de_mode',
        'Gas America', 'FC Porto Store', 'Heltonville Store', 'Taller_Suzuki', 'Magasin de vente',
        'Venta_de_Viveres', 'Salon', 'Ware_House', 'Despensa', 'Cookery', 'Fechada', 'Solar Center', 'Moteles', 'Cubrelechos',
        'Private', 'Hilos_E_Hilazas', 'Herrajes_y_cremalleras', 'IQOS Store', 'Jarceria', 'Mutualiteit', 'Horneburger Zaunbau',
        'Defence Shopping Center', 'Gerz', 'Afroshop', 'Grill', 'Marqueteria los alamos', 'FAROVON',
        'OTOP_-_One_Tambon_One_Product', 'Tienda_de_Embutidos', 'Repuesto_de_Vehiculos', 'CIAST', 'Aakkrikkada',
        'tienda_de_comida', 'temporal', 'varie', 'housebuilding', 'cool_bar', 'fresh_market', 'discs', 'fancy_store',
        "tankshop", 'minisuper', 'disk', 'leisure', 'removals', 'property', 'bio', 'used', 'implement', 'öl',
        'Tamirhane', 'Consorzio_Agrario', 'Ballmill_maker', 'Kasiglahan Market', 'Materias_Primas', 'Bar de boisson', 'Deco_Lar',
        'Mercado', 'ZBGIS', 'Hilos', 'CBD', 'Piscinas', 'Agencia Seguros', 'Tecnologia', 'GMA', 'ICA', 'Hen', 'Konyaku Donya',
        'Retrosaria_haberdashery', 'Peracion motos', 'Agencias de anuncios publicitarios', 'Mitumba', 'Korbwaren', 'CBG',
        'South Tapanuli, North Sumatra, Indonesia', 'Peritaciones', 'glacier_-_terroir_-_décoration', 'Benodigdheden_Hengelsport',
        'Steamship_Agents', 'Multiprecio', 'Almacen', 'Impresiones', 'Tertiary', 'DNEC', 'Alfaiate', 'Andaimes_e_Escoramentos',
        'comida_Animales', 'Pijama', 'Chostic shop', 'Manilal Marga', 'Coffee Project', 'Tienda_TRD', 'Kopkun', 'Kontor', 'MAIZ',
        'Servicio_Tecnico_y_ventas_de_accesorios_para_celulares', 'Electrica', 'Digicel', 'Casa de Bordados', 'Ropa',
        'TRUONG MAM NON DOI LAU', 'Pulpería', 'Vazia', 'Drogaria', 'Verduras', 'Pan_pasteles', 'Tienda informatica',
        'Nourriture_pour_animaux', 'Ladies Store', 'Pangar', 'Keels Super', 'Oxxo',
        'Vivero', 'Venda_de_GLP', 'Mkaa', 'Aadarsha Krisi Samagri Bhandari', 'Tent_House', 'El Rayo cafeteria', 'Merch On Demand',
        'Aswathy Traders', 'Inmobiliaria', 'Venda_de_carros_usados', 'DJ', 'Countertops', 'Small_shop', 'Pusat_Perbelanjaan',
        'key', 'culture', 'shophouses', 'technology', 'trader', 'eco', 'off', 'Libre', 'junk', 'auto', 
        'whirlpool', 'deco', 'equitation', 'multi', 'frozen', 'satelite', 'airtime', 'records', 'gestoria', 
        'scuola', 'Maquinas_de_coser', 'Ultramarinos', 'minoterie', 'viveres', 'place', 'lambering',
        'Loja', 'autoescuela', 'têxteis', "mkaa", 'buil', 'duka', 'Sanitär', 'matres', 'σφραγίδες', '印',
        'schulmöbel', 'mobil', 'Distribuidora', 'naturista', 'volailles', 'Panaderia',
        'Minimercado', 'Toko_Ponsel', 'Armarinho', 'pasar', 'Desechables', 'svapo', 'λευκά_είδη', 'tchotchke',
        'loja_de_acessórios', 'Saloon', 'traiteur', 'isp', 'Tienda', 'Sonstige', 'mercerie', '觀光旅遊', '手作坊', 'tienda',
        'estanco', 'maroquinerie', 'Otros consultorios del sector privado para el cuidado de la salud', 'ASISTENCIA_AL_VIAJERO',
        'Hilos_e_Hilazas', 'Otros servicios de apoyo a los negocios', 'Diseño gráfico', 'colour', '民俗表演', '其他農產',
        'loja_de_calçados', 'Butique_de_Balões', 'candy (حلويات)', '豆腐店', 'WERBUNG + car',
        'Embarcation,_articles_de_pêche_et_loisir', 'Piața de gros Antrefrig',
        '娯楽施設', 'استنلس_استیل', 'یدکی ماشین', 'Confección_y_venta_de_cubrelechos',
        '蜂蜜直売店', 'agropécuaria', 'εκκλησιαστικές_εικόνες', 'venta_de_guayas,_guadañas', 'fromages, beurre ...',
        '不動産', '不動產', '988799611,9861227450', 'ハム・ソーセージ', 'စတတခင',
        'ημιπολύτιμοι_λίθοι', 'الخيمة_للخضار_والفواكة', 'roupa,_acessórios,_chinês', 'سوق_الكهربا', '印刷店', 'fútbol', 'leña',
        'Geschäft_für_Heimtierbedarf,_Tankstelle', 'gráfica,_Estamparia_e_Personalizados',
        'fenêtres;volets;vérandas;stores;portes;ossatures_métalliques', 'یراق', 'Pott_Belly_Stoves_&_Stove_Supplies',
        'lan_house_e_assistência_técnica', 'Home_Decor_&_Emroidery', 'Loja_de_Decoração''Pulpería',
        'Tienda_de_artículos_de_fontanería', 'Θέρμανση', 'Vente de matériel frigorifiques', '弱電', 'ιερατικά_είδη',
        'Solar D. Marinez', '+38(04572)30147', 'www.evansonthecommon.com', 'Campers & Caravans',
        'интернет_магазин', 'شیرآلات', 'ماشین های اداری', 'şok market', "Magasin d'instruments agricoles",
        'cmm._centre', 'детские_товары', '반찬가게', '天燈,_紀念品,_民宿', 'camera tripods & bags',
        '牛乳店', 'LOCAÇÃO_DE_EQUIPAMENTOS PARA EVENTOS', 'Doña Alcira', '補習班', 'decoração_e_bricolage', 'эсо_маркет',
        'Производственная_коммерческая_фирма', 'Aide_à_la_personne', 'غذائيات', 'wasserbetten,_feinkost_und_mehr...',
        'reparações_e_alugueres', "men's", 'artesanías', 'اقمشة و شراشف', 'Função_desconhecida',
        'মসরস_মদল_টরডরস', "john's village market", 'متجر كهربائي', 'toldos,_rótulos', '瓦斯行', 'сільмаг', '禮儀用品店',
        'مصالح_فروشی_و_درب_و_پنجره_سازی', 'taller confección', 'バッグ', 'Arte_Indígena', 'Lolo Automóveis', '9741836325',
        'وكالة سيارات', "chemist's-sundries", 'پوشاک', '楽市街道 箱崎店', 'حمام للرجال', '雜糧行',
        'Espumas,_Siliconados,_Muñqueria...', 'متجر_بيع_أبواب_داخلي_و_خارجي', 'محل بخ حشرات', 'cooperativa_agrícola',
        'Tienda_hípica', 'буд._матеріали', 'Bait & Tackle', 'Trade (Betis House of Decor)', 'gewächshaus-_&_treibhaustechnik',
        'Ведомствена книжарница', 'Архітекрута і будівництво', 'pisciniste,_aménagement_piscine,',
        'regalos_y_alimentación', 'Card_Machines_&_Accessories', 'colchões', '문구점', 'Produtos_Agropecuários',
        'Μαρμελάδες,_Σαπούνια,_χειροποίητα_προϊόντα', 'Жастар', 'telefon_dükkanı', 'droguería', 'حر ۵۱', 'حر ۵۳',
        'fiscalía', 'نقل وتحميل', 'produtos_esotéricos', 'Wein,_Spirituosen,_Gewürze,_Tee,_Floristik',
        'miešaný_tovar', 'EST 85', 'massage + acupressure', 'coiffure à domicile', "RETNA'S ENTERPRISE",
        'ζωοτροφες', 'Sec D Ph 1', 'Cheese_&_Yogurt', 'Pièce détachée pour moto', "D'Cardos Mechanical Auto Repair",
        'Chalulani Departmental Store', 'Popcorns', 'Γεωργικά_προϊόντα,_Λιπάσματα_-_Agricultural_products,_fertilizers',
        'Platsak Depot', 'CSD Shop', 'Maquina_de_coser', 'Hartford Denim Company', 'lifestyle,_Porzellan,_Geschenke,_Workshops',
        'Digicel Fiji Ltd', 'Schmuck Uhren', 'TIENDA', 'NP Fuel Station', 'Animal Salt', 'Deposito Dental', 'Bistro',
        'Moda_praia_e_ginática', 'miscelánea', 'Ballet_&_Dancewear', '60', 'loja_chinesa_de_artigos_vários',
        '便利商店', 'محمصة العنازة', 'ذهب مجوهرات', 'متجر العاب', "rider's hub", "boutique_d'art_et_d'artisanat",
        'Mega auto', 'no Working Toilet', 'Shoukat Plaza', 'RAJA MULTIPURPOSE SHOP', 'Plaza de mercado San Benito',
        'chauffe eau solaires', 'Farines_et_produits_agricoles', 'Tissus', 'Estanco', 'Drogueria', 'Staetimes Authorised Dealer',
        'Loja_de_variedades', 'Old_Shop', 'Pelze', 'Kawasaki', 'SUBJECT', 'Equipos_Industriales_de Guatemala',
        'Magazin online de produse naturiste', 'B2B', 'Pan', 'Camp Walden', 'Loja_de_motas', 'gate manufacturing',
        'Cellullar', 'TCM', 'ricambi elettrodomestici', 'Cargo_Services', 'vente de planche',
        'food and retrail', 'Anthem Board Shop', 'no other goods', 'Signs', 'Xtream', 'Agua Purificada Reyna',
        'Repuestos_Maquinas_de_Coser', 'Artigos_para_pesca', 'Ruko', 'Dobby', "magasin_d'expo",
        '아파트상가', '豊橋前田南店', 'loja_náutica,_pesca', 'sanitary & heating', 'سوق الخميس بالقطيف', '清掃サービス', 'Elaboración_de_avisos', '9813892114,9848830674', '佛教用具', 'französische_Artikel', 'سوق_الزاهرة_التجاري',
        'сейитбек', '2 Poniente', 'alexandre imóveis', 'affiches,cartes,..', 'Sähkötarvike_kauppa', '창고형_마트',
        'Materiais_de_Construção,_Moveis,_Eletrodomésticos', 'فروشگاه_ابزار_و_یراق', 'کوروش غربی',
        "produits_d'entretien,_détergents", 'mercado;perfumería;electrodomésticos', '通訊行', 'Químico', '구멍가게',
        'Cadlab', 'sms insurence agency', 'Car Aircon', 'Hotelbedarf; Gastronomietechnik', 'BANGUNAN', 'Mercado Cotripal',
        'Discoteca El Rancho de Juancho', 'Cookry Shop', 'rizky cell', 'supermercado de Limpieza',
        'EDREDONES_Y_LENCERIA', 'Bruce Tea', 'Fast Stop', 'Solar_Store', 'Centre_Nautique', 'Bath_and_Body',
        'ETS Jehovah El Shadai', 'Delta Glass', 'Plating Service', 'Vanitha Vyavasaya Kendram',
        'pets dressing', 'Depot ciment', 'Banca de jornal', 'trade stores', 'vine; zips', 'Equipo_de_oficina', 'vada pasal',
        'Uber', 'SWISS', 'Produktion', 'Pflegedienst', 'Aviamentos', 'Engomadoria', 'Lazare Couture DAME',
        'BANK WAKALA', 'Avicola', 'WeidBlick', 'Medikal', 'wet market', 'OXXO', 'sofaset shop', 'Navking',
        'Pépinière', 'غسيل سيارات', 'Consertos_e_manutenção_de_motores_elétricos', 'Schweißgeräte', '焼肉',
        'dattes, miel, huiles...', 'تم_تولدی،لوازم_قنادی_و_یکبارمصرف', 'Máquinas_e_equipamentos_de_escritorio',
        'متعهد بناء', '洗衣店', 'serviços_técnicos_e_de_construção', 'conv11', '藥房', 'Víveres', '包装資材店',
        'massothérapie', 'shopping/Market', 'Heladería', 'علیخانی', 'Reparações_multimédia', 'Ferretería',
        'Automação', 'اطارات سيارات', 'variado_(ponto_de_entrega)', 'Tamil shop.', 'Informática',
        'Κορνίζες,_αφίσες,Passe-Partout,Καθρέπτες_κ.λ.π.', 'لوازم_جانبی_اتومبیل', '観賞魚', 'telecommunication+_electronics',
        'manutenção_de_impressão', 'Boquete la Flor Panameña', 'روغن', 'Θέρμανση_Υδραυλικά', 'dietética',
        'Ebanistería Carpintería', 'autopeças', 'سوق_الحميدية', 'art,_design_and_crafts.', 'さざんか千坊館',
        '510', 'カーディテーリング業', 'Aγορά_χρυσού', 'materiales_para_tapicería', 'الاسدي_لبيع_مواد_التنضيف',
        'Tresore und Geldschränke', 'معهد تحفيظ قرآن', '(vxs)Vatrix systems + EKONS', 'بيع مرمر',
        'lubricantes; ferretería', 'Βιολογικά,οργανικά,φυσικά_προϊόντα', 'сщт', 'میوه_و_تره_بار',
        'Marchand de fruits et légumes épicerie fine', '貸会議室', 'لوازم بناء وتمديدات صحية', '真珠',
        'Negozio_di_abbigliamento_ed_elettronica', 'Toko', 'Forellenzucht', 'Don Olmedo', 'Masjid Shop',
        'IBROXIM OTA SAVDO MARKAZI', 'Aeromodelismo_e_afins', 'Roupas', 'howllo_blocks,_boubler,_Home_pipe',
        'Bau und Investmentshop', 'Tienda_Escolar', 'De todo', 'Caps', 'Peoples', 'Concept_store_et_centre_culturel',
        'Afro Centric', 'Genge universe city cyber', 'JPG_Comercial', 'Avtoholl', 'Heizungsbau', 'IMPORT_EXPORT', 'Country',
        'Dorms', 'Impresos', 'Momo', 'Abhilash stores', 'Turkey', 'Interceramic', 'Lanchonete', 'Coconut Store',
        'Mapbox', 'Kodak Express', 'Mini-Sam_AGATA', 'Repuesto_de_maquina_de_coser', 'Bouncing', 'Almacen_Natural', 'Small Conver',
        'Loja_fechada', 'Startimes Shop', 'IES Llombai', 'Nummernschilder', 'Nehru Putala', 'Авокадо', 'Super Verduras',
        'Firestone', 'Agencia_publicitaria', 'Abazi', 'Lidl', 'Telas', 'Hair Point', 'Artigos_de_Pesca Desportiva', 'Aphrodite',
        'Alpha Computer', 'Repuestos_de_maquina_de_coser', 'Xanaf', 'Movistar', 'Care_Agency', 'IECLB',
        'Toner-Partes-Copiadoras', 'Sensual moment', 'centro_de_Estudos', 'Tau Sports', 'Produtos_de_Limpeza', 'Tostao',
        'Fancy_store', 'Talabarteria', 'Parcel', 'Kauf- und Bestellshop', 'Jambo', 'Jefferson Barracks Park South Trailhead',
        'Hilos,_cuellos', 'Novelty_store', 'Maderereira', 'Vintage_Boutique', 'saloon, Stationery, Godown',
        'Teodor Service Center', 'fireworks_Building', 'PAEAR', 'Solas_e_Cabedeais', 'Kantor_Pemasaran', '24_horas',
        'Charcuteria-Vinoteca', 'Tienda_de_articulos_varios', 'Resthouse', 'Cook shop', 'Lan_House', 'Towbars',
        'Soluciones_en_productos_de_limpieza_consuno_y_seguridad_industrial', 'Magasin de vente' 'Plaza de mercado Tunjuelito',
        'Venda_de_artigos_militar', 'Komis_RTV,sprzedaż_części_RTV,naprawa_sprzetu_RTV', 'Work Shop', 'Unicentro', 'کافی نت آریا',
        'Varios', 'NET SUGU', 'Agri of Batangas', 'Childzplay', 'SpotColor', 'Express Facials', 'ร้านกาแฟ',
        'reparação_calçado,_matrículas,_fechaduras,_gravações_e_comandos', 'Buvette traditionnelle',
        'fantasia y Alquoler de sillas Arianny', 'Tienda_de_pamelas_y_tocados', 'Handarbeitswaren', 'Shoke Shop',
        'Aluguer_de_motas', 'Roji_Glass_House', 'Essbares,_Trinkbares,_Handwerk,_Geschenke',
        'Limpezas_de_fossas_,_desentupimentos', 'KRINA_STORE', 'Tienda_de_miel', 'Loja_de_armas', 'Elaboracion_de_avisos',
        'Abarrotes, vino y licores', 'Chinese posho mill', 'Swalayan A', 'Chevron', 'Abhilaash Stores', 'Lonin', 'Genge',
        'ARTICLES_DE_PLOMBERIE', 'UCS CAMVA', 'Jamalpur Colony Market', 'Grabmale', 'abarrotes_y_Cremeria', 'Oakley',
        'feste Brennstoffe', 'Papelaria', 'Shubha lakshmi suppliers', 'Verduleria', 'Negocio_local',
        'Venta_de_repuestos_de_maquina', 'Loja_de_Roupas', 'Alquiler_de_motos', 'Ofimatica - impresoras', 'Rado Store',
        'GULF_BAZAR', 'Confiserie Artisanale', 'Kiosque café', 'Masala Chai', 'AC', 'TD', 'True love', 'Almatec', 'Kidsshop',
        'Abrasive Blasting, Cleaning Services, Fabrication, Hygiene', 'Irrigation', 'General Merchandise',
        'Fabrica_de_Pastas', 'Postanahme,_Paketannahme_DHL,_Geschennkartikel,_Schreibwaren,_Zigarettem',
        'Mods,_Accesorios,_Vapor', 'Sunlight store- inkk mobile', 'Agnihotra,_Organic_Farming',
        'Ranching', 'Courier', 'Calls_shop', 'IMPRESOS_LA_PLUMA_Y_SURTIACRILICOS_SUPERIOR', 'Solar',
        'sanitary', 'condo', 'amusements', 'workshop', 'Decoração', 'construção',
        'Captación, tratamiento y suministro de agua realizados por el sector privado', 'γραμματόσημα_-_νομίσματα',
        'isännöintitoimisto', 'gráfica', '甜點', 'Peças_de_barro', 'فرهنگیان', 'dřevovýroba,_historická_lukostřelba',
        'リフレッシュサロン', 'Dépôt_de_câbles', 'たまご、お菓子、お米、地元産野菜', 'Em_remodelação',
        'jager_material_de_construções', 'сухофрукты,_фрукты,_офощи,_специи,_национальная_посуда', '農用品行',
        'interieur (baptiment)', 'عصرونية_الغيث', 'Decoración', 'decoração_de_bolo',
        'impressão', 'تأجير شاحنات', 'Compañías de seguros', 'Food & Delicacy', 'Forst- und Gartengeräte',
        'Escuelas del sector público que combinan diversos niveles de educación', 'درب و پنجره سازی',
        'alimentari_gastronomia_pastificio', 'boutique pencum palene', 'negozio_di_alimentari', 'electrical_forniture',
        'arreglos_y_telas', 'sartorial', 'gy', 'contability', 'ty', 'daily_use_items', 'brocante',
        'Boulangerie pâtisserie', '열림카센타', '文具百货', 'granitos,_pedras_pirenópolis', "espace_indépendant_dédié_à_l'art",
        'PCP № 2', '古書店', 'loja_do_colchão', 'escritório', 'お菓子', 'حلول_مياه', '新力源超市', 'لوازم یدکی شکوری',
        'κατάστημα δώρων', 'Venta_de_Dulce_y_diseños', 'Pièces_pour_Solex_et_mobylettes_anciennes',
        'دبستان غیردولتی کرامت دوره دوم', 'artigos_para_casa_e_decoração', '9846292044', 'seafood pescadería',
        'سوپر مارکت و نانوایی', '장소대여', 'γραβάτες_-_ζώνες', 'Servicios médicos',
        'assistência_técnica,_ar_condicionados', 'Vermessungstechnik,_Wärmebildtechnik', 'Επιγραφές',
        'têxteis_lar', 'aseliike_ja_sisäampumarata', '印鑑販売店', 'Cymraeg_/_Welsh-language',
        'affaire_éphémère', '金屋', 'Antijitos Mexicanos Ana´s', 'Maquinas_para_Hostelería',
        'comunicaçao_visual', 'radio & TV', 'decoração', 'Fabricación de ladrillos no refractarios',
        'αγροτικά_εφόδια', 'Productos estéticos', '紳士服', 'loja_de_material_de_construçao_civil', 'hojalatería',
        'pâine,_patiserie,_alimente', 'Перекрёсток', 'design,_brindes,_publicidade,_impressão', 'cash & carry',
        'махны', '宗教用品店', 'decoratore_d`_interni', 'مطعم سوري', 'vêtement', '商店', 'geschäft_für_papyrusbilder', 
        'librería', 'labores,_costura_y_enmarcación', '3D_Printer_Cafe_&_Store', 'Serviços_e_Tecnologia',
        'كافيتيريا', 'مجتمع_تجاری_فیروزه', '電気量販店', 'απεντομώσεις', 'Κατασκευές_Τζάκια', 'artigos_em_segunda_mão',
        'รานเอกดวด', '09:00-17:00', 'Baja_térségének_hivatalos_STIHL_és_VIKING_szakkereskedése_és_szervize',
        'Importación_y_venta_de_bombas_de_agua_LINZ_originales_italianas,_tanques_de_presión_VAREM,',
        'Tapeçaria', 'Gartengeräte', 'distribuidora_de_artículos_de_limpieza', 'Sec B Ph 1', 'Imóveis', '外燴',
        'Stationary_Shop', 'επιγραφές', '電器行', 'Colchoneria', 'comida', 'Celulares', 'Artesanato', 'rationkada',
        '水電行', 'namkeen', 'toddy', 'Construction', 'call', 'cutler', 'químico', 'sacco', 'BDOrtho IGN', 'fire',
        'Roupa', 'depot', 'con', 'present', 'شحن سيارات', 'agropecuária', 'químicos', 'fitness',
        'Loja_de_móveis_e_eletro-eletrônicos', 'موقف تكاسي', 'نمایندگی_ایران_رادیاتور', 'tapeçaria_e_toldos',
        'vente de pieces détachés', 'Tienda_de_Liquidación', 'pop-kläder', 'st.pierre', "Pick 'n Pay", '果菜舖',
        'ñconfectionery', 'Catering_Equipment_&_Supplies', 'construçao', 'Big Market (تاك و كو)',
        'car_repair, neumáticos, vulcanizadora', '本、ホビー、CD、携帯', '東京システム運輸', 'барилгын материал',
        'Υφάσματα,_κλπ', 'かまぼこ', 'Nähkurse', 'قاسم_نژاد', 'クロタ硝子', 'boutique bassaro et frères de sibila',
        'artigos_decorativos', 'compro_oro', 'hinge', 'pravasthi boutique', 'flex', 'coll', 'hielo',
        'refill', 'scale', 'verandas', 'doi', 'all', 'tip', 'yea', 'nea', 'tra', 'med', 'govt', 'help',
        'Hilos,_repuestos_de_maquina_de_coser', 'Conserto_de_Alto_falantes', 'Venta,_respuestos_y_accesorios',
        'Trommelfilter', 'Jugueton', 'Cremalleras', 'Airtime Agent', 'Hermes PaketShop', 'crystal', '3',
        'Games_Nights_Tuesday_Evening', 'Madaba Handicraft Centre', 'travaux_publiques', 'arms', 'credit', 'glas',
        'curio', 'webshop_delivery', 'Bazar', 'mobility', 'Produtos_naturais', 'Estores,_Toldos,_tectos_falsos',
        "memorial", "rural", 'ad', 'tack', 'camp', 'toll', 'engineering', 'Eco Living Store', 'Practise_Area',
        'Micelanea', 'Miscelanea', 'Concept_Store', 'Provision', 'Accessoires_pour_Voitures', 'merchandise',
        'интернет-магазин_автозапчастей', 'építőanyag', 'token_buyer', 'pesca', 'mining', 'spikes', 'Ciudad Jardín',
        'Paper Power', 'Posho mill', 'Lonja_Mercantil', 'Cabinetry', "céramique_d'art", 'Spielautomaten',
        'Distribuidor_de_Purina', 'Fruits_et_Produits_du_Terroir', 'fundacion_Waflam', 'Rastech cyber cafe',
        'servicio de inversión', 'applied_Industrial_Technologies', 'stores_and_Shopping', 'Postobon',
        'duka la vitanda', 'magazin_Haine', 'Agrobotiga', 'ECOLIGHT', 'Vendor_Mall', 'hijama Service Center',
        'Corralón', 'cash', 'magic', 'Veranstaltungstechnik', 'Road_travel', 'Alugel_de_Ropas', 'Press',
        'Alfombras_persas', 'Mi Store', 'CACAO_Y_CAFE', 'Tabac', 'Relay', 'Kiron', 'Public_Distribution_System',
        'Herbolarío', 'Торгово-строительная компания', 'زريبة_لبيع_الفحم', 'Carniceria,_pastelería,_panadería',
        '農園', 'Büromöbel und Bürotechnik', '工具店', '米舖', 'داروخانه باتري  خودرو', 'Online Perde Mağazası',
        'είδη_κυνηγιού', '檳榔攤', 'fa', 'liquidation', 'disabled', 'thrift', '五金百貨', 'Pulperìa', 'forecourt', 'paan',
        'childrens', 'cargo', 'arts', 'Carro', 'waters', 'Cargo', 'car_w', 'Foothills Mall', 'comercio',
        'import', 'sanity', 'solicitors', 'shops', 'atelier', 'parade', 'fantasy', 'plush', 'oneworld', 'male', 'home'
        'Cigarrería', 'tienda_y_cafetería', 'ラーメン店', '漆器店', 'خصوصی', 'продуктовий', "VIJHU'S SHOP", 
        'Design_e_produção_de_Cartazes_e_Publicidade_Gráfica', "magasin_d'accessoires_de_camping", 'Talktime',
        'NETIS_Togo_Vente_de_groupes_électrogènes', 'Artículos_para_el_hogar', 'mensajería_y_domicilios',
        "Breathe Hawke's Bay", 'ケーキ・アイスクリーム・パン', 'سروستان', 'بزورية_دركل', 'microorganism', 'Hypoxi',
        'Kvety,_domáce_potreby,_krmivá_pre_zvieratá', 'army_&_navy_surplus_shop', 'Speiseöle', 'تعویض روغنی',
        'https://www.conceptate.com.au/weborder?location=263&sale_type=102', '豆腐', 'Depósito_y_tienda_de_harina',
        'Maquis kaplin', 'Package_shop', 'Loja_de_Produtos_Mineiros', 'Mealie Meal Centre', 'Desarrollo_web',
        'LTC + Mairie', "Vente d'oeufs", "negozio_di_prodotti_alimentari_all'ingrosso", 'นำดมเยนเยน',
        'Alimentation_générale', '청소용품,_사무용품', 'فرخ آباد ۲۲', 'äänitysstudio', 'Gráfica', 'Galería Comercial', 
        'fabricação_de_replicas_de_paredões_de_som', 'Artigos_em_segunda_mão', 'tea;米舖', 'Dietética', 'VinMart+',
        'roça,_fazenda,_animais', 'AMPJ - Partenaire du développement communautaire (ONG)', 'Hojalatería',
        'τεντες', 'Bodenbeläge', 'productor_de_alimentos_lácteos', 'montaña', 'Materiais_de_Construção',
        'Trabajos de albañilería', 'rainwear,雨具', '50', 'Eichenzäune', 'γραβάτες', 'Unit 3A',
        'Colchões', 'Generación de electricidad a partir de combustibles fósiles', 'Cleaning & Wellness',
        'Equipamentos_Para_Panificação', 'tecnologia_médica_cardio_e_endovascular', 'Centro_de_impressões',
        'بلبرینگ و ابزار', 'Tổng Kho Điện Tử - ĐIện Lạnh', 'تجارة خارجية', 'ሴንተራል ፕሪንቲግ', 'ferretería', '玩具槍店',
        'G-10/3, Islamabad', 'προσκλητήρια_γάμου_-βάπτισης', '三井造船マシナリーサービス', 'Agrarian=Processing Plant',
        'ενεργειακές_πέτρες', 'Instalações_comerciais', 'R # 6', 'servicios médicos', 'Relojería', '不動産会社', 'bric-à-brac',
        'Roupas_étnicas', '玩具商店', 'Librería_Jesusito', '醫療器材', 'Empréstimos', '運輸サービス', 'دكان مرمر',
        'tienda_de_suministros_eléctricos,_tienda_de_iluminación,_ferretería', 'ラジコンショップ',
        'Société_de_fourniture_et_équipement', 'jarcería', 
        'houseware;security; interior_decoration', 'Regalos_y_Bike_Rental.',
        'ferestre,_uși,_termopane', 'Venda_de_colchões_a_domicílio.', 'فروشگاه_رنگ', 'магазин',
        'card', 'cards', 'design', 'laundry_shop_,_Pasalubong_shop', 'alarmas', 'dollar', 'miso',
        'alimentos_de_origen_vegetal', 'casters', 'auto_ac_electricals', 'transportation',
        'provision', 'concession', 'photostat_shop', 'bait_shop', 'estate', 'wireless', 'sharpening',
        'multi_swap', 'senetary', 'empresa_de_engenharia', 'ekmek', 'tratamento_de_roupa', 'ruitersportwinkel',
        'petti_kada', 'dibiterie', 'vend', 'agrivet', 'concessions', 'tara', 'papereria safir', 'sapataria',
        'bar_b_que', 'turner', 'claro', 'bakproducten', 'miellerie', 'ebenisterie', 'main', 
        'madera y bricolaje', 'aq', 'awning', 'blind', 'sadewa77', 'public_market', 'stall', 'grooming',
        'Frutas Rocha', 'department', 'dealer', 'flagging', 'koi', 'sun_studio', 'sun_control',
        'electric_furniture', 'farine', 'variedades', 'milliner', 'tackle', 'toldos', 'marmol',
        'Sanitair', 'Frigoriste', 'Supu', 'Indomaret', 'Borrachas_e_Plasticos', 'Loja_de_tintas',
        'loja_de_Placas', 'Ourivesaria', 'Serviman Levante', 'Gewindefahrwerke_-_suspensions', 'Plaza de mercado Tunjuelito',
        'Vidros_e_espelhos', 'Venta_de_repuesto_de_maquina', 'Manikanteshwara Provision Stores', 'Toddy',
        'https://telem.si/trgovina/', 'Steuerungstechnik, Anlagen- und Maschinenbau, Simulationsmodellbau',
        'Apoio_Escolar', 'Canal', 'Boliches', 'Lonery', 'kiosk-nagar cholafadi',
        'Venta_de_muebles,_repuestos_y_maquinas_de_coser', 'Diadora', 'Tienda_de_suplementacion',
        'JITENDRA ELECTRONICS', 'Expendio_de_Cerveza', 'WorkShop', 'General_Trading',
        'καταστήματα ειδών μόδας', 'Besteck für Gastronomie', 'preverificación', 'acessórios',
        'Tintas,_eletrodomésticos_e_materiais_de_contrução', 'χανολογικά_είδη',
        'Βιομηχανικά_είδη,_μηχανολογικός_εξοπλισμός,_ρουλεμάν,_εργαλεία,_τσιμούχες,_είδη_μετάδοσης_κίνησης',
        'Abogados SL', 'Leihladen', 'Armonia Marble', 'Abastos', 'Kengele Agencies property management division',
        'Makongoro Point', 'Local shop', 'Artigos_Ortopédicos_e_Hospitalares',
        'produtos_agrícolas', 'equipamentos_de_seguraça', '食用油', 'construcción', 'tienda_de_accesorios_para_móviles',
        'voda,_plyn,_topení', '媒體', 'كهربائيات', 'maderería', 'شركة_ابناء_محمد_بن_خلف_بن_قويد', 'ソープランド',
        'aide_à_domicile', 'UFD 10', 'empaste,_tornillería,_perfilería,_planchas,_iluminacion', 'مواد غذایی خارجی',
        '购物中心', 'κορνίζες', '1Stop Auto LLc', 'tapicería', 'shishas,_tabak,_und_zubehör',
        'comercio_de_retalho_de_louças', 'Fabrics, Trimmings & Clothes', 'Худалдааны_төв', 'mağaza',
        'Loja_Maçonica', '0003', '廣告印刷', '農機行', 'SURF_&_GIFT_SHOP', '照相館', 'cristalería', 'Půjčovna strojů',
        'Compras_Café_Cesar_Botero', 'przemysłowy', 'προσκλητήρια', '安全帽，雨衣，行車紀錄器', 'Sistemas_contra_incêndios',        'comestibles', 'telemarketing', 'emporium', 'sounds', 'reef', 'plaza', 'ups',
        "supply", "resale", "closes", "cold_storage", "local", 'lavoir', 'grinding meals', "agency", "lease",
        'تولیدی_کیسه_برنجی_و_ساک_دستی', 'tienda_de_abarrotes', 'exterior', 'telekom', 'jerky', 'home_service', 'gar',
        'decomorphose', 'bou', 'ch\\', 'produits_locaux_et_idees_cadeaux', 'mri', 'aid', 'akkukauppa',
        'fabricator', 'show', 'aquatics', 'nail', 'orthotics', "gazettes", "display",
        'microenterprises', 'micro_enterprise', "cooperative", "removalist", "rotisserie",
        'Εργαστήριο_ανακατασκευής_άδειων_μελανοδοχείων_και_laser_toner', 'スポーツ用品', 'Λευκά_Είδη', '鋁門窗行',
        'vertrieb_von_schüttgütern', 'минимаркет', 'pépinière', 'সমনত_মদ_দকন', 'Home Express Ltd.',
        'سوپر_گوشت_و_پروتئین_سیتکا', 'cafetería', 'www.mibels.com', 'μηχανολογικά_είδη',
        'Loja_de_Iluminação', '身心靈中心', 'سوق_البالة', 'Flipkart.com', 'Blachotrapez S.J.',
        'tienda_de_baños,_cerámica_y_materiales_de_construcción.', 'fincanon_&_Cia', 'Sportovní vybavení',
        'co1', 'Neumáticos', 'Productos_de_Aromatizacion_y_Limpieza.', 'restauração', 'είδη_γάμου', 'imprimerie',
        'mobile', 'mobile_shop', 'call_shop', "atelier_d'auto-réparation", 'café - épicerie - snacking',
        'husvagns_försäljning', 'captação_de_água_de_chuva_e_reuso_de_água', 'Reparações ', 
        'ရှိတ် shake', 'ร้านขายของฝาก_ของที่ระลึก', 'อุปกรณ์การเกษตร', 'ร้านขายไอศครีมมะพร้าวน้ำหอม', 'ร้านเอกดีวีดี',
        'たばこ・お菓子', 'သင်္ကန်းဆိုင်', 'Shops/kiosk', 'Gothic_&_Hippie',
        'فنی_مهندسی_سرو(حفاظتی،امنیتی_و_کنترلی)دوربین_مدار_بسته-کرکره_برقی-درب_کنترلی-تابلو_روان-تابلو_چلنیوم-شیشه(اپراتور)_برقی-دزدگیر_اماکن-اعلان_حریق-راهبند_بازویی-جک_بازویی_پارکینگ-راهبند_بازویی',
        'Plomberie_ppr_et_accessoires.', 'Imker-_und_Bienenwarengeschäft', 'çadır,_naylon',
        '衣料品プリント店', '飲食店', 'Épicerie_fine', 'سيراميك وملزمات الحمامات',
        'Construction_solutions', 'Klootschietballen', 'Réparation_et_vente_machines_à_café', 'water_supplies',
        'Venda_de_material_esportivo_e_de_armas', 'Rede Economia', 'Baguio_Products_Souvenir_Shop', 'Curio',
        'Communications', 'Smoky Valley Nursery', 'Rubber_Stores', 'PA_system', 'Plasticos',
        'mango,_banana,_lime,_Noy_naa', 'yes / shop = convenience', 'Importador_de_aluminio',
        'Clearing Purchased Goods', 'Gas_Cylinders', 'Futon Company', 'Airtime Vouchers',
        'UTE Colaboracion Recaudacion', 'Engineering works', 'Eco_Friendly', 'Shaheen_for_spices', 'Stainless Steel',
        'Inflatables', 'Porcelanas', 'building Services', 'Golf_Club_House',
        'Novelty Store', 'Novelty', 'escolar,_Oficna,_Costura', 'Bondoc Hardware', 'MilkTea_Shop',
        'logistics', 'freight', 'bait', 'parking', 'فروشگاه_لوازم_حیوانات_خانگی', 'viveres_licor', 'fabrica_de_jeans', 
        'cс', 'sale_services', 'pick_up', 'rashen_shop', 'সীমান্ত_মুদি_দোকান', 'yalıtım_malzemeleri', 'لوازم یدکی',
        'Stowarzyszenie Samopomocowe "Abakus"', 'bonito,かつおぶし', "prodotti per l'agricoltura", 'dietéticos',
        'chuyên_mỹ_phẩm_xách_tay_châu_âu', 'مكنين', 'Bricolage_e_decoração', 'ラーメン屋', 'louças', 'színesfém-áru', 
        'voda,_kúrenie,_plyn,_sanita', 'ጌጅ ቴክኖሎጂ ና ንግድ ኮሌጅ', 'غسان_صايمة_حمصي_للتمديدات_الصحية',  '雑貨屋',
        'รานขายของฝาก_ของทระลก', '購買部', 'fancy_centre', 'collective', 'продавница_мешовите_робе', '髮廊', 'jukebox',
        'idea', 'rexine_facilities_works', 'assesoria', 'Purification', 'Tapeçarias', "stove", "res", 'club',
        '茶楼', 'basílio imóveis', 'عناية بالحيوانات الضالة والمهجورة', '新潟交通観光バス 村上営業所', 'كراج',
        'キャッシングサービス', 'چاپ_دیجیتال', 'لوازم_قنادی_ظروف_یکبارمصرف', 'article', 'holiday', '写真用品店',
        'hospitality', 'venta_de_papa_y_viveres', 'land', 'iparcikk', 'others', '蚊帳生地の商品を売っているお店', 
        'شركة للبناء', 'اقمشة بالجملة', 'Card_&_Posters', 'αγορά_χρυσού', 'αξεσουάρ_για_κινητά_κλπ', 'calçados', 
        'audio_video', 'jokes', 'joke', 'community', 'recycling', 'recycle', 'صيانة السيارات', 'продукти',
        'فروشگاه الکترونیک شیراز', '家電、電気工事、水道工事', 'ТЦ', 'solicitor', 'saloon', 'bazar', 'warehouse-shop', 
        "salisali store", "goats", "tienda_mixta", "delikatesy", "woonwinkel", "maid", "screw", "seguros", 
        "sticker", 'monuments', "commercial_equipment", "water_technics", "cup", 'tienda_de_ropa', 'agricola', 'shelter',
        'pavilion', 'eclectic', 'screens', 'panel_beater', "fancy",
        'electronics;domotique;smart_home;KNX;Z-Wave;EnOcean;maison_connectée;maison_intelligente', '在宅介護ステーション',
        '13-магазин', 'فروشگاه_آنلاین_آنیاشاپ', 'Mom J Enterprise & Charging center',  'alimentaire(fruit&legumes)',
        'ΠΑΡΑΔΟΣΙΑΚΑ_ΠΡΟΪΟΝΤΑ_ΘΑΣΟΥ', 'ExtraQilo #39 laundry', 'Cuisines_aménagées,_Arts_de_la_Table,_SAMSUNG',
        'Parques de diversiones y temáticos del sector público', 'kitchen_stove_&_hob', 'desporto/lazer',
        'Impartición de justicia y mantenimiento de la seguridad y el orden público', 'eScooter / EKS', 
        'Clothing,_bags,_handicrafts,_wall-hangs,_cushion_covers.', 'loja_de_materiais_de_construção',
        'Farben, Tapeten, Teppichböden, Markisen', 'kiosk "shoshi"', 'artisan', 'imports', 'kabel_provider',
        'چینی_بهداشتی_و_کابین_دوش-شیرآلات', 'productos_de_belleza_para_el_cuidado_del_cabello,_manos_y_pies.',
        'Discoteca Mr. Charles', 'township/shopping centre', 'Representante_Claro_TV', 'Inwoods models', 'Rancho',
        'Education and Immigration', 'general_contractor',
]