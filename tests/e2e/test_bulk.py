"""E2E: bulk select, bulk delete, bulk edit."""
import pytest


def bulk_modal(page):
    return page.locator(".max-w-md")


class TestBulkSelect:
    def test_bulk_bar_hidden_initially(self, page):
        assert not page.locator("text=selected").is_visible()

    def test_checking_row_shows_bulk_bar(self, page):
        page.locator("table tbody tr").first.locator("input[type=checkbox]").check()
        assert page.locator("text=1 selected").is_visible()

    def test_checking_multiple_rows_updates_count(self, page):
        rows = page.locator("table tbody tr")
        rows.nth(0).locator("input[type=checkbox]").check()
        rows.nth(1).locator("input[type=checkbox]").check()
        rows.nth(2).locator("input[type=checkbox]").check()
        assert page.locator("text=3 selected").is_visible()

    def test_select_all_checkbox_checks_all_rows(self, page):
        page.locator("table thead input[type=checkbox]").check()
        page.wait_for_timeout(300)
        assert page.locator("text=10 selected").is_visible()

    def test_clear_button_deselects_all(self, page):
        page.locator("table tbody tr").first.locator("input[type=checkbox]").check()
        assert page.locator("text=1 selected").is_visible()
        page.click("text=✕ Clear")
        assert not page.locator("text=selected").is_visible()

    def test_row_highlighted_when_selected(self, page):
        first_row = page.locator("table tbody tr").first
        first_row.locator("input[type=checkbox]").check()
        assert "bg-blue-50" in first_row.get_attribute("class")


class TestBulkDelete:
    def test_bulk_delete_shows_confirm(self, page):
        page.locator("table tbody tr").first.locator("input[type=checkbox]").check()
        # click Delete in the bulk bar (not the row-level delete)
        page.locator(".bg-blue-700 button:text('Delete')").click()
        assert page.locator("text=Delete 1 selected movies?").is_visible()

    def test_cancel_bulk_delete_does_not_remove(self, page):
        page.locator("table tbody tr").first.locator("input[type=checkbox]").check()
        page.locator(".bg-blue-700 button:text('Delete')").click()
        page.click("text=Cancel")
        page.wait_for_timeout(300)
        assert page.locator("text=10 movies").is_visible()

    def test_bulk_delete_removes_selected(self, page):
        rows = page.locator("table tbody tr")
        rows.nth(0).locator("input[type=checkbox]").check()
        rows.nth(1).locator("input[type=checkbox]").check()
        page.locator(".bg-blue-700 button:text('Delete')").click()
        page.locator("button:text('Delete')").last.click()
        page.wait_for_selector("text=8 movies")


class TestBulkEdit:
    def _select_first_n(self, page, n: int):
        rows = page.locator("table tbody tr")
        for i in range(n):
            rows.nth(i).locator("input[type=checkbox]").check()

    def test_bulk_edit_opens_modal(self, page):
        self._select_first_n(page, 2)
        page.locator(".bg-blue-700 button:text('Edit')").click()
        assert page.locator("text=Bulk Edit (2 movies)").is_visible()

    def test_bulk_edit_cancel_closes_modal(self, page):
        self._select_first_n(page, 1)
        page.locator(".bg-blue-700 button:text('Edit')").click()
        bulk_modal(page).locator("text=Cancel").click()
        assert not page.locator("text=Bulk Edit").is_visible()

    def test_bulk_edit_genre_updates_rows(self, page):
        # select 2 rows, bulk-edit their genre, then verify in the table
        rows = page.locator("table tbody tr")
        row0_title = rows.nth(0).locator("td").nth(2).locator("div").first.text_content()
        row1_title = rows.nth(1).locator("td").nth(2).locator("div").first.text_content()

        rows.nth(0).locator("input[type=checkbox]").check()
        rows.nth(1).locator("input[type=checkbox]").check()
        page.locator(".bg-blue-700 button:text('Edit')").click()
        bulk_modal(page).locator("label:has-text('Genre') + input").fill("Documentary")
        bulk_modal(page).locator("button:text('Apply')").click()
        page.wait_for_timeout(600)

        # search for one of the edited rows and verify genre updated
        page.fill("input[placeholder*='Title']", row0_title)
        page.wait_for_timeout(500)
        genre_cell = page.locator("table tbody tr").first.locator("td").nth(4)
        assert "Documentary" in genre_cell.text_content()

    def test_bulk_edit_adds_keywords(self, page):
        self._select_first_n(page, 2)
        page.locator(".bg-blue-700 button:text('Edit')").click()
        kw_input = bulk_modal(page).locator("input[placeholder='Type keyword, press Enter']")
        kw_input.fill("bulk-tagged")
        kw_input.press("Enter")
        bulk_modal(page).locator("button:text('Apply')").click()
        page.wait_for_timeout(500)
        # keyword filter should return exactly the 2 edited rows
        page.fill("input[placeholder='e.g. horror']", "bulk-tagged")
        page.wait_for_function(
            "() => { const el = document.querySelector('div.text-gray-400'); return el && el.textContent.trim().startsWith('2 '); }",
            timeout=5000,
        )
