import asyncio
import mimetypes
import os
import re
from hashlib import md5
from typing import Dict, List, Optional
from urllib.parse import urlparse

import nest_asyncio
import pikepdf
import requests
from bs4 import BeautifulSoup
from loguru import logger
from markdownify import markdownify as md

from lexoid.core.llm_selector import LLMScoreRegressor


def split_pdf(input_path: str, output_dir: str, pages_per_split: int):
    paths = []
    with pikepdf.open(input_path) as pdf:
        total_pages = len(pdf.pages)
        for start in range(0, total_pages, pages_per_split):
            end = min(start + pages_per_split, total_pages)
            output_path = os.path.join(
                output_dir, f"split_{str(start + 1).zfill(4)}_{end}.pdf"
            )
            with pikepdf.new() as new_pdf:
                new_pdf.pages.extend(pdf.pages[start:end])
                new_pdf.save(output_path)
                paths.append(output_path)
    return paths


def create_sub_pdf(
    input_path: str, output_path: str, page_nums: Optional[tuple[int, ...] | int] = None
) -> str:
    if isinstance(page_nums, int):
        page_nums = (page_nums,)
    page_nums = tuple(sorted(set(page_nums)))
    with pikepdf.open(input_path) as pdf:
        indices = page_nums if page_nums else range(len(pdf.pages))
        with pikepdf.new() as new_pdf:
            new_pdf.pages.extend([pdf.pages[i - 1] for i in indices])
            new_pdf.save(output_path)
    return output_path


def get_file_type(path: str) -> str:
    """Get the file type of a file based on its extension."""
    return mimetypes.guess_type(path)[0]


def is_supported_file_type(path: str) -> bool:
    """Check if the file type is supported for parsing."""
    file_type = get_file_type(path)
    if (
        file_type == "application/pdf"
        or "wordprocessing" in file_type
        or "spreadsheet" in file_type
        or "presentation" in file_type
        or file_type.startswith("image/")
        or file_type.startswith("text")
    ):
        return True
    return False


def is_supported_url_file_type(url: str) -> bool:
    """
    Check if the file type from the URL is supported.

    Args:
        url (str): The URL of the file.

    Returns:
        bool: True if the file type is supported, False otherwise.
    """
    supported_extensions = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"]
    parsed_url = urlparse(url)
    ext = os.path.splitext(parsed_url.path)[1].lower()

    if ext in supported_extensions:
        return True

    # If no extension in URL, try to get content type from headers
    try:
        response = requests.head(url)
    except requests.exceptions.ConnectionError:
        return False
    content_type = response.headers.get("Content-Type", "")
    ext = mimetypes.guess_extension(content_type)

    return ext in supported_extensions


def download_file(url: str, temp_dir: str) -> str:
    """
    Downloads a file from the given URL and saves it to a temporary directory.

    Args:
        url (str): The URL of the file to download.
        temp_dir (str): The temporary directory to save the file.

    Returns:
        str: The path to the downloaded file.
    """
    response = requests.get(url)
    file_name = os.path.basename(urlparse(url).path)
    if not file_name:
        content_type = response.headers.get("Content-Type", "")
        ext = mimetypes.guess_extension(content_type)
        file_name = f"downloaded_file{ext}" if ext else "downloaded_file"

    file_path = os.path.join(temp_dir, file_name)
    with open(file_path, "wb") as f:
        f.write(response.content)
    return file_path


