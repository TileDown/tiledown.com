#!/usr/bin/env python3
"""Live browser smoke checks for the deployed TileDown website."""

import os
import sys

from playwright.sync_api import expect, sync_playwright


BASE_URL = os.environ.get("BASE_URL", "https://tiledown.com").rstrip("/")
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
    require(UMAMI_SCRIPT in response.text(), f"{path} missing live Umami analytics script")
    require(page.locator(UMAMI_SELECTOR).count() == 1, f"{path} should render one live Umami script")


def assert_favicon(page):
    expected = f"{BASE_URL}{FAVICON_PATH}"
    require(page.locator(f'link[rel="icon"][href="{expected}"]').count() == 1, "Missing live favicon link")
    response = page.request.get(expected)
    require(response.status == 200, f"{FAVICON_PATH} returned {response.status}")
    require(bytes(response.body())[:4] == b"\x00\x00\x01\x00", "Live favicon.ico is not an ICO file")


def assert_loaded_image(locator, label):
    expect(locator).to_be_visible()
    state = locator.evaluate(
        """(image) => ({
            complete: image.complete,
            width: image.naturalWidth,
            height: image.naturalHeight,
            src: image.getAttribute("src")
        })""",
    )
    require(
        state["complete"] and state["width"] > 0 and state["height"] > 0,
        f"{label} image did not load: {state}",
    )


def assert_article_pdf(page, slug):
    link = page.locator(".td-article-actions a[download]").first
    href = link.get_attribute("href") if link.count() else None
    expected = f"{BASE_URL}/{slug}.pdf"
    require(href == expected, f"Unexpected live article PDF link: {href}")

    response = page.request.get(expected)
    require(response.status == 200, f"{slug}.pdf returned {response.status}")
    require(bytes(response.body())[:5] == b"%PDF-", f"{slug}.pdf is not a PDF")

    nested = page.request.get(f"{BASE_URL}/posts/{slug}/index.pdf")
    require(nested.status == 404, f"Nested article PDF unexpectedly exists: {nested.status}")


def main():
    checks = 0
    blocked_wasm = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1600, "height": 900},
            color_scheme="dark",
            extra_http_headers={"Cache-Control": "no-cache"},
        )
        page = context.new_page()

        def route_handler(route):
            url = route.request.url
            if url.startswith("https://cloud.umami.is/"):
                route.abort()
                return
            if url.endswith(".wasm.gz"):
                blocked_wasm.append(url)
                route.abort()
                return
            route.continue_()

        page.route("**/*", route_handler)

        page.goto(f"{BASE_URL}/posts/", wait_until="networkidle")
        expect(page.locator(".td-brand-title")).to_have_text("TileDown")
        expect(page.locator(".td-brand-subtitle")).to_have_text("v0.4.1")
        expect(page.locator("h1").first).to_have_text("Fresh")
        assert_umami_analytics(page, "/posts/")
        assert_favicon(page)
        expect(page.get_by_role("link", name="TileDown 0.4.1 ships static code color").first).to_be_visible()
        assert_loaded_image(page.locator('img[src*="/assets/post-code-dark.svg"]').first, "code post card")
        broken_images = page.eval_on_selector_all(
            "img",
            "(imgs) => imgs.filter((img) => !img.complete || img.naturalWidth === 0).map((img) => img.getAttribute('src'))",
        )
        require(not broken_images, f"Broken live images: {broken_images}")
        checks += 1
        pass_check("live posts page shows loaded code image")

        page.goto(f"{BASE_URL}/posts/tiledown-0-4-1-static-code-color/", wait_until="networkidle")
        expect(page.locator("h1").first).to_have_text("TileDown 0.4.1 ships static code color")
        assert_umami_analytics(page, "/posts/tiledown-0-4-1-static-code-color/")
        assert_loaded_image(page.locator('img[src*="/assets/post-code-dark.svg"]').first, "code post hero")
        require(page.locator("code.language-swift .tok-keyword").count() >= 1, "Live Swift code has no keyword tokens")
        require(page.locator("code.language-json .tok-property").count() >= 1, "Live JSON code has no property tokens")
        assert_article_pdf(page, "tiledown-0-4-1-static-code-color")
        checks += 1
        pass_check("live article shows image, highlighted code, and PDF")

        page.goto(f"{BASE_URL}/tags/", wait_until="networkidle")
        tags_text = page.locator("body").inner_text()
        require("TileDown 0.4.1 ships static code color" in tags_text, "Live tags page is missing latest post")
        require("No posts match" not in tags_text, "Live tags page unexpectedly empty")
        checks += 1
        pass_check("live tags landing lists articles")

        for path, title in [
            ("/assets/playground.html", "Math playground"),
            ("/assets/pdf-playground.html", "PDF playground"),
        ]:
            page.goto(f"{BASE_URL}{path}", wait_until="networkidle")
            expect(page.locator("h1")).to_have_text(title)
            expect(page.get_by_role("button", name="Load the Swift engine")).to_be_visible()
        require(not blocked_wasm, f"WASM downloaded before opt-in: {blocked_wasm}")
        checks += 1
        pass_check("live WebAssembly playgrounds stay opt-in")

        browser.close()

    print(f"\n{checks}/{checks} live website checks passed")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"FAIL  {error}", file=sys.stderr)
        sys.exit(1)
