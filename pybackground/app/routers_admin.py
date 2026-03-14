from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from .repositories import (
    build_admin_category_tree,
    clear_uncategorized_sites,
    create_category,
    create_site,
    delete_friend_link,
    delete_category,
    delete_site,
    get_admin_by_username,
    get_category_options,
    list_friend_links,
    list_sites,
    update_admin_password,
    update_category,
    update_friend_link,
    update_site,
)
from .schemas import (
    AdminPasswordUpdateRequest,
    AdminCategoryCreate,
    AdminCategoryNode,
    AdminCategoryOut,
    AdminCategoryUpdate,
    CategoryOptionsResponse,
    DeleteResponse,
    FriendLinkOut,
    FriendLinkUpdate,
    LoginRequest,
    LoginResponse,
    OverviewResponse,
    SiteCreate,
    SiteOut,
)
from .security import create_access_token, require_admin_token, verify_admin_password


router = APIRouter(prefix="/api/v1", tags=["admin"])


@router.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    if not verify_admin_password(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    admin = get_admin_by_username(payload.username)
    assert admin is not None
    return LoginResponse(accessToken=create_access_token(admin["username"]), username=admin["username"])


@router.get("/admin/overview", response_model=OverviewResponse)
def get_admin_overview(_: str = Depends(require_admin_token)) -> OverviewResponse:
    all_sites = list_sites(None)
    category_count = len({(site.level1, site.level2) for site in all_sites if site.level1.strip() and site.level2.strip()})
    pending_count = sum(1 for site in all_sites if site.status == "pending")
    recent_sites = sorted(all_sites, key=lambda item: item.id, reverse=True)[:10]
    return OverviewResponse(
        totalSites=len(all_sites),
        totalCategories=category_count,
        pendingSubmissions=pending_count,
        recentSites=recent_sites,
    )


@router.get("/admin/sites", response_model=List[SiteOut])
def get_admin_sites(
    status_value: Optional[str] = Query(default=None, alias="status"),
    _: str = Depends(require_admin_token),
) -> List[SiteOut]:
    return list_sites(status_value)


@router.get("/admin/categories", response_model=CategoryOptionsResponse)
def get_admin_categories(_: str = Depends(require_admin_token)) -> CategoryOptionsResponse:
    return CategoryOptionsResponse(**get_category_options(None))


@router.get("/admin/categories/tree", response_model=List[AdminCategoryNode])
def get_admin_category_tree(_: str = Depends(require_admin_token)) -> List[AdminCategoryNode]:
    return build_admin_category_tree()


@router.post("/admin/categories", response_model=AdminCategoryOut, status_code=201)
def create_admin_category(payload: AdminCategoryCreate, _: str = Depends(require_admin_token)) -> AdminCategoryOut:
    return create_category(payload)


@router.put("/admin/categories/{category_id}", response_model=AdminCategoryOut)
def update_admin_category(
    category_id: int,
    payload: AdminCategoryUpdate,
    _: str = Depends(require_admin_token),
) -> AdminCategoryOut:
    return update_category(category_id, payload)


@router.delete("/admin/categories/{category_id}", response_model=DeleteResponse)
def delete_admin_category(
    category_id: int,
    delete_related_content: bool = Query(default=False, alias="deleteRelatedContent"),
    _: str = Depends(require_admin_token),
) -> DeleteResponse:
    delete_category(category_id, delete_related_content)
    return DeleteResponse(detail="Category deleted")


@router.put("/admin/password", response_model=DeleteResponse)
def update_password(
    payload: AdminPasswordUpdateRequest,
    username: str = Depends(require_admin_token),
) -> DeleteResponse:
    update_admin_password(username, payload.oldPass, payload.newPass)
    return DeleteResponse(detail="Password updated")


@router.post("/admin/sites", response_model=SiteOut, status_code=201)
def create_admin_site(payload: SiteCreate, _: str = Depends(require_admin_token)) -> SiteOut:
    return create_site(payload, payload.status or "approved")


@router.put("/admin/sites/{site_id}", response_model=SiteOut)
def update_admin_site(site_id: int, payload: SiteCreate, _: str = Depends(require_admin_token)) -> SiteOut:
    return update_site(site_id, payload)


@router.delete("/admin/sites/uncategorized", response_model=DeleteResponse)
def clear_admin_uncategorized_sites(_: str = Depends(require_admin_token)) -> DeleteResponse:
    deleted_count = clear_uncategorized_sites()
    return DeleteResponse(detail=f"Deleted {deleted_count} uncategorized items")


@router.delete("/admin/sites/{site_id}", response_model=DeleteResponse)
def delete_admin_site(
    site_id: int,
    content_type: str = Query(alias="type"),
    _: str = Depends(require_admin_token),
) -> DeleteResponse:
    if content_type not in {"site", "article"}:
        raise HTTPException(status_code=422, detail="Invalid content type")
    delete_site(site_id, content_type)
    return DeleteResponse(detail="Content deleted")


@router.get("/admin/friend-links", response_model=List[FriendLinkOut])
def get_admin_friend_links(
    status_value: Optional[str] = Query(default=None, alias="status"),
    _: str = Depends(require_admin_token),
) -> List[FriendLinkOut]:
    return list_friend_links(status_value)


@router.put("/admin/friend-links/{friend_link_id}", response_model=FriendLinkOut)
def update_admin_friend_link(
    friend_link_id: int,
    payload: FriendLinkUpdate,
    _: str = Depends(require_admin_token),
) -> FriendLinkOut:
    return update_friend_link(friend_link_id, payload)


@router.delete("/admin/friend-links/{friend_link_id}", response_model=DeleteResponse)
def delete_admin_friend_link(friend_link_id: int, _: str = Depends(require_admin_token)) -> DeleteResponse:
    delete_friend_link(friend_link_id)
    return DeleteResponse(detail="Friend link deleted")
