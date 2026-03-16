import axios from 'axios'

export type ContentType = 'site' | 'article'
export type ContentFormat = 'html' | 'markdown' | 'text'

export interface Site {
  id: number
  name: string
  url: string
  logo: string
  description: string
  level1: string
  level2: string
  level3: string
  tags: string[]
  isRecommended?: boolean
  sortOrder?: number
  clickCount?: number
  likes?: number
  dislikes?: number
  type?: ContentType
  content?: string
  contentFormat?: ContentFormat
  status?: 'draft' | 'approved' | 'pending'
  createdAt?: string
  updatedAt?: string
}

export interface TagInfo {
  name: string
  count: number
}

export interface SiteSubmissionPayload {
  name: string
  url: string
  logo?: string
  description?: string
  level1?: string
  level2?: string
  level3?: string
  tags?: string[] | string
  isRecommended?: boolean
  sortOrder?: number
  type?: ContentType
  content?: string
  contentFormat?: ContentFormat
  submitterEmail?: string
}

export interface FriendLinkPayload {
  siteName: string
  siteUrl: string
  siteDesc?: string
  contactEmail: string
}

export interface FriendLink {
  id: number
  siteName: string
  siteUrl: string
  siteDesc: string
  contactEmail: string
  status: 'pending' | 'approved' | 'rejected'
  createdAt: string
  updatedAt: string
}

export interface LoginPayload {
  username: string
  password: string
}

export interface LoginResponse {
  accessToken: string
  tokenType: string
  username: string
}

export interface AdminOverview {
  totalSites: number
  totalCategories: number
  pendingSubmissions: number
  recentSites: Site[]
}

export interface Level2Category {
  name: string
  total: number
}

export interface Level1Category {
  name: string
  total: number
  children: Level2Category[]
}

export interface NavigationResponse {
  categories: Level1Category[]
  sites: Site[]
}

export interface CategoryOptions {
  level1Options: string[]
  level2Options: string[]
  level2ByLevel1: Record<string, string[]>
}

export interface AdminCategoryNode {
  id: number
  name: string
  total: number
  sortOrder: number
  parentId: number | null
  children: AdminCategoryNode[]
}

export interface AdminCategory {
  id: number
  name: string
  sortOrder: number
  parentId: number | null
  createdAt: string
  updatedAt: string
}

export interface AdminCategoryPayload {
  name: string
  sortOrder?: number
  parentId?: number | null
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 10000
})

const ADMIN_TOKEN_KEY = 'nav_admin_token'

export const getAdminToken = () => localStorage.getItem(ADMIN_TOKEN_KEY)
export const setAdminToken = (token: string) => localStorage.setItem(ADMIN_TOKEN_KEY, token)
export const clearAdminToken = () => localStorage.removeItem(ADMIN_TOKEN_KEY)
export const isAdminLoggedIn = () => Boolean(getAdminToken())

api.interceptors.request.use((config) => {
  const token = getAdminToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearAdminToken()
    }
    return Promise.reject(error)
  }
)

const normalizeTags = (tags?: string[] | string) => {
  if (!tags) return []
  if (Array.isArray(tags)) return tags.filter(Boolean)
  return tags.split(',').map(item => item.trim()).filter(Boolean)
}

const buildSitePayload = (payload: Partial<SiteSubmissionPayload>) => ({
  name: payload.name || '',
  url: payload.url || '',
  logo: payload.logo || '',
  description: payload.description || '',
  level1: payload.level1 || '',
  level2: payload.level2 || '',
  level3: payload.level3 || '',
  tags: normalizeTags(payload.tags),
  isRecommended: Boolean(payload.isRecommended),
  sortOrder: Number(payload.sortOrder || 0),
  type: payload.type || 'site',
  content: payload.content || '',
  contentFormat: payload.contentFormat || 'html'
})

export const fetchSites = async (): Promise<Site[]> => {
  const { data } = await api.get<Site[]>('/sites')
  return data
}

export const fetchNavigation = async (): Promise<NavigationResponse> => {
  const { data } = await api.get<NavigationResponse>('/navigation')
  return data
}

