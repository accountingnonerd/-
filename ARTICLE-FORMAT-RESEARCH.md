# LinkedIn Articles for "One Painful Problem": distribution, editor limits, copy-out risks, tooling

Research date: 2026-11-18. Scope: web research only.

## How this was researched (read first)

- **Direct page fetching was blocked in this session.** www.linkedin.com, searchengineland.com and other hosts would not resolve through the session network, so **no LinkedIn Help page was read in full**. Every claim below comes from search-engine result snippets and summaries of the cited pages. Treat "strong" ratings as "official source, read through snippets only". To upgrade any of them, open the linked Help page and confirm the wording.
- Several LinkedIn Help pages surfaced with old "last updated" stamps (roughly 2022 to 2024). The editor may have changed since then. Items marked **UNVERIFIED** need a 5-minute check in the live editor.
- Strength scale: **Strong** = official LinkedIn Help, blog or developer docs. **Moderate** = large-dataset study (vendor-run, but with sample sizes). **Weak** = marketer or blog opinion, single-creator anecdote, or secondhand quote.

---

## 1. Distribution: articles vs posts (2025-2026)

### 1.1 Feed reach of articles

| Finding | Source | Strength |
|---|---|---|
| On personal profiles, articles reach a median of **596** people. Text posts reach 921, image posts 1,031 and document (PDF carousel) posts **1,198**. Articles reach about 0.69x the average post. Window: Mar 2025 to Feb 2026. Sample sizes cited range from about 372k to more than 3M posts, depending on the AuthoredUp page. | https://authoredup.com/blog/best-performing-content-on-linkedin ; https://authoredup.com/blog/linkedin-articles-vs-posts | Moderate |
| Median engagements: articles **12**, text posts 21, images 36, documents 35 (same dataset). | same as above | Moderate |
| Article reach was relatively stable year over year (about -6%). Video fell about 36% and images about 16%. | https://authoredup.com/blog/linkedin-algorithm | Moderate |
| Claims that articles get "5-10x fewer impressions" than posts come from unnamed creator analyses. | https://writio.ai/blog/linkedin-articles-vs-posts-thought-leadership-which-performs-better-2026 | Weak |
| Overall organic reach on LinkedIn fell sharply in 2025. Figures attributed to Richard van der Blom's Algorithm Insights 2025 range from -34% to -50%. These are secondhand and the original report was not verified. | https://www.socialpilot.co/blog/linkedin-algorithm ; https://brixongroup.com/en/linkedin-algorithm-dos-donts-for-organic-visibility-in-the-b2b-sector | Weak (secondhand) |

**Takeaway:** an article on its own gets roughly half the feed reach of a document/carousel post. That is the format the series has used so far.

### 1.2 Is an article auto-shared as a post? Can the share text be edited?

| Finding | Source | Strength |
|---|---|---|
| Publishing flow: write the Title and body, click **Next**, then **Publish**. On the Next screen you can add optional commentary ("Tell your network what your article is about"). That commentary appears as the feed post that carries the article card. | https://www.linkedin.com/help/linkedin/answer/a522427 ; https://www.linkedin.com/help/lms/answer/a522427?lang=en-US | Strong (snippet) |
| Articles are shared with connections and followers in their feeds, and **sometimes** through notifications. Not everyone is notified. | https://www.linkedin.com/help/linkedin/answer/a522427/creating-articles-on-linkedin?lang=en ; https://www.linkedin.com/pulse/what-happens-after-you-hit-publish-daniel-roth (LinkedIn editor, older) | Strong / Weak |
| One guide says the commentary field holds about 700 characters. Hashtags typed there show in the feed commentary, not in the article. | https://contentstudio.io/blog/linkedin-articles | Weak |
| Editing a post afterwards: **only the text** of a post can be edited. Shared rich media (articles, documents, photos, video) cannot be replaced. This implies the share commentary is editable later and the attached article card is not. No Help page says this explicitly for article shares (**inference**). | https://www.linkedin.com/help/linkedin/answer/a522811 | Strong (inference) |
| The article body itself can be edited after publishing (Me > Posts & Activity > Articles > More > Edit article > Update). This is **not available in the mobile app**. | https://www.linkedin.com/help/linkedin/answer/a515989/editing-your-published-articles-on-linkedin?lang=en | Strong (snippet) |
| An older source says hashtags on the share cannot be edited after publishing. | https://contentstudio.io/blog/linkedin-articles | Weak (old) |

