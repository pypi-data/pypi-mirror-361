"""Basic tests for NerdMan package."""

import unittest
import sys
import os
os.environ["NERDMAN_TEST_MODE"] = "1"

# Add the parent directory to the path so we can import nerdman
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import nerdman
except ImportError as e:
    print(f"Failed to import nerdman: {e}")
    sys.exit(1)


class TestNerdManBasics(unittest.TestCase):
    """Test basic functionality of NerdMan."""
    
    def test_import_success(self):
        """Test that nerdman can be imported."""
        self.assertTrue(hasattr(nerdman, 'icon'))
        self.assertTrue(hasattr(nerdman, 'search_icons'))
        self.assertTrue(hasattr(nerdman, 'get_icon_count'))
    
    def test_icon_function_exists(self):
        """Test that icon function returns something."""
        result = nerdman.icon("cod-home")
        self.assertIsInstance(result, str)
        # Should return either the icon character or '?'
        self.assertTrue(len(result) >= 1)
    
    def test_get_icon_count(self):
        """Test that get_icon_count returns a positive integer."""
        count = nerdman.get_icon_count()
        self.assertIsInstance(count, int)
        self.assertGreater(count, 0)
    
    def test_validate_icon_name(self):
        """Test icon name validation."""
        # Test with a likely valid icon name
        valid_result = nerdman.validate_icon_name("cod-home")
        self.assertIsInstance(valid_result, bool)
        
        # Test with definitely invalid icon name
        invalid_result = nerdman.validate_icon_name("definitely-not-an-icon-name-12345")
        self.assertFalse(invalid_result)
    
    def test_search_icons(self):
        """Test search functionality."""
        results = nerdman.search_icons("home")
        self.assertIsInstance(results, dict)
        # Should return a dictionary (even if empty)
    
    def test_get_categories(self):
        """Test category functionality."""
        categories = nerdman.get_categories()
        self.assertIsInstance(categories, dict)
    
    def test_get_random_icons(self):
        """Test random icon functionality."""
        random_icons = nerdman.get_random_icons(3)
        self.assertIsInstance(random_icons, list)
        # Should return a list (even if empty due to no data)


class TestNerdManUtilities(unittest.TestCase):
    """Test utility functions."""
    
    def test_get_version_info(self):
        """Test version information retrieval."""
        version_info = nerdman.get_version_info()
        self.assertIsInstance(version_info, dict)
    
    def test_find_similar_icons(self):
        """Test similar icon finding."""
        similar = nerdman.find_similar_icons("home", limit=3)
        self.assertIsInstance(similar, list)
        # Each item should be a tuple with 3 elements
        for item in similar[:1]:  # Check first item if any
            self.assertEqual(len(item), 3)
            self.assertIsInstance(item[0], str)  # name
            self.assertIsInstance(item[1], str)  # char
            self.assertIsInstance(item[2], int)  # distance


if __name__ == '__main__':
    # Try to suppress the interactive config creation during tests
    os.environ['NERDMAN_TEST_MODE'] = '1'
    unittest.main()
