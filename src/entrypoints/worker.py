"""Worker entrypoint : enregistre les workflows et demarre le worker Mistral."""

import asyncio

import mistralai.workflows as workflows

from src.workflows.veille_caen import VeillePolitiqueCaenWorkflow


async def main() -> None:
    await workflows.run_worker([VeillePolitiqueCaenWorkflow])


if __name__ == "__main__":
    asyncio.run(main())
