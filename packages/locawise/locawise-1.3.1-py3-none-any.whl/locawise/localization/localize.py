import asyncio
import logging

from locawise.dictutils import chunk_dict, simple_union
from locawise.llm import LLMContext
from locawise.localization.prompts import generate_system_prompt, generate_user_prompt


async def localize(llm_context: LLMContext,
                   pairs: dict[str, str],
                   target_language: str,
                   context: str = '',
                   tone: str = '',
                   glossary: dict[str, str] | None = None,
                   chunk_size: int = 300
                   ) -> dict[str, str]:
    if glossary is None:
        glossary = {}
    system_prompt = generate_system_prompt(context=context, glossary=glossary, tone=tone)
    chunks = chunk_dict(pairs, chunk_size)

    tasks = []
    async with asyncio.TaskGroup() as tg:
        for index, chunk in enumerate(chunks):
            logging.debug(f"Generating task for chunk {index + 1}/{len(chunks)} for {target_language}")
            user_prompt = generate_user_prompt(chunk, target_language)
            tasks.append(tg.create_task(llm_context.call(system_prompt, user_prompt)))

    results = [task.result() for task in tasks]
    return simple_union(*results)
