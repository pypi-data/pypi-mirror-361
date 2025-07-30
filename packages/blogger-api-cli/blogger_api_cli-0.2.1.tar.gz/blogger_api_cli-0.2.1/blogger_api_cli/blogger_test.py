"""
Test module for the Blogger API functionality.
This module provides functions to test the Blogger API by making GET requests to various endpoints.
"""

from typing import Optional
from blogger_api_cli.api import get_request
from blogger_api_cli.config import BloggerConfig
from blogger_api_cli.test_config import TestConfig


def blogger_test(config: Optional[BloggerConfig] = None, test_config: Optional[TestConfig] = None) -> bool:
    """
    Test the Blogger API by making GET requests to various endpoints.
    
    Args:
        config (BloggerConfig, optional): Configuration object with Blogger settings.
                                         If not provided, a new one will be created.
        test_config (TestConfig, optional): Configuration with test-specific IDs.
                                           If not provided, a new one will be created.
    
    Returns:
        bool: True if all tests that could be run were successful, False otherwise.
    """
    if config is None:
        config = BloggerConfig()
    
    if test_config is None:
        test_config = TestConfig()
    
    BLOG_ID = config.blog_id
    POST_ID = test_config.post_id
    USER_ID = config.user_id
    PAGE_ID = test_config.page_id
    BLOG_URL = config.blog_url
    BASE_URL = config.base_url
    
    # Track test results
    all_tests_successful = True
    tests_run = 0
    
    # --- Test Cases for GET Requests ---
    print("\n=== Running Blogger API Tests ===")

    # 1. Test GET request: Get a specific blog by ID
    if BLOG_ID:
        print("\nTest 1: Get Blog by ID")
        response = get_request(f'{BASE_URL}/blogs/{BLOG_ID}')
        tests_run += 1
        if not response or response.status_code != 200:
            all_tests_successful = False
    else:
        print("\nSkipping Test 1 (Get Blog by ID): BLOG_ID is not configured.")
        print("-" * 30)

    # 2. Test GET request: Get a blog by URL
    if BLOG_URL:
        print("\nTest 2: Get Blog by URL")
        response = get_request(f'{BASE_URL}/blogs/byurl', params={'url': BLOG_URL})
        tests_run += 1
        if not response or response.status_code != 200:
            all_tests_successful = False
    else:
        print("\nSkipping Test 2 (Get Blog by URL): BLOG_URL is not configured.")
        print("-" * 30)

    # 3. Test GET request: List blogs by user (e.g., 'self')
    # Note: Listing user-specific blogs might require OAuth for non-public blogs,
    # even with a GET request.
    if USER_ID:
        print("\nTest 3: List Blogs by User")
        response = get_request(f'{BASE_URL}/users/{USER_ID}/blogs')
        tests_run += 1
        if not response or response.status_code != 200:
            all_tests_successful = False
    else:
        print("\nSkipping Test 3 (List Blogs by User): USER_ID is not configured.")
        print("-" * 30)

    # 4. Test GET request: List posts from a specific blog
    if BLOG_ID:
        print("\nTest 4: List Posts")
        response = get_request(f'{BASE_URL}/blogs/{BLOG_ID}/posts')
        tests_run += 1
        if not response or response.status_code != 200:
            all_tests_successful = False
    else:
        print("\nSkipping Test 4 (List Posts): BLOG_ID is not configured.")
        print("-" * 30)

    # 5. Test GET request: Get a specific post by ID
    if BLOG_ID and POST_ID:
        print("\nTest 5: Get Specific Post by ID")
        response = get_request(f'{BASE_URL}/blogs/{BLOG_ID}/posts/{POST_ID}')
        tests_run += 1
        if not response or response.status_code != 200:
            all_tests_successful = False
    else:
        print("\nSkipping Test 5 (Get Specific Post by ID): BLOG_ID or POST_ID is not configured.")
        print("-" * 30)

    # 6. Test GET request: Search for posts within a blog (example search term)
    if BLOG_ID:
        print("\nTest 6: Search Posts")
        response = get_request(f'{BASE_URL}/blogs/{BLOG_ID}/posts/search', params={'q': 'test'})
        tests_run += 1
        if not response or response.status_code != 200:
            all_tests_successful = False
    else:
        print("\nSkipping Test 6 (Search Posts): BLOG_ID is not configured.")
        print("-" * 30)

    # 7. Test GET request: List pages from a specific blog
    if BLOG_ID:
        print("\nTest 7: List Pages")
        response = get_request(f'{BASE_URL}/blogs/{BLOG_ID}/pages')
        tests_run += 1
        if not response or response.status_code != 200:
            all_tests_successful = False
    else:
        print("\nSkipping Test 7 (List Pages): BLOG_ID is not configured.")
        print("-" * 30)

    # 8. Test GET request: Get a specific page by ID
    if BLOG_ID and PAGE_ID:
        print("\nTest 8: Get Specific Page by ID")
        response = get_request(f'{BASE_URL}/blogs/{BLOG_ID}/pages/{PAGE_ID}')
        tests_run += 1
        if not response or response.status_code != 200:
            all_tests_successful = False
    else:
        print("\nSkipping Test 8 (Get Specific Page by ID): BLOG_ID or PAGE_ID is not configured.")
        print("-" * 30)
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Tests run: {tests_run}")
    print(f"Result: {'All tests successful' if all_tests_successful else 'Some tests failed'}")
    
    return all_tests_successful