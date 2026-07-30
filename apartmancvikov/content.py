# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

from dataclasses import dataclass
from typing import Literal

from django.utils.translation import gettext_lazy as _


@dataclass(frozen=True)
class Attraction:
    slug: str
    name: object
    summary: object
    description: object
    distance_km: int | float
    difficulty: object
    family_tip: object
    map_url: str
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
    description_paragraphs: tuple[object, ...] = ()


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
        image="vylety/klic.jpg",
        image_width=1600,
        image_height=1064,
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
        distance_km=17,
        distance_kind="driving",
        difficulty=MODERATE,
        family_tip=_("Na hrad vede stoupání a schody; pro malé děti se hodí nosítko."),
        map_url="https://mapy.com/s/locacosoge",
        official_url="https://oybin.com/erleben-entdecken/burg-und-kloster/",
        stroller_access=_("Ne"),
        admission=_("2–9 €; cena se liší podle věku návštěvníka a sezony."),
        opening_hours=_("V létě denně 9–18, mimo léto denně 10–16."),
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
    stroller_access: object
    admission: object
    opening_hours: object
    travel_tip: object | None = None


SWIMMING_IMAGE = "vylety/koupaliste-jonsdorf.jpg"
SWIMMING_IMAGE_WIDTH = 1920
SWIMMING_IMAGE_HEIGHT = 1081


SWIMMING_TIPS = (
    SwimmingTip(
        name=_("Koupaliště Sloup v Čechách"),
        description=_("Přírodní koupaliště v kempu s lanovým centrem a občerstvením."),
        official_url="https://koupaliste.sloupvcechach.cz/",
        stroller_access=_("Ano"),
        admission=_(
            "Dítě do 6 let 30 Kč, dítě od 6 do 15 let 45 Kč, návštěvníci nad "
            "15 let 70 Kč; parkování auta 100 Kč."
        ),
        opening_hours=_("V létě 7–18."),
        travel_tip=_("Ze Cvikova se sem můžete vydat také autobusem."),
    ),
    SwimmingTip(
        name=_("Koupaliště Jablonné v Podještědí"),
        description=_(
            "Koupaliště v kempu s dětským hřištěm, restaurací a nafukovací "
            "skluzavkou na vodě."
        ),
        official_url="https://www.kempjablonne.cz/",
        stroller_access=_("Ano"),
        admission=_("Dítě 30 Kč, dospělý 50 Kč."),
        opening_hours=_("V létě 8–22."),
    ),
    SwimmingTip(
        name=_("Rekreační areál Kristýna"),
        description=_(
            "Koupání v zatopeném bývalém dole s písčitou pláží, dětským "
            "hřištěm, šlapadly a restaurací."
        ),
        official_url="https://www.kemp-kristyna.cz/",
        stroller_access=_("Ano"),
        admission=_("70 Kč za osobu."),
        opening_hours=_("V létě 8–21."),
    ),
    SwimmingTip(
        name=_("Horské koupaliště Jonsdorf"),
        description=_(
            "Koupaliště s tobogánem, dětským bazénem, vzduchovou trampolínou "
            "a občerstvením."
        ),
        official_url="https://www.jonsdorf.de/gebirgsbad/",
        stroller_access=_("Ano"),
        admission=_("Dospělý 5 €, dítě 3 €, rodinné vstupné 12 €."),
        opening_hours=_("V létě 11–19."),
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
        stroller_access=_("Ano"),
        admission=_(
            "30–150 Kč podle sezony, věku a času vstupu; celodenní parkování 150 Kč."
        ),
        opening_hours=_("V létě 9–21."),
    ),
    SwimmingTip(
        name=_("Městské koupaliště Česká Kamenice"),
        description=_(
            "Koupaliště s bistrem. Návštěvu lze spojit s výletem k ručnímu "
            "přívozu a do parku miniatur Mlýnky Brand, kam se dostanete i "
            "s kočárkem, nebo na skalní vyhlídku Ponorka."
        ),
        official_url=("https://ceska-kamenice.cz/mapa-vyletu/mestske-koupaliste/"),
        stroller_access=_("Ano"),
        admission=_("Dítě 40 Kč, dospělý 80 Kč."),
        opening_hours=_("V létě 10–19."),
    ),
)
