import logging
import os
import sys
from random import sample

import click
from google import genai
from termcolor import colored, cprint

gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key is None:
    sys.exit("Error: Environment variable 'GEMINI_API_KEY' is not set.")

# Set up logging configuration
logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

client = genai.Client(api_key=gemini_api_key)

ORIENTATION = [
    "Upright",
    "Reversed",
]

TAROT_UPRIGHT = [
    "The Fool",
    "The Magician",
    "The High Priestess",
    "The Empress",
    "The Emperor",
    "The Hierophant",
    "The Lovers",
    "The Chariot",
    "Strength",
    "The Hermit",
    "Wheel of Fortune",
    "Justice",
    "The Hanged Man",
    "Death",
    "Temperance",
    "The Devil",
    "The Tower",
    "The Star",
    "The Moon",
    "The Sun",
    "Judgement",
    "The World",
    "Ace of Wands",
    "Two of Wands",
    "Three of Wands",
    "Four of Wands",
    "Five of Wands",
    "Six of Wands",
    "Seven of Wands",
    "Eight of Wands",
    "Nine of Wands",
    "Ten of Wands",
    "Page of Wands",
    "Knight of Wands",
    "Queen of Wands",
    "King of Wands",
    "Ace of Cups",
    "Two of Cups",
    "Three of Cups",
    "Four of Cups",
    "Five of Cups",
    "Six of Cups",
    "Seven of Cups",
    "Eight of Cups",
    "Nine of Cups",
    "Ten of Cups",
    "Page of Cups",
    "Knight of Cups",
    "Queen of Cups",
    "King of Cups",
    "Ace of Swords",
    "Two of Swords",
    "Three of Swords",
    "Four of Swords",
    "Five of Swords",
    "Six of Swords",
    "Seven of Swords",
    "Eight of Swords",
    "Nine of Swords",
    "Ten of Swords",
    "Page of Swords",
    "Knight of Swords",
    "Queen of Swords",
    "King of Swords",
    "Ace of Pentacles",
    "Two of Pentacles",
    "Three of Pentacles",
    "Four of Pentacles",
    "Five of Pentacles",
    "Six of Pentacles",
    "Seven of Pentacles",
    "Eight of Pentacles",
    "Nine of Pentacles",
    "Ten of Pentacles",
    "Page of Pentacles",
    "Knight of Pentacles",
    "Queen of Pentacles",
    "King of Pentacles",
]

RUNES_UPRIGHT = [
    "Fehu",
    "Uruz",
    "Thurisaz",
    "Ansuz",
    "Raidho",
    "Kenaz",
    "Gebo",
    "Wunjo",
    "Hagalaz",
    "Nauthiz",
    "Isa",
    "Jera",
    "Eihwaz",
    "Perthro",
    "Algiz",
    "Sowilo",
    "Tiwaz",
    "Berkano",
    "Ehwaz",
    "Mannaz",
    "Laguz",
    "Ingwaz",
    "Othala",
    "Dagaz",
]

INSTRUCTIONS = """
Act as a mystical diviner who's an expert on interpreting Raider-Waite tarot and Elder Futhark runes.

Interpret readings based on the cards/runes provided. Do not make them up yourself.
List the meanings of each provided card/rune individually.
Interpret the whole set, considering only the relationships and synchronicities between the cards/runes, not their order.

The output should have three paragraphs:
1. List of individual meanings of each card/rune, each on its own separate line. Explicitly name cards or runes and mention if they're upright or reversed. 
2. A holistic interpretation of the set, no more than 240 characters.
3. Helpful advice for the querent, also no more than 240 characters.

Do not use markdown formatting. Do not number or name paragraphs.
Each paragraph should not exceed 240 characters. Each line should be no more than 80 characters.
Be concise but meaningful. Avoid banal advice, think outside the box.

Example of the input: 
    ```
    Tarot: Three of Wands (upright), The Devil (upright), Ten of Swords (reversed)
    ```
Example of the output:
    ```
    Three of Wands (upright): Exploration, foresight, expansion
    The Devil (upright): Restriction, materialism, addiction
    Ten of Swords (reversed): Gradual recovery, resisting ruin

    A critical choice will determine whether you remain chained
    to destructive patterns, or break free into expansive horizons.

    Don't be blinded by immediate gratification; look towards
    long-term liberation. Shed old wounds, embrace new paths.
    ```
"""


