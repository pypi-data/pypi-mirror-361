"""
API operations for exporting posts and pages, searching posts, and retrieving blog information.
This module provides functions to export blog posts and pages via API,
search for posts within a blog, and retrieve blog information by ID or URL.
"""

import json
import os
from typing import Optional, Dict, Any, Union
from blogger_api_cli.api import get_request
from blogger_api_cli.config import BloggerConfig


def export_posts(config: BloggerConfig, output_path: Optional[str] = None) -> bool:
    """
    Export all posts from a blog via the Blogger API and save them to a JSON file.
    
    Args:
        config (BloggerConfig): Configuration object with Blogger settings.
        output_path (str, optional): Path to save the posts JSON file.
                                    If not provided, it will use a default path.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    blog_id = config.blog_id
    base_url = config.base_url
    
    if not blog_id:
        print("\nError: BLOG_ID is not configured.")
        return False
    
    # Set default output path if not provided
    if output_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(base_dir, "data", "posts.json")
    
    # Create directory if it doesn't exist
    dir_path = os.path.dirname(output_path)
    if dir_path:  # Only try to create directory if the path is not empty
        os.makedirs(dir_path, exist_ok=True)
    else:
        # Use current directory if no directory specified
        output_path = os.path.join(os.getcwd(), os.path.basename(output_path))
        print(f"No directory specified, using current directory: {os.getcwd()}")
    
    print(f"\nExporting posts from blog ID: {blog_id}")
    print(f"Output will be saved to: {output_path}")
    
    # Get all posts from the blog
    response = get_request(f'{base_url}/blogs/{blog_id}/posts', params={'maxResults': 500})
    
    if response and response.status_code == 200:
        # Process and save the response
        data = response.json()
        
        # Save the raw response
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        post_count = len(data.get('items', []))
        print(f"Successfully exported {post_count} posts to {output_path}")
        return True
    else:
        print("Failed to export posts")
        return False


def export_pages(config: BloggerConfig, output_path: Optional[str] = None) -> bool:
    """
    Export all pages from a blog via the Blogger API and save them to a JSON file.
    
    Args:
        config (BloggerConfig): Configuration object with Blogger settings.
        output_path (str, optional): Path to save the pages JSON file.
                                    If not provided, it will use a default path.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    blog_id = config.blog_id
    base_url = config.base_url
    
    if not blog_id:
        print("\nError: BLOG_ID is not configured.")
        return False
    
    # Set default output path if not provided
    if output_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(base_dir, "data", "pages.json")
    
    # Create directory if it doesn't exist
    dir_path = os.path.dirname(output_path)
    if dir_path:  # Only try to create directory if the path is not empty
        os.makedirs(dir_path, exist_ok=True)
    else:
        # Use current directory if no directory specified
        output_path = os.path.join(os.getcwd(), os.path.basename(output_path))
        print(f"No directory specified, using current directory: {os.getcwd()}")
    
    print(f"\nExporting pages from blog ID: {blog_id}")
    print(f"Output will be saved to: {output_path}")
    
    # Get all pages from the blog
    response = get_request(f'{base_url}/blogs/{blog_id}/pages', params={'maxResults': 500})
    
    if response and response.status_code == 200:
        # Process and save the response
        data = response.json()
        
        # Save the raw response
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        page_count = len(data.get('items', []))
        print(f"Successfully exported {page_count} pages to {output_path}")
        return True
    else:
        print("Failed to export pages")
        return False


def search_posts(config: BloggerConfig, search_query: str, max_results: int = 10) -> bool:
    """
    Search for posts within a blog using the Blogger API.
    
    Args:
        config (BloggerConfig): Configuration object with Blogger settings.
        search_query (str): The search query to look for in blog posts.
        max_results (int, optional): Maximum number of results to return. Default is 10.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    blog_id = config.blog_id
    base_url = config.base_url
    
    if not blog_id:
        print("\nError: BLOG_ID is not configured.")
        return False
    
    print(f"\nSearching posts in blog ID: {blog_id}")
    print(f"Search query: '{search_query}'")
    
    # Search for posts
    response = get_request(
        f'{base_url}/blogs/{blog_id}/posts/search',
        params={'q': search_query, 'maxResults': max_results}
    )
    
    if response and response.status_code == 200:
        data = response.json()
        posts = data.get('items', [])
        
        if not posts:
            print("No posts found matching the query.")
            return True
            
        print(f"Found {len(posts)} posts matching the query:")
        
        # Display search results in a readable format
        for i, post in enumerate(posts, 1):
            print(f"\n--- Result {i} ---")
            print(f"Title: {post.get('title', 'No title')}")
            print(f"URL: {post.get('url', 'No URL')}")
            print(f"Published: {post.get('published', 'Unknown date')}")
            
        return True
    else:
        print("Search failed or no results found")
        return False


def get_blog_info(config: BloggerConfig, output_path: Optional[str] = None) -> bool:
    """
    Retrieve blog information by ID or URL from the config file.
    
    Args:
        config (BloggerConfig): Configuration object with Blogger settings.
        output_path (str, optional): Path to save the blog info JSON file.
                                    If not provided, it will just display the information.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    base_url = config.base_url
    blog_id = config.blog_id
    blog_url = config.blog_url
    
    # Check if we have configuration for either blog ID or URL
    if not blog_id and not blog_url:
        print("\nError: Neither blog_id nor blog_url is configured in config.json.")
        print("Please update your config.json file with at least one of these values.")
        return False
    
    # Try using blog ID first (preferred method)
    if blog_id:
        print(f"\nRetrieving blog information for ID: {blog_id}")
        response = get_request(f'{base_url}/blogs/{blog_id}')
    else:
        # Fall back to blog URL if ID is not available
        print(f"\nRetrieving blog information for URL: {blog_url}")
        response = get_request(f'{base_url}/blogs/byurl', params={'url': blog_url})
    
    if response and response.status_code == 200:
        data = response.json()
        
        # Display blog information
        print("\n=== Blog Information ===")
        print(f"Name: {data.get('name', 'N/A')}")
        print(f"Description: {data.get('description', 'N/A')}")
        print(f"URL: {data.get('url', 'N/A')}")
        print(f"Kind: {data.get('kind', 'N/A')}")
        print(f"ID: {data.get('id', 'N/A')}")
        print(f"Published: {data.get('published', 'N/A')}")
        print(f"Updated: {data.get('updated', 'N/A')}")
        
        # Additional information if available
        if 'posts' in data:
            posts_info = data['posts']
            print(f"Total Posts: {posts_info.get('totalItems', 'N/A')}")
        
        if 'pages' in data:
            pages_info = data['pages']
            print(f"Total Pages: {pages_info.get('totalItems', 'N/A')}")
        
        # Save to file if output path is provided
        if output_path:
            try:
                dir_path = os.path.dirname(os.path.abspath(output_path))
                if dir_path:  # Only try to create directory if the path is not empty
                    os.makedirs(dir_path, exist_ok=True)
                else:
                    # Use current directory if no directory specified
                    output_path = os.path.join(os.getcwd(), os.path.basename(output_path))
                    print(f"No directory specified, using current directory: {os.getcwd()}")
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                print(f"\nBlog information saved to: {output_path}")
            except Exception as e:
                print(f"\nError saving blog information to file: {e}")
                return False
        
        return True
    else:
        print("Failed to retrieve blog information")
        return False