### 1.3 Google and LinkedIn search indexing; SEO settings

| Finding | Source | Strength |
|---|---|---|
| The editor offers **SEO title** and **SEO description** fields, found under Settings in the publishing menu (or "Manage" in newer guides), alongside the article URL. SEO titles over **60 characters are truncated**. The description guidance is **140-160 characters**. Both replace the article title and opening lines in search results. Grammarly-type extensions can block the Title field. | https://www.linkedin.com/help/learning/answer/a6244140 (Help page "SEO settings for articles or Newsletters published on LinkedIn") | Strong (snippet) |
| The feature launched around 2022 (SEO title and description for articles). | https://www.searchenginejournal.com/linkedin-introduces-seo-tools-for-articles (older) | Moderate (older) |
| Public articles are still indexable, typically within 24-48h. Indexing is described as inconsistent: articles can appear and then drop out. | https://socialrails.com/blog/linkedin-pulse-guide ; https://blog.thetrustedvoice.co/does-linkedin-content-get-indexed/ | Weak |
| Pulse pages ranking in Google reportedly fell from about 5M to about 500k (**-89% traffic**) between Mar 2024 and Mar 2026. This is a third-party SEO-tool analysis. | https://foundationinc.co/lab/linkedin-pulse-post-traffic/ ; https://contengi.com/blog/linkedin-articles-seo | Moderate |
| LinkedIn does not support canonical tags, so publish the canonical version elsewhere first if Google ranking matters. | https://contengi.com/blog/linkedin-articles-seo | Weak |
| Pulse content is reportedly heavily cited by AI answer engines (ChatGPT and Google AI Overviews). | https://www.pepper.inc/blog/linkedin-posts-vs-linkedin-pulse/ | Weak |
| LinkedIn on-site search of articles: **UNVERIFIED**. No 2025-2026 source found. | n/a | n/a |

**Takeaway:** fill in the SEO title and description on every article. Don't rely on Google traffic. The public GitHub repo, or a project site if one exists, is the better canonical, Google-findable home for the prompt.

### 1.4 LinkedIn Newsletters

| Topic | Finding | Source | Strength |
|---|---|---|---|
| Creator mode | The Creator Mode toggle was removed in **March 2024**. Its tools, newsletters included, were opened to members by default (announced Feb 2024). | https://natlawreview.com/article/what-linkedins-decision-remove-creator-mode-means-you ; https://www.commenti.in/blogs/what-happened-to-creator-mode-on-linkedin | Weak/Moderate (secondary, consistent) |
| Eligibility (personal) | **Conflicting.** The Help page "LinkedIn Newsletter access criteria" (a591266) is quoted as saying "Members and Pages with more than **150 followers and/or connections** are eligible to be evaluated", plus recent original content and good standing. Other quotes of LinkedIn Help (answer 134850 / Growigami) say "**All LinkedIn members** have access to create a newsletter." Social Media Today reports individuals can create newsletters regardless of follower count, while Pages need >150 followers. Most likely current state: no follower minimum for personal profiles, 150+ for Pages. **Verify** by opening Write article > Manage and checking for "Create newsletter". No "professional mode" requirement was found. | https://www.linkedin.com/help/linkedin/answer/a591266 ; https://www.linkedin.com/help/learning/answer/134850 ; https://growigami.com/blog/linkedin-newsletter ; https://www.socialmediatoday.com/news/linkedin-expands-newsletter-access-developing-premium-for-smbs/757515/ | Strong but conflicting |
| Setup | Write article > **Manage** > **Create newsletter**. Fields: title, description, "How often do you want to publish?" and an optional logo (300x300 recommended per guides). Up to **5 newsletters** per author. After creating or deleting one, you must wait **2 weeks** before creating another. | https://www.linkedin.com/help/linkedin/answer/a517925 ; https://nealschaffer.com/linkedin-newsletter/ | Strong (snippet) / Weak for logo size |
| Cadence options | The Help page names the frequency field but the snippet did not list its values. Guides list daily, weekly, biweekly and monthly; some list only weekly, biweekly and monthly. The declared cadence is a label, not an enforced schedule (**UNVERIFIED** that LinkedIn penalizes missed cadence). | https://www.linkedin.com/help/linkedin/answer/a517925 ; https://blog.brandghost.ai/posts/linkedin-newsletters-scheduling/ | Weak |
| First edition | By default, your **connections and followers are invited by notification to subscribe** once the first edition is published. The invite option can be unchecked. New followers are later auto-invited. | https://www.linkedin.com/help/linkedin/answer/a522525 ; https://www.linkedin.com/help/linkedin/answer/a517925 | Strong (snippet) |
| Every edition | After each edition, **push, in-app and email notifications** are sent to all subscribers. A Page-newsletter FAQ wording says in-app, push **or** email, deduplicated. One creator reports only about half of subscribers got the email because delivery follows each member's notification settings. | https://www.linkedin.com/help/linkedin/answer/a522525 ; https://theailab.substack.com/p/linkedin-newsletter-whats-happening | Strong / Weak (anecdote) |
| Analytics | **Email sends** and **email open rate** per edition were added to newsletter analytics in **Feb 2025**. You never get subscriber email addresses. | https://www.searchenginejournal.com/linkedin-rolls-out-email-metrics-for-newsletter-publishers/540469/ ; https://www.contentgrip.com/linkedin-enhances-newsletter-analytics/ | Moderate (trade press) |
| Converting an existing article | **No source documents converting an already-published standalone article into a newsletter edition.** The edition-or-standalone choice is made in the editor before publishing (dropdown near your name: "Individual article" vs your newsletter). The documented workaround is to republish the content as a new edition. Treat as **not possible** unless the live editor shows otherwise. | https://www.linkedin.com/help/linkedin/answer/a522427 ; https://www.socialmediaexaminer.com/how-to-use-linkedin-newsletters-a-guide-for-marketers/ | Strong (choice at publish) / Weak (no-convert) |
| Scheduling editions | The clock icon next to Publish schedules articles and Page newsletter editions. Personal editions use the same editor, but this is not separately documented. | https://www.linkedin.com/help/linkedin/answer/a569569 ; https://www.linkedin.com/help/linkedin/answer/a522427 | Strong (snippet) |

