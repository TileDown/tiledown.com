#!/usr/bin/env python3
"""Browser checks for the public Tiledown website."""

import os
import sys

from playwright.sync_api import expect, sync_playwright


BASE_URL = os.environ.get("BASE_URL", "http://localhost:8092").rstrip("/")


def pass_check(name, detail=""):
    suffix = f"  [{detail}]" if detail else ""
    print(f"PASS  {name}{suffix}")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    checks = 0
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.emulate_media(color_scheme="light")

        page.goto(f"{BASE_URL}/", wait_until="networkidle")
        expect(page).to_have_title("Tiledown")
        checks += 1
        pass_check("home title", "Tiledown")

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
        checks += 1
        pass_check("light hero image renders")

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
        require(theme == "dark", f"Expected first toggle to select dark, got {theme}")
        expect(dark_hero).to_be_visible()
        expect(light_hero).not_to_be_visible()
        checks += 1
        pass_check("theme toggle sets data-theme", theme)
        checks += 1
        pass_check("dark hero image renders")

        page.goto(f"{BASE_URL}/features/", wait_until="networkidle")
        expect(page.locator("h1")).to_have_text("Feature Tour")
        require(page.locator(".td-callout").count() >= 1, "Feature page has no callout")
        checks += 1
        pass_check("feature page renders callout")

        page.goto(f"{BASE_URL}/tags/", wait_until="networkidle")
        expect(page.locator("h1").first).to_have_text("Tags")
        expect(page.locator(".td-tagbar")).to_be_visible()
        checks += 1
        pass_check("tags landing has tag bar")

        page.goto(f"{BASE_URL}/tags/tiles/", wait_until="networkidle")
        expect(page.locator("h1").first).to_have_text("Tiles")
        expect(page.locator(".td-post-card")).to_have_count(1)
        checks += 1
        pass_check("tag filter page lists matching post")

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
        require("Browser-Visible Tiles" in feed_body, "Feed is missing a post")
        checks += 1
        pass_check("rss feed renders")

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
