# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

from dataclasses import dataclass

from django.utils.translation import gettext_lazy as _


@dataclass(frozen=True)
class Attraction:
    slug: str
    name: object
    summary: object
    description: object
    distance_km: int
    difficulty: object
    family_tip: object
    map_url: str
    official_url: str
    travel_tip: object | None = None
    image: str | None = None
    image_width: int | None = None
    image_height: int | None = None
    credit_name: str | None = None
    credit_url: str | None = None
    license_name: str | None = None
    license_url: str | None = None


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
        distance_km=2,
        difficulty=EASY,
        family_tip=_(
            "Vhodné i pro kratší výlet s menšími dětmi; část cest vede lesem."
        ),
        map_url="https://mapy.cz/s/rodateluge",
        official_url="https://www.cvikov.cz/vychazkove-okruhy/ms-1081/p1=1081",
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
            "okruh umožňuje rychlejší a techničtější jízdu."
        ),
        distance_km=1,
        difficulty=EASY,
        family_tip=_(
            "Nezapomeňte na helmu; menší okruh je vhodný pro první zkušenosti."
        ),
        map_url="https://mapy.cz/turisticka?q=Pumptrack%20Cvikov",
        official_url=(
            "https://admin-storage.munipolis.com/cvikov/bulletin/files/"
            "2b5ab9d5-83b9-438d-a11e-30e8bfe85010.pdf"
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
            "terén vyžadují u menších dětí zvýšenou pozornost."
        ),
        distance_km=4,
        difficulty=MODERATE,
        family_tip=_("Pro děti, které zvládnou schody a nerovný terén; bez kočárku."),
        map_url="https://mapy.cz/turisticka?q=Dut%C3%BD%20k%C3%A1men",
        official_url="https://www.cvikov.cz/turista/ms-1091/p1=1091",
        image="vylety/duty-kamen.jpg",
        image_width=800,
        image_height=533,
        credit_name="Lutz Maertens",
        credit_url="https://commons.wikimedia.org/wiki/File:Koerner.jpg",
        license_name="CC BY-SA 3.0",
        license_url="https://creativecommons.org/licenses/by-sa/3.0/",
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
        distance_km=8,
        difficulty=MODERATE,
        family_tip=_("Počítejte se schody a dohledem nad dětmi na vyhlídkách."),
        map_url="https://mapy.cz/turisticka?q=Skaln%C3%AD%20hrad%20Sloup",
        official_url="https://www.hrad-sloup.cz/",
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
        distance_km=4,
        difficulty=EASY,
        family_tip=_(
            "Dobrá volba pro všechny věkové skupiny a také pro kratší program."
        ),
        map_url="https://mapy.cz/turisticka?q=Pa%C4%8Dinek%20Glass",
        official_url="https://www.pacinekglass.com/sklenena-zahrada",
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
        distance_km=7,
        difficulty=EASY,
        family_tip=_("Exkurzi nebo zážitek pro děti si předem ověřte a rezervujte."),
        map_url="https://mapy.cz/turisticka?q=AJETO%20Lindava",
        official_url="https://www.ajetoglass.com/",
        image="vylety/ajeto.jpg",
        image_width=1600,
        image_height=1064,
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
        distance_km=8,
        difficulty=MODERATE,
        family_tip=_("Vhodné pro zdatnější děti; vezměte pevnou obuv a dostatek pití."),
        map_url="https://mapy.cz/turisticka?q=Kl%C3%AD%C4%8D%20Lu%C5%BEick%C3%A9%20hory",
        official_url="https://www.liberecky-kraj.cz/dr-cs/636-vrch-klic.html",
        image="vylety/klic.jpg",
        image_width=1600,
        image_height=1064,
    ),
    Attraction(
        slug="polevsko",
        name=_("Polevsko v létě i v zimě"),
        summary=_("Rodinné lyžování, cyklistika a výlety v krajině nad Novým Borem."),
        description=_(
            "Polevsko nabízí v zimě menší lyžařský areál a během roku síť cest "
            "pro pěší a cyklisty. Díky krátké dojezdové vzdálenosti lze program "
            "snadno přizpůsobit počasí a zkušenostem dětí."
        ),
        distance_km=12,
        difficulty=EASY,
        family_tip=_(
            "Aktuální provoz areálu a podmínky vždy zkontrolujte před odjezdem."
        ),
        map_url="https://mapy.cz/turisticka?q=Polevsko",
        official_url="https://www.polevsko.ski/",
        image="vylety/polevsko.jpg",
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
        distance_km=22,
        difficulty=MODERATE,
        family_tip=_("Na hrad vede stoupání a schody; pro malé děti se hodí nosítko."),
        map_url="https://mapy.cz/turisticka?q=Burg%20und%20Kloster%20Oybin",
        official_url="https://oybin.com/erleben-entdecken/burg-und-kloster/",
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
        distance_km=20,
        difficulty=EASY,
        family_tip=_("Celoroční krytý program vhodný i za deště."),
        map_url="https://mapy.cz/turisticka?q=Exotenhaus%20Jonsdorf",
        official_url="https://www.exotenhaus.info/",
        travel_tip=MOUNTAIN_EXPRESS_TIP,
        image="vylety/jonsdorf.jpg",
        image_width=1600,
        image_height=1200,
    ),
)