export const fetchCategoryOptions = async (): Promise<CategoryOptions> => {
  const { data } = await api.get<CategoryOptions>('/categories')
  return data
}

export const fetchSiteById = async (type: ContentType, id: number): Promise<Site | undefined> => {
  try {
    const { data } = await api.get<Site>(`/contents/${type}/${id}`)
    return data
  } catch {
    return undefined
  }
}

export const submitSite = async (payload: SiteSubmissionPayload): Promise<Site> => {
  const { data } = await api.post<Site>('/submissions/sites', {
    ...buildSitePayload(payload),
    submitterEmail: payload.submitterEmail || null
  })
  return data
}

export const submitFriendLink = async (payload: FriendLinkPayload) => {
  const { data } = await api.post<FriendLink>('/friend-links', payload)
  return data
}

export const fetchFriendLinks = async (): Promise<FriendLink[]> => {
  const { data } = await api.get<FriendLink[]>('/friend-links')
  return data
}

export const loginAdmin = async (payload: LoginPayload): Promise<LoginResponse> => {
  const { data } = await api.post<LoginResponse>('/auth/login', payload)
  setAdminToken(data.accessToken)
  return data
}

export const fetchAdminOverview = async (): Promise<AdminOverview> => {
  const { data } = await api.get<AdminOverview>('/admin/overview')
  return data
}

export const fetchAdminSites = async (status?: string): Promise<Site[]> => {
  const { data } = await api.get<Site[]>('/admin/sites', {
    params: status ? { status } : undefined
  })
  return data
}

export const fetchAdminCategoryOptions = async (): Promise<CategoryOptions> => {
  const { data } = await api.get<CategoryOptions>('/admin/categories')
  return data
}

export const fetchAdminCategoryTree = async (): Promise<AdminCategoryNode[]> => {
  const { data } = await api.get<AdminCategoryNode[]>('/admin/categories/tree')
  return data
}

export const createAdminCategory = async (payload: AdminCategoryPayload): Promise<AdminCategory> => {
  const { data } = await api.post<AdminCategory>('/admin/categories', {
    name: payload.name,
    sortOrder: Number(payload.sortOrder || 0),
    parentId: payload.parentId ?? null
  })
  return data
}

export const updateAdminCategory = async (id: number, payload: AdminCategoryPayload): Promise<AdminCategory> => {
  const { data } = await api.put<AdminCategory>(`/admin/categories/${id}`, {
    name: payload.name,
    sortOrder: Number(payload.sortOrder || 0),
    parentId: payload.parentId ?? null
  })
  return data
}

export const deleteAdminCategory = async (id: number, deleteRelatedContent = false): Promise<void> => {
  await api.delete(`/admin/categories/${id}`, {
    params: { deleteRelatedContent }
  })
}

export const createAdminSite = async (payload: SiteSubmissionPayload & { status?: 'draft' | 'approved' | 'pending' }): Promise<Site> => {
  const { data } = await api.post<Site>('/admin/sites', {
    ...buildSitePayload(payload),
    status: payload.status || 'approved'
  })
  return data
}

export const updateAdminSite = async (id: number, payload: SiteSubmissionPayload & { status?: 'draft' | 'approved' | 'pending' }): Promise<Site> => {
  const { data } = await api.put<Site>(`/admin/sites/${id}`, {
    ...buildSitePayload(payload),
    status: payload.status || 'approved'
  })
  return data
}

export const deleteAdminSite = async (id: number, type: ContentType): Promise<void> => {
  await api.delete(`/admin/sites/${id}`, {
    params: { type }
  })
}

export const clearAdminUncategorizedSites = async (): Promise<void> => {
  await api.delete('/admin/sites/uncategorized')
}

export const fetchAdminFriendLinks = async (status?: string): Promise<FriendLink[]> => {
  const { data } = await api.get<FriendLink[]>('/admin/friend-links', {
    params: status ? { status } : undefined
  })
  return data
}

