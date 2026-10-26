"""Worker entrypoint : enregistre les workflows et demarre le worker Mistral."""

import asyncio


async def main() -> None:
    import mistralai_workflows

    try:
        from mistralai.workflows import discover_workflows
    except ImportError:
        from mistralai_workflows import discover_workflows

    discovered = discover_workflows()
    await mistralai_workflows.run_worker(discovered)


if __name__ == "__main__":
    asyncio.run(main())
