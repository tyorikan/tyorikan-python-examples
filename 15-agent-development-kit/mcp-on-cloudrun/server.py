import asyncio
import json
import logging
import os
from typing import Any, Dict, List

from fastmcp import FastMCP

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("Zoo Animal MCP Server 🦁🐧🐻")


# JSONファイルから動物データを読み込む
def load_zoo_data() -> List[Dict[str, Any]]:
    """Loads zoo animal data from a JSON file."""
    try:
        with open("zoo_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("zoo_data.json not found!")
        return []


ZOO_ANIMALS = load_zoo_data()


@mcp.tool()
def get_animals_by_species(species: str) -> List[Dict[str, Any]]:
    """
    Retrieves all animals of a specific species from the zoo.
    Can also be used to collect the base data for aggregate queries
    of animals of a specific species - like counting the number of penguins
    or finding the oldest lion.

    Args:
        species: The species of the animal (e.g., 'lion', 'penguin').

    Returns:
        A list of dictionaries, where each dictionary represents an animal
        and contains details like name, age, enclosure, and trail.
    """
    logger.info(f">>> 🛠️ Tool: 'get_animals_by_species' called for '{species}'")
    return [
        animal for animal in ZOO_ANIMALS if animal["species"].lower() == species.lower()
    ]


@mcp.tool()
def get_animal_details(name: str) -> Dict[str, Any]:
    """
    Retrieves the details of a specific animal by its name.

    Args:
        name: The name of the animal.

    Returns:
        A dictionary with the animal's details (species, name, age, enclosure, trail)
        or an empty dictionary if the animal is not found.
    """
    logger.info(f">>> 🛠️ Tool: 'get_animal_details' called for '{name}'")
    for animal in ZOO_ANIMALS:
        if animal["name"].lower() == name.lower():
            return animal
    return {}


@mcp.prompt()
def find(animal: str) -> str:
    """
    Find which exhibit and trail a specific animal might be located.
    """

    return (
        f"Please find the exhibit and trail information for {animal} in the zoo. "
        f"Respond with '[animal] can be found in the [exhibit] on the [trail].'"
        f"Example: Penguins can be found in The Arctic Exhibit on the Polar Path."
    )


if __name__ == "__main__":
    logger.info(f"🚀 MCP server started on port {os.getenv('PORT', 8080)}")
    try:
        asyncio.run(
            mcp.run_async(
                transport="http",
                host="0.0.0.0",
                port=os.getenv("PORT", 8080),
            )
        )
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user.")
