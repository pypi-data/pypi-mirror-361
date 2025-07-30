from blogger_api_cli.api import blogger_api_request
from blogger_api_cli.config import BloggerConfig
from blogger_api_cli.test_config import TestConfig


def permission_test(config=None, test_config=None):
    """
    Test the Blogger API permissions by making various requests to test API key permissions.
    
    Args:
        config (BloggerConfig, optional): Configuration object with Blogger settings.
                                         If not provided, a new one will be created.
        test_config (TestConfig, optional): Configuration with test-specific IDs.
                                           If not provided, a new one will be created.
    """
    if config is None:
        config = BloggerConfig()
    
    if test_config is None:
        test_config = TestConfig()
    
    BLOG_ID = config.blog_id
    POST_ID = test_config.post_id
    BASE_URL = config.base_url
    
    # --- Test Cases ---

    # 1. Test POST request (Create a new post - usually requires OAuth 2.0)
    # Note: For a real POST, you'd need a valid blog ID and content.
    # This will likely fail with an API key, confirming read-only nature.
    new_post_data = {
        "kind": "blogger#post",
        "blog": {
            "id": BLOG_ID
        },
        "title": "Test Post from API Key Script",
        "content": "This is a test post created using the API key testing script. "
                "It is expected to fail if the API key is read-only."
    }
    blogger_api_request('POST', f'{BASE_URL}/blogs/{BLOG_ID}/posts/', data=new_post_data)


    # 2. Test DELETE request (Delete an existing post - usually requires OAuth 2.0)
    # This will require a valid POST_ID and BLOG_ID and will likely fail.
    if POST_ID:
        blogger_api_request('DELETE', f'{BASE_URL}/blogs/{BLOG_ID}/posts/{POST_ID}')
    else:
        print("\nSkipping DELETE test: POST_ID is not configured.")
        print("-" * 30)


    # 3. Test PATCH request (Update an existing post partially - usually requires OAuth 2.0)
    # This will require a valid POST_ID and BLOG_ID and will likely fail.
    updated_post_data = {
        "title": "Updated Title from API Key Script",
        "content": "This post content has been updated via the PATCH method. "
                "It is expected to fail if the API key is read-only."
    }
    if POST_ID:
        blogger_api_request('PATCH', f'{BASE_URL}/blogs/{BLOG_ID}/posts/{POST_ID}', data=updated_post_data)
    else:
        print("\nSkipping PATCH test: POST_ID is not configured.")
        print("-" * 30)


    # 4. Test PUT request (Update an existing post completely - less common for posts, often overlaps with PATCH's use case)
    # Note: Blogger API primarily uses PATCH for updates. A PUT request might not be directly supported
    # for full resource replacement in the same way as PATCH. It's included for completeness.
    # This will require a valid POST_ID and BLOG_ID and will likely fail.
    put_post_data = {
        "kind": "blogger#post",
        "id": POST_ID, # ID is crucial for PUT/PATCH
        "blog": {
            "id": BLOG_ID
        },
        "title": "Completely Replaced Title from API Key Script",
        "content": "This post content has been completely replaced via the PUT method. "
                "It is expected to fail if the API key is read-only or if PUT is not fully supported."
    }
    if POST_ID:
        blogger_api_request('PUT', f'{BASE_URL}/blogs/{BLOG_ID}/posts/{POST_ID}', data=put_post_data)
    else:
        print("\nSkipping PUT test: POST_ID is not configured.")
        print("-" * 30)