ATTRACTIONS_BY_SLUG = {item.slug: item for item in ATTRACTIONS}


@dataclass(frozen=True)
class SwimmingTip:
    name: object
    description: object
    official_url: str
    travel_tip: object | None = None


SWIMMING_IMAGE = "vylety/koupaliste-jonsdorf.jpg"
SWIMMING_IMAGE_WIDTH = 1920
SWIMMING_IMAGE_HEIGHT = 1081


SWIMMING_TIPS = (
    SwimmingTip(
        name=_("Koupaliště Sloup v Čechách"),
        description=_("Přírodní koupaliště v kempu s lanovým centrem a občerstvením."),
        official_url="https://koupaliste.sloupvcechach.cz/",
        travel_tip=_("Ze Cvikova se sem můžete vydat také autobusem."),
    ),
    SwimmingTip(
        name=_("Koupaliště Jablonné v Podještědí"),
        description=_(
            "Koupaliště v kempu s dětským hřištěm, restaurací a nafukovací "
            "skluzavkou na vodě."
        ),
        official_url="https://www.kempjablonne.cz/",
    ),
    SwimmingTip(
        name=_("Rekreační areál Kristýna"),
        description=_(
            "Koupání v zatopeném bývalém dole s písčitou pláží, dětským "
            "hřištěm, šlapadly a restaurací."
        ),
        official_url="https://www.kemp-kristyna.cz/",
    ),
    SwimmingTip(
        name=_("Horské koupaliště Jonsdorf"),
        description=_(
            "Koupaliště s tobogánem, dětským bazénem, vzduchovou trampolínou "
            "a občerstvením."
        ),
        official_url="https://www.jonsdorf.de/gebirgsbad/",
        travel_tip=MOUNTAIN_EXPRESS_TIP,
    ),
    SwimmingTip(
        name=_("Koupaliště Dubice"),
        description=_(
            "Koupaliště u České Lípy s tobogány a brouzdalištěm. Na přilehlém "
            "rybníce je možné vyzkoušet wakeboarding, paddleboarding i koupání "
            "a v okolí je volně přístupné 3D bludiště."
        ),
        official_url="https://www.sportlipa.cz/venkovni-koupaliste-dubice",
    ),
    SwimmingTip(
        name=_("Městské koupaliště Česká Kamenice"),
        description=_(
            "Koupaliště s bistrem. Návštěvu lze spojit s výletem k ručnímu "
            "přívozu a do parku miniatur Mlýnky Brand, kam se dostanete i "
            "s kočárkem, nebo na skalní vyhlídku Ponorka."
        ),
        official_url=("https://ceska-kamenice.cz/mapa-vyletu/mestske-koupaliste/"),
    ),
)
