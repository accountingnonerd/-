# From post to LinkedIn article: what changes (review of 2026-11-18)

Sources and strength ratings are in [ARTICLE-FORMAT-RESEARCH.md](ARTICLE-FORMAT-RESEARCH.md). linkedin.com
could not be opened from the build environment, so LinkedIn Help pages were read through search
summaries; the items marked "test" are checked in a draft before the first article goes out.

## 1. Distribution
- **An article alone reaches fewer people than our carousel posts.** In AuthoredUp's data
  (Mar 2025 to Feb 2026), the median article on a personal profile reached 596 people; a document
  (carousel) post reached 1,198. Articles hold their reach year to year, and they last: people can
  find them from the profile and by search, which a feed post does not do.
- **Publish it as a newsletter edition, not a plain article.** The first edition of a LinkedIn
  newsletter sends every connection and follower a one-time invitation to subscribe; every later
  edition notifies subscribers (in the app, by push and by email). That is the follow mechanism the
  series needs: "Subscribe" is a stronger promise than "Follow", and it reaches people the feed
  does not. The choice is made before publishing; a published article cannot be turned into an
  edition later. **Recommendation:** create the "One Painful Problem" newsletter (monthly or
  biweekly) and publish Agent 5 as edition 1.
- **The text in "Tell your network what your article is about" becomes the feed post.** Treat it as
  the hook: 2 to 4 lines, the money or the deadline, no link needed (the article card is the link).
  It can be edited later; the card cannot.
- **Keep a companion carousel post, 1 to 3 days later.** Carousels have the highest reach, and the
  last slide points to the article. Links in posts cost an estimated 15 to 25% of reach in large
  studies, so the article link goes in the post's last line (the link test from GROWTH.md continues).
- **Title, SEO and cover.** Headline at most 100 characters, in the accountant's words. SEO title at
  most 60 characters and SEO description 140 to 160, filled every time; but Google traffic to
  LinkedIn articles has fallen sharply since 2024, so the GitHub repository stays the searchable
  home. Cover 1920 x 1080, with the title centred so the feed crop does not cut it.

## 2. What the editor supports
- **Supported:** headings, bold, italic, bulleted and numbered lists, block quotes, dividers,
  inline links, images, a "Code" snippet block, and embeds by link (YouTube, Vimeo, SlideShare).
  Drafts, and scheduling from the clock icon next to Publish.
- **Not supported:** tables (so every table is an image), writing or editing on the mobile app,
  and, as far as can be found, native video upload and image captions.
- **Unknown until tested:** whether the Code block keeps line breaks and copies cleanly, and its
  length limit. Long prompts can pick up curly quotes and lose blank lines when copied out of any
  web page. **So the prompt always has a master copy in the repository** (a plain .txt file with a
  "copy" button on GitHub), linked right above the block in the article.
- **No API.** LinkedIn has no public way to create article or newsletter drafts for a personal
  profile, and Typefully, Buffer and Hootsuite cannot publish them. The article is pasted into the
  editor by hand (a paste kit makes that a 10-minute job) or set up in a session on the owner's
  computer.

## 3. What the extra space is for
- **Earns a place:** the full build-it-yourself walkthrough (tool, account level, time, numbered
  steps, what you should see, what to do if it fails); the prompt itself; the sample data and the
  expected result, so a reader can check their rebuild; the limits; one worked example told as a
  story.
- **Still belongs elsewhere:** the test results case by case, the review findings, the answer key
  and the source code (the repository); the hook and the swipe-through summary (the carousel
  post).

## 4. Standards for every article from now on
1. One template: headline, the problem told through one client, what the agent produces (images),
   how it works (automatic vs your decision), build it yourself, what it does not do, what is next
   and how to subscribe.
2. Every agent ships a `PROMPT.txt` (the master copy) and a `sample/` folder with input files and
   the expected result, and its README matches the article's steps.
3. Every article is tested before it is offered: the prompt copied out of the rendered article is
   compared with the master copy, and a fresh session rebuilds the agent from the article alone.
4. Published as the next newsletter edition, with SEO fields, a 1920 x 1080 cover from one
   template, and a companion carousel post 1 to 3 days later.
5. Tables become images; no claim about another firm's product.
