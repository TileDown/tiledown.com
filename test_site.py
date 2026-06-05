#!/usr/bin/env python3
"""Browser checks for the public TileDown website."""

import os
import sys

from playwright.sync_api import expect, sync_playwright


BASE_URL = os.environ.get("BASE_URL", "http://localhost:8092").rstrip("/")
UMAMI_SCRIPT = (
    '<script defer src="https://cloud.umami.is/script.js" '
    'data-website-id="193d757c-9f02-40b0-b59f-cf5332d24f43"></script>'
)
UMAMI_SELECTOR = (
    'script[src="https://cloud.umami.is/script.js"]'
    '[data-website-id="193d757c-9f02-40b0-b59f-cf5332d24f43"]'
)
FAVICON_PATH = "/favicon.ico"


def pass_check(name, detail=""):
    suffix = f"  [{detail}]" if detail else ""
    print(f"PASS  {name}{suffix}")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def assert_umami_analytics(page, path):
    response = page.request.get(f"{BASE_URL}{path}")
    require(response.status == 200, f"{path} returned {response.status}")
    require(UMAMI_SCRIPT in response.text(), f"{path} missing Umami analytics script")
    require(page.locator(UMAMI_SELECTOR).count() == 1, f"{path} should render one Umami script")


def assert_favicon(page, expected_href):
    require(page.locator(f'link[rel="icon"][href="{expected_href}"]').count() == 1, "Missing favicon link")
    response = page.request.get(f"{BASE_URL}{FAVICON_PATH}")
    require(response.status == 200, f"{FAVICON_PATH} returned {response.status}")
    require(bytes(response.body())[:4] == b"\x00\x00\x01\x00", "favicon.ico is not an ICO file")


def click_center(page, locator):
    locator.wait_for(state="visible")
    locator.scroll_into_view_if_needed()
    box = locator.bounding_box()
    require(box is not None, "Click target has no bounding box")
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2
    handle = locator.element_handle()
    receives_click = handle.evaluate(
        """(element, point) => {
            const hit = document.elementFromPoint(point.x, point.y);
            return hit === element || element.contains(hit);
        }""",
        {"x": x, "y": y},
    )
    require(receives_click, "Click target is covered at its center")
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.up()


def can_receive_center_click(locator):
    locator.wait_for(state="visible")
    locator.scroll_into_view_if_needed()
    box = locator.bounding_box()
    if box is None:
        return False
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2
    handle = locator.element_handle()
    return handle.evaluate(
        """(element, point) => {
            const hit = document.elementFromPoint(point.x, point.y);
            return hit === element || element.contains(hit);
        }""",
        {"x": x, "y": y},
    )


def assert_article_share_links(page, expected_path):
    links = page.eval_on_selector_all(
        ".td-article-share a",
        "els => els.map((el) => [el.textContent, el.getAttribute('href'), el.getAttribute('target'), el.getAttribute('rel')])",
    )
    require([item[0] for item in links] == ["X", "LinkedIn", "Facebook", "Email"], f"Unexpected share links: {links}")
    require(all(item[2] == "_blank" and item[3] == "noopener" for item in links), f"Unsafe share attrs: {links}")
    encoded_path = expected_path.replace("/", "%2F")
    require(encoded_path in links[0][1], f"Share URL missing article path: {links[0][1]}")
    require(can_receive_center_click(page.locator(".td-article-share a").first), "Share link center is covered")


def assert_article_pdf(page, slug, expected_href):
    link = page.locator(".td-article-actions a[download]").first
    href = link.get_attribute("href") if link.count() else None
    require(href == expected_href, f"Unexpected article PDF link: {href}")

    response = page.request.get(f"{BASE_URL}/{slug}.pdf")
    require(response.status == 200, f"{slug}.pdf returned {response.status}")
    require(bytes(response.body())[:5] == b"%PDF-", f"{slug}.pdf is not a PDF")

    nested = page.request.get(f"{BASE_URL}/posts/{slug}/index.pdf")
    require(nested.status == 404, f"Nested article PDF unexpectedly exists: {nested.status}")


