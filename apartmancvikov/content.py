# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

from dataclasses import dataclass
from typing import Literal

from django.utils.translation import gettext_lazy as _


@dataclass(frozen=True)
class TripRelation:
    target_kind: Literal["attraction", "swimming", "restaurant"]
    target_slug: str
    description: object


@dataclass(frozen=True)
class RouteVariant:
    name: object
    distance_km: int | float
    map_url: str
    description: object
    distance_km_max: int | float | None = None


@dataclass(frozen=True)
class Attraction:
    slug: str
    name: object
    summary: object
    description: object
    distance_km: int | float
    difficulty: object
    family_tip: object
    map_url: str | None
    official_url: str
    stroller_access: object
    admission: object
    opening_hours: object
    travel_tip: object | None = None
    image: str | None = None
    image_width: int | None = None
    image_height: int | None = None
    credit_name: str | None = None
    credit_url: str | None = None
    license_name: str | None = None
    license_url: str | None = None
    distance_kind: Literal["from_apartment", "walking_loop", "cycling", "driving"] = (
        "from_apartment"
    )
    driving_distance_km: int | float | None = None
    alternate_distance_label: object | None = None
    alternate_distance_km: int | float | None = None
    description_paragraphs: tuple[object, ...] = ()
    route_variants: tuple[RouteVariant, ...] = ()
    related_trips: tuple[TripRelation, ...] = ()


EASY = _("Lehká")
MODERATE = _("Střední")
MOUNTAIN_EXPRESS_TIP = _(
    "V létě sem ve vybraných termínech jezdí Horský expres z náměstí ve "
    "Cvikově; termín a dostupnost jízdenek si ověřte předem."
)