def find_dominant_heading_level(markdown_content: str) -> str:
    """
    Finds the most common heading level that occurs more than once.
    Also checks for underline style headings (---).

    Args:
        markdown_content (str): The markdown content to analyze

    Returns:
        str: The dominant heading pattern (e.g., '##' or 'underline')
    """
    # Check for underline style headings first
    underline_pattern = r"^[^\n]+\n-+$"
    underline_matches = re.findall(underline_pattern, markdown_content, re.MULTILINE)
    if len(underline_matches) > 1:
        return "underline"

    # Find all hash-style headings in the markdown content
    heading_patterns = ["#####", "####", "###", "##", "#"]
    heading_counts = {}

    for pattern in heading_patterns:
        # Look for headings at the start of a line
        regex = f"^{pattern} .*$"
        matches = re.findall(regex, markdown_content, re.MULTILINE)
        if len(matches) > 1:  # Only consider headings that appear more than once
            heading_counts[pattern] = len(matches)

    if not heading_counts:
        return "#"  # Default to h1 if no repeated headings found

    return min(heading_counts.keys(), key=len)


def split_md_by_headings(markdown_content: str, heading_pattern: str) -> List[Dict]:
    """
    Splits markdown content by the specified heading pattern and structures it.

    Args:
        markdown_content (str): The markdown content to split
        heading_pattern (str): The heading pattern to split on (e.g., '##' or 'underline')

    Returns:
        List[Dict]: List of dictionaries containing metadata and content
    """
    structured_content = []

    if heading_pattern == "underline":
        # Split by underline headings
        pattern = r"^([^\n]+)\n-+$"
        sections = re.split(pattern, markdown_content, flags=re.MULTILINE)
        # Remove empty sections and strip whitespace
        sections = [section.strip() for section in sections]

        # Handle content before first heading if it exists
        if sections and not re.match(r"^[^\n]+\n-+$", sections[0], re.MULTILINE):
            structured_content.append(
                {
                    "metadata": {"page": "Introduction"},
                    "content": sections.pop(0),
                }
            )

        # Process sections pairwise (heading, content)
        for i in range(0, len(sections), 2):
            if i + 1 < len(sections):
                structured_content.append(
                    {
                        "metadata": {"page": sections[i]},
                        "content": sections[i + 1],
                    }
                )
    else:
        # Split by hash headings
        regex = f"^{heading_pattern} .*$"
        sections = re.split(regex, markdown_content, flags=re.MULTILINE)
        headings = re.findall(regex, markdown_content, flags=re.MULTILINE)

        # Remove empty sections and strip whitespace
        sections = [section.strip() for section in sections]

        # Handle content before first heading if it exists
        if len(sections) > len(headings):
            structured_content.append(
                {
                    "metadata": {"page": "Introduction"},
                    "content": sections.pop(0),
                }
            )

        # Process remaining sections
        for heading, content in zip(headings, sections):
            clean_heading = heading.replace(heading_pattern, "").strip()
            structured_content.append(
                {
                    "metadata": {"page": clean_heading},
                    "content": content,
                }
            )

    return structured_content


def html_to_markdown(html: str, title: str, url: str) -> str:
    """
    Converts HTML content to markdown.

    Args:
        html (str): The HTML content to convert.
        title (str): The title of the HTML page
        url (str): The URL of the HTML page

    Returns:
        Dict: Dictionary containing parsed document data
    """
    markdown_content = md(html)

    # Find the dominant heading level
    heading_pattern = find_dominant_heading_level(markdown_content)

    # Split content by headings and structure it
    split_md = split_md_by_headings(markdown_content, heading_pattern)

    content = {
        "raw": markdown_content,
        "segments": split_md,
        "title": title,
        "url": url,
        "parent_title": "",
        "recursive_docs": [],
    }

    return content


def get_webpage_soup(url: str) -> BeautifulSoup:
    try:
        from playwright.async_api import async_playwright

        nest_asyncio.apply()

        async def fetch_page():
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--window-size=1920,1080",
                    ],
                )
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    bypass_csp=True,
                )
                page = await context.new_page()

                # Add headers to appear more like a real browser
                await page.set_extra_http_headers(
                    {
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none",
                        "Sec-Fetch-User": "?1",
                    }
                )

                await page.goto(url)

                # Wait for Cloudflare check to complete
                await page.wait_for_load_state("domcontentloaded")

                # Additional wait for any dynamic content
                try:
                    await page.wait_for_selector("body", timeout=30000)
                except Exception:
                    pass

                html = await page.content()
                await browser.close()
                return html

        loop = asyncio.get_event_loop()
        html = loop.run_until_complete(fetch_page())
        soup = BeautifulSoup(html, "html.parser")
    except Exception as e:
        logger.debug(
            f"Error reading HTML content from URL, attempting with default https request: {str(e)}"
        )
        response = requests.get(url)
        soup = BeautifulSoup(
            response.content, "html.parser", from_encoding="iso-8859-1"
        )
    return soup


