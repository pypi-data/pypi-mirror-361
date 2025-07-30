"""
Configuration for test cases.
This module contains a separate class for test-specific configuration
to keep it separate from the main blogger configuration.
"""


class TestConfig:
    """
    A class to manage test-specific configuration values.
    These are separate from the main BloggerConfig class to keep
    test-specific settings isolated from production settings.
    """

    def __init__(self, post_id="", page_id="", comment_id="", user_id="", 
                 test_post_title="Test Post", test_page_title="Test Page",
                 test_content="This is test content"):
        """
        Initialize the test configuration.
        
        Args:
            post_id (str, optional): ID of a post to use for testing.
            page_id (str, optional): ID of a page to use for testing.
            comment_id (str, optional): ID of a comment to use for testing.
            user_id (str, optional): ID of a user to use for testing.
            test_post_title (str, optional): Title to use for test posts.
            test_page_title (str, optional): Title to use for test pages.
            test_content (str, optional): Content to use for test posts/pages.
        """
        self._post_id = post_id
        self._page_id = page_id
        self._comment_id = comment_id
        self._user_id = user_id
        self._test_post_title = test_post_title
        self._test_page_title = test_page_title
        self._test_content = test_content
    
    @property
    def post_id(self):
        """Get the post ID for testing."""
        return self._post_id
    
    @post_id.setter
    def post_id(self, value):
        """Set the post ID for testing."""
        self._post_id = value
    
    @property
    def page_id(self):
        """Get the page ID for testing."""
        return self._page_id
    
    @page_id.setter
    def page_id(self, value):
        """Set the page ID for testing."""
        self._page_id = value
        
    @property
    def comment_id(self):
        """Get the comment ID for testing."""
        return self._comment_id
    
    @comment_id.setter
    def comment_id(self, value):
        """Set the comment ID for testing."""
        self._comment_id = value
        
    @property
    def user_id(self):
        """Get the user ID for testing."""
        return self._user_id
    
    @user_id.setter
    def user_id(self, value):
        """Set the user ID for testing."""
        self._user_id = value
        
    @property
    def test_post_title(self):
        """Get the test post title."""
        return self._test_post_title
    
    @test_post_title.setter
    def test_post_title(self, value):
        """Set the test post title."""
        self._test_post_title = value
        
    @property
    def test_page_title(self):
        """Get the test page title."""
        return self._test_page_title
    
    @test_page_title.setter
    def test_page_title(self, value):
        """Set the test page title."""
        self._test_page_title = value
        
    @property
    def test_content(self):
        """Get the test content."""
        return self._test_content
    
    @test_content.setter
    def test_content(self, value):
        """Set the test content."""
        self._test_content = value