**Takeaway:** if a newsletter is the plan, create it **before** publishing the next tool and publish the tool as **edition #1**. The one-time "subscribe" invitation to all connections and followers fires on the first edition, and a standalone article cannot (per available evidence) be moved into the newsletter afterwards.

### 1.5 Companion feed post and the link penalty

| Finding | Source | Strength |
|---|---|---|
| LinkedIn has no published rule penalizing links. In Sept 2025, LinkedIn's Sr. Director of Product (Rishi Jobanputra) was quoted as saying "We don't intentionally limit the reach of posts with links." This is secondhand via Threads; the original post was not read. | https://www.threads.com/@mattnavarra/post/DOWa_61Cown/ ; https://contentin.io/glossary/external-link-penalty/ | Weak (secondhand official quote) |
| Measured gaps for posts with external links in the body: about 17-21% fewer impressions in MagicPost (287k and 866k posts), 18.8% in a van der Blom study (1.3M posts, secondhand) and 26.5% in Ordinal data. Some vendors claim 40-60%. | https://magicpost.in/studies/linkedin-link-penalty ; https://magicpost.in/blog/linkedin-external-links-reach ; https://ra-aha.com/blog/external-links-and-reach/ | Moderate (correlational) |
| "Link in first comment": MagicPost found posts saying "link in comments" sat about 16% below the author's no-link baseline, close to a typed URL (-21%). Some 2026 sources (citing a July 2026 Forbes piece, not located) say the workaround no longer helps. Link clicks in comments are not counted in LinkedIn analytics. | https://magicpost.in/studies/linkedin-link-penalty ; https://gromming.com/blog/linkedin-external-links-penalty | Moderate / Weak |
| A link **to a LinkedIn article** is an internal link. No study isolating internal-article links vs external links was found (**UNVERIFIED** whether "link penalty" findings apply). | n/a | n/a |
| Document/PDF carousel posts have the highest median reach of any format (1,198) and about 35 engagements. A carousel ending in a call to action that points to the article or repo is the common recommendation. | https://authoredup.com/blog/best-performing-content-on-linkedin ; https://socialbee.com/blog/how-to-post-linkedin-carousels/ | Moderate / Weak |

**Takeaway:** the publish-time share of the article already acts as a companion post (article card plus your commentary). A **separate** carousel post a day or two later, with the article URL in the post text or first comment, is the evidence-consistent way to get document-post reach. Expect any link to cost roughly 15-25%, not a collapse.

### 1.6 Title and cover image