def read_html_content(url: str) -> Dict:
    """
    Reads the content of an HTML page from the given URL and converts it to markdown or structured content.

    Args:
        url (str): The URL of the HTML page.

    Returns:
        Dict: Dictionary containing parsed document data
    """

    soup = get_webpage_soup(url)
    title = soup.title.string.strip() if soup.title else "No title"
    url_hash = md5(url.encode("utf-8")).hexdigest()[:8]
    full_title = f"{title} - {url_hash}"
    return html_to_markdown(str(soup), title=full_title, url=url)


def extract_urls_from_markdown(content: str) -> List[str]:
    """
    Extracts URLs from markdown content using regex.
    Matches both [text](url) and bare http(s):// URLs.

    Args:
        content (str): Markdown content to search for URLs

    Returns:
        List[str]: List of unique URLs found
    """
    # Match markdown links [text](url) and bare URLs
    markdown_pattern = r"\[([^\]]+)\]\((https?://[^\s\)]+)\)"
    bare_url_pattern = r"(?<!\()(https?://[^\s\)]+)"

    urls = []
    # Extract URLs from markdown links
    urls.extend(match.group(2) for match in re.finditer(markdown_pattern, content))
    # Extract bare URLs
    urls.extend(match.group(0) for match in re.finditer(bare_url_pattern, content))

    return list(set(urls))  # Remove duplicates


def recursive_read_html(url: str, depth: int, visited_urls: set = None) -> Dict:
    """
    Recursively reads HTML content from URLs up to specified depth.

    Args:
        url (str): The URL to parse
        depth (int): How many levels deep to recursively parse
        visited_urls (set): Set of already visited URLs to prevent cycles

    Returns:
        Dict: Dictionary containing parsed document data
    """
    if visited_urls is None:
        visited_urls = set()

    if url in visited_urls:
        return {
            "raw": "",
            "segments": [],
            "title": "",
            "url": url,
            "parent_title": "",
            "recursive_docs": [],
        }

    visited_urls.add(url)

    try:
        content = read_html_content(url)
    except Exception as e:
        print(f"Error processing URL {url}: {str(e)}")
        return {
            "raw": "",
            "segments": [],
            "title": "",
            "url": url,
            "parent_title": "",
            "recursive_docs": [],
        }

    if depth <= 1:
        return content

    # Extract URLs from all content sections
    urls = extract_urls_from_markdown(content["raw"])

    # Recursively process each URL
    recursive_docs = []
    for sub_url in urls:
        if sub_url not in visited_urls:
            sub_content = recursive_read_html(sub_url, depth - 1, visited_urls)
            recursive_docs.append(sub_content)

    content["recursive_docs"] = recursive_docs
    return content


def has_image_in_pdf(path: str):
    with open(path, "rb") as fp:
        content = fp.read()
    return "Image".lower() in list(
        map(lambda x: x.strip(), (str(content).lower().split("/")))
    )


def has_hyperlink_in_pdf(path: str):
    with open(path, "rb") as fp:
        content = fp.read()
    # URI tag is used if Links are hidden.
    return "URI".lower() in list(
        map(lambda x: x.strip(), (str(content).lower().split("/")))
    )


