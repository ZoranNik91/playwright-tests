from e2e_tests.pages.reversing_labs_page import ReversingLabsPage


def test_reversing_labs_home(page):
    rl = ReversingLabsPage(page)

    rl.go_to_website("https://www.reversinglabs.com/")

    assert "ReversingLabs" in page.title()
    rl.assert_text_contains("title", "ReversingLabs")