| Finding | Source | Strength |
|---|---|---|
| Cover image: LinkedIn Help is cited by several guides as recommending **1920 x 1080 px (16:9)**. 1280 x 720 appears only in one blog. An older Help FAQ said 2000 x 600 (legacy layout). Max image size: 7680 x 4320 px. File limit: 5 MB (article help page) vs 10 MB (older FAQ). Formats: JPG, PNG and static GIF (WEBP per one guide). | https://heroshotphotography.com/linkedin-photo-size-dimensions/ ; https://sleekpost.com/blog/linkedin-article-image-size ; https://www.linkedin.com/help/linkedin/answer/a521719 ; https://www.linkedin.com/help/linkedin/answer/a522463 (older) | Strong-ish (official figure seen secondhand) |
| Feed and link-preview crops are about 1.91:1 (1200x627 or 1200x644 per different guides). Keep key text in the centre safe zone of a 16:9 cover. | https://viraly.io/blog/linkedin-image-sizes ; https://growigami.com/blog/linkedin-image-sizes | Weak |
| Article headline limit: **100 or 150 characters**, depending on the guide (unresolved). Body: about **110,000-125,000 characters** (125,000 is attributed to LinkedIn Help by two guides). The SEO title is truncated at 60. | https://authoredup.com/blog/linkedin-character-limit ; https://boldlytype.com/blog/linkedin-character-limit ; https://www.ghostwriting-ai.com/posts/linkedin-character-limits | Weak (conflicting) |
| Effect of a cover image on reach: no 2025-2026 data found (**UNVERIFIED**). | n/a | n/a |

---

## 2. What the article editor supports (checked against Help snippets)

| Feature | Status | Source | Strength |
|---|---|---|---|
| Headings | Yes, via the "Style" control. The levels are **unclear**: older docs and guides say Normal / Heading 1 / Heading 2; one 2026 guide says H2/H3. The article title is the page H1. **Verify in the editor.** | https://www.linkedin.com/help/linkedin/answer/a522427 ; https://www.linkedin.com/pulse/linkedin-articles-formatting-options-jim-kernicky (old) ; https://postsyncer.com/blog/how-do-i-post-an-article-on-linkedin | Strong (exists) / Weak (levels) |
| Bold, italic | Yes | a522427 (above) | Strong |
| Underline | Listed in older guides. **UNVERIFIED** for 2026. | Kernicky (old) | Weak |
| Strikethrough | No evidence it exists. **UNVERIFIED** | n/a | n/a |
| Bulleted and numbered lists | Yes ("ordered or unordered lists") | a522427 | Strong |
| Block quote | Yes | a522427 | Strong |
| Divider | Yes | a522427 | Strong |
| **Code block / snippet** | **Yes, per Help.** The help text says "Click **Code** to add a highlighted snippet" (older wording: "Snippets/Code"). Older third-party posts show it in the "+" insert menu. A keyboard shortcut (Ctrl+Alt+6 / Cmd+Opt+6) is described in a ~2019 LinkedIn Pulse post. **Not verified:** whether it preserves blank lines and indentation, renders monospace, has a copy button (almost certainly none), or has a length limit. No source covers these. | https://www.linkedin.com/help/linkedin/answer/a522427 ; https://www.linkedin.com/pulse/technical-writing-linkedin-just-got-better-now-you-can-anderson ; https://www.linkedin.com/pulse/include-code-snippet-pulse-articles-florent-georges | Strong (exists) / UNVERIFIED (behaviour) |
| Tables | **Not supported.** Help: "inserting tables isn't currently possible". Use an image. | https://www.linkedin.com/help/linkedin/answer/a521719 | Strong (snippet) |
| Images | Yes, inline. 5 MB vs 10 MB conflict (see 1.6). Max 7680x4320. Captions and alt text: **UNVERIFIED** (no Help snippet found). | https://www.linkedin.com/help/linkedin/answer/a521719 ; https://www.linkedin.com/help/linkedin/answer/a522463 | Strong / UNVERIFIED |
| Video | Embedding by pasting a link: **YouTube, Vimeo** among supported providers. Native video upload into articles: **UNVERIFIED**. | https://www.linkedin.com/help/linkedin/answer/a522472 | Strong (embeds) |
| Slides and documents | **SlideShare** embeds are supported. Native PDF upload into articles: no evidence (**UNVERIFIED**). Other providers listed include Spotify, SoundCloud and Prezi. Unsupported providers render as a large non-interactive link card. Pasted embed code is not supported, only URLs. Other LinkedIn articles cannot be embedded. LinkedIn posts can be embedded. | https://www.linkedin.com/help/linkedin/answer/a522472 ; https://www.linkedin.com/help/linkedin/answer/a522427 | Strong (snippet) |
| GitHub embed | GitHub is not in the provider list seen in snippets. A pasted repo URL will likely show as a link card (**UNVERIFIED**). | a522472 | Weak |
| Inline hyperlinks | Yes (text link in toolbar). | a522427 ; Kernicky | Strong/Weak |
| Max length | About 110k-125k characters (conflicting, see 1.6). | as above | Weak |
| Pasting rich text | **No official guidance.** Third parties say Google Docs/Word paste keeps bold, italic, lists and links, but strips code blocks and flattens nested lists. Raw Markdown pastes as literal characters. Heading mapping is unreliable. | https://md2rich.com/blog/markdown-to-linkedin-en ; https://postformatter.com/blog/how-to-paste-from-chatgpt-to-linkedin/ | Weak |
| Mobile app | **Writing and publishing articles is not available in the mobile app** (Help). Editing a published article is also desktop-only per Help. One blog claims mobile editing works (conflict). | https://www.linkedin.com/help/linkedin/answer/a522427 ; https://www.linkedin.com/help/linkedin/answer/a515989 ; https://linkedinpreview.com/blog/how-to-edit-linkedin-article | Strong / Weak |
| Drafts | Yes. Unpublished articles save as drafts (Manage > Drafts per guides). | https://www.linkedin.com/help/linkedin/answer/a522427 | Strong (snippet) |
| **Scheduling** | **Yes.** A clock icon next to Publish schedules articles (and Page newsletter editions). The feed-post scheduling window is 10 min to 3 months. Whether the same window applies to articles is **UNVERIFIED**. | https://www.linkedin.com/help/linkedin/answer/a522427 ; https://www.linkedin.com/help/linkedin/answer/a569569 ; https://www.linkedin.com/help/linkedin/answer/a1347212 | Strong (snippet) |
| Mobile preview before publishing | **No native preview** found. Workaround: schedule or publish, then check on a phone. | https://linkedinpreview.com/blog/how-to-preview-linkedin-post-mobile | Weak |