ATTRACTIONS = (
    Attraction(
        slug="cvikovske-vyhlidky",
        name=_("Kalvárie a cvikovské vyhlídky"),
        summary=_("Nenáročný výlet přímo ze Cvikova s výhledy na Lužické hory."),
        description=_(
            "Křížová cesta na Kalvárii a značené vycházkové okruhy patří k "
            "nejbližším výletům od apartmánu. Trasu lze přizpůsobit věku dětí "
            "a spojit ji s krátkou procházkou po městě."
        ),
        description_paragraphs=(
            _(
                "Poutní místo na Křížovém vrchu začal roku 1728 budovat "
                "punčochář Johann Franz Richter. Podél cesty postupně vznikly "
                "zděné kapličky se zastaveními Ježíšova utrpení. Po obnově areálu "
                "po roce 1991 dnes lipovou alej lemuje čtrnáct kaplí křížové cesty."
            ),
            _(
                "Navazující okruh po Zeleném vrchu vede kolem lesního divadla, "
                "které cvikovští ochotníci vybudovali roku 1920 v bývalém "
                "pískovcovém lomu. Dochovala se tu místnost vytesaná ve skále, "
                "krátká chodba a zbytky hlediště."
            ),
            _(
                "Cestou se zastavíte také u dřevěného altánu Švýcárna s výhledem "
                "do českolipské krajiny a na Schillerově vyhlídce, odkud jsou "
                "vidět vrcholy Luže, Hvozdu a Jezevčího vrchu. Okruh se uzavírá "
                "u rozcestí Pod lesním divadlem."
            ),
        ),
        distance_km=8.7,
        distance_kind="walking_loop",
        difficulty=EASY,
        family_tip=_(
            "Vhodné i pro kratší výlet s menšími dětmi; část cest vede lesem."
        ),
        map_url="https://mapy.cz/s/rodateluge",
        official_url="https://www.cvikov.cz/vychazkove-okruhy/ms-1081/p1=1081",
        stroller_access=_("Celý okruh ne; samotná Kalvárie pouze s terénním kočárkem."),
        admission=_("Zdarma"),
        opening_hours=_("Volně přístupné"),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="duty-kamen",
                description=_(
                    "Dutý kámen je zkrácenou variantou okruhu pro den, kdy "
                    "nechcete absolvovat celou trasu."
                ),
            ),
        ),
        image="vylety/kalvarie.jpg",
        image_width=1600,
        image_height=1064,
    ),
    Attraction(
        slug="pumptrack-cvikov",
        name=_("Pumptrack ve Cvikově"),
        summary=_("Dva asfaltové okruhy pro děti, začátečníky i zkušenější jezdce."),
        description=_(
            "Nový pumptrack u cyklostezky Svaté Zdislavy nabízí dvě oddělené "
            "tratě. Menší okruh je určený především dětem a začátečníkům, větší "
            "okruh umožňuje rychlejší a techničtější jízdu. Přímo u pumptracku "
            "je také velké dětské hřiště, workoutové hřiště, atletický ovál, "
            "občerstvení a placené vzduchové trampolíny."
        ),
        distance_km=1.3,
        distance_kind="cycling",
        difficulty=EASY,
        family_tip=_(
            "Nezapomeňte na helmu; menší okruh je vhodný pro první zkušenosti."
        ),
        map_url="https://mapy.com/s/dezohapela",
        official_url=(
            "https://admin-storage.munipolis.com/cvikov/bulletin/files/"
            "2b5ab9d5-83b9-438d-a11e-30e8bfe85010.pdf"
        ),
        stroller_access=_(
            "Ano, cíl je ale určený především pro výlet na kole nebo odrážedle."
        ),
        admission=_("Pumptrack zdarma; vzduchové trampolíny jsou placené."),
        opening_hours=_("Volně přístupné"),
        related_trips=(
            TripRelation(
                target_kind="restaurant",
                target_slug="na-krajicku",
                description=_(
                    "Přímo u pumptracku a trampolín se můžete občerstvit Na Krajíčku."
                ),
            ),
        ),
        image="vylety/pumptrack-cvikov.jpg",
        image_width=1600,
        image_height=1200,
    ),
    Attraction(
        slug="duty-kamen",
        name=_("Dutý kámen"),
        summary=_("Pískovcový hřbet s vyhlídkou a neobvyklými skalními útvary."),
        description=_(
            "Dutý kámen mezi Cvikovem a Kunraticemi nabízí krátkou lesní túru, "
            "skalní reliéfy a výhled směrem ke Cvikovu. Závěrečné schody a skalní "
            "terén vyžadují u menších dětí zvýšenou pozornost. Odkazovaná trasa "
            "je zkrácenou variantou cvikovského okruhu po vyhlídkách."
        ),
        description_paragraphs=(
            _(
                "Chráněná přírodní památka tvoří přibližně 600 metrů dlouhý "
                "pískovcový hřbet, který vystupuje 20 až 30 metrů nad okolní "
                "terén. Jméno dostal podle nejvyšší skalní věže hřibovitého tvaru "
                "se skalním oknem."
            ),
            _(
                "Stezka prochází kolem zarostlých těžebních jam a starého lomu "
                "ke skalní lavici Karolínin odpočinek. Na Široký kámen vede úzká "
                "chodba a schodiště vysekané ve skále. Dochovaly se tu zbytky "
                "rozhledové růžice a slunečních hodin i reliéf německého básníka "
                "Theodora Körnera."
            ),
            _(
                "Z vyhlídky se otevírá pohled na Ortel, Klíč, Cvikov a Zelený "
                "vrch s altánem Švýcárna. Porost už část někdejšího rozhledu "
                "zakrývá, samotné skalní útvary a stopy po jejich zpřístupnění "
                "však zůstávají hlavním zážitkem trasy."
            ),
        ),
        distance_km=4.5,
        distance_kind="walking_loop",
        difficulty=MODERATE,
        family_tip=_("Pro děti, které zvládnou schody a nerovný terén; bez kočárku."),
        map_url="https://mapy.com/s/madepucoso",
        official_url="https://www.cvikov.cz/turista/ms-1091/p1=1091",
        stroller_access=_("Ne"),
        admission=_("Zdarma"),
        opening_hours=_("Volně přístupné"),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="cvikovske-vyhlidky",
                description=_(
                    "Pokud chcete delší výlet, projděte celý okruh přes Kalvárii "
                    "a cvikovské vyhlídky."
                ),
            ),
            TripRelation(
                target_kind="attraction",
                target_slug="kunraticke-svycarsko",
                description=_(
                    "Na delší cestu zdejšími pískovcovými skalami navazuje "
                    "okruh Kunratickým Švýcarskem."
                ),
            ),
        ),
        image="vylety/duty-kamen.jpg",
        image_width=800,
        image_height=533,
        credit_name="Lutz Maertens",
        credit_url="https://commons.wikimedia.org/wiki/File:Koerner.jpg",
        license_name="CC BY-SA 3.0",
        license_url="https://creativecommons.org/licenses/by-sa/3.0/",
    ),
    Attraction(
        slug="kunraticke-svycarsko",
        name=_("Kunratické Švýcarsko"),
        summary=_(
            "Malé skalní město s reliéfy, kaplemi a ukrytými místy nedaleko Cvikova."
        ),
        description=_(
            "Osmikilometrový pěší okruh vede přímo od apartmánu do krajiny "
            "nižších pískovcových skal mezi Drnovcem a Kunraticemi. Čekají vás "
            "skalní reliéfy, kaple, vyhlídky i stopy příběhů, které se k tomuto "
            "malému skalnímu městu vážou."
        ),
        description_paragraphs=(
            _(
                "Jednou ze zastávek je kaple vytesaná ve skále ve tvaru "
                "antického chrámku. Poblíž ní se ukrývá další skalní kaple "
                "s lavicí, upravená při obnově místa v roce 1934."
            ),
            _(
                "Pod převisem najdete Karlův odpočinek s lavicí, kterou členové "
                "kunratické sekce Horského spolku věnovali svému předsedovi "
                "Karlu Beckertovi. Dvojice podobných skal na ostrožně dostala "
                "příznačné jméno Blíženci."
            ),
            _(
                "Nevelký skalní úkryt Waltro připomíná odbojovou skupinu "
                "Waltera Hofmanna a uprchlíky, kteří se zde skrývali za druhé "
                "světové války. Trasa spojuje tato drobná místa do pestrého "
                "výletu, na který se vyplatí vzít pevnou obuv."
            ),
        ),
        distance_km=8,
        distance_kind="walking_loop",
        difficulty=MODERATE,
        family_tip=_(
            "Dobrodružná cesta pro děti, které zvládnou osm kilometrů a nerovný terén."
        ),
        map_url="https://mapy.com/s/bupomahunu",
        official_url=(
            "https://www.kraj-lbc.cz/aktuality/okolim-cvikova-waltro-karluv-"
            "odpocinek-a-skalni-kaple-u-drnovce-n575612.htm"
        ),
        stroller_access=_("Ne"),
        admission=_("Zdarma"),
        opening_hours=_("Volně přístupné"),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="duty-kamen",
                description=_(
                    "Pro kratší výlet podobnou skalní krajinou zvolte okruh "
                    "kolem Dutého kamene."
                ),
            ),
        ),
        image="vylety/kunraticke-svycarsko.jpg",
        image_width=1280,
        image_height=960,
    ),
    Attraction(
        slug="milstejn-nadeje",
        name=_("Milštejn a Naděje"),
        summary=_(
            "Lesní okruh za skalními pozůstatky hradu a chladnou horskou nádrží."
        ),
        description=_(
            "Pestrý okruh z Trávníku vede přes skalní areál zaniklého hradu "
            "Milštejn k přehradní nádrži Naděje. Cestou se střídají lesní "
            "cesty, pískovcové skály, stopy po těžbě mlýnských kamenů a údolí "
            "Hamerského potoka."
        ),
        description_paragraphs=(
            _(
                "Hrad Milštejn vznikl na pískovcové skále u staré obchodní "
                "stezky mezi Českem a Lužicí. Po opuštění hradu jeho podobu "
                "zásadně proměnila dlouhá těžba kvalitního pískovce pro výrobu "
                "mlýnských kamenů. Dnes místo připomíná především mohutný "
                "skalní útvar, brána, dutiny a jen nepatrné zbytky zdiva."
            ),
            _(
                "Nádrž Naděje byla vybudována v letech 1937 až 1938 na "
                "Hamerském potoce jako zásobárna vody pro mlýn a pilu. Leží v "
                "hlubokém zalesněném údolí a její voda zůstává velmi chladná "
                "i během léta."
            ),
            _(
                "Základní okruh měří 8,2 kilometru a vede místy po užších "
                "lesních cestách. Pro kočárek je připravená samostatná "
                "varianta dlouhá 8,4 kilometru, která využívá schůdnější cesty "
                "a přitom propojuje stejné hlavní cíle."
            ),
        ),
        distance_km=8.2,
        distance_kind="walking_loop",
        driving_distance_km=4,
        difficulty=MODERATE,
        family_tip=_(
            "Skalní brána a dutiny na Milštejně jsou pro děti dobrodružným "
            "cílem; v teplém dni lze výlet spojit s koupáním v Naději."
        ),
        map_url=None,
        official_url="https://www.luzicke-hory.cz/mista/index.php?pg=zmmilsc",
        stroller_access=_("Hlavní trasa ne; kočárková varianta 8,4 km ano."),
        admission=_("Zdarma"),
        opening_hours=_("Volně přístupné"),
        travel_tip=_("Do Trávníku je možné dojet autem nebo autobusem."),
        route_variants=(
            RouteVariant(
                name=_("Hlavní okruh přes Milštejn a Naději"),
                distance_km=8.2,
                map_url="https://mapy.com/s/nojudacesu",
                description=_(
                    "Lesní okruh přes skalní areál Milštejna, nádrž Naděje "
                    "a osadu Naděje není vhodný pro kočárek."
                ),
            ),
            RouteVariant(
                name=_("Kočárková varianta"),
                distance_km=8.4,
                map_url="https://mapy.com/s/galusenedu",
                description=_(
                    "Mírně delší varianta vede po cestách sjízdných s "
                    "kočárkem a propojuje Milštejn s nádrží Naděje."
                ),
            ),
        ),
        related_trips=(
            TripRelation(
                target_kind="swimming",
                target_slug="nadrz-nadeje",
                description=_(
                    "Okruh vede kolem nádrže Naděje, kde se můžete osvěžit v "
                    "chladné horské vodě."
                ),
            ),
        ),
        image="vylety/milstejn.jpg",
        image_width=4000,
        image_height=3000,
    ),
    Attraction(
        slug="skalni-hrad-sloup",
        name=_("Skalní hrad Sloup"),
        summary=_("Skalní památka s vyhlídkami, chodbami a poustevnickou historií."),
        description=_(
            "Skalní hrad ve Sloupu v Čechách je oblíbeným rodinným cílem s "
            "prohlídkovým okruhem vytesaným do pískovce. Návštěvu lze spojit s "
            "procházkou obcí nebo dalšími cíli v okolních skalách."
        ),
        description_paragraphs=(
            _(
                "Pískovcový suk se zvedá více než třicet metrů nad okolní terén. "
                "Jeho svislé až převislé stěny, rozlehlé horní plató a množství "
                "prostor vytesaných uvnitř skály vytvářejí neobvyklý prohlídkový "
                "areál."
            ),
            _(
                "Ze středověkého hradu se zachovaly především skalní místnosti "
                "a zbytky staveb. Místo později výrazně proměnily barokní úpravy "
                "spojené s poustevnou. Jednotlivé světské i sakrální prostory "
                "propojují chodby, schodiště a ochozy."
            ),
            _(
                "Interiéry nejsou zaplněné sbírkami; hlavní dojem vytváří samotná "
                "skála, prázdné vytesané prostory a výhledy z horní části. Právě "
                "spojení přírodní dominanty s lidskými zásahy dává místu jeho "
                "výraznou atmosféru."
            ),
        ),
        distance_km=8,
        distance_kind="driving",
        difficulty=MODERATE,
        family_tip=_("Počítejte se schody a dohledem nad dětmi na vyhlídkách."),
        map_url="https://mapy.com/s/judatacovu",
        official_url="https://www.hrad-sloup.cz/",
        stroller_access=_("Ne"),
        admission=_("Dítě 70 Kč, dospělý 140 Kč, rodinné vstupné 330 Kč."),
        opening_hours=_("V létě denně 9–17, mimo léto pouze o víkendech 9–16."),
        related_trips=(
            TripRelation(
                target_kind="swimming",
                target_slug="koupaliste-sloup",
                description=_(
                    "Po prohlídce skalního hradu se můžete v létě osvěžit na "
                    "koupališti ve Sloupu."
                ),
            ),
            TripRelation(
                target_kind="restaurant",
                target_slug="na-strazi",
                description=_(
                    "Po prohlídce hradu můžete pokračovat za moderní gastronomií "
                    "do restaurace Na Stráži."
                ),
            ),
            TripRelation(
                target_kind="restaurant",
                target_slug="sloupska-terasa",
                description=_("Na zmrzlinu a zákusky se zastavte ve Sloupské Terase."),
            ),
        ),
        travel_tip=_("Do Sloupu v Čechách je možné dojet také autobusem."),
        image="vylety/sloup.jpg",
        image_width=1600,
        image_height=1200,
    ),
    Attraction(
        slug="pacinek-glass",
        name=_("Pačinek Glass a Skleněná zahrada"),
        summary=_("Barevná skleněná zahrada a živá sklářská tradice v Kunraticích."),
        description=_(
            "Areál Pačinek Glass spojuje venkovní Skleněnou zahradu, umělecké "
            "sklo a možnost nahlédnout do práce sklářů. Pro děti je atraktivní "
            "především zahrada plná skleněných rostlin a zvířat."
        ),
        description_paragraphs=(
            _(
                "Skleněné květy, listy a další objekty jsou zasazené přímo mezi "
                "živé rostliny. Zahrada proto působí jinak v ranním a večerním "
                "světle i v jednotlivých ročních obdobích, kdy se sklo střídavě "
                "propojuje se zelení, podzimními barvami nebo námrazou."
            ),
            _(
                "Součástí areálu je tradiční sklářská huť, kde lze zblízka "
                "pozorovat ruční výrobu, a také brusírna a prodejní galerie "
                "moderního skla. Návštěva tak ukazuje cestu výrobku od žhavé "
                "skloviny přes opracování až po hotové umělecké dílo."
            ),
            _(
                "Zahrada není jen doplňkem sklárny, ale samostatnou venkovní "
                "expozicí. Díky spojení skutečných a skleněných rostlin nabízí "
                "pokaždé trochu jinou podívanou a dobře funguje i jako kratší "
                "zastávka s dětmi."
            ),
        ),
        distance_km=4,
        difficulty=EASY,
        family_tip=_(
            "Dobrá volba pro všechny věkové skupiny a také pro kratší program."
        ),
        map_url="https://mapy.com/s/fejukapobu",
        official_url="https://www.pacinekglass.com/sklenena-zahrada",
        stroller_access=_("Ano"),
        admission=_(
            "100 Kč za osobu, děti do 5 let zdarma; galerie a Skleněný kostel "
            "mohou být za příplatek."
        ),
        opening_hours=_(
            "Skleněná zahrada je přístupná stále; provoz hutě a dalších expozic "
            "ověřte na webu."
        ),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="ajeto-lindava",
                description=_(
                    "Pokračujte za další ukázkou ruční výroby skla a do "
                    "Sklářské krčmy v Lindavě."
                ),
            ),
            TripRelation(
                target_kind="attraction",
                target_slug="stezky-brniste",
                description=_(
                    "Na Skleněné stezce v Brništi potkáte další díla Jiřího "
                    "Pačinka zasazená přímo do krajiny."
                ),
            ),
        ),
        image="vylety/pacinek.jpg",
        image_width=1600,
        image_height=1064,
    ),
    Attraction(
        slug="ajeto-lindava",
        name=_("Sklárna AJETO v Lindavě"),
        summary=_("Sklářská huť, zážitkové prohlídky a Sklářská krčma."),
        description=_(
            "Ve sklárně AJETO lze sledovat ruční výrobu skla a po předchozí "
            "domluvě využít nabídku exkurzí a sklářských zážitků. Výlet můžete "
            "spojit s návštěvou přilehlé Sklářské krčmy."
        ),
        distance_km=6,
        distance_kind="driving",
        difficulty=EASY,
        family_tip=_("Exkurzi nebo zážitek pro děti si předem ověřte a rezervujte."),
        map_url="https://mapy.com/s/budufokado",
        official_url="https://www.ajetoglass.com/",
        stroller_access=_("Ne"),
        admission=_("Dospělý 150 Kč, dítě 100 Kč, rodinné vstupné 450 Kč."),
        opening_hours=_("Prohlídky od pondělí do pátku 9–13."),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="pacinek-glass",
                description=_(
                    "Sklářský výlet můžete doplnit procházkou mezi skleněnými "
                    "rostlinami v Kunraticích."
                ),
            ),
        ),
        image="vylety/ajeto.jpg",
        image_width=1600,
        image_height=1064,
    ),
    Attraction(
        slug="panska-skala",
        name=_("Panská skála"),
        summary=_(
            "Čedičové varhany známé z pohádky Pyšná princezna a krátká procházka."
        ),
        description=_(
            "Panská skála u Kamenického Šenova je jednou z nejznámějších "
            "geologických památek v Česku. Pravidelné čedičové sloupce "
            "připomínají píšťaly varhan a místo poznají i děti z pohádky "
            "Pyšná princezna."
        ),
        description_paragraphs=(
            _(
                "Dnešní podoba skály se odkryla při někdejší těžbě. Pěti až "
                "šestiboké sloupce vznikly při chladnutí magmatu, jsou téměř "
                "svislé a dosahují délky až patnáct metrů."
            ),
            _(
                "Z horní části se otevírá výhled na Kamenický Šenov a okolní "
                "kopce. Pod skálou leží malé jezírko naplněné srážkovou vodou "
                "v prohlubni po těžbě a na jihovýchodním úpatí stojí historický "
                "Mariánský sloup."
            ),
            _(
                "Od parkoviště je to ke skále jen krátká cesta, takže jde o "
                "dobrý cíl i na půldenní výlet nebo jako zastávku při cestě "
                "do České Kamenice."
            ),
        ),
        distance_km=13,
        distance_kind="driving",
        difficulty=EASY,
        family_tip=_(
            "Krátký a snadno dostupný výlet; na mokrém čediči dávejte pozor na uklouznutí."
        ),
        map_url="https://mapy.com/s/nupocenega",
        official_url=(
            "https://www.kamenicky-senov.cz/turistika/turisticke-informacni-"
            "centrum-a-parkoviste/?lang=cs&mapa-webu=1"
        ),
        stroller_access=_("Ano"),
        admission=_(
            "Vstup zdarma; parkovné 70 Kč za prvních 75 minut, poté 50 Kč za "
            "každou další hodinu; od listopadu do března 100 Kč za den."
        ),
        opening_hours=_("Skála je volně přístupná celoročně."),
        image="vylety/panska-skala.jpg",
        image_width=1360,
        image_height=900,
    ),
    Attraction(
        slug="klic",
        name=_("Výstup na Klíč"),
        summary=_("Výrazný vrchol Lužických hor s dalekým kruhovým výhledem."),
        description=_(
            "Klíč je jedním z nejznámějších vrcholů Lužických hor. Výstup vede "
            "lesem a v závěru prudším kamenitým svahem, odměnou je rozsáhlý "
            "výhled do krajiny."
        ),
        description_paragraphs=(
            _(
                "Osamocený znělcový vrch má nápadný kuželovitý až pyramidový "
                "tvar a tvoří výraznou dominantu nad Svorem a Novým Borem. "
                "Nejnáročnější je závěrečná část stoupání, kde se cesta vine "
                "kamenitým svahem."
            ),
            _(
                "Na trase minete Kamzičí studánku a kamenné moře. Z vrcholu se "
                "otevírá kruhový rozhled do Lužických hor i vzdálenější krajiny; "
                "za velmi dobré viditelnosti lze zahlédnout také Říp. Klíč je "
                "působivý při západu slunce i v podzimních barvách."
            ),
        ),
        distance_km=2.8,
        distance_kind="walking_loop",
        driving_distance_km=6,
        difficulty=MODERATE,
        family_tip=_("Vhodné pro zdatnější děti; vezměte pevnou obuv a dostatek pití."),
        map_url="https://mapy.com/s/masavogaza",
        official_url="https://www.liberecky-kraj.cz/dr-cs/636-vrch-klic.html",
        stroller_access=_("Ne"),
        admission=_("Zdarma"),
        opening_hours=_("Volně přístupné"),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="polevsko",
                description=_(
                    "Po výstupu můžete pokračovat do nedalekého Polevska za "
                    "cyklistikou nebo sezonními aktivitami."
                ),
            ),
        ),
        image="vylety/klic.jpg",
        image_width=1600,
        image_height=1064,
    ),
    Attraction(
        slug="hvozd",
        name=_("Výstup na Hvozd"),
        summary=_(
            "Hraniční vrchol s rozhlednou, horskou chatou a výhledy do Čech i Saska."
        ),
        description=_(
            "Z Krompachu vystoupáte po červené značce na Hvozd, výrazný "
            "hraniční vrchol vysoký 749 metrů. Šest a půl kilometru dlouhý "
            "okruh nabízí horskou cestu, daleké rozhledy a možnost občerstvení "
            "na vrcholu."
        ),
        description_paragraphs=(
            _(
                "Kamenná rozhledna Hochwaldturm stojí na německé straně vrcholu. "
                "Za dobré viditelnosti je z ní možné přehlédnout Lužické hory, "
                "Žitavskou pánev i vzdálenější hřebeny."
            ),
            _(
                "Přímo u vrcholu se nachází horská chata Hochwaldbaude, kde se "
                "lze během výletu zastavit na jídlo. Otevírací dobu chaty i "
                "rozhledny je vhodné ověřit před cestou."
            ),
            _(
                "Do Krompachu se můžete z Cvikova dopravit také autobusem. "
                "Trasa vede lesním a místy kamenitým terénem, proto není vhodná "
                "pro kočárek."
            ),
        ),
        distance_km=6.5,
        distance_kind="walking_loop",
        driving_distance_km=10,
        difficulty=MODERATE,
        family_tip=_("Vhodné pro děti zvyklé na delší stoupání; přibalte pevnou obuv."),
        map_url="https://mapy.com/s/hacajetave",
        official_url=(
            "https://www.hochwaldbaude.de/bergbaude-im-naturpark-zittauer-gebirge"
        ),
        stroller_access=_("Ne"),
        admission=_("Výlet zdarma; vstup na rozhlednu je placený."),
        opening_hours=_(
            "Trasa je volně přístupná; provoz rozhledny a chaty ověřte předem."
        ),
        travel_tip=_("Do Krompachu je možné dojet také autobusem ze Cvikova."),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="oybin",
                description=_(
                    "Další výrazný vrchol Žitavských hor nabízí skalní hrad "
                    "a klášter Oybin."
                ),
            ),
            TripRelation(
                target_kind="restaurant",
                target_slug="resort-hvozd",
                description=_(
                    "Před výstupem nebo po návratu se můžete najíst v restauraci "
                    "Resortu Hvozd."
                ),
            ),
            TripRelation(
                target_kind="restaurant",
                target_slug="pivovar-krompach",
                description=_(
                    "Výlet lze zakončit českou kuchyní a vlastním pivem v "
                    "Pivovaru Krompach."
                ),
            ),
        ),
        image="vylety/hvozd.jpg",
        image_width=1600,
        image_height=1068,
    ),
    Attraction(
        slug="polevsko",
        name=_("Polevsko v létě i v zimě"),
        summary=_("Rodinné lyžování, cyklistika a výlety v krajině nad Novým Borem."),
        description=_(
            "Polevsko nabízí v zimě menší lyžařský areál. V létě se můžete vydat "
            "po naučné stezce Za polevskými obry, která propojuje zdejší mohutné "
            "stromy, nebo navštívit bikepark."
        ),
        description_paragraphs=(
            _(
                "Bikepark Polevsko nabízí trasy pro zkušenější jezdce i děti, "
                "které si chtějí jízdu v terénu teprve vyzkoušet. Okolní cesty "
                "umožňují spojit návštěvu areálu s kratší rodinnou projížďkou "
                "nebo delším cyklistickým výletem."
            ),
            _(
                "Krajina kolem Polevska rychle přechází od horských svahů k "
                "pastvinám a klidnějším cestám. Díky tomu si zde mohou trasu "
                "vybrat rodiny, rekreační cyklisté i sportovněji založení jezdci."
            ),
        ),
        distance_km=12,
        distance_kind="driving",
        difficulty=EASY,
        family_tip=_(
            "Aktuální provoz areálu a podmínky vždy zkontrolujte před odjezdem."
        ),
        map_url="https://mapy.com/s/gunedatolu",
        official_url="https://www.polevsko.ski/",
        stroller_access=_("Ne"),
        admission=_("Ceny skipasů a podmínky bikeparku ověřte na webu areálu."),
        opening_hours=_(
            "Naučná stezka je přístupná celoročně, bikepark podle aktuálních "
            "informací a zimní areál podle sněhových podmínek."
        ),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="klic",
                description=_(
                    "Pro náročnější pěší výlet v okolí vystoupejte na výrazný "
                    "vrchol Klíč."
                ),
            ),
        ),
        image="vylety/polevsko.jpg",
        image_width=1600,
        image_height=1200,
    ),
    Attraction(
        slug="sloni-kameny",
        name=_("Sloní kameny"),
        summary=_("Krátká rodinná procházka k nápadným bílým skalám u Jítravy."),
        description=_(
            "Bílé neboli Sloní kameny připomínají hřbety odpočívajících slonů. "
            "Dvoukilometrová pěší trasa od Jítravy vede mírným terénem a patří "
            "k nejjednodušším skalním výletům v Lužických horách."
        ),
        description_paragraphs=(
            _(
                "Skály jsou vidět už ze silnice a od malého parkoviště k nim "
                "dojdete po červené značce přibližně za dvacet minut velmi "
                "pomalé chůze. Pozvolné stoupání zvládnou i menší děti."
            ),
            _(
                "Nápadně světlý pískovec vytváří zaoblené bloky, úzké průchody "
                "a drobné prohlubně. Jde o chráněnou přírodní památku, proto je "
                "zakázáno lézt přímo na skály nebo do nich zasahovat."
            ),
            _(
                "Kdo má dost sil, může pokračovat po mezinárodní naučné stezce "
                "směrem k Vraním skalám. Tato delší varianta už vede náročnějším "
                "terénem a není vhodná pro kočárky."
            ),
        ),
        distance_km=2,
        distance_kind="walking_loop",
        driving_distance_km=18,
        difficulty=EASY,
        family_tip=_("Nenáročný výlet pro malé děti; na chráněné skály se nesmí lézt."),
        map_url="https://mapy.com/s/bokedakepe",
        official_url=(
            "https://www.rynoltice.cz/obec/zajimavosti/tipy-na-vylety/"
            "po-hrbetech-slonu-251cs.html?lang=cs&mapa-webu=1"
        ),
        stroller_access=_("Ano"),
        admission=_("Zdarma"),
        opening_hours=_("Volně přístupné"),
        image="vylety/sloni-kameny.jpg",
        image_width=800,
        image_height=517,
    ),
    Attraction(
        slug="loreta-rumburk",
        name=_("Loreta Rumburk"),
        summary=_("Barokní poutní areál s nejseverněji položenou loretou v Evropě."),
        description=_(
            "Loretánská kaple Panny Marie v Rumburku vznikla v letech 1704 až "
            "1709 podle návrhu Jana Lucase Hildebrandta. Je přesnou kopií "
            "Svaté chýše v italském Loretu, zde však zdobenou místním pískovcem."
        ),
        description_paragraphs=(
            _(
                "Bohatě zdobená kaple stojí uprostřed ambitu bývalého "
                "kapucínského kláštera. Spolu s kostelem svatého Vavřince "
                "vytváří klidný uzavřený areál jen několik kroků od centra "
                "Rumburku."
            ),
            _(
                "Návštěva ukazuje architekturu, výzdobu i duchovní tradici "
                "místa. V areálu se konají výstavy a je zde také expozice "
                "církevního umění, k níž se však vystupuje po schodech."
            ),
            _(
                "Hlavní kaple, ambity a kostel jsou přístupné s kočárkem. "
                "Aktuální program a případné změny návštěvní doby si ověřte "
                "před cestou na oficiálním webu."
            ),
        ),
        distance_km=31,
        distance_kind="driving",
        difficulty=EASY,
        family_tip=_(
            "Klidný kulturní program vhodný i do horšího počasí a pro více generací."
        ),
        map_url="https://mapy.com/s/fokuhejoko",
        official_url=("https://www.loretarumburk.cz/kontakt-navstevni-doba-a-vstupne/"),
        stroller_access=_(
            "Ano do hlavních prostor; expozice církevního umění je pouze po schodech."
        ),
        admission=_("Dospělý 80 Kč, dítě od 7 do 15 let 40 Kč, děti do 6 let zdarma."),
        opening_hours=_(
            "Od listopadu do dubna v sobotu 9–16:30; od května do října "
            "od úterý do soboty 9–16:30."
        ),
        image="vylety/loreta-rumburk.jpg",
        image_width=400,
        image_height=274,
    ),
    Attraction(
        slug="transborder-chrastava",
        name=_("Transbordér u Chrastavy"),
        summary=_(
            "Ruční převoz přes Lužickou Nisu na výletě po cyklostezce u Chrastavy."
        ),
        description=_(
            "Hlavním zážitkem osmikilometrového okruhu je transbordér u "
            "Andělské Hory: zavěšená kabina, kterou se vlastní silou převezete "
            "přes Lužickou Nisu. Trasa vede převážně po cyklostezce a spojuje "
            "přírodu s technickými památkami."
        ),
        description_paragraphs=(
            _(
                "Kabina překonává řeku na více než dvacetimetrovém závěsu. "
                "Cestující otáčením kliky pohánějí jednoduchý mechanismus a "
                "převezou na druhý břeh sebe, jízdní kolo i dětský kočárek."
            ),
            _(
                "Při pokračování směrem do Chrastavy minete výraznou secesní "
                "textilní továrnu z červených cihel. Ve městě lze navštívit také "
                "muzeum hasičské techniky nebo expozici vodního náhonu a "
                "Francisovy turbíny."
            ),
            _(
                "Transbordér je volně přístupný a funguje bez obsluhy, takže "
                "samotné převezení je pro děti součástí dobrodružství. Při "
                "vyšším stavu vody vždy respektujte aktuální podmínky na místě."
            ),
        ),
        distance_km=8.3,
        distance_kind="walking_loop",
        driving_distance_km=29,
        difficulty=EASY,
        family_tip=_(
            "Děti si mohou kabinu samy pohánět; menším pomůže s klikou dospělý."
        ),
        map_url="https://mapy.com/s/latagomabe",
        official_url=(
            "https://www.chrastava.eu/volny-cas/turista/co-navstivit/"
            "transborder-1905cs.html"
        ),
        stroller_access=_("Ano"),
        admission=_("Zdarma"),
        opening_hours=_("Volně přístupné celoročně."),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="privoz-mlynky-vyhlidky",
                description=_(
                    "Další přívoz, který děti ovládají vlastní silou, najdete "
                    "u České Kamenice."
                ),
            ),
        ),
        image="vylety/transborder-chrastava.jpg",
        image_width=1280,
        image_height=960,
    ),
    Attraction(
        slug="lesopark-horka",
        name=_("Lesopark Horka"),
        summary=_("Les plný hádanek, herních prvků a odpočinkových míst pod Ještědem."),
        description=_(
            "Volnočasový lesopark Horka v Rozstání proměňuje procházku lesem "
            "v hravé objevování. Na jednom až dvou kilometrech můžete řešit "
            "hádanky, zkoušet herní prvky a zastavovat se na mnoha místech "
            "připravených pro děti."
        ),
        description_paragraphs=(
            _(
                "U vstupu návštěvníky vítá spící obr Máza, který po zavolání "
                "odpovídá. V areálu je přibližně pět set hádanek a zajímavostí, "
                "lesní hřiště, lanové prvky, amfiteátr i dráhy pro golfové míčky."
            ),
            _(
                "Cesty jsou sjízdné s kočárkem a podél nich najdete dostatek "
                "laviček a míst k odpočinku. Délku procházky lze snadno "
                "přizpůsobit věku dětí a času, který chcete v lese strávit."
            ),
            _(
                "Parkování pro návštěvníky je vyhrazené pod budovou golfového "
                "areálu. V jeho sousedství je restaurace, dětský koutek a další "
                "placené aktivity, které lze s návštěvou lesoparku spojit."
            ),
        ),
        distance_km=35,
        distance_kind="driving",
        difficulty=EASY,
        family_tip=_(
            "Délku procházky si zvolíte podle nálady; dostatek zastávek zabaví i menší děti."
        ),
        map_url=None,
        official_url="https://golfjested.cz/lesopark-horka/",
        stroller_access=_("Ano"),
        admission=_("Zdarma"),
        opening_hours=_("Volně přístupné"),
        route_variants=(
            RouteVariant(
                name=_("Procházka lesoparkem"),
                distance_km=1,
                distance_km_max=2,
                map_url="https://mapy.com/s/leredazeka",
                description=_(
                    "Okruh můžete zkrátit nebo prodloužit podle vybraných "
                    "herních zastávek a věku dětí."
                ),
            ),
        ),
        image="vylety/lesopark-horka.jpg",
        image_width=1024,
        image_height=684,
    ),
    Attraction(
        slug="stezky-brniste",
        name=_("Stezky kolem Brniště"),
        summary=_("Tři rodinné trasy za skalními sochami, hastrmany a českým sklem."),
        description=_(
            "V Brništi si můžete vybrat ze tří tematických stezek různé délky. "
            "Každá má vlastní mapu a jiný příběh: umění ukryté v lese, vodní "
            "svět hastrmanů nebo skleněná díla zasazená do krajiny."
        ),
        description_paragraphs=(
            _(
                "Trasy začínají na různých místech v okolí obce, proto si před "
                "odjezdem otevřete mapu vybrané varianty. Všechny jsou volně "
                "přístupné a lze je projít samostatně."
            ),
            _(
                "Stezky propojují přírodní prostředí s úkoly, herními prvky a "
                "uměleckými objekty. Díky tomu se hodí pro rodiny, které chtějí "
                "dětem rozdělit procházku na řadu menších objevů."
            ),
        ),
        distance_km=10,
        distance_kind="driving",
        difficulty=EASY,
        family_tip=_(
            "Vyberte trasu podle věku dětí: od krátkých skalních soch po šestikilometrové hastrmany."
        ),
        map_url=None,
        official_url=(
            "https://www.brniste.cz/volny-cas/turistika-5/"
            "mapa-stezek-v-brnisti/?rss=200"
        ),
        stroller_access=_("Ano; pro Sochy ve skalách je vhodnější terénní kočárek."),
        admission=_("Zdarma"),
        opening_hours=_("Všechny tři stezky jsou volně přístupné celoročně."),
        route_variants=(
            RouteVariant(
                name=_("Sochy ve skalách"),
                distance_km=1.5,
                map_url="https://mapy.com/s/jenojasole",
                description=_(
                    "Lesní trasa mezi trolly, bohyněmi, strážci lesa a land "
                    "artem vede až ke znovuobjevené kapličce z roku 1863."
                ),
            ),
            RouteVariant(
                name=_("Stezka Hastrmanů"),
                distance_km=6,
                map_url="https://mapy.com/s/jatubucura",
                description=_(
                    "Devět zastavení s úkoly a herními prvky provází světem "
                    "potoků, mokřadů, mlýnů, hastrmanů a víl."
                ),
            ),
            RouteVariant(
                name=_("Skleněná stezka"),
                distance_km=3.7,
                map_url="https://mapy.com/s/nujepuhota",
                description=_(
                    "Cesta ke Schrötrově kapli míjí skleněný strom a díla "
                    "Bořka Šípka i Jiřího Pačinka; zpět se vraťte stejnou trasou, "
                    "okolní pozemky jsou soukromé."
                ),
            ),
        ),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="pacinek-glass",
                description=_(
                    "Po Skleněné stezce pokračujte za dalšími díly Jiřího "
                    "Pačinka do sklářské zahrady v Kunraticích."
                ),
            ),
        ),
        image="vylety/brniste-stezky.jpg",
        image_width=1440,
        image_height=1080,
    ),
    Attraction(
        slug="privoz-mlynky-vyhlidky",
        name=_("Přívoz, Mlýnky a vyhlídky"),
        summary=_("Dětský přívoz, vodní miniatury a skalní vyhlídky v České Kamenici."),
        description=_(
            "Od městského koupaliště se vydejte k rybníku s ručním přívozem, "
            "na kterém se děti mohou vlastní silou převézt na druhý břeh. "
            "Krátká cesta pokračuje do parku miniatur Mlýnky a stejnou trasou "
            "se vrací zpět."
        ),
        description_paragraphs=(
            _(
                "Mlýnky tvoří modely českokamenických domů rozmístěné kolem "
                "potůčku. Voda roztáčí pohyblivé části mlýna, pily a dalších "
                "staveb; děti mohou také pumpovat vodu, zvedat hráze a měnit "
                "její tok."
            ),
            _(
                "Delší okruh stoupá lesem na pískovcové vyhlídky Žába a "
                "Ponorka. Ponorku tvoří tři skalní věže přístupné po vytesaných "
                "schodech a propojené můstky se zábradlím. Z nejvyšší skály je "
                "výhled na Jehlu, Zámecký vrch a okolní krajinu."
            ),
            _(
                "Podle sil můžete do trasy zařadit také čedičovou Jehlu. K její "
                "malé vyhlídkové plošině vede stezka po úzkém skalnatém "
                "hřbítku, proto se tato část nehodí pro kočárky ani pro děti, "
                "které si nejsou jisté v prudším terénu."
            ),
        ),
        distance_km=4,
        distance_kind="walking_loop",
        driving_distance_km=22,
        alternate_distance_label=_("K Mlýnkům a zpět"),
        alternate_distance_km=1.4,
        difficulty=MODERATE,
        family_tip=_(
            "Krátká varianta k přívozu a Mlýnkům je nenáročná; na vyhlídkách "
            "počítejte se schody a dohledem nad dětmi."
        ),
        map_url="https://mapy.com/s/gacumosara",
        official_url=("https://ceska-kamenice.cz/mapa-vyletu/okruh-vyhlidky-brand/"),
        stroller_access=_(
            "K přívozu a Mlýnkům ano; celý okruh přes skalní vyhlídky ne."
        ),
        admission=_("Zdarma"),
        opening_hours=_("Přívoz, Mlýnky i vyhlídky jsou volně přístupné."),
        related_trips=(
            TripRelation(
                target_kind="swimming",
                target_slug="koupaliste-ceska-kamenice",
                description=_(
                    "Po výletě se můžete osvěžit na nedalekém městském "
                    "koupališti s bistrem."
                ),
            ),
            TripRelation(
                target_kind="attraction",
                target_slug="transborder-chrastava",
                description=_(
                    "Podobné dobrodružství s ručním převozem přes vodu zažijete "
                    "na transbordéru u Chrastavy."
                ),
            ),
        ),
        image="vylety/ceska-kamenice-privoz.jpg",
        image_width=1600,
        image_height=1200,
    ),
    Attraction(
        slug="oybin",
        name=_("Hrad a klášter Oybin"),
        summary=_("Romantické zříceniny na skalním masivu v Žitavských horách."),
        description=_(
            "Hrad a klášter Oybin stojí na výrazném pískovcovém masivu nad "
            "lázeňským městečkem. Rodinný výlet spojuje historii, skály, výhledy "
            "a možnost jízdy úzkorozchodnou železnicí."
        ),
        distance_km=17,
        distance_kind="driving",
        difficulty=MODERATE,
        family_tip=_("Na hrad vede stoupání a schody; pro malé děti se hodí nosítko."),
        map_url="https://mapy.com/s/locacosoge",
        official_url="https://oybin.com/erleben-entdecken/burg-und-kloster/",
        stroller_access=_("Ne"),
        admission=_("2–9 €; cena se liší podle věku návštěvníka a sezony."),
        opening_hours=_("V létě denně 9–18, mimo léto denně 10–16."),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="motyli-dum-jonsdorf",
                description=_(
                    "Výlet do Žitavských hor můžete doplnit krytým programem "
                    "se zvířaty v nedalekém Jonsdorfu."
                ),
            ),
            TripRelation(
                target_kind="attraction",
                target_slug="hvozd",
                description=_(
                    "Pro pěší horský výlet s rozhlednou vystoupejte na nedaleký "
                    "hraniční vrchol Hvozd."
                ),
            ),
        ),
        travel_tip=MOUNTAIN_EXPRESS_TIP,
        image="vylety/oybin.jpg",
        image_width=1600,
        image_height=1200,
    ),
    Attraction(
        slug="motyli-dum-jonsdorf",
        name=_("Dům exotických zvířat (Exotenhaus) Jonsdorf"),
        summary=_(
            "Plazi, obojživelníci, hmyz a mořské akvárium; motýlí část je "
            "momentálně uzavřená."
        ),
        description=_(
            "Exotenhaus představuje přibližně 40 různých tropických živočichů "
            "v teráriích: ještěry, želvy, hady, obojživelníky, hmyz, pavouky "
            "a štíry. Výrazným prvkem expozice je třímetrové mořské akvárium "
            "o objemu 2 000 litrů s korálovými rybami a živými korály. Část "
            "s motýly je momentálně uzavřená."
        ),
        description_paragraphs=(
            _(
                "Expozice je bezbariérová a lze ji navštívit s kočárkem, takže "
                "dobře poslouží jako rodinný program i za deště. Děti mohou "
                "zblízka porovnat různé druhy plazů, obojživelníků a bezobratlých "
                "živočichů."
            ),
            _(
                "Návštěvu lze spojit s procházkou lázeňským Jonsdorfem. U rybníka "
                "Gondelfahrt najdete lodičky, kachny, ryby a dětské hřiště; pro "
                "zdatnější výletníky jsou v okolí také Jonsdorfské skalní město "
                "a další značené cesty."
            ),
            _(
                "V teplých dnech můžete program doplnit koupáním v místním "
                "horském koupališti. Exotenhaus tak může být samostatným cílem "
                "na kratší část dne i zastávkou při delším výletu do Žitavských "
                "hor."
            ),
        ),
        distance_km=15,
        distance_kind="driving",
        difficulty=EASY,
        family_tip=_("Celoroční krytý program vhodný i za deště."),
        map_url="https://mapy.com/s/mamubazode",
        official_url="https://www.exotenhaus.info/",
        stroller_access=_("Ano"),
        admission=_("Dospělý 9 €, dítě 4,50 €, rodinné vstupné 22,50 €."),
        opening_hours=_("Denně 10–18."),
        related_trips=(
            TripRelation(
                target_kind="swimming",
                target_slug="koupaliste-jonsdorf",
                description=_(
                    "V teplém dni spojte návštěvu s koupáním v horském "
                    "koupališti v Jonsdorfu."
                ),
            ),
            TripRelation(
                target_kind="attraction",
                target_slug="oybin",
                description=_(
                    "Pro delší výlet v Žitavských horách pokračujte k hradu "
                    "a klášteru Oybin."
                ),
            ),
        ),
        travel_tip=MOUNTAIN_EXPRESS_TIP,
        image="vylety/jonsdorf.jpg",
        image_width=1600,
        image_height=1200,
    ),
)


