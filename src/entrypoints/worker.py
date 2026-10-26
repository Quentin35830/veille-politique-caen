"""Worker entrypoint : enregistre les workflows et demarre le worker Mistral."""

import asyncio


async def main() -> None:
    from mistralai.workflows import discover_workflows, run_worker

    discovered = discover_workflows()
    await run_worker(discovered)


if __name__ == "__main__":
    asyncio.run(main())
