# CareerToolFinder

Programmatic SEO comparison site for job-seeker tools: resume/ATS, interview prep,
job boards, and LinkedIn tools. Built on the same zero-cost stack as osalfinder.com,
emailtoolcompare.com, and aitoolalternatives.com.

## Stack
- Python + Jinja2 static site generator (`build.py`)
- Data lives in `data/tools.yaml` — add tools here, no code changes needed
- GitHub Actions (`.github/workflows/pipeline.yml`) builds on push + weekly cron, deploys to `gh-pages` branch
- GitHub Pages serves from `gh-pages`

## Local build
```
pip install -r requirements.txt
python build.py
```
Output goes to `docs/` (gitignored from Pages serving; the `gh-pages` branch is what's actually published).

## Before you launch
1. **Pick a domain** from the shortlist and buy it on Namecheap (same flow as aitoolalternatives.com).
2. Replace `SITE_URL` in `build.py` with the real domain.
3. Add a `CNAME` file to `static/` with the domain so it survives the gh-pages deploy.
4. Set up GSC the same way you did for osalfinder/aitoolalternatives — submit `sitemap.xml`.
5. Expand `data/tools.yaml`: currently 18 tools / 32 comparison pairs. Same growth pattern
   as osalfinder (93 tools) or aitoolalternatives (126 pairs) — add tools incrementally,
   rebuild, resubmit sitemap.
6. Decide on affiliate programs for LinkedIn/interview-prep tools (Jobscan, Rezi, Taplio
   all run affiliate programs worth checking) — `affiliate_link` field is already in the
   data schema, just empty for now.

## Canonical URL handling
Learned from the emailtoolcompare.com incident: comparison pairs are only generated in
alphabetical slug order (e.g. `atskiller-vs-jobscan.html`, never the reverse as a full
page). The reverse URL (`jobscan-vs-atskiller.html`) exists only as a meta-refresh
redirect with a canonical tag pointing at the real page. Only canonical URLs are
included in `sitemap.xml`.

## ATSKILLER placement
- Primary CTA block on the resume/ATS category page (`category.html`, gated on
  `category == 'resume'`)
- Also appears on any comparison page where ATSKILLER is one of the two tools
  (gated on `tool_a.featured or tool_b.featured` in `comparison.html`)
- Not shown elsewhere, to keep it from feeling like a sitewide banner
