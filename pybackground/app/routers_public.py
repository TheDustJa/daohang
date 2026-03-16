from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from .repositories import (
    build_navigation_categories,
    create_feedback,
    create_friend_link,
    create_report,
    create_site,
    do_checkin,
    do_vote,
    get_all_tags,
    get_category_options,
    get_checkin_status,
    get_popular_sites,
    get_random_sites,
    get_recent_sites,
    get_related_sites,
    get_site_by_id,
    get_stats,
    get_submission_status,
    search_suggest,
    get_vote_status,
    list_announcements,
    list_friend_links,
    list_sites,
    record_click,
)
from .schemas import (
    CategoryOptionsResponse,
    CheckinRequest,
    CheckinResponse,
    FeedbackCreate,
    FriendLinkCreate,
    FriendLinkOut,
    NavigationResponse,
    ReportCreate,
    SiteOut,
    SiteSubmissionCreate,
    VoteRequest,
    VoteResponse,
)


router = APIRouter(prefix="/api/v1", tags=["public"])


@router.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@router.get("/stats")
def stats() -> Dict[str, Any]:
    return get_stats()


@router.get("/search/suggest")
def suggest(q: str = "", limit: int = 8) -> Dict[str, Any]:
    return search_suggest(q, min(limit, 20))


@router.get("/sites", response_model=List[SiteOut])
def get_sites(tag: str = "") -> List[SiteOut]:
    return list_sites("approved", tag.strip() or None)


@router.get("/navigation", response_model=NavigationResponse)
def get_navigation(tag: str = "") -> NavigationResponse:
    sites = list_sites("approved", tag.strip() or None)
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


@router.post("/contents/{content_type}/{content_id}/click")
def click_content(content_type: str, content_id: int) -> Dict[str, int]:
    if content_type not in {"site", "article"}:
        raise HTTPException(status_code=404, detail="Content not found")
    count = record_click(content_type, content_id)
    return {"clickCount": count}


@router.get("/random", response_model=List[SiteOut])
def random_sites(count: int = 5) -> List[SiteOut]:
    return get_random_sites(min(count, 20))


@router.get("/recent", response_model=List[SiteOut])
def recent_sites(count: int = 10) -> List[SiteOut]:
    return get_recent_sites(min(count, 30))


@router.get("/popular", response_model=List[SiteOut])
def popular_sites(count: int = 10) -> List[SiteOut]:
    return get_popular_sites(min(count, 30))


@router.get("/tags")
def all_tags() -> List[Dict[str, Any]]:
    return get_all_tags()


@router.post("/checkin", response_model=CheckinResponse)
def checkin(payload: CheckinRequest) -> CheckinResponse:
    result = do_checkin(payload.fingerprint)
    return CheckinResponse(**result)


@router.get("/checkin/{fingerprint}")
def checkin_status(fingerprint: str) -> Dict[str, Any]:
    return get_checkin_status(fingerprint)


@router.post("/contents/{content_type}/{content_id}/vote", response_model=VoteResponse)
def vote_content(content_type: str, content_id: int, payload: VoteRequest) -> VoteResponse:
    if content_type not in {"site", "article"}:
        raise HTTPException(status_code=404, detail="Content not found")
    result = do_vote(payload.fingerprint, content_type, content_id, payload.voteType)
    return VoteResponse(**result)


@router.get("/contents/{content_type}/{content_id}/vote/{fingerprint}")
def get_content_vote(content_type: str, content_id: int, fingerprint: str) -> Dict[str, Any]:
    vote = get_vote_status(fingerprint, content_type, content_id)
    return {"userVote": vote}


@router.get("/contents/{content_type}/{content_id}/related", response_model=List[SiteOut])
def related_content(content_type: str, content_id: int, count: int = 6) -> List[SiteOut]:
    if content_type not in {"site", "article"}:
        raise HTTPException(status_code=404, detail="Content not found")
    return get_related_sites(content_type, content_id, min(count, 12))


@router.get("/announcements")
def get_announcements() -> List[Dict[str, Any]]:
    return list_announcements(active_only=True)


@router.get("/submissions/status")
def submission_status(name: str = "", url: str = "") -> List[Dict[str, Any]]:
    if not name and not url:
        raise HTTPException(status_code=400, detail="Provide name or url")
    return get_submission_status(name, url)


@router.post("/feedback")
def submit_feedback(payload: FeedbackCreate) -> Dict[str, str]:
    create_feedback(payload.type, payload.content)
    return {"status": "ok"}


@router.post("/report")
def submit_report(payload: ReportCreate) -> Dict[str, str]:
    site = get_site_by_id(payload.contentId, payload.contentType, allow_pending=False)
    if site is None:
        raise HTTPException(status_code=404, detail="Content not found")
    create_report(payload.contentType, payload.contentId, payload.reason)
    return {"status": "ok"}


@router.get("/rss.xml")
def rss_feed() -> Response:
    base_url = "https://your-domain.com"
    sites = list_sites("approved")
    recent = sorted(sites, key=lambda s: s.createdAt or "", reverse=True)[:20]

    items = []
    for site in recent:
        ct = getattr(site, "type", "site") or "site"
        link = f"{base_url}/content/{ct}/{site.id}"
        pub_date = site.createdAt or ""
        items.append(
            f"    <item>\n"
            f"      <title>{site.name}</title>\n"
            f"      <link>{link}</link>\n"
            f"      <description>{site.description}</description>\n"
            f"      <pubDate>{pub_date}</pubDate>\n"
            f"    </item>"
        )

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<rss version="2.0">\n  <channel>\n'
    xml += f"    <title>AI \u5bfc\u822a\u7ad9</title>\n"
    xml += f"    <link>{base_url}</link>\n"
    xml += f"    <description>\u6536\u5f55\u4f18\u8d28 AI \u5de5\u5177\u3001\u5e73\u53f0\u4e0e\u7ad9\u5185\u6587\u7ae0</description>\n"
    xml += "\n".join(items)
    xml += "\n  </channel>\n</rss>"

    return Response(content=xml, media_type="application/rss+xml")


@router.get("/sitemap.xml")
def sitemap() -> Response:
    """Generate a dynamic sitemap based on approved sites and articles."""
    base_url = "https://your-domain.com"
    sites = list_sites("approved")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    urls = [
        f'  <url><loc>{base_url}/</loc><lastmod>{now}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>',
        f'  <url><loc>{base_url}/submit</loc><changefreq>monthly</changefreq><priority>0.5</priority></url>',
        f'  <url><loc>{base_url}/friend-link</loc><changefreq>monthly</changefreq><priority>0.4</priority></url>',
    ]

    for site in sites:
        content_type = getattr(site, "type", "site") or "site"
        loc = f"{base_url}/content/{content_type}/{site.id}"
        lastmod = ""
        if hasattr(site, "updated_at") and site.updated_at:
            lastmod = f"<lastmod>{str(site.updated_at)[:10]}</lastmod>"
        priority = "0.8" if getattr(site, "is_recommended", False) else "0.6"
        urls.append(f"  <url><loc>{loc}</loc>{lastmod}<changefreq>weekly</changefreq><priority>{priority}</priority></url>")

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += "\n".join(urls)
    xml += "\n</urlset>"

    return Response(content=xml, media_type="application/xml")