def assert_theme_image_pair(page, selector, expected_dark_src):
    light = page.locator(f"{selector} .td-theme-image-light").first
    dark = page.locator(f"{selector} .td-theme-image-dark").first
    expect(dark).to_be_visible()
    expect(light).not_to_be_visible()

    actual_src = dark.get_attribute("src")
    require(actual_src == expected_dark_src, f"Expected {expected_dark_src}, got {actual_src}")

    sizes = page.eval_on_selector_all(
        f"{selector} img",
        """(imgs) => imgs.map((img) => ({
            src: img.getAttribute("src"),
            complete: img.complete,
            width: img.naturalWidth,
            height: img.naturalHeight
        }))""",
    )
    require(len(sizes) == 2, f"Expected image pair for {selector}, got {len(sizes)}")
    for size in sizes:
        require(size["complete"], f"Image did not finish loading: {size['src']}")
        require(size["width"] > 0 and size["height"] > 0, f"Image has no natural size: {size['src']}")
    require(
        sizes[0]["width"] == sizes[1]["width"] and sizes[0]["height"] == sizes[1]["height"],
        f"Theme image sizes differ: {sizes}",
    )


def assert_playground_asset(page, path, expected_asset, expected_runtime_text):
    response = page.request.get(f"{BASE_URL}{path}")
    require(response.status == 200, f"{path} returned {response.status}")
    body = response.text()
    require(expected_asset in body, f"{path} missing expected WASM asset URL")
    require("WebAssembly.compile" in body, f"{path} missing WebAssembly compile path")
    require(expected_runtime_text in body, f"{path} missing expected runtime text")


def visible_image_box(page, selector):
    return page.eval_on_selector(
        selector,
        """(root) => {
            const images = Array.from(root.querySelectorAll("img"));
            const visible = images.find((image) => {
                const rect = image.getBoundingClientRect();
                const style = getComputedStyle(image);
                return style.display !== "none" && rect.width > 0 && rect.height > 0;
            });
            if (!visible) return null;
            const rect = visible.getBoundingClientRect();
            return {
                top: rect.top,
                bottom: rect.bottom,
                width: rect.width,
                height: rect.height,
                objectFit: getComputedStyle(visible).objectFit
            };
        }""",
    )


def element_box(page, selector):
    return page.eval_on_selector(
        selector,
        """(element) => {
            const rect = element.getBoundingClientRect();
            return {
                top: rect.top,
                bottom: rect.bottom,
                width: rect.width,
                height: rect.height,
                marginBottom: parseFloat(getComputedStyle(element).marginBottom)
            };
        }""",
    )


def sampled_image_pixel(locator, x_ratio, y_ratio):
    locator.wait_for(state="visible")
    return locator.evaluate(
        """async (image, point) => {
            if (!image.complete) {
                await new Promise((resolve, reject) => {
                    image.addEventListener("load", resolve, { once: true });
                    image.addEventListener("error", reject, { once: true });
                });
            }
            const width = image.naturalWidth;
            const height = image.naturalHeight;
            const canvas = document.createElement("canvas");
            canvas.width = width;
            canvas.height = height;
            const context = canvas.getContext("2d");
            context.drawImage(image, 0, 0);
            const x = Math.max(0, Math.min(width - 1, Math.round(width * point.x)));
            const y = Math.max(0, Math.min(height - 1, Math.round(height * point.y)));
            return Array.from(context.getImageData(x, y, 1, 1).data);
        }""",
        {"x": x_ratio, "y": y_ratio},
    )


