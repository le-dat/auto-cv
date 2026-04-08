import asyncio
import sys
sys.path.insert(0, 'backend')

from unittest.mock import AsyncMock, MagicMock
import json

json_content = '{"matched_skills":["Python"],"missing_skills":["AWS"],"weak_skills":[],"skill_match_score":0.67,"suggestions":[]}'

m = MagicMock()
m.ainvoke = AsyncMock(return_value=MagicMock(content=json_content))

async def test():
    result = await m.ainvoke(['msg'])
    content = result.content if hasattr(result, 'content') else str(result)
    print(f'content: {repr(content[:50])}')

    if content.startswith('```'):
        content = content.split('\n', 1)[1]
        content = content.rsplit('```', 1)[0].strip()

    print(f'After strip: {repr(content[:50])}')
    parsed = json.loads(content)
    print(f'Parsed: {parsed}')

asyncio.run(test())