---

## 3. Problems copying text out of LinkedIn articles

**No LinkedIn-specific documentation was found** on copy-out fidelity from articles. The relevant general risks are below. Treat all of them as **UNVERIFIED for LinkedIn articles** until tested.

- **Smart quotes:** rich-text editors commonly convert typed `"` and `'` to curly quotes. No source confirms or denies this for LinkedIn's article editor. For an AI prompt, curly quotes are mostly harmless. For code, JSON or shell commands they break parsing. https://articleformatter.com/fix-smart-quotes-curly-quotes/ (Weak, general)
- **Line breaks and blank lines:** sources about the LinkedIn **post** composer report collapsed blank lines when pasting HTML. Copying out of rendered rich text often turns paragraphs into single line breaks or merges list items. https://markdowntolinkedin.com/blog/linkedin-line-breaks/ ; https://snaptextclean.com/guides/copy-paste-web-text (Weak)
- **Non-breaking spaces and invisible characters** sneak into copied web text. https://linebreakremover.com/blog/how-to-clean-up-text-copied-from-website.html (Weak)
- **"See more" truncation** applies to **feed posts** (about 140-210 characters on mobile), not to the article page itself. A reader who copies from the article page sees the full text. Some apps restrict text selection: one guide says LinkedIn apps often block selection, and the fix is opening in a browser tab. https://jemully.com/guide-how-to-copy-text-from-linkedin-posts-2025/ (Weak)
- **Bullets and numbering** in lists usually copy as markers, or are dropped depending on the browser. This was not tested.

