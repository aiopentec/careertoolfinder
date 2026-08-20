#!/usr/bin/env python3
"""
add_amazon_cta.py
Adds Amazon Associates CTA blocks to CareerToolFinder (category, comparison,
and alternatives pages), using your aiopentec20-20 associate tag.

USAGE:
    Save this file in the ROOT of your careertoolfinder repo (same folder
    as build.py), then run:

        python3 add_amazon_cta.py

    Then rebuild and check the output:

        python3 build.py

What it does:
  1. Creates data/amazon_products.yaml — one book-recommendation CTA per
     category (resume / interview / jobboard / linkedin), using Amazon
     search-result links tagged with aiopentec20-20. Search links work
     immediately with no ASIN lookup, and still carry your tag. You can
     swap any "url" for a specific /dp/ASIN/ link later if you want to
     point at exact titles.
  2. Creates templates/_amazon_cta.html — a CTA partial styled to match
     your existing ATSKILLER CTA, with an Amazon Associates disclosure line.
  3. Patches build.py to load amazon_products.yaml and pass the right
     category's CTA data into category, comparison, and alternatives pages.
  4. Patches templates/category.html, comparison.html, alternatives.html
     to render the new CTA block.
  5. Appends .amazon-cta styles to static/style.css.

Safe to re-run: every step checks for its own marker/file first and skips
if already applied, so running this twice won't double-patch anything.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(ROOT, path)) as f:
        return f.read()


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)


def exists(path):
    return os.path.exists(os.path.join(ROOT, path))


AMAZON_YAML = '''# Amazon Associates CTA content — one recommendation per tool category.
# Your tag=aiopentec20-20 is baked into each url below.
#
# These use Amazon search-result links, which work immediately with no
# ASIN lookup and still carry your associate tag when someone clicks
# through. Swap any "url" for a specific product page later (add
# /dp/ASIN/ before the ? ) once you've picked exact titles you want to
# vouch for.

resume:
  eyebrow: "Before you apply"
  title: "Level up your resume with the right playbook"
  blurb: "A well-reviewed resume-writing guide can round out what these tools do — handy if you'd rather not commit to a monthly subscription."
  url: "https://www.amazon.com/s?k=resume+writing+guide+book&tag=aiopentec20-20"
  cta_text: "Browse resume guides on Amazon →"

interview:
  eyebrow: "Prepping for the call"
  title: "Interview prep books that actually help"
  blurb: "Pair your interview-prep tool with a structured prep book — useful for behavioral and situational questions the apps don't always cover."
  url: "https://www.amazon.com/s?k=job+interview+preparation+book&tag=aiopentec20-20"
  cta_text: "Browse interview prep books on Amazon →"

jobboard:
  eyebrow: "Job search strategy"
  title: "The job-hunting classic, updated yearly"
  blurb: "Job boards surface the openings — a solid job-search strategy book helps you actually land one, especially if you're job hunting for more than a few weeks."
  url: "https://www.amazon.com/s?k=job+search+strategy+book&tag=aiopentec20-20"
  cta_text: "Browse job search books on Amazon →"

linkedin:
  eyebrow: "Your profile, optimized"
  title: "LinkedIn profile & personal branding guides"
  blurb: "LinkedIn tools handle formatting and analytics — these guides help with the positioning and copywriting the tools can't do for you."
  url: "https://www.amazon.com/s?k=linkedin+profile+optimization+book&tag=aiopentec20-20"
  cta_text: "Browse LinkedIn guides on Amazon →"
'''

AMAZON_PARTIAL = '''<div class="amazon-cta">
  <p class="cta-eyebrow">{{ amazon.eyebrow }}</p>
  <h3>{{ amazon.title }}</h3>
  <p>{{ amazon.blurb }}</p>
  <a href="{{ amazon.url }}" target="_blank" rel="nofollow noopener sponsored" class="cta-button cta-button-alt">{{ amazon.cta_text }}</a>
  <p class="cta-disclosure">As an Amazon Associate we earn from qualifying purchases.</p>
</div>
'''

AMAZON_CSS = '''
/* --- Amazon Associates CTA (added by add_amazon_cta.py) --- */
.amazon-cta {
  border: 1px solid var(--sage);
  border-left: 4px solid var(--sage);
  border-radius: 4px;
  padding: 24px 28px;
  margin: 24px auto 0;
  max-width: 980px;
  background: var(--paper-raised);
}
.amazon-cta .cta-eyebrow {
  font-family: var(--font-mono);
  color: var(--sage);
  font-weight: 500;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin: 0 0 6px;
}
.amazon-cta h3 {
  font-family: var(--font-display);
  font-size: 1.25rem;
  margin: 0 0 8px;
}
.cta-button-alt { background: var(--sage); }
.cta-button-alt:hover { background: var(--ink); }
.amazon-cta .cta-disclosure {
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin: 10px 0 0;
}
'''


def step_data_file():
    path = "data/amazon_products.yaml"
    if exists(path):
        print(f"  SKIP (already exists): {path}")
        return
    write(path, AMAZON_YAML)
    print(f"  Created: {path}")


def step_partial():
    path = "templates/_amazon_cta.html"
    if exists(path):
        print(f"  SKIP (already exists): {path}")
        return
    write(path, AMAZON_PARTIAL)
    print(f"  Created: {path}")


def step_css():
    path = "static/style.css"
    css = read(path)
    if "Amazon Associates CTA" in css:
        print(f"  SKIP (already patched): {path}")
        return
    write(path, css.rstrip() + "\n" + AMAZON_CSS)
    print(f"  Patched: {path}")


def step_build_py():
    path = "build.py"
    src = read(path)
    if "AMAZON_DATA_FILE" in src:
        print(f"  SKIP (already patched): {path}")
        return

    # 1. load amazon products alongside DATA_FILE
    src = src.replace(
        'DATA_FILE = "data/tools.yaml"',
        'DATA_FILE = "data/tools.yaml"\nAMAZON_DATA_FILE = "data/amazon_products.yaml"',
    )

    # 2. add a loader function right after load_tools()
    src = src.replace(
        "def clean_output():",
        'def load_amazon_products():\n'
        '    with open(AMAZON_DATA_FILE) as f:\n'
        '        return yaml.safe_load(f)\n\n\n'
        "def clean_output():",
    )

    # 3. category.html — pass amazon=<category's CTA>
    src = src.replace(
        "    for cat in categories:\n"
        "        cat_tools = sorted(\n"
        "            [t for t in tools if t[\"category\"] == cat], key=lambda t: t[\"name\"]\n"
        "        )\n"
        "        cat_tools_by_slug = sorted(cat_tools, key=lambda t: t[\"slug\"])\n"
        "        pairs = [\n"
        "            {\"a\": a, \"b\": b}\n"
        "            for a, b in itertools.combinations(cat_tools_by_slug, 2)\n"
        "        ]\n"
        "        html = tmpl.render(\n"
        "            site_name=SITE_NAME,\n"
        "            site_url=SITE_URL,\n"
        "            category=cat,\n"
        "            category_label=CATEGORY_LABELS[cat],\n"
        "            tools=cat_tools,\n"
        "            pairs=pairs,\n"
        "        )",
        "    amazon_products = load_amazon_products()\n"
        "    for cat in categories:\n"
        "        cat_tools = sorted(\n"
        "            [t for t in tools if t[\"category\"] == cat], key=lambda t: t[\"name\"]\n"
        "        )\n"
        "        cat_tools_by_slug = sorted(cat_tools, key=lambda t: t[\"slug\"])\n"
        "        pairs = [\n"
        "            {\"a\": a, \"b\": b}\n"
        "            for a, b in itertools.combinations(cat_tools_by_slug, 2)\n"
        "        ]\n"
        "        html = tmpl.render(\n"
        "            site_name=SITE_NAME,\n"
        "            site_url=SITE_URL,\n"
        "            category=cat,\n"
        "            category_label=CATEGORY_LABELS[cat],\n"
        "            tools=cat_tools,\n"
        "            pairs=pairs,\n"
        "            amazon=amazon_products[cat],\n"
        "        )",
    )

    # 4. alternatives.html — pass amazon=<tool's category CTA>
    src = src.replace(
        "def build_alternatives(tools, by_slug):\n"
        "    tmpl = env.get_template(\"alternatives.html\")\n"
        "    categories = sorted(set(t[\"category\"] for t in tools))",
        "def build_alternatives(tools, by_slug):\n"
        "    tmpl = env.get_template(\"alternatives.html\")\n"
        "    categories = sorted(set(t[\"category\"] for t in tools))\n"
        "    amazon_products = load_amazon_products()",
    )
    src = src.replace(
        "        html = tmpl.render(\n"
        "            site_name=SITE_NAME,\n"
        "            site_url=SITE_URL,\n"
        "            tool=tool,\n"
        "            category_label=CATEGORY_LABELS[tool[\"category\"]],\n"
        "            alternatives=alt_entries,\n"
        "        )",
        "        html = tmpl.render(\n"
        "            site_name=SITE_NAME,\n"
        "            site_url=SITE_URL,\n"
        "            tool=tool,\n"
        "            category_label=CATEGORY_LABELS[tool[\"category\"]],\n"
        "            alternatives=alt_entries,\n"
        "            amazon=amazon_products[tool[\"category\"]],\n"
        "        )",
    )

    # 5. comparison.html — pass amazon=<pair's category CTA>
    src = src.replace(
        "def build_comparisons(tools, by_slug):\n"
        "    tmpl = env.get_template(\"comparison.html\")\n"
        "    redirect_tmpl = env.get_template(\"redirect.html\")\n"
        "    os.makedirs(os.path.join(OUT_DIR, \"compare\"), exist_ok=True)",
        "def build_comparisons(tools, by_slug):\n"
        "    tmpl = env.get_template(\"comparison.html\")\n"
        "    redirect_tmpl = env.get_template(\"redirect.html\")\n"
        "    os.makedirs(os.path.join(OUT_DIR, \"compare\"), exist_ok=True)\n"
        "    amazon_products = load_amazon_products()",
    )
    src = src.replace(
        "            html = tmpl.render(\n"
        "                site_name=SITE_NAME,\n"
        "                site_url=SITE_URL,\n"
        "                tool_a=a,\n"
        "                tool_b=b,\n"
        "                canonical_path=f\"/compare/{canonical_slug}.html\",\n"
        "                category_label=CATEGORY_LABELS[cat],\n"
        "            )",
        "            html = tmpl.render(\n"
        "                site_name=SITE_NAME,\n"
        "                site_url=SITE_URL,\n"
        "                tool_a=a,\n"
        "                tool_b=b,\n"
        "                canonical_path=f\"/compare/{canonical_slug}.html\",\n"
        "                category_label=CATEGORY_LABELS[cat],\n"
        "                amazon=amazon_products[cat],\n"
        "            )",
    )

    write(path, src)
    print(f"  Patched: {path}")


def step_templates():
    # category.html — add after the existing atskiller include block
    path = "templates/category.html"
    tmpl = read(path)
    if "_amazon_cta.html" not in tmpl:
        tmpl = tmpl.replace(
            "  {% if category == 'resume' %}\n"
            "  {% include \"_atskiller_cta.html\" %}\n"
            "  {% endif %}\n"
            "</section>",
            "  {% if category == 'resume' %}\n"
            "  {% include \"_atskiller_cta.html\" %}\n"
            "  {% endif %}\n"
            "  {% include \"_amazon_cta.html\" %}\n"
            "</section>",
        )
        write(path, tmpl)
        print(f"  Patched: {path}")
    else:
        print(f"  SKIP (already patched): {path}")

    # comparison.html
    path = "templates/comparison.html"
    tmpl = read(path)
    if "_amazon_cta.html" not in tmpl:
        tmpl = tmpl.replace(
            "  {% if tool_a.featured or tool_b.featured %}\n"
            "  {% include \"_atskiller_cta.html\" %}\n"
            "  {% endif %}\n"
            "</section>",
            "  {% if tool_a.featured or tool_b.featured %}\n"
            "  {% include \"_atskiller_cta.html\" %}\n"
            "  {% endif %}\n"
            "  {% include \"_amazon_cta.html\" %}\n"
            "</section>",
        )
        write(path, tmpl)
        print(f"  Patched: {path}")
    else:
        print(f"  SKIP (already patched): {path}")

    # alternatives.html
    path = "templates/alternatives.html"
    tmpl = read(path)
    if "_amazon_cta.html" not in tmpl:
        tmpl = tmpl.replace(
            "  {% if tool.featured %}\n"
            "  {% include \"_atskiller_cta.html\" %}\n"
            "  {% endif %}\n"
            "</section>",
            "  {% if tool.featured %}\n"
            "  {% include \"_atskiller_cta.html\" %}\n"
            "  {% endif %}\n"
            "  {% include \"_amazon_cta.html\" %}\n"
            "</section>",
        )
        write(path, tmpl)
        print(f"  Patched: {path}")
    else:
        print(f"  SKIP (already patched): {path}")


def main():
    if not exists("build.py"):
        print("ERROR: build.py not found in this folder.")
        print("Run this script from the root of your careertoolfinder repo.")
        sys.exit(1)

    print("1/5 data/amazon_products.yaml")
    step_data_file()
    print("2/5 templates/_amazon_cta.html")
    step_partial()
    print("3/5 static/style.css")
    step_css()
    print("4/5 build.py")
    step_build_py()
    print("5/5 templates (category, comparison, alternatives)")
    step_templates()

    print("\nDone. Next steps:")
    print("  1. python3 build.py        # rebuild and confirm no errors")
    print("  2. open a page in docs/compare/ or docs/category/ and check the CTA renders")
    print("  3. git add -A && git commit -m 'Add Amazon Associates CTA' && git push")


if __name__ == "__main__":
    main()