ATTRACTIONS_BY_SLUG = {item.slug: item for item in ATTRACTIONS}


@dataclass(frozen=True)
class SwimmingTip:
    slug: str
    name: object
    description: object
    official_url: str | None
    admission: object
    opening_hours: object
    distance_km: int | float | None = None
    distance_label: object | None = None
    map_url: str | None = None
    travel_tip: object | None = None
    related_trips: tuple[TripRelation, ...] = ()


SWIMMING_IMAGE = "vylety/koupaliste-jonsdorf.jpg"
SWIMMING_IMAGE_WIDTH = 1920
SWIMMING_IMAGE_HEIGHT = 1081


SWIMMING_TIPS = (
    SwimmingTip(
        slug="koupaliste-sloup",
        name=_("Koupaliště Sloup v Čechách"),
        description=_("Přírodní koupaliště v kempu s lanovým centrem a občerstvením."),
        official_url="https://koupaliste.sloupvcechach.cz/",
        admission=_(
            "Dítě do 6 let 30 Kč, dítě od 6 do 15 let 45 Kč, návštěvníci nad "
            "15 let 70 Kč; parkování auta 100 Kč."
        ),
        opening_hours=_("V létě 7–18."),
        travel_tip=_("Ze Cvikova se sem můžete vydat také autobusem."),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="skalni-hrad-sloup",
                description=_(
                    "Koupání můžete spojit s prohlídkou skalního hradu "
                    "a poustevny ve Sloupu."
                ),
            ),
            TripRelation(
                target_kind="restaurant",
                target_slug="na-strazi",
                description=_(
                    "Po koupání můžete zajít na moderní gastronomii do restaurace "
                    "Na Stráži."
                ),
            ),
            TripRelation(
                target_kind="restaurant",
                target_slug="sloupska-terasa",
                description=_(
                    "Na zmrzlinu nebo zákusek se zastavte ve Sloupské Terase."
                ),
            ),
        ),
    ),
    SwimmingTip(
        slug="koupaliste-jablonne",
        name=_("Koupaliště Jablonné v Podještědí"),
        description=_(
            "Koupaliště v kempu s dětským hřištěm, restaurací a nafukovací "
            "skluzavkou na vodě."
        ),
        official_url="https://www.kempjablonne.cz/",
        admission=_("Dítě 30 Kč, dospělý 50 Kč."),
        opening_hours=_("V létě 8–22."),
    ),
    SwimmingTip(
        slug="nadrz-nadeje",
        name=_("Nádrž Naděje"),
        description=_(
            "Volně přístupná přehradní nádrž v hlubokém lesním údolí s "
            "chladnou horskou vodou."
        ),
        official_url=None,
        map_url="https://mapy.com/s/jamobakeju",
        admission=_("Zdarma"),
        opening_hours=_("Volně přístupné"),
        distance_km=13,
        distance_label=_("Vzdálenost od apartmánu"),
        travel_tip=_(
            "Přímo k nádrži nelze dojet autem; poslední úsek je nutné dojít "
            "pěšky. Výchozí Trávník je dostupný autem i autobusem."
        ),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="milstejn-nadeje",
                description=_(
                    "Koupání spojte s okruhem z Trávníku přes skalní areál Milštejna."
                ),
            ),
        ),
    ),
    SwimmingTip(
        slug="kristyna",
        name=_("Rekreační areál Kristýna"),
        description=_(
            "Koupání v zatopeném bývalém dole s písčitou pláží, dětským "
            "hřištěm, šlapadly a restaurací."
        ),
        official_url="https://www.kemp-kristyna.cz/",
        admission=_("70 Kč za osobu."),
        opening_hours=_("V létě 8–21."),
    ),
    SwimmingTip(
        slug="koupaliste-jonsdorf",
        name=_("Horské koupaliště Jonsdorf"),
        description=_(
            "Koupaliště s tobogánem, dětským bazénem, vzduchovou trampolínou "
            "a občerstvením."
        ),
        official_url="https://www.jonsdorf.de/gebirgsbad/",
        admission=_("Dospělý 5 €, dítě 3 €, rodinné vstupné 12 €."),
        opening_hours=_("V létě 11–19."),
        travel_tip=MOUNTAIN_EXPRESS_TIP,
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="motyli-dum-jonsdorf",
                description=_(
                    "Koupání můžete spojit s návštěvou exotických zvířat, "
                    "případně sem zamířit za horšího počasí."
                ),
            ),
        ),
    ),
    SwimmingTip(
        slug="koupaliste-dubice",
        name=_("Koupaliště Dubice"),
        description=_(
            "Koupaliště u České Lípy s tobogány a brouzdalištěm. Na přilehlém "
            "rybníce je možné vyzkoušet wakeboarding, paddleboarding i koupání "
            "a v okolí je volně přístupné 3D bludiště."
        ),
        official_url="https://www.sportlipa.cz/venkovni-koupaliste-dubice",
        admission=_(
            "30–150 Kč podle sezony, věku a času vstupu; celodenní parkování 150 Kč."
        ),
        opening_hours=_("V létě 9–21."),
        related_trips=(
            TripRelation(
                target_kind="restaurant",
                target_slug="kaido-sushi",
                description=_(
                    "Před koupáním nebo po něm se můžete zastavit na sushi "
                    "a ramen v Kaido Sushi."
                ),
            ),
        ),
    ),
    SwimmingTip(
        slug="koupaliste-ceska-kamenice",
        name=_("Městské koupaliště Česká Kamenice"),
        description=_("Koupaliště s bistrem."),
        official_url=("https://ceska-kamenice.cz/mapa-vyletu/mestske-koupaliste/"),
        admission=_("Dítě 40 Kč, dospělý 80 Kč."),
        opening_hours=_("V létě 10–19."),
        distance_km=22,
        distance_label=_("Vzdálenost autem"),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="privoz-mlynky-vyhlidky",
                description=_(
                    "Od koupaliště se vydejte přes ruční přívoz a Mlýnky na "
                    "skalní vyhlídky."
                ),
            ),
        ),
    ),
)


SWIMMING_TIPS_BY_SLUG = {item.slug: item for item in SWIMMING_TIPS}
