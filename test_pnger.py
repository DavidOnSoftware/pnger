import unittest
import os
import shutil
import filecmp

# Add the directory containing pnger.py to the Python path
# This is often needed if pnger.py is not installed as a package
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pnger

class TestPnger(unittest.TestCase):

    TEST_DIR = "test_temp_files"
    ORIGINAL_EMPTY_FILE = os.path.join(TEST_DIR, "empty.txt")
    ORIGINAL_TEXT_FILE = os.path.join(TEST_DIR, "test.txt")
    ORIGINAL_TEXT_CONTENT = "This is a test file for pnger.\nWith multiple lines."
    ORIGINAL_BINARY_FILE = os.path.join(TEST_DIR, "test.bin")
    ORIGINAL_BINARY_CONTENT = os.urandom(128) # 128 random bytes

    PNG_OUTPUT_FILE = os.path.join(TEST_DIR, "output.png")
    UNPNG_OUTPUT_FILE = os.path.join(TEST_DIR, "extracted_data.txt")

    @classmethod
    def setUpClass(cls):
        """Create the temporary directory for test files."""
        if os.path.exists(cls.TEST_DIR):
            shutil.rmtree(cls.TEST_DIR)
        os.makedirs(cls.TEST_DIR, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary directory after all tests are done."""
        if os.path.exists(cls.TEST_DIR):
            shutil.rmtree(cls.TEST_DIR)

    def setUp(self):
        """Create sample input files before each test."""
        # Create empty file
        with open(self.ORIGINAL_EMPTY_FILE, 'w') as f:
            pass
        
        # Create text file
        with open(self.ORIGINAL_TEXT_FILE, 'w') as f:
            f.write(self.ORIGINAL_TEXT_CONTENT)

        # Create binary file
        with open(self.ORIGINAL_BINARY_FILE, 'wb') as f:
            f.write(self.ORIGINAL_BINARY_CONTENT)

        # Ensure output files from previous tests are removed
        if os.path.exists(self.PNG_OUTPUT_FILE):
            os.remove(self.PNG_OUTPUT_FILE)
        if os.path.exists(self.UNPNG_OUTPUT_FILE):
            os.remove(self.UNPNG_OUTPUT_FILE)

    def tearDown(self):
        """Clean up created files after each test if necessary (mostly handled by setUp)."""
        # setUp ensures clean state for PNG_OUTPUT_FILE and UNPNG_OUTPUT_FILE
        pass

    def test_round_trip_empty_file(self):
        """Test pngit and unpngit with an empty file."""
        pnger.pngit(self.ORIGINAL_EMPTY_FILE, self.PNG_OUTPUT_FILE)
        self.assertTrue(os.path.exists(self.PNG_OUTPUT_FILE))
        
        pnger.unpngit(self.PNG_OUTPUT_FILE, self.UNPNG_OUTPUT_FILE)
        self.assertTrue(os.path.exists(self.UNPNG_OUTPUT_FILE))
        
        # Assert that the extracted file is empty
        self.assertEqual(os.path.getsize(self.UNPNG_OUTPUT_FILE), 0)
        # Assert files are identical (though for empty, size check is primary)
        self.assertTrue(filecmp.cmp(self.ORIGINAL_EMPTY_FILE, self.UNPNG_OUTPUT_FILE, shallow=False))

    def test_round_trip_text_file(self):
        """Test pngit and unpngit with a small text file."""
        pnger.pngit(self.ORIGINAL_TEXT_FILE, self.PNG_OUTPUT_FILE)
        self.assertTrue(os.path.exists(self.PNG_OUTPUT_FILE))

        pnger.unpngit(self.PNG_OUTPUT_FILE, self.UNPNG_OUTPUT_FILE)
        self.assertTrue(os.path.exists(self.UNPNG_OUTPUT_FILE))

        with open(self.UNPNG_OUTPUT_FILE, 'r') as f:
            extracted_content = f.read()
        self.assertEqual(extracted_content, self.ORIGINAL_TEXT_CONTENT)
        self.assertTrue(filecmp.cmp(self.ORIGINAL_TEXT_FILE, self.UNPNG_OUTPUT_FILE, shallow=False))

    def test_round_trip_binary_file(self):
        """Test pngit and unpngit with a small binary file."""
        pnger.pngit(self.ORIGINAL_BINARY_FILE, self.PNG_OUTPUT_FILE)
        self.assertTrue(os.path.exists(self.PNG_OUTPUT_FILE))

        pnger.unpngit(self.PNG_OUTPUT_FILE, self.UNPNG_OUTPUT_FILE)
        self.assertTrue(os.path.exists(self.UNPNG_OUTPUT_FILE))

        with open(self.UNPNG_OUTPUT_FILE, 'rb') as f:
            extracted_content = f.read()
        self.assertEqual(extracted_content, self.ORIGINAL_BINARY_CONTENT)
        self.assertTrue(filecmp.cmp(self.ORIGINAL_BINARY_FILE, self.UNPNG_OUTPUT_FILE, shallow=False))

    def test_header_verification(self):
        """Verify that pngit prepends the FAKE_IMAGE_HEADER correctly."""
        pnger.pngit(self.ORIGINAL_TEXT_FILE, self.PNG_OUTPUT_FILE)
        self.assertTrue(os.path.exists(self.PNG_OUTPUT_FILE))

        with open(self.PNG_OUTPUT_FILE, 'rb') as f:
            header_from_file = f.read(len(pnger.FAKE_IMAGE_HEADER))
        
        self.assertEqual(header_from_file, pnger.FAKE_IMAGE_HEADER)

    def test_unpngit_content_offset(self):
        """Verify unpngit correctly skips the header and extracts original content."""
        # 1. Create the PNG file
        pnger.pngit(self.ORIGINAL_TEXT_FILE, self.PNG_OUTPUT_FILE)
        self.assertTrue(os.path.exists(self.PNG_OUTPUT_FILE))

        # 2. Extract using unpngit
        pnger.unpngit(self.PNG_OUTPUT_FILE, self.UNPNG_OUTPUT_FILE)
        self.assertTrue(os.path.exists(self.UNPNG_OUTPUT_FILE))

        # 3. Read the content of the output file from unpngit
        with open(self.UNPNG_OUTPUT_FILE, 'r') as f:
            extracted_content = f.read()
        
        # 4. Assert that this is identical to the original text file's content
        self.assertEqual(extracted_content, self.ORIGINAL_TEXT_CONTENT)

    def test_unpngit_on_small_file(self):
        """Test unpngit with a file smaller than the header, expecting sys.exit."""
        TOO_SMALL_FILE = os.path.join(self.TEST_DIR, "too_small.png")
        with open(TOO_SMALL_FILE, 'wb') as f:
            f.write(b"small") # Content much smaller than header

        # pnger.unpngit calls sys.exit(1) on error.
        # We need to catch SystemExit.
        with self.assertRaises(SystemExit) as cm:
            pnger.unpngit(TOO_SMALL_FILE, self.UNPNG_OUTPUT_FILE)
        self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
