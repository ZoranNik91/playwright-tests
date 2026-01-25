from e2e_tests.pages.reversing_labs_page import ReversingLabsPage
from pathlib import Path
from urllib.parse import urlparse


def test_reversing_labs(page):
    rl = ReversingLabsPage(page)
    reversing_labs_url = "https://www.reversinglabs.com/"

    # Navigate to ReversingLabs home page
    rl.go_to_website(reversing_labs_url)

    # Validate home page title
    assert "ReversingLabs" in page.title()

    # Navigate to Product & Technology tab
    assert rl.is_visible_by_selector_and_text(".main-nav_category__dMVd6", "Product & Technology")
    rl.click_by_selector_and_text(".main-nav_category__dMVd6", "Product & Technology")

    # Validate dropdown - Spectra Analyze option
    assert rl.is_visible_by_selector_and_text('a[href="/products/spectra-analyze"]', "Spectra Analyze")
    rl.click_by_selector_and_text('a[href="/products/spectra-analyze"]', "Spectra Analyze")

    # Validate URL - Spectra Analyze page
    page.wait_for_url("**/products/spectra-analyze**")
    assert "/products/spectra-analyze" in page.url

    # Validate title - Advanced Malware Analysis & Threat Hunting
    spectra_analyze_title = "Advanced Malware Analysis & Threat Hunting | ReversingLabs"
    assert page.title() == spectra_analyze_title

    # Validate text visibility - Spectra Analyze
    assert rl.is_visible_by_selector_and_text(
        ".slide_container__EGEZp h1",
        "Efficacy. Speed. Privacy. Malware Analysis that Delivers.",
    )

    # Navigate to Product & Technology tab
    assert rl.is_visible_by_selector_and_text(".main-nav_category__dMVd6", "Product & Technology")
    rl.click_by_selector_and_text(".main-nav_category__dMVd6", "Product & Technology")

    # Validate dropdown - Spectra Detect option
    assert rl.is_visible_by_selector_and_text('a[href="/products/spectra-detect"]', "Spectra Detect")
    rl.click_by_selector_and_text('a[href="/products/spectra-detect"]', "Spectra Detect")

    # Ensure navigation actually happened before validating the title changed
    page.wait_for_url("**/products/spectra-detect**")
    assert "/products/spectra-detect" in page.url

    # Validate title is no longer Spectra Analyze title
    assert page.title() != spectra_analyze_title

    # Navigate with url method back to Spectra Analyze page
    rl.go_to_website("https://www.reversinglabs.com/products/spectra-analyze")

    # Validate Download button is visible
    assert rl.is_visible_by_selector_and_text(".button_button__iBnBy", "DOWNLOAD DATASHEET")

    # Get expected PDF URL + filename from the actual link
    expected_pdf_url = rl.get_link_href(".button_button__iBnBy", "DOWNLOAD DATASHEET")
    assert expected_pdf_url, "DOWNLOAD DATASHEET link has no href"

    parsed = urlparse(expected_pdf_url)
    expected_filename = Path(parsed.path).name
    assert expected_filename.lower().endswith(".pdf"), f"Expected a .pdf link, got: {expected_pdf_url}"

    # Download the PDF into files/downloads and ensure the old file is removed first
    downloads_dir = Path("files") / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)

    target_file = downloads_dir / expected_filename
    if target_file.exists():
        rl.logger.debug('Removing existing file: "%s"', expected_filename)
        target_file.unlink()
    else:
        rl.logger.debug('No existing file to remove (skipping): "%s"', expected_filename)

    saved_path, download_url = rl.download_file_by_selector_and_text(
        ".button_button__iBnBy",
        "DOWNLOAD DATASHEET",
        downloads_dir,
        filename=expected_filename,
    )

    # Validate the download came from the same URL as the link on the page
    assert download_url == expected_pdf_url

    # Validate the file was saved
    assert saved_path.exists()
    assert saved_path.name == expected_filename
    assert saved_path.suffix.lower() == ".pdf"
    assert saved_path.stat().st_size > 10_000  # downloaded file isn't empty/tiny
