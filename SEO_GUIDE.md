# AI 导航站 SEO 优化实践指南

## 一、已完成的技术 SEO（代码层面）

### 1. HTML 基础 Meta 标签
- `index.html` 已设置 `lang="zh-CN"`、description、keywords、OG 标签、Twitter Card
- **需要修改**：`robots.txt` 和 `index.html` 中的 `your-domain.com` 替换为你的真实域名

### 2. 路由级动态 Title / Description
- 每个路由页面都配置了独立的 `title` 和 `description`
- 路由守卫 `afterEach` 自动更新 `document.title` 和 meta description
- 管理后台页面已标记 `robots: 'noindex, nofollow'`

### 3. 结构化数据（JSON-LD）
- **首页**：`WebSite` schema + `SearchAction`（支持搜索引擎直接搜索框）
- **详情页**：
  - 文章类型 → `Article` schema（含 headline、datePublished、dateModified）
  - 工具类型 → `SoftwareApplication` schema（含 name、url、applicationCategory）

### 4. Canonical URL
- 详情页已注入 `<link rel="canonical">`，避免重复内容问题

### 5. 图片优化
- 所有 `<img>` 标签已添加 `alt` 属性
- 使用 `loading="lazy"` + `decoding="async"` 延迟加载

### 6. robots.txt
- 位于 `web/public/robots.txt`
- 允许爬取公开页面，禁止 `/admin` 和 `/login`
- 声明 Sitemap 地址

### 7. 动态 Sitemap
- 后端 `/api/v1/sitemap.xml` 自动根据数据库内容生成
- Nginx 将 `/sitemap.xml` 代理到后端
- 推荐内容 priority=0.8，普通内容 priority=0.6

### 8. Nginx 静态资源缓存
- JS/CSS/图片等静态资源设置 30 天缓存 + immutable 标记

---

## 二、部署后需要手动操作的 SEO 工作

### 1. 域名替换 ⚠️ 必须

以下文件中的 `your-domain.com` 需要替换为实际域名：

| 文件 | 位置 |
|------|------|
| `web/public/robots.txt` | Sitemap URL |
| `pybackground/app/routers_public.py` | sitemap() 中的 base_url |

### 2. 搜索引擎提交

| 搜索引擎 | 操作 | 地址 |
|-----------|------|------|
| **百度** | 提交站点 + Sitemap | https://ziyuan.baidu.com/site/ |
| **Google** | 提交 Search Console | https://search.google.com/search-console/ |
| **Bing** | 提交 Webmaster Tools | https://www.bing.com/webmasters/ |
| **头条搜索** | 提交站长平台 | https://zhanzhang.toutiao.com/ |

**提交步骤**：
1. 注册并验证域名所有权（通常 DNS TXT 验证最方便）
2. 提交 Sitemap 地址：`https://your-domain.com/sitemap.xml`
3. 使用"URL 检测"工具手动请求抓取首页

### 3. 百度专项优化

```
<!-- 可选：在 index.html 中添加百度自动推送 -->
<script>
(function(){
    var bp = document.createElement('script');
    var curProtocol = window.location.protocol.split(':')[0];
    bp.src = curProtocol === 'https' ? 'https://zz.bdstatic.com/linksubmit/push.js' : 'http://push.zz.bdstatic.com/push.js';
    var s = document.getElementsByTagName("script")[0];
    s.parentNode.insertBefore(bp, s);
})();
</script>
```

### 4. HTTPS 配置
- 确保全站 HTTPS，搜索引擎偏好 HTTPS
- 配置 HTTP → HTTPS 301 重定向
- 更新 OG 标签和 Sitemap 中的 URL 为 https://

### 5. 备案信息
- 在 `FooterLinks.vue` 中修改 ICP 备案号为真实信息
- 国内搜索引擎（百度、头条）对已备案站点有明显收录优势

---

## 三、内容层面 SEO 建议

### 1. 高质量内容产出
- **定期更新**：每周至少更新 3-5 个新工具收录或文章
- **原创描述**：每个工具的 description 应该是原创的、有价值的，不要直接复制官网介绍
- **长尾关键词**：工具描述中自然融入搜索关键词，如"免费 AI 写作工具"、"AI 图片生成器"

### 2. 标签策略
- 每个工具至少设置 2-3 个标签
- 标签应该是用户真实会搜索的词汇
- 建议标签体系：功能类（写作、画图、编程）+ 属性类（免费、开源、中文）

### 3. 内链建设
- 文章中可以引用其他收录的工具，形成内链网络
- 分类页之间建立关联（如"AI 写作"页面底部推荐"AI 提示词"分类）

### 4. 外链获取
- 友链交换（已有机制）
- 在知乎、掘金、V2EX 等社区发布内容并附带链接
- GitHub README 中添加链接
- 提交到其他导航站收录

---

## 四、性能优化（影响 SEO 排名）

### Core Web Vitals 优化建议

| 指标 | 当前状态 | 优化建议 |
|------|----------|----------|
| **LCP** (最大内容绘制) | 需测量 | 首屏内容应在 2.5s 内加载完成 |
| **FID** (首次输入延迟) | 良好（Vue 轻量） | 保持 JS bundle 体积小 |
| **CLS** (累积布局偏移) | 需测量 | 图片/卡片设置固定尺寸 |

### 优化方法
1. **开启 Gzip/Brotli 压缩**（Nginx 配置）：
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml;
gzip_min_length 1024;
```

2. **图片格式优化**：考虑使用自建 favicon 缓存服务替代 Google favicon API
3. **预加载关键资源**：
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="dns-prefetch" href="https://www.google.com">
```

---

## 五、SPA SEO 进阶方案

当前项目是 Vue SPA（客户端渲染），搜索引擎爬虫对 SPA 的支持情况：

| 搜索引擎 | JS 渲染支持 |
|-----------|-------------|
| Google | ✅ 完整支持（Chromium 渲染） |
| Bing | ✅ 基本支持 |
| 百度 | ⚠️ 有限支持（不稳定） |
| 头条搜索 | ⚠️ 有限支持 |

### 如果百度收录效果不好，考虑以下方案：

#### 方案 A：Prerender.io / 预渲染
- 部署 prerender 服务，针对爬虫返回预渲染的 HTML
- Nginx 判断 User-Agent 分流

#### 方案 B：Nuxt.js SSR 迁移
- 将 Vue SPA 迁移到 Nuxt.js 实现服务端渲染
- 成本较高但 SEO 效果最好

#### 方案 C：静态页面生成
- 定时任务将热门页面生成静态 HTML
- 爬虫访问时返回静态版本

**推荐**：先用当前方案上线，监测 1-2 个月的收录情况，如果百度收录不理想再考虑方案 A。

---

## 六、监控与持续优化

### 推荐工具
- **Google Search Console**：监控收录、排名、点击率
- **百度统计**：国内流量分析
- **Google Analytics 4**：用户行为分析
- **PageSpeed Insights**：性能评分（https://pagespeed.web.dev/）
- **Ahrefs / 5118**：关键词排名跟踪

### 月度 SEO 检查清单
- [ ] 检查 sitemap 是否正常生成
- [ ] 检查 robots.txt 是否正确
- [ ] 查看 Search Console 是否有抓取错误
- [ ] 检查关键页面的 title/description 是否合适
- [ ] 查看 Core Web Vitals 是否达标
- [ ] 更新新增内容的结构化数据
- [ ] 检查死链和 404 页面