**Mitigation regardless of editor behaviour:** put the canonical prompt in the GitHub repo as a plain `.md` or `.txt` file, linked from the article as a "copy-safe version" (GitHub's raw view and copy button preserve exact characters). Write the prompt to tolerate formatting loss: no reliance on indentation, straight-quote-only content, and section markers that survive line merging.

---

## 4. API and third-party schedulers

| Finding | Source | Strength |
|---|---|---|
| LinkedIn's Posts API "article" content type creates a **link-share post** (source URL, title, description and thumbnail you supply) using `w_member_social` for members. It does **not** create a native long-form LinkedIn Article. | https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api | Strong |
| No public API endpoint for creating native articles, article drafts or newsletter editions (personal or Page) was found. Developers and integrators (Make community, PostProxy, open-source pipelines) report they must be created in the web editor. | https://postproxy.dev/blog/linkedin-api-automate-company-page-publishing/ ; https://community.make.com/t/adding-an-article-to-linkedin-newsletter/32007 ; https://github.com/xSakix/ainews/pull/16 | Weak (consistent; absence of evidence) |
| Third-party schedulers (Buffer, Hootsuite and others) **cannot schedule LinkedIn native articles or newsletters**; they are native-only. Attributed to vendor help centers secondhand. | https://blog.brandghost.ai/posts/schedule-linkedin-articles/ ; https://adaptlypost.com/en/blog/best-linkedin-scheduler ; https://linkedgrow.ai/compare/buffer-vs-hootsuite | Weak |
| Typefully: its help center lists LinkedIn personal profiles and Pages for **posts**. No LinkedIn Articles support was found (it supports **X** Articles drafting). | https://support.typefully.com/en/articles/8728077-what-and-where-can-i-publish-with-typefully ; https://support.typefully.com/llms.txt | Moderate (vendor docs via snippet) |
| Practical path: write in the LinkedIn web editor and use **native scheduling** (clock icon). Typefully, Buffer and similar tools can schedule the **companion feed post** (text or PDF document) that links to the article. | as above | n/a |

---

## Recommendations

**Distribution**
1. Decide on the newsletter **before** this launch. If yes, create it (Write article > Manage > Create newsletter; cadence "monthly" or "biweekly" is the safest promise) and publish this tool as **edition #1**. That edition triggers the one-time subscribe invitation to all connections and followers, and each later edition notifies subscribers by in-app, push and email. Evidence suggests a published standalone article cannot be converted later.
2. Use the publish-screen commentary as the hook post: 2-4 short lines on the painful problem, with no hashtags you'll regret, since they may be uneditable. The text can be edited later; the attached article card cannot.
3. Keep the PDF carousel. Post it as a **separate** document post 1-3 days later, with the last slide pointing to the article. Put the article URL in the post text or first comment; evidence suggests either placement costs about 15-25% in reach, and LinkedIn says it does not intentionally penalize links. Document posts have the highest median reach; articles alone get about half.
4. Fill in **SEO title (≤60 chars)** and **SEO description (140-160 chars)** every time. Don't count on Google traffic (Pulse lost most of its Google visibility in 2024-2026). Treat the GitHub repo as the durable, searchable home.

**Layout, given the editor's limits**
5. Put the prompt in the editor's **Code** snippet block. If a test shows it collapses lines or adds smart quotes, fall back to a block quote or plain paragraphs. **Always** link a copy-safe version: the prompt as a `.md`/`.txt` file in the GitHub repo, with an explicit "Copy the exact prompt from GitHub" line right above the block.
6. Before publishing the first article, do a 5-minute test draft: paste the prompt, publish to a throwaway draft or schedule it, copy it back out on desktop and mobile browser, and diff the result against the original (quotes, blank lines, indentation, length). Record the results; this resolves most UNVERIFIED items above.
7. No tables: render any comparison table as a 1920-wide image. Use Heading styles for sections, short paragraphs, and a divider before the prompt. Use a YouTube or Vimeo link if a demo video exists; a GitHub URL will most likely appear as a plain link card.
8. Cover: 1920x1080 (16:9) with title text centred so it survives the about 1.91:1 feed crop. Keep headlines ≤100 characters to stay under the lower of the two reported limits. Write, edit and schedule on **desktop** only.

**Standardize for future articles**
9. Use a fixed template: Hook → The painful problem → What the tool does (screenshot) → How to rebuild it (prompt in Code block plus GitHub copy-safe link) → Caveats and disclaimer (CPA, not advice) → Repo link and "subscribe" line. Also fix a standard SEO title/description pattern, a cover template, a carousel template whose last slide links to the article, and a launch checklist (newsletter edition chosen, SEO fields filled, cover uploaded, scheduled via clock icon, companion carousel queued in a scheduler).
10. Re-check this report against live Help pages when network access allows. Key pages: a522427 (publish articles), a521719 (rich media), a522472 (embeds), a6244140 (SEO), a517925 / a522525 / a591266 (newsletters).
