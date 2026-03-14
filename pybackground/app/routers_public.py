from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, HTTPException

from .repositories import (
    build_navigation_categories,
    create_friend_link,
    create_site,
    get_category_options,
    get_site_by_id,
    list_friend_links,
    list_sites,
)
from .schemas import CategoryOptionsResponse, FriendLinkCreate, FriendLinkOut, NavigationResponse, SiteOut, SiteSubmissionCreate


router = APIRouter(prefix="/api/v1", tags=["public"])


@router.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@router.get("/sites", response_model=List[SiteOut])
def get_sites() -> List[SiteOut]:
    return list_sites("approved")


@router.get("/navigation", response_model=NavigationResponse)
def get_navigation() -> NavigationResponse:
    sites = list_sites("approved")
    return NavigationResponse(categories=build_navigation_categories(sites), sites=sites)


@router.get("/categories", response_model=CategoryOptionsResponse)
def get_categories() -> CategoryOptionsResponse:
    return CategoryOptionsResponse(**get_category_options("approved"))


@router.get("/contents/{content_type}/{content_id}", response_model=SiteOut)
def get_content(content_type: str, content_id: int) -> SiteOut:
    if content_type not in {"site", "article"}:
        raise HTTPException(status_code=404, detail="Content not found")
    site = get_site_by_id(content_id, content_type, allow_pending=False)
    if site is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return site


@router.get("/sites/{site_id}", response_model=SiteOut)
def get_site(site_id: int) -> SiteOut:
    site = get_site_by_id(site_id, "site", allow_pending=False)
    if site is None:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.post("/submissions/sites", response_model=SiteOut, status_code=201)
def create_site_submission(payload: SiteSubmissionCreate) -> SiteOut:
    return create_site(payload, "pending", payload.submitterEmail)


@router.post("/friend-links", response_model=FriendLinkOut, status_code=201)
def submit_friend_link(payload: FriendLinkCreate) -> FriendLinkOut:
    return create_friend_link(payload)


@router.get("/friend-links", response_model=List[FriendLinkOut])
def get_friend_links() -> List[FriendLinkOut]:
    return list_friend_links("approved")
