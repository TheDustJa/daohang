from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


ContentType = Literal["site", "article"]
ContentFormat = Literal["html", "markdown", "text"]


class SiteBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    url: str = Field(default="")
    logo: str = Field(default="")
    description: str = Field(default="", max_length=1000)
    level1: str = Field(default="")
    level2: str = Field(default="")
    level3: str = Field(default="")
    tags: List[str] = Field(default_factory=list)
    isRecommended: bool = False
    sortOrder: int = 0
    type: ContentType = "site"
    content: str = Field(default="")
    contentFormat: ContentFormat = "html"

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        raise ValueError("tags format is invalid")


class SiteOut(SiteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    createdAt: str
    updatedAt: str


class SiteCreate(SiteBase):
    status: Optional[Literal["draft", "approved", "pending"]] = None


class SiteSubmissionCreate(SiteBase):
    submitterEmail: Optional[str] = None


class FriendLinkCreate(BaseModel):
    siteName: str = Field(min_length=1, max_length=120)
    siteUrl: str = Field(min_length=1, max_length=255)
    siteDesc: str = Field(default="", max_length=500)
    contactEmail: str = Field(min_length=3, max_length=120)


class FriendLinkOut(FriendLinkCreate):
    id: int
    status: str
    createdAt: str
    updatedAt: str


class FriendLinkUpdate(BaseModel):
    status: Literal["pending", "approved", "rejected"]


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class LoginResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    username: str


class AdminPasswordUpdateRequest(BaseModel):
    oldPass: str = Field(
        min_length=1,
        max_length=128,
        validation_alias=AliasChoices("oldPass", "password"),
    )
    newPass: str = Field(
        min_length=6,
        max_length=128,
        validation_alias=AliasChoices("newPass", "newPassword"),
    )


class OverviewResponse(BaseModel):
    totalSites: int
    totalCategories: int
    pendingSubmissions: int
    recentSites: List[SiteOut]


class Level2CategoryOut(BaseModel):
    name: str
    total: int


class Level1CategoryOut(BaseModel):
    name: str
    total: int
    children: List[Level2CategoryOut]


class NavigationResponse(BaseModel):
    categories: List[Level1CategoryOut]
    sites: List[SiteOut]


class CategoryOptionsResponse(BaseModel):
    level1Options: List[str]
    level2Options: List[str]
    level2ByLevel1: Dict[str, List[str]]


class AdminCategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sortOrder: int = 0


class AdminCategoryCreate(AdminCategoryBase):
    parentId: Optional[int] = None


class AdminCategoryUpdate(AdminCategoryBase):
    parentId: Optional[int] = None


class AdminCategoryOut(AdminCategoryBase):
    id: int
    parentId: Optional[int] = None
    createdAt: str
    updatedAt: str


class AdminCategoryNode(BaseModel):
    id: int
    name: str
    total: int
    sortOrder: int = 0
    parentId: Optional[int] = None
    children: List["AdminCategoryNode"] = Field(default_factory=list)


class DeleteResponse(BaseModel):
    detail: str