export const updateAdminFriendLink = async (
  id: number,
  status: 'pending' | 'approved' | 'rejected'
): Promise<FriendLink> => {
  const { data } = await api.put<FriendLink>(`/admin/friend-links/${id}`, { status })
  return data
}

export const deleteAdminFriendLink = async (id: number): Promise<void> => {
  await api.delete(`/admin/friend-links/${id}`)
}

export const updateAdminPassword = async (oldPass: string, newPass: string): Promise<void> => {
  await api.put('/admin/password', { oldPass, newPass })
}

export const recordClick = async (type: ContentType, id: number): Promise<number> => {
  const { data } = await api.post<{ clickCount: number }>(`/contents/${type}/${id}/click`)
  return data.clickCount
}

export const fetchRandomSites = async (count = 5): Promise<Site[]> => {
  const { data } = await api.get<Site[]>('/random', { params: { count } })
  return data
}

export const fetchRecentSites = async (count = 10): Promise<Site[]> => {
  const { data } = await api.get<Site[]>('/recent', { params: { count } })
  return data
}

export const fetchPopularSites = async (count = 10): Promise<Site[]> => {
  const { data } = await api.get<Site[]>('/popular', { params: { count } })
  return data
}

export const fetchAllTags = async (): Promise<TagInfo[]> => {
  const { data } = await api.get<TagInfo[]>('/tags')
  return data
}

export interface CheckinResult {
  checkinDate: string
  streak: number
  totalPoints: number
  pointsEarned: number
  isNewCheckin: boolean
}

export interface CheckinStatus {
  checkinDate: string
  streak: number
  totalPoints: number
  checkedInToday: boolean
}

export interface VoteResult {
  likes: number
  dislikes: number
  userVote: string | null
}

export interface Announcement {
  id: number
  title: string
  content: string
  type: 'info' | 'warning' | 'success'
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export const doCheckin = async (fingerprint: string): Promise<CheckinResult> => {
  const { data } = await api.post<CheckinResult>('/checkin', { fingerprint })
  return data
}

export const getCheckinStatus = async (fingerprint: string): Promise<CheckinStatus> => {
  const { data } = await api.get<CheckinStatus>(`/checkin/${fingerprint}`)
  return data
}

export const voteContent = async (type: ContentType, id: number, fingerprint: string, voteType: 'like' | 'dislike'): Promise<VoteResult> => {
  const { data } = await api.post<VoteResult>(`/contents/${type}/${id}/vote`, { fingerprint, voteType })
  return data
}

export const getVoteStatus = async (type: ContentType, id: number, fingerprint: string): Promise<{ userVote: string | null }> => {
  const { data } = await api.get<{ userVote: string | null }>(`/contents/${type}/${id}/vote/${fingerprint}`)
  return data
}

export const fetchRelatedSites = async (type: ContentType, id: number, count = 6): Promise<Site[]> => {
  const { data } = await api.get<Site[]>(`/contents/${type}/${id}/related`, { params: { count } })
  return data
}

export const fetchAnnouncements = async (): Promise<Announcement[]> => {
  const { data } = await api.get<Announcement[]>('/announcements')
  return data
}

export const checkSubmissionStatus = async (name: string, url: string): Promise<any[]> => {
  const { data } = await api.get('/submissions/status', { params: { name, url } })
  return data
}

export interface StatsResponse {
  totalSites: number
  totalArticles: number
  totalCategories: number
  totalTags: number
}

export const fetchStats = async (): Promise<StatsResponse> => {
  const { data } = await api.get<StatsResponse>('/stats')
  return data
}

export interface SearchSuggestResponse {
  sites: Site[]
  tags: string[]
}

export const fetchSearchSuggest = async (q: string, limit = 8): Promise<SearchSuggestResponse> => {
  const { data } = await api.get<SearchSuggestResponse>('/search/suggest', { params: { q, limit } })
  return data
}

export const submitFeedback = async (type: 'feature' | 'bug' | 'other', content: string): Promise<void> => {
  await api.post('/feedback', { type, content })
}

export const submitReport = async (contentType: ContentType, contentId: number, reason: string): Promise<void> => {
  await api.post('/report', { contentType, contentId, reason })
}
