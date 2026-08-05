# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

from dataclasses import dataclass
from typing import Literal

from django.utils.translation import gettext_lazy as _

from .content import TripRelation


@dataclass(frozen=True)
class RestaurantTip:
    slug: str
    name: object
    description: object
    official_url: str
    distance_km: int | float
    distance_kind: Literal["walking", "driving"]
    schedule_note: object | None = None
    travel_tip: object | None = None
    related_trips: tuple[TripRelation, ...] = ()


RESTAURANTS = (
    RestaurantTip(
        slug="plechovka",
        name=_("Plechovka"),
        description=_(
            "Jídelna pro rychlý a cenově dostupný oběd během pracovního týdne."
        ),
        official_url="https://www.facebook.com/profile.php?id=100057442390304",
        distance_km=0.3,
        distance_kind="walking",
        schedule_note=_("Obědy v pracovní dny."),
    ),
    RestaurantTip(
        slug="sladovna-cvikov",
        name=_("Sladovna Cvikov (Pivovar Cvikov)"),
        description=_(
            "Moderní česká kuchyně a řemeslné pivo přímo v areálu Pivovaru Cvikov."
        ),
        official_url="https://restauracesladovna.cz/cs/sladovna-cvikov",
        distance_km=0.6,
        distance_kind="walking",
    ),
    RestaurantTip(
        slug="restaurace-sever",
        name=_("Restaurace Pizzerie Sever"),
        description=_(
            "Česká klasika k obědu a pizza, kterou si můžete o víkendu objednat "
            "s rozvozem."
        ),
        official_url="https://www.facebook.com/profile.php?id=61579240842007",
        distance_km=0.8,
        distance_kind="walking",
        schedule_note=_(
            "Obědy v pracovní dny; o víkendu rozvoz pizzy. V létě bývá někdy "
            "otevřená zahrádka také o víkendu."
        ),
    ),
    RestaurantTip(
        slug="na-krajicku",
        name=_("Občerstvení Na Krajíčku"),
        description=_(
            "Občerstvení přímo u pumptracku, dětského areálu a placených "
            "vzduchových trampolín."
        ),
        official_url="https://www.facebook.com/groups/662887772360954",
        distance_km=1.2,
        distance_kind="walking",
        schedule_note=_("V létě se zde v pátek konají koncerty."),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="pumptrack-cvikov",
                description=_(
                    "Občerstvení leží přímo u pumptracku a navazujícího dětského "
                    "areálu."
                ),
            ),
        ),
    ),
    RestaurantTip(
        slug="sklarska-krcma",
        name=_("Sklářská krčma"),
        description=_("Tradiční česká kuchyně."),
        official_url="https://www.ajetoglass.com/sklarska-krcma",
        distance_km=6,
        distance_kind="driving",
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="ajeto-lindava",
                description=_(
                    "Návštěvu Sklářské krčmy můžete spojit s prohlídkou "
                    "sklárny AJETO a ukázkou ruční výroby skla."
                ),
            ),
        ),
    ),
    RestaurantTip(
        slug="sloupska-terasa",
        name=_("Sloupská Terasa"),
        description=_(
            "Zmrzlina a zákusky pro sladkou zastávku během výletu do Sloupu."
        ),
        official_url="https://www.sloupskazmrzlina.cz/",
        distance_km=7,
        distance_kind="driving",
        travel_tip=_("Do Sloupu v Čechách je možné dojet také autobusem."),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="skalni-hrad-sloup",
                description=_(
                    "Na zmrzlinu nebo zákusek se zastavte při návštěvě skalního "
                    "hradu ve Sloupu."
                ),
            ),
            TripRelation(
                target_kind="swimming",
                target_slug="koupaliste-sloup",
                description=_(
                    "Sladkou zastávku můžete spojit také s letním koupáním ve Sloupu."
                ),
            ),
        ),
    ),
    RestaurantTip(
        slug="na-strazi",
        name=_("Restaurace Na Stráži"),
        description=_(
            "Moderní gastronomie v příjemném prostředí nedaleko sloupských "
            "výletních cílů."
        ),
        official_url="https://www.nastrazi.cz/restaurace/",
        distance_km=9,
        distance_kind="driving",
        travel_tip=_("Do Sloupu v Čechách je možné dojet také autobusem."),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="skalni-hrad-sloup",
                description=_(
                    "Návštěvu restaurace můžete spojit s prohlídkou skalního "
                    "hradu ve Sloupu."
                ),
            ),
            TripRelation(
                target_kind="swimming",
                target_slug="koupaliste-sloup",
                description=_(
                    "V létě se nabízí spojení s koupáním na sloupském koupališti."
                ),
            ),
        ),
    ),
    RestaurantTip(
        slug="bep-novy-bor",
        name=_("BẾP Nový Bor"),
        description=_(
            "Asijská kuchyně založená na vietnamských a čínských chutích s "
            "japonskou inspirací a moderním pojetím."
        ),
        official_url="https://www.restauracebep.cz/",
        distance_km=9,
        distance_kind="driving",
        travel_tip=_("Do Nového Boru je možné dojet také autobusem."),
        related_trips=(
            TripRelation(
                target_kind="cycling",
                target_slug="novy-bor",
                description=_(
                    "Restauraci můžete zařadit jako zastávku na cyklistickém "
                    "okruhu přes Nový Bor."
                ),
            ),
        ),
    ),
    RestaurantTip(
        slug="royal-maharaja",
        name=_("The Royal Maharaja"),
        description=_("Indická restaurace v Novém Boru."),
        official_url="https://www.facebook.com/profile.php?id=61586811792679",
        distance_km=9,
        distance_kind="driving",
        travel_tip=_("Do Nového Boru je možné dojet také autobusem."),
        related_trips=(
            TripRelation(
                target_kind="cycling",
                target_slug="novy-bor",
                description=_(
                    "Indickou restauraci můžete zařadit jako zastávku na "
                    "cyklistickém okruhu přes Nový Bor."
                ),
            ),
        ),
    ),
    RestaurantTip(
        slug="resort-hvozd",
        name=_("Restaurace Resort Hvozd"),
        description=_(
            "Tradiční i moderní česká kuchyně v restauraci známé také jako Farma Hvozd."
        ),
        official_url="https://www.resorthvozd.cz/restaurace",
        distance_km=10,
        distance_kind="driving",
        travel_tip=_("Do Krompachu je možné dojet také autobusem ze Cvikova."),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="hvozd",
                description=_(
                    "Restaurace je vhodnou zastávkou před výstupem na Hvozd "
                    "nebo po návratu z výletu."
                ),
            ),
        ),
    ),
    RestaurantTip(
        slug="pivovar-krompach",
        name=_("Pivovar Krompach"),
        description=_("Česká kuchyně doplněná pivem z vlastního pivovaru."),
        official_url="https://www.pivovarkrompach.cz/",
        distance_km=10,
        distance_kind="driving",
        travel_tip=_("Do Krompachu je možné dojet také autobusem ze Cvikova."),
        related_trips=(
            TripRelation(
                target_kind="attraction",
                target_slug="hvozd",
                description=_(
                    "Pivovar nabízí občerstvení před výstupem na Hvozd nebo po "
                    "návratu z okruhu."
                ),
            ),
        ),
    ),
    RestaurantTip(
        slug="lemberk",
        name=_("Restaurace a penzion Lemberk"),
        description=_(
            "Rybí speciality z vlastních rybníků a sádek i tradiční česká kuchyně."
        ),
        official_url=("https://penzionlemberk.cz/penzion-restaurace/restaurace"),
        distance_km=11,
        distance_kind="driving",
    ),
    RestaurantTip(
        slug="kaido-sushi",
        name=_("Kaido Sushi"),
        description=_("Sushi a ramen v České Lípě."),
        official_url=("https://www.facebook.com/p/Kaido-Sushi-%C4%8CL-61556848413838/"),
        distance_km=19,
        distance_kind="driving",
        related_trips=(
            TripRelation(
                target_kind="swimming",
                target_slug="koupaliste-dubice",
                description=_(
                    "Návštěvu Kaido Sushi můžete spojit s koupáním na "
                    "koupališti Dubice."
                ),
            ),
        ),
    ),
)


RESTAURANTS_BY_SLUG = {item.slug: item for item in RESTAURANTS}
