"""Worker entrypoint : enregistre les workflows et demarre le worker Mistral."""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import mistralai.workflows as workflows

from src.workflows.veille_caen import VeillePolitiqueCaenWorkflow


async def main() -> None:
    await workflows.run_worker([VeillePolitiqueCaenWorkflow])


if __name__ == "__main__":
    asyncio.run(main())
