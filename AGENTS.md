# Pokyny pro práci v repozitáři

Tyto pokyny platí pro celý repozitář. Aktuální výslovný požadavek uživatele
má vždy přednost.

## Běh webu

- Jde o web v Django 5.2.
- Pokud již vývojový web běží, kvůli kontrole jej znovu nespouštěj ani
  nerestartuj.
- Zachovej existující uživatelské změny a neupravuj nesouvisející soubory.
- Nikdy neukládej přihlašovací údaje ani SMTP hesla do repozitáře.

## Obsah výletů, koupání a restaurací

- Výletní cíle a koupání udržuj v `apartmancvikov/content.py`, restaurace
  v `apartmancvikov/restaurants.py`.
- Delší podklady od hostitele jsou ve složce `vylety/`. Původní dokumenty
  zachovej a jejich textové přepisy ukládej přímo do stejné složky, protože se
  budou používat opakovaně.
- Nevymýšlej vzdálenosti ani je z mapy nepřepočítávej. Údaje dodané uživatelem
  jsou autoritativní; chybějící hodnoty si vyžádej.
- Vždy rozlišuj:
  - vzdálenost od apartmánu,
  - vzdálenost autem nebo na kole,
  - délku pěší trasy či celého okruhu,
  - jednotlivé varianty trasy.
- Délku okruhu nikdy neprezentuj jen jako „vzdálenost“. Pro více tras použij
  `RouteVariant`, aby každá varianta měla vlastní název, délku, popis a mapu.
- Dopravu zobrazuj strukturovaně stejně jako ostatní praktické údaje. Pokud je
  cíl dostupný autobusem, uveď to.
- Vstupné, provozní dobu a přístupnost kočárkem u výletů udržuj ve
  strukturovaných polích. Zároveň vždy zobraz upozornění, že aktuální podmínky
  je vhodné ověřit u provozovatele nebo v mapě.
- U koupání údaj o kočárku vůbec neuchovávej ani nezobrazuj. `SwimmingTip`
  používá obecné `distance_km`, volitelný `distance_label`, `map_url` a
  `travel_tip`; nevytvářej pro něj zvláštní způsob vykreslení dopravy.
- Odkaz „Aktuální informace“ zobrazuj jen tehdy, když existuje skutečný web
  provozovatele. Přírodní lokality mohou mít pouze odkaz „Zobrazit mapu“.
- Texty z oficiálních webů používej jako podklad pro popis, ale nepřebírej
  dlouhé pasáže doslova. Neaktuální nebo uživatelem odmítnuté informace
  nevracej; například u Exotenhausu je motýlí část uzavřená, skupinové prohlídky
  se neuvádějí a zůstává fotografie s motýlem.

## Propojování obsahu

- Související výlety, koupání a restaurace propojuj přes `TripRelation`.
- Každá vazba musí být obousměrná a oba směry mají mít smysluplný vlastní
  popis.
- Ověř, že cílový `slug` existuje. Rozšíření grafu vazeb promítni do testu
  jeho validity.
- Související tipy musí zůstat viditelné také při tisku.

## Překlady, počty a metadata

- Veškerý nový uživatelský text označ pro gettext a doplň českou, anglickou
  i německou variantu.
- Aktualizuj oba katalogy v `apartmancvikov/locale/*/LC_MESSAGES/django.po`.
  Nenechávej nové nebo změněné řetězce prázdné či fuzzy a nevytvářej zbytečný
  přeformátovací šum v celém katalogu.
- Před testy spusť `compilemessages`, protože soubory `.mo` nejsou verzované.
- Při přidání nebo odebrání položek zkontroluj všechny ručně formulované počty
  v šablonách, `structured_data.py`, `views.py`, SEO popisech a testech.
- Zachovej správné canonical a lokalizované URL, JSON-LD, sitemapu a `llms.txt`.

## Fotografie

- Zdrojové fotografie výletů ukládej do `apartmancvikov/static/vylety/` a
  uchovej jejich správné rozměry v datech.
- Po přidání nebo změně fotografie spusť:

  ```sh
  .venv/bin/python scripts/generate-images.py
  ```

- Do výsledné změny zahrň zdrojovou fotografii, všechny vygenerované JPG/WebP
  varianty i aktualizovaný
  `apartmancvikov/static/responsive/manifest.json`.
- U cizích fotografií zachovej autora, zdroj a licenci. Již vybranou fotografii
  bez výslovného požadavku uživatele nenahrazuj.

## Tisk výletních stránek

- Přehled výletů, koupání, restaurací i každý detail výletu musí být použitelný
  při samostatném tisku.
- Tisk má být jedna strana A4 na výšku, s hlavičkou Apartmánu Cvikov a QR kódem
  aktuální lokalizované stránky.
- Skryj navigaci, mapová tlačítka, odkazy „Aktuální informace“, výzvy k rezervaci
  a další interaktivní prvky, které na papíře nedávají smysl.
- Nadpisy musí fungovat bez kontextu webové navigace. Obecné označení „Náš tip“
  netiskni automaticky na každé stránce.
- Zachovej související výlety a restaurace. Rámečky drž uvnitř tiskové plochy,
  zejména jejich pravé hrany, a nepoužívej příliš tenký tah.
- Po obsahové změně ověř v Chromiu skutečný počet stran alespoň pro CS, EN a DE.
  Nevyvozuj jednostránkovost jen z CSS nebo z testu šablony.

## Rezervační formulář

- Minimální datum příjezdu je nejbližší volný termín, nejdříve však zítřek.
- Maximální datum je dva roky do budoucnosti.
- Stejné meze vynucuj v HTML i na serveru.
- Odeslání musí odmítnout každý pobyt kolidující s obsazeností. Odjezd v den
  příjezdu následující rezervace se za kolizi nepovažuje.

## Ověření změn

Podle rozsahu změny spusť zejména:

```sh
.venv/bin/python manage.py compilemessages -v 0
.venv/bin/python manage.py check
.venv/bin/python manage.py test
.venv/bin/python scripts/generate-images.py --check
.venv/bin/pre-commit run --all-files
```

U tiskových změn navíc vytvoř dočasná PDF z již běžícího webu, zkontroluj A4
a počet stran pomocí `pdfinfo` a vizuálně prohlédni alespoň přehled výletů,
koupání a změněný detail.
