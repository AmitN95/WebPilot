import asyncio

from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from web_pilot.clients.pools_admin import PoolAdmin
from web_pilot.config import config as conf
from web_pilot.schemas.requests import PageActionRequest
from web_pilot.schemas.responses import PageContentResponse
from web_pilot.logger import logger
from web_pilot.exc import PageSessionNotFoundError


router = APIRouter(prefix=f"{conf.v1_url_prefix}/sessions", tags=["Page Sessions"])


@router.get(
    "/sessions/new",
    status_code=status.HTTP_201_CREATED,
    description="Start a new, in-memory, remote, page session",
)
async def start_page_session(pool_id: str) -> str:
    pool = PoolAdmin.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found")

    browser = await pool.get_next_browser()
    session_id = await browser.start_remote_page_session(
        session_id_prefix=f"{pool.id}_{browser.id}"
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"session_id": session_id},
    )


@router.patch(
    "/sessions/{session_id}/close",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Close a remote page session",
)
async def close_page_session(session_id: str) -> None:
    try:
        _, browser, page_session = PoolAdmin.get_session_owners_chain(session_id)
        await browser.close_page_session(page_session.id)

    except PageSessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    except KeyError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=str(e))


@router.post(
    "/sessions/{session_id}/action",
    response_model=PageContentResponse,
    status_code=status.HTTP_200_OK,
    description="Perform an action on a remote page session",
)
async def perform_action_on_page(session_id: str, args: PageActionRequest):
    async def action_on_page(session_id: str, args: PageActionRequest):
        _, _, page = PoolAdmin.get_session_owners_chain(session_id)
        return await page.perform_page_action(**args.dict())

    try:
        return await asyncio.wait_for(
            action_on_page(session_id, args), timeout=conf.default_timeout
        )

    except KeyError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=str(e))
