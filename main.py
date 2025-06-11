import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin, urlparse
import logging
logging.basicConfig(level=logging.INFO)

class WebCrawler:
    def __init__(self):
        self.index = defaultdict(list)
        self.visited = set()

    def crawl(self, url, base_url=None):
        if url in self.visited:
            return
        self.visited.add(url)

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            self.index[url] = soup.get_text()

            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                        href = urljoin(base_url or url, href)
                        if href.startswith(base_url or url):
                            self.crawl(href, base_url=base_url or url)
        except Exception as e:
            print(f"Error crawling {url}: {e}")

    def search(self, keyword):
        results = []
        for url, text in self.index.items():
            if keyword.lower() in text.lower():
                results.append(url)
        return results

    def print_results(self, results):
        if results:
            print("Search results:")
            for result in results:
                print(f"- {result}")
        else:
            print("No results found.")

def main():
    crawler = WebCrawler()
    start_url = "https://example.com"
    crawler.crawl(start_url)

    keyword = "test"
    results = crawler.search(keyword)
    crawler.print_results(results)

import unittest
from unittest.mock import patch, MagicMock
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin, urlparse
import sys
from io import StringIO

class WebCrawlerTests(unittest.TestCase):
    @patch('requests.get')
    def test_crawl_success(self, mock_get):
        sample_html = """
        <html><body>
            <h1>Welcome!</h1>
            <a href="/about">About Us</a>
            <a href="https://www.external.com">External Link</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_get.return_value = mock_response

        crawler = WebCrawler()
        crawler.crawl("https://example.com")

        # Assert that 'about' was added to visited URLs
        self.assertIn("https://example.com/about", crawler.visited)
        # Assert that external link was not crawled
        self.assertNotIn("https://www.external.com", crawler.visited)
        # Assert that index contains crawled pages
        self.assertIn("https://example.com", crawler.index)
        self.assertIn("https://example.com/about", crawler.index)

    @patch('requests.get')
    def test_crawl_already_visited(self, mock_get):
        crawler = WebCrawler()
        crawler.visited.add("https://example.com")
        crawler.crawl("https://example.com")
        # Should not call requests.get if already visited
        mock_get.assert_not_called()

    @patch('requests.get')
    def test_crawl_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Test Error")
        crawler = WebCrawler()
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            crawler.crawl("https://example.com")
            self.assertIn("Error crawling https://example.com: Test Error", mock_stdout.getvalue())

    @patch('requests.get')
    def test_crawl_empty_url(self, mock_get):
        crawler = WebCrawler()
        crawler.crawl("")
        # Should add empty string to visited
        self.assertIn("", crawler.visited)

    @patch('requests.get')
    def test_crawl_malformed_html(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = "<html><body><a href='/next'>Next"
        mock_get.return_value = mock_response
        crawler = WebCrawler()
        crawler.crawl("https://example.com")
        self.assertIn("https://example.com/next", crawler.visited)

    def test_search_keyword_present(self):
        crawler = WebCrawler()
        crawler.index["page1"] = "This has the keyword"
        crawler.index["page2"] = "No keyword here"
        results = crawler.search("keyword")
        self.assertEqual(sorted(results), ["page1", "page2"])

    def test_search_keyword_absent(self):
        crawler = WebCrawler()
        crawler.index["page1"] = "No match"
        results = crawler.search("notfound")
        self.assertEqual(results, [])

    def test_search_case_insensitive(self):
        crawler = WebCrawler()
        crawler.index["page1"] = "KEYword"
        results = crawler.search("keyword")
        self.assertEqual(results, ["page1"])

    def test_search_empty_index(self):
        crawler = WebCrawler()
        results = crawler.search("anything")
        self.assertEqual(results, [])

    def test_search_empty_keyword(self):
        crawler = WebCrawler()
        crawler.index["page1"] = "something"
        results = crawler.search("")
        self.assertEqual(results, ["page1"])

    def test_print_results_with_results(self):
        crawler = WebCrawler()
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            crawler.print_results(["https://test.com/result"])
            output = mock_stdout.getvalue()
            self.assertIn("Search results:", output)
            self.assertIn("- https://test.com/result", output)

    def test_print_results_no_results(self):
        crawler = WebCrawler()
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            crawler.print_results([])
            output = mock_stdout.getvalue()
            self.assertIn("No results found.", output)

    @patch('requests.get')
    def test_crawl_relative_and_absolute_links(self, mock_get):
        # Test both relative and absolute links
        html = """
        <html><body>
            <a href="page2">Page2</a>
            <a href="https://example.com/page3">Page3</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response
        crawler = WebCrawler()
        crawler.crawl("https://example.com")
        self.assertIn("https://example.com/page2", crawler.visited)
        self.assertIn("https://example.com/page3", crawler.visited)

    @patch('requests.get')
    def test_crawl_does_not_follow_external_links(self, mock_get):
        html = """
        <html><body>
            <a href="https://external.com/page">External</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = html
        mock_get.return_value = mock_response
        crawler = WebCrawler()
        crawler.crawl("https://example.com")
        self.assertNotIn("https://external.com/page", crawler.visited)

if __name__ == "__main__":
    unittest.main()
    main()