def assert_home_hero_rhythm(page):
    hero = element_box(page, ".td-theme-image.td-hero")
    image = visible_image_box(page, ".td-theme-image.td-hero")
    title = element_box(page, "h1")
    require(image is not None, "Home hero has no visible image")

    gap = title["top"] - hero["bottom"]
    require(gap >= 64, f"Home hero/title gap is too small: {gap:.0f}px")
    require(hero["marginBottom"] >= 64, f"Home hero margin is too small: {hero['marginBottom']:.0f}px")
    require(image["objectFit"] == "contain", f"Home hero object-fit is {image['objectFit']}")
    require(title["bottom"] <= page.viewport_size["height"], "Home title is pushed below the first viewport")


def main():
    checks = 0
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.route(
            "https://www.youtube-nocookie.com/**",
            lambda route: route.fulfill(status=204, body=""),
        )
        page.route("https://cloud.umami.is/**", lambda route: route.abort())
        page.emulate_media(color_scheme="light")

        page.goto(f"{BASE_URL}/", wait_until="networkidle")
        expect(page).to_have_title("TileDown")
        expect(page.locator(".td-brand-title")).to_have_text("TileDown")
        expect(page.locator(".td-brand-subtitle")).to_have_text("v0.5.1")
        assert_umami_analytics(page, "/")
        assert_favicon(page, FAVICON_PATH)
        checks += 1
        pass_check("home title, version, analytics, and favicon", "TileDown v0.5.1")

        home_title = page.locator("h1").first
        title_alignment = home_title.evaluate(
            """(title) => {
                const titleRect = title.getBoundingClientRect();
                const mainRect = document.querySelector(".td-main").getBoundingClientRect();
                return {
                    textAlign: getComputedStyle(title).textAlign,
                    titleCenter: titleRect.left + titleRect.width / 2,
                    mainCenter: mainRect.left + mainRect.width / 2
                };
            }""",
        )
        require(title_alignment["textAlign"] == "center", f"Homepage title is not centered: {title_alignment}")
        require(
            abs(title_alignment["titleCenter"] - title_alignment["mainCenter"]) <= 1,
            f"Homepage title box is not centered: {title_alignment}",
        )
        checks += 1
        pass_check("homepage title is centered")

        visible_copy = page.locator("body").inner_text()
        require("Tiledown" not in visible_copy, "Visible copy uses old Tiledown capitalization")
        expect(page.locator(".td-built")).to_have_text("Built with TileDown")
        expect(page.locator(".td-nav").get_by_role("link", name="Fresh")).to_be_visible()
        require(page.locator(".td-nav").get_by_role("link", name="Updates").count() == 0, "Navigation still says Updates")
        checks += 1
        pass_check("visible copy uses TileDown brand and Fresh nav")

        repo_link = page.get_by_role("link", name="github.com/TileDown/tile-down").first
        expect(repo_link).to_be_visible()
        require(repo_link.get_attribute("href") == "/out/repo/", "Homepage repo link does not route through link:repo")
        require(can_receive_center_click(repo_link), "Homepage repo link center is covered")
        checks += 1
        pass_check("homepage exposes repository link")

        broken_images = page.eval_on_selector_all(
            "img",
            "(imgs) => imgs.filter((img) => !img.complete || img.naturalWidth === 0).map((img) => img.getAttribute('src'))",
        )
        require(not broken_images, f"Broken images: {broken_images}")
        checks += 1
        pass_check("home images load", "0 broken")

        light_hero = page.locator(".td-theme-image.td-hero .td-theme-image-light")
        dark_hero = page.locator(".td-theme-image.td-hero .td-theme-image-dark")
        expect(light_hero).to_be_visible()
        expect(dark_hero).not_to_be_visible()
        assert_home_hero_rhythm(page)
        checks += 1
        pass_check("theme image starts light with readable hero rhythm")

        counter = page.locator("[data-td-counter]").first
        value = counter.locator("[data-td-counter-value]")
        expect(value).to_have_text("0")
        counter.locator("button").click()
        counter.locator("button").click()
        expect(value).to_have_text("2")
        checks += 1
        pass_check("counter tile increments", "0->2")

        page.locator("[data-td-theme-toggle]").click()
        theme = page.locator("html").get_attribute("data-theme")
        require(theme in ["dark", "light"], f"Unexpected theme value: {theme}")
        checks += 1
        pass_check("theme toggle sets data-theme", theme)

        require(theme == "dark", f"Expected dark theme after light-mode toggle, got {theme}")
        expect(dark_hero).to_be_visible()
        expect(light_hero).not_to_be_visible()
        assert_home_hero_rhythm(page)
        assert_theme_image_pair(page, ".td-theme-image.td-hero", "/assets/site-preview-dark.svg")
        checks += 1
        pass_check("theme image switches dark with readable hero rhythm")

        page.goto(f"{BASE_URL}/features/", wait_until="networkidle")
        expect(page.locator("h1")).to_have_text("Feature Tour")
        require(page.locator(".td-callout").count() >= 1, "Feature page has no callout")
        mark = page.locator('img[alt="TileDown mark"]').first
        expect(mark).to_be_visible()
        mark_src = mark.get_attribute("src")
        require(mark_src == "/assets/tiledown-mark.svg", f"Unexpected mark source: {mark_src}")
        mark_svg = page.request.get(f"{BASE_URL}/assets/tiledown-mark.svg").text()
        require('width="256" height="256"' in mark_svg, "TileDown mark size changed")
        require('rect width="256" height="256"' not in mark_svg, "TileDown mark still has a full background")
        center_pixel = sampled_image_pixel(mark, 0.5, 0.5)
        require(center_pixel[3] == 0, f"TileDown mark center is not transparent: {center_pixel}")
        checks += 1
        pass_check("feature page renders callout and transparent mark")

        embed = page.locator(".td-embed iframe").first
        expect(embed).to_be_visible()
        require(
            embed.get_attribute("src") == "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
            "Feature page embed did not normalize to youtube-nocookie",
        )
        embed_box = element_box(page, ".td-embed-frame")
        ratio = embed_box["width"] / embed_box["height"]
        require(abs(ratio - (16 / 9)) < 0.05, f"Feature page embed ratio is {ratio:.2f}")
        checks += 1
        pass_check("feature page renders safe responsive embed")

        themed_routes = [
            ("/features/", "Feature Tour", "/assets/feature-tour-dark.svg"),
            ("/docs/", "Docs", "/assets/docs-preview-dark.svg"),
            ("/posts/default-article-style/", "Default Article Style", "/assets/post-article-dark.svg"),
            ("/posts/interactive-tiles/", "Interactive Tiles", "/assets/post-interactive-dark.svg"),
            ("/posts/tag-intersections/", "Tag Intersections", "/assets/post-tags-dark.svg"),
            ("/posts/tiledown-0-4-1-static-code-color/", "TileDown 0.4.1 ships static code color", "/assets/post-code-dark.svg"),
            ("/posts/publishing-pipeline/", "Publishing Pipeline", "/assets/post-publishing-dark.svg"),
            ("/posts/browser-visible-tiles/", "Browser-Visible Tiles", "/assets/post-tiles-dark.svg"),
            ("/posts/linux-first-builds/", "Linux-First Builds", "/assets/post-linux-dark.svg"),
            ("/posts/markdown-canonical-source/", "Markdown as Canonical Source", "/assets/post-markdown-dark.svg"),
            ("/posts/reference-routing/", "Slug Overrides and References", "/assets/post-routing-dark.svg"),
            ("/posts/service-contracts/", "Service Contracts Are Next", "/assets/post-services-dark.svg"),
        ]
        for path, title, dark_src in themed_routes:
            page.goto(f"{BASE_URL}{path}", wait_until="networkidle")
            expect(page.locator("h1").first).to_have_text(title)
            assert_theme_image_pair(page, ".td-theme-image.td-hero", dark_src)
        checks += 1
        pass_check("demo hero images switch dark", f"{len(themed_routes)} routes")

        page.goto(f"{BASE_URL}/posts/browser-visible-tiles/", wait_until="networkidle")
        expect(page.locator(".td-article")).to_be_visible()
        assert_article_share_links(page, "/posts/browser-visible-tiles/")
        checks += 1
        pass_check("article share links render and are tappable")

        page.goto(f"{BASE_URL}/posts/default-article-style/", wait_until="networkidle")
        default_article_text = page.locator("body").inner_text()
        require("Default Article Style" in default_article_text, "Default article demo missing title")
        require("Social share links are enabled once" in default_article_text, "Default article demo missing callout copy")
        assert_article_share_links(page, "/posts/default-article-style/")
        checks += 1
        pass_check("default article demo renders")

        page.goto(f"{BASE_URL}/posts/tiledown-0-4-1-static-code-color/", wait_until="networkidle")
        expect(page.locator("h1").first).to_have_text("TileDown 0.4.1 ships static code color")
        assert_umami_analytics(page, "/posts/tiledown-0-4-1-static-code-color/")
        syntax = page.eval_on_selector(
            "code.language-swift",
            """(code) => {
                const keyword = code.querySelector(".tok-keyword");
                const string = code.querySelector(".tok-string");
                return {
                    tokenCount: code.querySelectorAll("[class^='tok-']").length,
                    keywordColor: keyword ? getComputedStyle(keyword).color : "",
                    stringColor: string ? getComputedStyle(string).color : "",
                    plainColor: getComputedStyle(code).color
                };
            }""",
        )
        require(syntax["tokenCount"] >= 6, f"Syntax highlighting emitted too few tokens: {syntax}")
        require(syntax["keywordColor"] and syntax["keywordColor"] != syntax["plainColor"], f"Keyword color did not apply: {syntax}")
        require(syntax["stringColor"] and syntax["stringColor"] != syntax["plainColor"], f"String color did not apply: {syntax}")
        require(page.locator("code.language-json .tok-property").count() >= 1, "JSON code block has no property tokens")
        assert_article_pdf(
            page,
            "tiledown-0-4-1-static-code-color",
            "/tiledown-0-4-1-static-code-color.pdf",
        )
        checks += 1
        pass_check("static source highlighting renders colored tokens and PDF")

        page.goto(f"{BASE_URL}/posts/interactive-tiles/", wait_until="networkidle")
        demo_counter = page.locator("[data-td-counter]").first
        demo_value = demo_counter.locator("[data-td-counter-value]")
        expect(demo_value).to_have_text("0")
        demo_counter.locator("button").click()
        expect(demo_value).to_have_text("1")
        checks += 1
        pass_check("interactive tile demo increments")

        page.goto(f"{BASE_URL}/posts/", wait_until="networkidle")
        expect(page.locator("h1").first).to_have_text("Fresh")
        card_pairs = page.locator(".td-post-card .td-theme-image")
        card_pair_count = card_pairs.count()
        require(card_pair_count >= 9, f"Expected post card image pairs, got {card_pair_count}")
        for index in range(card_pair_count):
            expect(card_pairs.nth(index).locator(".td-theme-image-dark")).to_be_visible()
            expect(card_pairs.nth(index).locator(".td-theme-image-light")).not_to_be_visible()
        checks += 1
        pass_check("post card images switch dark", f"{card_pair_count} cards")

        page.goto(f"{BASE_URL}/tags/", wait_until="networkidle")
        expect(page.locator("h1").first).to_have_text("Tags")
        expect(page.locator(".td-tagbar")).to_be_visible()
        checks += 1
        pass_check("tags landing has tag bar")

        page.goto(f"{BASE_URL}/tags/tiles/", wait_until="networkidle")
        expect(page.locator("h1").first).to_have_text("Tiles")
        tiles_text = page.locator("body").inner_text()
        require("Browser-Visible Tiles" in tiles_text, "Tiles tag missing browser post")
        require("Interactive Tiles" in tiles_text, "Tiles tag missing interactive post")
        checks += 1
        pass_check("tag filter page lists matching post")

        page.goto(f"{BASE_URL}/tags/taxonomy/", wait_until="networkidle")
        expect(page.locator("h1").first).to_have_text("Taxonomy")
        require("Tag Intersections" in page.locator("body").inner_text(), "Taxonomy tag missing intersection demo")
        checks += 1
        pass_check("tag intersections demo appears under Taxonomy")

        page.goto(f"{BASE_URL}/tags/markdown/", wait_until="networkidle")
        markdown_text = page.locator("body").inner_text()
        require("Markdown as Canonical Source" in markdown_text, "Markdown tag missing Markdown post")
        require("Slug Overrides and References" in markdown_text, "Markdown tag missing routing post")
        clear = page.locator(".td-tagbar .td-tag-clear").first
        require(clear.get_attribute("href") == "/tags/", "Tag clear link does not return to all tags")
        click_center(page, clear)
        page.wait_for_url("**/tags/")
        all_tags_text = page.locator("body").inner_text()
        require("TileDown 0.4.1 ships static code color" in all_tags_text, "Cleared tag page is missing latest post")
        require("Markdown as Canonical Source" in all_tags_text, "Cleared tag page is missing older post")
        page.goto(f"{BASE_URL}/tags/markdown/", wait_until="networkidle")
        click_center(page, page.locator(".td-tagbar").get_by_role("link", name="Swift").first)
        page.wait_for_url("**/tags/markdown/swift/")
        markdown_swift_text = page.locator("body").inner_text()
        require("Markdown as Canonical Source" in markdown_swift_text, "Markdown AND Swift missing shared post")
        require("Slug Overrides and References" not in markdown_swift_text, "Markdown AND Swift included Markdown-only post")
        click_center(page, page.locator(".td-tagbar").get_by_role("link", name="Swift").first)
        page.wait_for_url("**/tags/markdown/")
        checks += 1
        pass_check("tag AND chip flow narrows and removes")

        response = page.goto(f"{BASE_URL}/posts/reference-routing/", wait_until="networkidle")
        require(response and response.status == 200, "Slug override page did not render")
        checks += 1
        pass_check("slug override page renders")

        draft = page.request.get(f"{BASE_URL}/posts/draft-preview/")
        require(draft.status == 404, f"Draft returned {draft.status}")
        checks += 1
        pass_check("draft is excluded", "status=404")

        feed = page.request.get(f"{BASE_URL}/feed.xml")
        require(feed.status == 200, f"Feed returned {feed.status}")
        feed_body = feed.text()
        require("<rss" in feed_body, "Feed is not RSS")
        require("<title>TileDown</title>" in feed_body, "Feed title is not TileDown")
        require("TileDown Blog" not in feed_body, "Feed title still says Blog")
        require("TileDown 0.4.1 ships static code color" in feed_body, "Feed is missing the latest post")
        require("Browser-Visible Tiles" in feed_body, "Feed is missing a post")
        checks += 1
        pass_check("rss feed renders")

        assert_playground_asset(
            page,
            "/assets/playground.html",
            "wasm-playground-asset/docs/playground/tiledown-math.wasm.gz",
            "Math playground",
        )
        assert_playground_asset(
            page,
            "/assets/pdf-playground.html",
            "pdf-playground-asset/docs/playground/markdownpdf.wasm.gz",
            "application/pdf",
        )
        checks += 1
        pass_check("webassembly playground assets remain wired")

        shim = page.request.get(f"{BASE_URL}/out/repo/")
        require(shim.status == 200, f"Redirect shim returned {shim.status}")
        require("https://github.com/TileDown/tile-down" in shim.text(), "Shim target missing")
        checks += 1
        pass_check("outbound redirect shim renders")

        browser.close()

    print(f"\n{checks}/{checks} website checks passed")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"FAIL  {error}", file=sys.stderr)
        sys.exit(1)