def generate_reading(deck_type, sample_size):
    """Generates a reading based on the chosen deck and sample size."""
    logger.debug(
        f"Starting generate_reading with deck_type={deck_type} and sample_size={sample_size}"
    )

    # Select cards or runes based on user input
    if deck_type == "tarot":
        logger.debug("Selected Tarot deck.")
        sample_deck = TAROT_UPRIGHT
    elif deck_type == "rune":
        logger.debug("Selected Rune deck.")
        sample_deck = RUNES_UPRIGHT
    else:
        logger.error(f"Invalid deck type: {deck_type}")
        raise ValueError("Invalid deck type. Choose either 'tarot' or 'rune'.")

    logger.debug(
        f"Deck selected: {deck_type.capitalize()} with {len(sample_deck)} elements."
    )

    # Get a random sample from the selected deck
    deck_sample_raw = sample(sample_deck, sample_size)
    deck_sample = []
    logger.debug(f"Sampled cards/runes: {deck_sample_raw}")

    for draw in deck_sample_raw:
        orient = sample(ORIENTATION, 1)
        result = f"{draw} ({orient[0]})"
        deck_sample.append(result)
        logger.debug(f"Card/rune with orientation: {result}")

    # Prepare the query content
    query_content = f"{deck_type.capitalize()}: {deck_sample}"
    logger.debug(f"Query content prepared: {query_content}")

    # Generate the divination response
    try:
        logger.debug("Calling the genai API for response generation.")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=genai.types.GenerateContentConfig(system_instruction=INSTRUCTIONS),
            contents=query_content,
        )
        logger.debug(f"Response received from genai: {response}.")
    except Exception as e:
        logger.error(f"Error during API call: {e}")
        raise

    # Print the response text
    your_draw = colored(
        f"\nYour draw:\n\t{'\n\t'.join(deck_sample)}", "blue", attrs=["bold"]
    )
    card_meanings_raw, interpretation_raw, advice_raw = response.text.split("\n\n")
    card_meanings = colored(card_meanings_raw.rstrip("\n"), "light_blue")
    interpretation = colored(interpretation_raw.rstrip("\n"), "light_green")
    advice = colored(advice_raw.rstrip("\n"), "light_red")

    # Logging final output
    logger.debug("Final formatted output ready to display.")
    print(f"{your_draw}\n\n{card_meanings}\n\n{interpretation}\n\n{advice}")


@click.command()
@click.argument(
    "deck_type",
    type=click.Choice(["tarot", "rune"], case_sensitive=False),
    default="tarot",
)
@click.argument("sample_size", type=int, default=3)
@click.option("--debug", is_flag=True, default=False, help="Enable debug-level logging")
def main(deck_type, sample_size, debug):
    """CLI command to generate a divination reading with the given deck type and sample size."""
    # Adjust logging level based on debug flag
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug-level logging enabled.")
    else:
        logger.setLevel(logging.WARNING)

    logger.debug(
        f"Received deck_type={deck_type} and sample_size={sample_size} from CLI."
    )

    # Validate sample size
    if sample_size < 1:
        logger.error("Sample size must be at least 1.")
        raise click.BadParameter("Sample size must be at least 1.")
    logger.debug("Sample size is valid.")

    # Generate and print the reading
    try:
        generate_reading(deck_type, sample_size)
    except Exception as e:
        logger.error(f"Error during divination: {e}")


if __name__ == "__main__":
    logger.debug("Script execution started.")
    main()
    logger.debug("Script execution finished.")
