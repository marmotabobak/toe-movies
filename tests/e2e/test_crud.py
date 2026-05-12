"""E2E: create, edit, delete single movie."""
import pytest


def modal(page):
    """Return a locator scoped to the open modal (max-w-2xl container)."""
    return page.locator(".max-w-2xl")


def fill_modal_field(page, label_text: str, value: str):
    modal(page).locator(f"label:has-text('{label_text}') + input").fill(value)


def fill_modal_textarea(page, label_text: str, value: str):
    modal(page).locator(f"label:has-text('{label_text}') + textarea").fill(value)


class TestAddMovie:
    def test_opens_add_modal(self, page):
        page.click("text=+ Add Movie")
        assert page.locator("text=Add Movie").nth(1).is_visible()

    def test_closes_on_cancel(self, page):
        page.click("text=+ Add Movie")
        page.click("text=Cancel")
        assert not page.locator("text=Add Movie").nth(1).is_visible()

    def test_title_required(self, page):
        page.click("text=+ Add Movie")
        modal(page).locator("button:text('Save')").click()
        # HTML5 required validation prevents submit; modal stays open
        assert modal(page).is_visible()

    def test_creates_movie_appears_in_list(self, page):
        page.click("text=+ Add Movie")
        fill_modal_field(page, "Russian Title", "E2E Test Movie")
        fill_modal_field(page, "English Title", "E2E English Title")
        fill_modal_field(page, "Year", "2023")
        modal(page).locator("button:text('Save')").click()
        page.wait_for_selector("text=E2E English Title")
        assert page.locator("text=E2E English Title").is_visible()

    def test_creates_movie_with_keywords(self, page):
        page.click("text=+ Add Movie")
        fill_modal_field(page, "Russian Title", "Тест ключевых слов")
        fill_modal_field(page, "English Title", "Keyword Test Movie")
        kw_input = modal(page).locator("input[placeholder='Type keyword, press Enter']")
        kw_input.fill("e2e")
        kw_input.press("Enter")
        kw_input.fill("testing")
        kw_input.press("Enter")
        modal(page).locator("button:text('Save')").click()
        page.wait_for_selector("text=Keyword Test Movie")
        # keyword chips appear in the row
        assert page.locator("span.rounded-full:has-text('e2e')").is_visible()


class TestEditMovie:
    def _open_edit_for(self, page, title_fragment: str):
        page.fill("input[placeholder*='Title']", title_fragment)
        page.wait_for_timeout(500)
        page.locator("text=Edit").first.click()
        page.wait_for_selector("text=Edit Movie")

    def test_opens_edit_modal(self, page):
        self._open_edit_for(page, "Matrix")
        assert page.locator("text=Edit Movie").is_visible()

    def test_modal_prepopulated(self, page):
        self._open_edit_for(page, "Matrix")
        year_val = modal(page).locator("label:has-text('Year') + input").input_value()
        assert year_val == "1999"

    def test_edit_year(self, page):
        self._open_edit_for(page, "Interstellar")
        modal(page).locator("label:has-text('Year') + input").fill("2015")
        modal(page).locator("button:text('Save')").click()
        page.wait_for_timeout(500)
        # re-open to verify persistence
        self._open_edit_for(page, "Interstellar")
        assert modal(page).locator("label:has-text('Year') + input").input_value() == "2015"

    def test_edit_adds_keyword(self, page):
        self._open_edit_for(page, "Fight Club")
        kw_input = modal(page).locator("input[placeholder='Type keyword, press Enter']")
        kw_input.fill("psychological")
        kw_input.press("Enter")
        modal(page).locator("button:text('Save')").click()
        page.wait_for_selector("text=Fight Club")
        assert page.locator("span.rounded-full:has-text('psychological')").is_visible()

    def test_edit_removes_keyword(self, page):
        # Shawshank has keyword "prison" from seed data
        self._open_edit_for(page, "Shawshank")
        modal(page).locator("span:has-text('prison') button").click()
        modal(page).locator("button:text('Save')").click()
        page.wait_for_timeout(500)
        page.fill("input[placeholder*='Title']", "Shawshank")
        page.wait_for_timeout(500)
        assert not page.locator("span.rounded-full:has-text('prison')").is_visible()

    def test_cancel_discards_changes(self, page):
        self._open_edit_for(page, "Pulp Fiction")
        modal(page).locator("label:has-text('Year') + input").fill("1800")
        page.click("text=Cancel")
        self._open_edit_for(page, "Pulp Fiction")
        assert modal(page).locator("label:has-text('Year') + input").input_value() == "1994"


class TestKeywordSuggestions:
    def test_suggestions_appear_on_focus_without_typing(self, page):
        # Clicking the input with no text should show top 10 keywords immediately
        page.click("text=+ Add Movie")
        modal(page).locator("input[placeholder='Type keyword, press Enter']").click()
        page.wait_for_selector("ul li")
        count = page.locator("ul li").count()
        assert 1 <= count <= 10

    def test_suggestions_appear_when_typing(self, page):
        # "sci-fi" appears in 2 seed movies (Interstellar + Matrix) so it's in top 20
        page.click("text=+ Add Movie")
        modal(page).locator("input[placeholder='Type keyword, press Enter']").fill("sci")
        page.wait_for_selector("ul li:has-text('sci-fi')")

    def test_clicking_suggestion_adds_keyword_chip(self, page):
        page.click("text=+ Add Movie")
        kw_input = modal(page).locator("input[placeholder='Type keyword, press Enter']")
        kw_input.fill("sci")
        page.wait_for_selector("ul li:has-text('sci-fi')")
        page.locator("ul li:has-text('sci-fi')").click()
        assert modal(page).locator("span.rounded-full:has-text('sci-fi')").is_visible()
        assert kw_input.input_value() == ""

    def test_applied_keyword_excluded_from_suggestions(self, page):
        page.click("text=+ Add Movie")
        kw_input = modal(page).locator("input[placeholder='Type keyword, press Enter']")
        kw_input.fill("sci")
        page.wait_for_selector("ul li:has-text('sci-fi')")
        page.locator("ul li:has-text('sci-fi')").click()
        # After adding sci-fi, typing "sci" again should not show it
        kw_input.fill("sci")
        page.wait_for_timeout(300)
        assert not page.locator("ul li:has-text('sci-fi')").is_visible()

    def test_suggestions_filter_by_input(self, page):
        page.click("text=+ Add Movie")
        modal(page).locator("input[placeholder='Type keyword, press Enter']").fill("pri")
        page.wait_for_selector("ul li:has-text('prison')")
        assert not page.locator("ul li:has-text('sci-fi')").is_visible()


class TestDeleteMovie:
    def test_delete_shows_confirm_dialog(self, page):
        page.locator("text=Delete").first.click()
        assert page.locator("text=Delete this movie?").is_visible()

    def test_cancel_does_not_delete(self, page):
        page.locator("text=Delete").first.click()
        page.click("text=Cancel")
        page.wait_for_timeout(300)
        assert page.locator("text=10 movies").is_visible()

    def test_confirm_deletes_movie(self, page):
        page.fill("input[placeholder*='Title']", "Forrest Gump")
        page.wait_for_selector("text=1 movies")
        page.locator("text=Delete").first.click()
        page.locator("button:text('Delete')").last.click()
        page.wait_for_selector("text=No movies found")
