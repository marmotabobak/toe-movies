"""E2E: movie list, filters, sorting, pagination."""
import pytest


def movie_count(page) -> int:
    """Read the 'N movies' counter below the table header."""
    text = page.locator("div.text-gray-400").filter(has_text="movies").text_content()
    return int(text.split()[0])


def wait_for_count(page, expected: int, timeout: int = 5000):
    page.wait_for_function(
        f"() => {{ const el = document.querySelector('div.text-gray-400'); return el && el.textContent.trim().startsWith('{expected} '); }}",
        timeout=timeout,
    )


class TestMovieList:
    def test_page_title_and_header(self, page):
        assert page.title() == "tvoe-movies"
        assert page.locator("h1").text_content() == "tvoe-movies"

    def test_shows_total_count(self, page):
        assert movie_count(page) == 10

    def test_shows_movie_rows(self, page):
        assert page.locator("table tbody tr").count() == 10

    def test_shows_english_title(self, page):
        assert page.locator("text=The Shawshank Redemption").first.is_visible()

    def test_shows_russian_subtitle(self, page):
        assert page.locator("text=Побег из Шоушенка").first.is_visible()

    def test_imdb_rating_badge_visible(self, page):
        assert page.locator("text=9.3").first.is_visible()

    def test_rt_badge_visible(self, page):
        assert page.locator("text=89%").first.is_visible()

    def test_add_movie_button_visible(self, page):
        assert page.locator("text=+ Add Movie").is_visible()


class TestSearch:
    def test_search_filters_rows(self, page):
        page.fill("input[placeholder*='Title']", "matrix")
        page.wait_for_selector("text=The Matrix")
        wait_for_count(page, 1)

    def test_search_no_results(self, page):
        page.fill("input[placeholder*='Title']", "xyznonexistentfilm")
        page.wait_for_selector("text=No movies found")

    def test_clearing_search_restores_all(self, page):
        page.fill("input[placeholder*='Title']", "nolan")
        wait_for_count(page, 2)
        page.fill("input[placeholder*='Title']", "")
        wait_for_count(page, 10)

    def test_search_by_director(self, page):
        page.fill("input[placeholder*='Title']", "Fincher")
        page.wait_for_selector("text=Fight Club")


class TestFilters:
    def test_genre_filter(self, page):
        page.select_option("select", "Drama")
        page.wait_for_timeout(600)
        count = movie_count(page)
        assert count < 10

    def test_imdb_min_filter(self, page):
        page.locator("input[placeholder='0']").first.fill("9.1")
        page.wait_for_timeout(600)
        wait_for_count(page, 2)  # 9.2 (Godfather) and 9.3 (Shawshank)

    def test_year_from_filter(self, page):
        page.fill("input[placeholder='1900']", "2000")
        page.wait_for_timeout(600)
        # 2000+: Dark Knight (2008), Interstellar (2014), LOTR: ROTK (2003)
        wait_for_count(page, 3)

    def test_year_to_filter(self, page):
        page.fill("input[placeholder='2026']", "1994")
        page.wait_for_timeout(600)
        # Up to 1994: Godfather (72), Schindler's (93), Shawshank (94), Pulp Fiction (94), Forrest Gump (94)
        wait_for_count(page, 5)

    def test_keyword_filter(self, page):
        page.fill("input[placeholder='e.g. horror']", "sci-fi")
        page.wait_for_timeout(600)
        # Interstellar + Matrix
        wait_for_count(page, 2)


class TestKeywordFilterSuggestions:
    def test_shows_top_keywords_on_focus(self, page):
        page.locator("input[placeholder='e.g. horror']").click()
        page.wait_for_selector("ul li")
        count = page.locator("ul li").count()
        assert 1 <= count <= 10

    def test_selecting_suggestion_applies_filter(self, page):
        page.locator("input[placeholder='e.g. horror']").click()
        page.wait_for_selector("ul li:has-text('sci-fi')")
        page.locator("ul li:has-text('sci-fi')").click()
        wait_for_count(page, 2)  # Interstellar + Matrix

    def test_typing_filters_suggestions(self, page):
        page.locator("input[placeholder='e.g. horror']").click()
        page.locator("input[placeholder='e.g. horror']").fill("pri")
        page.wait_for_selector("ul li:has-text('prison')")
        assert not page.locator("ul li:has-text('sci-fi')").is_visible()


class TestSorting:
    def test_sort_by_imdb_desc(self, page):
        # First click on IMDB = sort asc, second = desc
        page.locator("th:has-text('IMDB')").click()
        page.wait_for_timeout(400)
        page.locator("th:has-text('IMDB')").click()
        # Wait until Shawshank (9.3) appears in the first row
        page.wait_for_function(
            "() => document.querySelector('table tbody tr:first-child')?.textContent?.includes('9.3')"
        )

    def test_sort_by_year_asc(self, page):
        page.locator("th:has-text('Year')").click()
        # Godfather (1972) should be first
        page.wait_for_function(
            "() => { const cell = document.querySelector('table tbody tr:first-child td:nth-child(4)'); return cell && cell.textContent.trim() === '1972'; }"
        )

    def test_sort_indicator_shown(self, page):
        page.locator("th:has-text('IMDB')").click()
        page.wait_for_timeout(300)
        header_text = page.locator("th:has-text('IMDB')").text_content()
        assert "↑" in header_text or "↓" in header_text