def get_api_provider_for_model(model: str) -> str:
    if model.startswith("gemini"):
        return "gemini"
    if model.startswith("gpt"):
        return "openai"
    if model.startswith("meta-llama"):
        if "Turbo" in model or model == "meta-llama/Llama-Vision-Free":
            return "together"
        return "huggingface"
    if any(model.startswith(prefix) for prefix in ["microsoft", "google", "qwen"]):
        return "openrouter"
    if model.startswith("accounts/fireworks"):
        return "fireworks"
    if model.startswith("claude"):
        return "anthropic"
    if model.startswith("mistral"):
        return "mistral"
    if model.startswith("ds4sd/SmolDocling"):
        return "local"
    raise ValueError(f"Unsupported model: {model}")


def is_api_key_set(api_provider: str) -> bool:
    if api_provider == "openai":
        return bool(os.getenv("OPENAI_API_KEY"))
    elif api_provider == "gemini":
        return bool(os.getenv("GOOGLE_API_KEY"))
    elif api_provider == "together":
        return bool(os.getenv("TOGETHER_API_KEY"))
    elif api_provider == "huggingface":
        return bool(os.getenv("HUGGINGFACEHUB_API_TOKEN"))
    elif api_provider == "openrouter":
        return bool(os.getenv("OPENROUTER_API_KEY"))
    elif api_provider == "fireworks":
        return bool(os.getenv("FIREWORKS_API_KEY"))
    elif api_provider == "anthropic":
        return bool(os.getenv("ANTHROPIC_API_KEY"))
    elif api_provider == "mistral":
        return bool(os.getenv("MISTRAL_API_KEY"))
    elif api_provider == "local":
        return True  # Local models don't require an API key
    return False


def router(path: str, priority: str = "speed", autoselect_llm: bool = True) -> str:
    """
    Routes the file path to the appropriate parser based on the file type.

    Args:
        path (str): The file path to route.
        priority (str): The priority for routing: "accuracy" (preference to LLM_PARSE) or "speed" (preference to STATIC_PARSE).
    """
    file_type = get_file_type(path)
    if (
        file_type.startswith("text/")
        or "spreadsheet" in file_type
        or "presentation" in file_type
    ):
        return "STATIC_PARSE", None

    model_name = None
    if autoselect_llm:
        logger.debug("Autoselecting LLM for parsing.")
        model_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "model_data"
        )
        selector = LLMScoreRegressor(model_dir=model_dir)
        ranking = selector.rank_models(path)
        for model, _ in ranking:
            api_provider = get_api_provider_for_model(model)
            if is_api_key_set(api_provider):
                logger.debug(f"Selected model: {model}.")
                model_name = model
                break

    if priority == "accuracy":
        # If the file is a PDF without images but has hyperlinks, use STATIC_PARSE
        # Otherwise, use LLM_PARSE
        has_image = has_image_in_pdf(path)
        has_hyperlink = has_hyperlink_in_pdf(path)
        if file_type == "application/pdf" and not has_image and has_hyperlink:
            logger.debug("Using STATIC_PARSE for PDF with hyperlinks and no images.")
            return "STATIC_PARSE", None
        logger.debug(
            f"Using LLM_PARSE because PDF has image ({has_image}) or has no hyperlink ({has_hyperlink})."
        )
        return "LLM_PARSE", model_name
    else:
        # If the file is a PDF without images, use STATIC_PARSE
        # Otherwise, use LLM_PARSE
        if file_type == "application/pdf" and not has_image_in_pdf(path):
            logger.debug("Using STATIC_PARSE for PDF without images.")
            return "STATIC_PARSE", None
        logger.debug("Using LLM_PARSE because PDF has images")
        return "LLM_PARSE", model_name


def get_uri_rect(path):
    with open(path, "rb") as fp:
        byte_str = str(fp.read())
    pattern = r"\((https?://[^\s)]+)\)"
    uris = re.findall(pattern, byte_str)
    rect_splits = byte_str.split("/Rect [")[1:]
    rects = [
        list(map(float, rect_split.split("]")[0].split())) for rect_split in rect_splits
    ]
    return {uri: rect for uri, rect in zip(uris, rects)}
