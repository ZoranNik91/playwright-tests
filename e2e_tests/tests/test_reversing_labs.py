from e2e_tests.pages.reversing_labs_page import ReversingLabsPage
from pathlib import Path
from urllib.parse import urlparse

def test_reversing_labs(page):
    rl = ReversingLabsPage(page)

    rl.go_to_website(ReversingLabsPage.HOME_URL)

    assert "ReversingLabs" in page.title()

    assert rl.is_visible_by_selector_and_text(ReversingLabsPage.productAndTechnology, ReversingLabsPage.productAndTechnologyText)
    rl.click_by_selector_and_text(ReversingLabsPage.productAndTechnology, ReversingLabsPage.productAndTechnologyText)

    assert rl.is_visible_by_selector_and_text(ReversingLabsPage.spectraAnalyzeLink, ReversingLabsPage.spectraAnalyzeText)
    rl.click_by_selector_and_text(ReversingLabsPage.spectraAnalyzeLink, ReversingLabsPage.spectraAnalyzeText)

    page.wait_for_url(f"**{ReversingLabsPage.spectraAnalyze}**")
    assert ReversingLabsPage.spectraAnalyze in page.url

    spectra_analyze_title = "Advanced Malware Analysis & Threat Hunting | ReversingLabs"
    assert page.title() == spectra_analyze_title

    assert rl.is_visible_by_selector_and_text(ReversingLabsPage.slideContainerH1, ReversingLabsPage.slideContainerH1Text)

    assert rl.is_visible_by_selector_and_text(ReversingLabsPage.productAndTechnology, ReversingLabsPage.productAndTechnologyText)
    rl.click_by_selector_and_text(ReversingLabsPage.productAndTechnology, ReversingLabsPage.productAndTechnologyText)

    assert rl.is_visible_by_selector_and_text(ReversingLabsPage.spectraDetectLink, ReversingLabsPage.spectraDetectText)
    rl.click_by_selector_and_text(ReversingLabsPage.spectraDetectLink, ReversingLabsPage.spectraDetectText)

    page.wait_for_url(f"**{ReversingLabsPage.spectraDetect}**")
    assert ReversingLabsPage.spectraDetect in page.url

    assert page.title() != spectra_analyze_title

    rl.go_to_website(ReversingLabsPage.spectraAnalyzeUrl)

    assert rl.is_visible_by_selector_and_text(ReversingLabsPage.downloadDatasheet, ReversingLabsPage.downloadDatasheetText)

    # Get expected PDF URL + filename from the actual link
    expected_pdf_url = rl.get_link_href(ReversingLabsPage.downloadDatasheet, ReversingLabsPage.downloadDatasheetText)
    assert expected_pdf_url, "DOWNLOAD DATASHEET link has no href"

    parsed = urlparse(expected_pdf_url)
    expected_filename = Path(parsed.path).name
    assert expected_filename.lower().endswith(".pdf"), f"Expected a .pdf link, got: {expected_pdf_url}"

    downloads_dir = Path("e2e_tests") / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    target_file = downloads_dir / expected_filename
    rl.remove_file_if_exists(target_file)

    saved_path, download_url = rl.download_file_by_selector_and_text(
        ReversingLabsPage.downloadDatasheet,
        ReversingLabsPage.downloadDatasheetText,
        downloads_dir,
        filename=expected_filename,
    )

    # Validate the download came from the same URL as the link on the page
    assert download_url == expected_pdf_url

    # Validate the file was saved
    assert saved_path.exists()
    assert saved_path.name == expected_filename
    assert saved_path.suffix.lower() == ".pdf"
    assert saved_path.stat().st_size > 10_000  # downloaded file isn't empty
