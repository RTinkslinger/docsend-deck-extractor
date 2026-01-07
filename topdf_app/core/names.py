"""Random cartoon name generator for PDF files.

Assigns fun, memorable names to converted PDFs until all names are used.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject

# 1000 cartoon/animated character first names
CARTOON_NAMES = [
    # Classic Disney
    "Mickey", "Minnie", "Donald", "Daisy", "Goofy", "Pluto", "Chip", "Dale",
    "Dumbo", "Bambi", "Thumper", "Flower", "Simba", "Nala", "Mufasa", "Scar",
    "Timon", "Pumbaa", "Rafiki", "Zazu", "Ariel", "Flounder", "Sebastian",
    "Eric", "Ursula", "Belle", "Beast", "Gaston", "Lumiere", "Cogsworth",
    "Jasmine", "Aladdin", "Genie", "Jafar", "Abu", "Rajah", "Pocahontas",
    "Meeko", "Flit", "Mulan", "Mushu", "Shang", "Tarzan", "Jane", "Terk",
    "Tantor", "Lilo", "Stitch", "Nani", "Jumba", "Pleakley", "Moana", "Maui",
    "Elsa", "Anna", "Olaf", "Kristoff", "Sven", "Rapunzel", "Flynn", "Pascal",
    "Maximus", "Merida", "Elinor", "Fergus", "Vanellope", "Ralph", "Felix",

    # Pixar
    "Woody", "Buzz", "Jessie", "Rex", "Slinky", "Hamm", "Bullseye", "Lotso",
    "Forky", "Bonnie", "Andy", "Nemo", "Marlin", "Dory", "Gill", "Bloat",
    "Peach", "Jacques", "Bubbles", "Gurgle", "Nigel", "Crush", "Squirt",
    "Hank", "Destiny", "Bailey", "Sully", "Mike", "Boo", "Randall", "Roz",
    "Celia", "Lightning", "Mater", "Sally", "Doc", "Ramone", "Flo", "Luigi",
    "Guido", "Sheriff", "Fillmore", "Sarge", "Cruz", "Jackson", "Remy",
    "Linguini", "Colette", "Ego", "Emile", "Django", "Carl", "Russell",
    "Dug", "Kevin", "Muntz", "Ellie", "Joy", "Sadness", "Fear", "Anger",
    "Disgust", "Bing", "Riley", "Miguel", "Hector", "Dante", "Imelda",
    "Ernesto", "Coco", "Luca", "Alberto", "Giulia", "Ercole", "Massimo",

    # Looney Tunes
    "Bugs", "Daffy", "Porky", "Tweety", "Sylvester", "Foghorn", "Speedy",
    "Pepe", "Wile", "Roadrunner", "Taz", "Marvin", "Elmer", "Yosemite",
    "Granny", "Lola", "Gossamer", "Michigan", "Ralph", "Sam",

    # Hanna-Barbera
    "Scooby", "Shaggy", "Velma", "Daphne", "Fred", "Scrappy", "Yogi",
    "Booboo", "Cindy", "Ranger", "Flintstones", "Barney", "Betty", "Wilma",
    "Pebbles", "Bamm", "Dino", "Jetsons", "George", "Jane", "Judy", "Elroy",
    "Astro", "Rosie", "Johnny", "Dexter", "Dee", "Mandark", "Blossom",
    "Bubbles", "Buttercup", "Mojo", "Fuzzy", "Courage", "Muriel", "Eustace",

    # Nickelodeon
    "SpongeBob", "Patrick", "Squidward", "Sandy", "Krabs", "Plankton",
    "Karen", "Gary", "Pearl", "Larry", "Tommy", "Chuckie", "Angelica",
    "Phil", "Lil", "Susie", "Dil", "Kimi", "Timmy", "Cosmo", "Wanda",
    "Poof", "Sparky", "Crocker", "Vicky", "Chester", "Arnold", "Helga",
    "Gerald", "Phoebe", "Harold", "Rhonda", "Eugene", "Aang", "Katara",
    "Sokka", "Toph", "Zuko", "Iroh", "Azula", "Appa", "Momo", "Korra",
    "Mako", "Bolin", "Asami", "Tenzin", "Jinora", "Lincoln", "Lori",
    "Leni", "Luna", "Luan", "Lynn", "Lucy", "Lana", "Lola", "Lisa", "Lily",

    # Cartoon Network
    "Finn", "Jake", "Marceline", "Bubblegum", "Ice", "BMO", "Lumpy",
    "Flame", "Gunter", "Mordecai", "Rigby", "Benson", "Skips", "Pops",
    "Muscle", "High", "Thomas", "Margaret", "Eileen", "Gumball", "Darwin",
    "Anais", "Nicole", "Richard", "Penny", "Carrie", "Tobias", "Steven",
    "Garnet", "Amethyst", "Pearl", "Peridot", "Lapis", "Jasper", "Connie",
    "Greg", "Rose", "Spinel", "Ed", "Edd", "Eddy", "Rolf", "Kevin", "Nazz",
    "Jimmy", "Sarah", "Jonny", "Plank", "Samurai", "Aku", "Scotsman",

    # DreamWorks
    "Shrek", "Fiona", "Donkey", "Puss", "Dragon", "Farquaad", "Charming",
    "Arthur", "Rumpel", "Po", "Tigress", "Viper", "Crane", "Mantis",
    "Monkey", "Shifu", "Oogway", "Tai", "Shen", "Kai", "Hiccup", "Toothless",
    "Astrid", "Stormfly", "Snotlout", "Fishlegs", "Ruffnut", "Tuffnut",
    "Stoick", "Valka", "Gobber", "Grimmel", "Alex", "Marty", "Melman",
    "Gloria", "King", "Maurice", "Mort", "Skipper", "Kowalski", "Rico",
    "Private", "Mason", "Phil", "Vitaly", "Gia", "Stefano", "Branch",
    "Poppy", "Creek", "Bridget", "Gristle", "Guy", "Eep", "Grug", "Ugga",
    "Thunk", "Sandy", "Gran", "Belt", "Metro", "Roxanne", "Megamind",
    "Minion", "Tighten", "Spirit", "Rain", "Lucky",

    # Anime/Japanese
    "Pikachu", "Ash", "Misty", "Brock", "Gary", "Meowth", "Jessie",
    "James", "Oak", "Joy", "Jenny", "Goku", "Vegeta", "Gohan", "Piccolo",
    "Krillin", "Bulma", "Trunks", "Goten", "Frieza", "Cell", "Buu",
    "Naruto", "Sasuke", "Sakura", "Kakashi", "Hinata", "Shikamaru",
    "Choji", "Ino", "Rock", "Neji", "Gaara", "Itachi", "Jiraiya", "Orochimaru",
    "Tsunade", "Luffy", "Zoro", "Nami", "Usopp", "Sanji", "Chopper",
    "Robin", "Franky", "Brook", "Jinbe", "Totoro", "Mei", "Satsuki",
    "Catbus", "Chihiro", "Haku", "Yubaba", "Zeniba", "Boh", "Kamaji",
    "Ponyo", "Sosuke", "Howl", "Sophie", "Calcifer", "Kiki", "Jiji", "Tombo",
    "Porco", "Gina", "Ashitaka", "San", "Moro", "Eboshi", "Jigo",

    # Classic Animation
    "Popeye", "Olive", "Bluto", "Wimpy", "Swee", "Felix", "Betty",
    "Bimbo", "Koko", "Casper", "Wendy", "Richie", "Cadbury", "Droopy",
    "Spike", "Tom", "Jerry", "Nibbles", "Butch", "Quacker", "Spike",
    "Tyke", "Woody", "Winnie", "Buzz", "Chilly", "Andy", "Miranda",
    "Inspector", "Penny", "Brain", "Claw", "Pink", "Panther", "Clouseau",

    # Modern Animation
    "Bluey", "Bingo", "Bandit", "Chilli", "Muffin", "Socks", "Stripe",
    "Trixie", "Chloe", "Judo", "Mackenzie", "Rusty", "Jack", "Honey",
    "Phineas", "Ferb", "Candace", "Perry", "Doofenshmirtz", "Vanessa",
    "Isabella", "Buford", "Baljeet", "Stacy", "Jeremy", "Monogram",
    "Carl", "Norm", "Dipper", "Mabel", "Stan", "Ford", "Soos", "Wendy",
    "Waddles", "Bill", "Pacifica", "Gideon", "Star", "Marco", "Ludo",
    "Toffee", "Glossaryck", "Hekapoo", "Pony", "Janna", "Jackie",

    # Video Game Characters (cartoon-style)
    "Mario", "Luigi", "Peach", "Toad", "Yoshi", "Bowser", "Wario",
    "Waluigi", "Daisy", "Rosalina", "Toadette", "Birdo", "Donkey",
    "Diddy", "Dixie", "Cranky", "Funky", "Kirby", "Dedede", "Meta",
    "Waddle", "Link", "Zelda", "Ganondorf", "Impa", "Navi", "Epona",
    "Sonic", "Tails", "Knuckles", "Amy", "Shadow", "Rouge", "Eggman",
    "Cream", "Cheese", "Vector", "Espio", "Charmy", "Silver", "Blaze",
    "Crash", "Coco", "Cortex", "Aku", "Uka", "Dingodile", "Tiny",
    "Spyro", "Sparx", "Hunter", "Elora", "Moneybags", "Bianca", "Sgt",
    "Ratchet", "Clank", "Qwark", "Nefarious", "Rivet", "Kit", "Jak",
    "Daxter", "Keira", "Samos", "Torn", "Ashelin", "Rayman", "Globox",
    "Barbara", "Murfy", "Teensie", "Sackboy", "Toggle", "Oddsock",

    # Misc Cartoon Characters
    "Groot", "Rocket", "Drax", "Gamora", "Mantis", "Nebula", "Starlord",
    "Baymax", "Hiro", "Wasabi", "Gogo", "Honey", "Fred", "Tadashi",
    "Callaghan", "Wall", "Eve", "Mo", "Auto", "Captain", "McCrea",
    "Flint", "Sam", "Steve", "Brent", "Earl", "Tim", "Chester",
    "Barb", "Gil", "Manny", "Sid", "Diego", "Scrat", "Ellie", "Peaches",
    "Crash", "Eddie", "Buck", "Shira", "Granny", "Brooke", "Julian",
    "Horton", "Morton", "Vlad", "Katie", "Ted", "Audrey", "Grammy",
    "Lorax", "Once", "Ferdinand", "Lupe", "Bones", "Angus", "Una",
    "Dos", "Cuatro", "Valiente", "Guapo", "Paco", "Gru", "Lucy",
    "Margo", "Edith", "Agnes", "Vector", "Nefario", "Wild", "Scarlet",
    "Herb", "Balthazar", "Dru", "Fritz", "Kevin", "Bob", "Stuart",
    "Otto", "Paddington", "Brown", "Bird", "Curry", "Gruber", "Bucket",
    "Phoenix", "Knuckles", "Judy", "Nick", "Bogo", "Clawhauser",
    "Bellwether", "Lionheart", "Finnick", "Flash", "Yax", "Gazelle",

    # More Characters
    "Archer", "Lana", "Cyril", "Pam", "Cheryl", "Krieger", "Malory",
    "Ray", "Woodhouse", "Barry", "Katya", "Conway", "Brett", "Figgis",
    "Rick", "Morty", "Beth", "Jerry", "Summer", "Birdperson", "Squanchy",
    "Unity", "Tammy", "Phoenix", "Scary", "Terry", "Goldenfold",
    "Poopybutthole", "Jaguar", "Pickle", "Noob", "Evil", "Snuffles",
    "BoJack", "Diane", "Todd", "Carolyn", "Peanutbutter", "Hollyhock",
    "Beatrice", "Butterscotch", "Sarah", "Herb", "Wanda", "Penny",
    "Charlotte", "Kelsey", "Rutabaga", "Judah", "Pickles", "Paige",
    "Tuca", "Bertie", "Speckle", "Kara", "Figgy", "Dapper",
    "Hilda", "Twig", "Alfur", "Frida", "David", "Johanna", "Raven",
    "Kaisa", "Erik", "Victoria", "Gerda", "Cedric", "Edmund",

    # Even More to reach ~1000
    "Alvin", "Simon", "Theodore", "Brittany", "Jeanette", "Eleanor",
    "Dave", "Ian", "Zoe", "Toby", "Julie", "Miles", "Samantha", "Ashley",
    "Rocko", "Heffer", "Filburt", "Spunky", "Bev", "Virginia", "Ralph",
    "Paula", "Peter", "Peaches", "Widget", "Wubbzy", "Walden", "Daisy",
    "Daizy", "Huggy", "Earl", "Moxy", "Nox", "Ox", "Ug", "Mandy", "Ugly",
    "Charlie", "Itchy", "Killer", "Carface", "Annabelle", "Belladonna",
    "Flo", "Webster", "Cuddles", "Giggles", "Toothy", "Lumpy", "Petunia",
    "Handy", "Nutty", "Sniffles", "Pop", "Cub", "Flaky", "Mime", "Disco",
    "Russell", "Lifty", "Shifty", "Cro", "Splendid", "Lammy", "Truffles",
    "Beavis", "Butthead", "Daria", "Jane", "Trent", "Quinn", "Helen",
    "Jake", "Brittany", "Kevin", "Mack", "Jodie", "Andrea", "Sandi",
    "Stacy", "Tiffany", "Upchuck", "Tom", "Jesse", "Wind",
    "Catra", "Adora", "Glimmer", "Bow", "Hordak", "Entrapta", "Scorpia",
    "Mermista", "Perfuma", "Frosta", "Spinnerella", "Netossa", "Swift",
    "Seahawk", "Horde", "Shadow", "Double", "Kyle", "Rogelio", "Lonnie",
    "Angella", "Micah", "Castaspella", "Light", "Hope", "Mara", "Razz",
    "Madame", "Huntara", "Tung", "Flutterina", "Peekablue", "Sweet",
    "Tallstar", "Jewelstar", "Starla", "Swen", "Imp", "Grizzlor",
    "Leech", "Mantenna", "Modulok", "Squidish", "Multi", "Octavia",
    "Scorpia", "Catra", "Spinerella", "Netossa", "Mermista", "Frosta",
    "Perfuma", "Glimmer", "Bow", "Adora", "Hordak", "Entrapta", "Wrong",
    "Emily", "Sparkles", "Thundercat", "Lion", "Cheetara", "Tygra",
    "Panthro", "Snarf", "Wilykit", "Wilykat", "Jaga", "Bengali", "Pumyra",
    "Lynxo", "Mumm", "Slithe", "Jackalman", "Monkian", "Vultureman",
    "Rataro", "Grune", "Kaynar", "Addicus", "Ssslithe", "Claudus",
    "Voltron", "Keith", "Lance", "Pidge", "Hunk", "Shiro", "Allura",
    "Coran", "Lotor", "Zarkon", "Haggar", "Sendak", "Acxa", "Ezor",
    "Zethrid", "Narti", "Romelle", "Kolivan", "Ulaz", "Thace", "Regris",
    "Krolia", "Cosmo", "Veronica", "James", "Nadia", "Ryan", "Kinkade",
    "Leifsdottir", "Griffin", "Iverson", "Sanda", "Slav", "Matt",
    "Commander", "Dayak", "Ladnok", "Branko", "Morvok", "Varkon", "Lahn",
    "Honerva", "Sincline", "Bandor", "Kova", "Cupcake", "Cherry",
]


class NameManager(QObject):
    """Manages random name assignment for PDFs.

    Tracks which names have been used and assigns unique names
    until all are exhausted, then resets.
    """

    def __init__(self, parent=None):
        """Initialize name manager.

        Args:
            parent: Optional parent QObject
        """
        super().__init__(parent)
        self._config_path = Path.home() / ".config" / "topdf" / "used_names.json"
        self._used_names: set[str] = set()
        self._load()

    def _load(self) -> None:
        """Load used names from disk."""
        try:
            if self._config_path.exists():
                data = json.loads(self._config_path.read_text())
                self._used_names = set(data.get("used", []))
        except Exception:
            self._used_names = set()

    def _save(self) -> None:
        """Save used names to disk."""
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            data = {"used": list(self._used_names)}
            self._config_path.write_text(json.dumps(data))
        except Exception:
            pass

    def get_random_name(self) -> str:
        """Get a random unused cartoon name.

        Returns:
            A random cartoon character name
        """
        # Get available names
        available = set(CARTOON_NAMES) - self._used_names

        # If all names used, reset
        if not available:
            self._used_names = set()
            available = set(CARTOON_NAMES)

        # Pick a random name
        name = random.choice(list(available))
        self._used_names.add(name)
        self._save()

        return name

    def release_name(self, name: str) -> None:
        """Release a name back to the pool (if user changes it).

        Args:
            name: Name to release
        """
        if name in self._used_names:
            self._used_names.discard(name)
            self._save()

    def get_available_count(self) -> int:
        """Get count of available names.

        Returns:
            Number of unused names
        """
        return len(CARTOON_NAMES) - len(self._used_names)


# Global instance
_name_manager: Optional[NameManager] = None


def get_name_manager() -> NameManager:
    """Get the global name manager instance.

    Returns:
        NameManager singleton
    """
    global _name_manager
    if _name_manager is None:
        _name_manager = NameManager()
    return _name_manager
