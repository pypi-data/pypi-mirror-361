import os
import sys
import argparse

from blogger_api_cli.config import BloggerConfig
from blogger_api_cli.test_config import TestConfig


def is_running_as_executable():
    """
    Detects if the application is running as a PyInstaller executable.
    
    Returns:
        bool: True if running as an executable, False if running as a Python module.
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def parse_arguments():
    """
    Parse command line arguments for the Blogger CLI tool.
    
    Returns:
        argparse.Namespace: The parsed command line arguments.
    """
    # Determine command prefix based on execution environment
    cmd_prefix = "blogger_api_cli.exe" if is_running_as_executable() else "python -m blogger_api_cli"
    
    # Create the epilog text with the appropriate command prefix
    epilog_text = f"""
Examples:
  {cmd_prefix} -b                              # Run Blogger API test
  {cmd_prefix} -b --post-id 123456789 --page-id 987654321  # Test with specific IDs
  {cmd_prefix} -p                              # Run permission test
  {cmd_prefix} -x -f path/to/blog-export.xml --include-drafts  # Convert XML to JSON
  {cmd_prefix} -x -f path/to/blog-export.xml -pj posts.json --gj pages.json
  {cmd_prefix} --export-posts -o my-posts.json  # Export posts via API
  {cmd_prefix} --export-pages -o my-pages.json  # Export pages via API
  {cmd_prefix} --search "query" --max-results 20  # Search for posts
  {cmd_prefix} --get-blog -o blog-info.json  # Get blog info using ID/URL from config.json
        """
    
    parser = argparse.ArgumentParser(
        description="Blogger CLI Tool - Command-line interface for working with the Blogger API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog_text
    )
    
    # Create a group for the different command modes
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('-b', '--blogger', action='store_true', help='Run Blogger API test')
    mode_group.add_argument('-p', '--permission', action='store_true', help='Run Blogger API permission test')
    mode_group.add_argument('-x', '--xml-to-json', action='store_true', help='Convert XML blog backup entries to JSON\'s')
    mode_group.add_argument('--export-posts', action='store_true', help='Export posts via Blogger API')
    mode_group.add_argument('--export-pages', action='store_true', help='Export pages via Blogger API')
    mode_group.add_argument('--search', metavar='QUERY', help='Search for posts in the blog')
    mode_group.add_argument('--get-blog', action='store_true', help='Retrieve blog information using ID/URL from config.json')
    
    # TestConfig parameters
    parser.add_argument('--post-id', '--pid', help='Post ID for testing')
    parser.add_argument('--page-id', '--pgid', help='Page ID for testing')
    parser.add_argument('-c', '--comment-id', default='', help='Comment ID for testing')
    parser.add_argument('-u', '--user-id', default='', help='User ID for testing')
    parser.add_argument('--test-post-title', '-pt', default='Test Post', help='Title for test posts')
    parser.add_argument('--test-page-title', '-pg', default='Test Page', help='Title for test pages')
    parser.add_argument('-t', '--test-content', default='This is test content', help='Content for test posts/pages')
    
    # File path parameters
    parser.add_argument('-f', '--xml-file', help='Path to the XML blog backup file (required for XML to JSON conversion)')
    parser.add_argument('--posts-json', '-pj', default=None, help='Path to save posts JSON')
    parser.add_argument('--pages-json', '-gj', default=None, help='Path to save pages JSON')
    parser.add_argument('--config-file', '-cf', default=None, help='Path to the config file')
    parser.add_argument('-o', '--output', help='Path to save the exported data')
    
    # Export and search parameters
    parser.add_argument('--max-results', type=int, default=10, help='Maximum number of results to return for search')
    
    # XML to JSON specific options
    parser.add_argument('--include-drafts', '-d', action='store_true', help='Include draft posts and pages in the JSON output')
    
    return parser.parse_args()


def main():
    """
    Main entry point for the Blogger CLI application.
    Parses command line arguments and executes the appropriate function.
    """
    args = parse_arguments()
    
    # Create config objects
    config = BloggerConfig(config_path=args.config_file)
    test_config = TestConfig(
        post_id=args.post_id,
        page_id=args.page_id,
        comment_id=args.comment_id,
        user_id=args.user_id,
        test_post_title=args.test_post_title,
        test_page_title=args.test_page_title,
        test_content=args.test_content
    )
    
    # Default file paths relative to the script
    base_dir = os.path.dirname(os.path.dirname(__file__))
    default_posts_json = os.path.join(base_dir, "data", "posts.json")
    default_pages_json = os.path.join(base_dir, "data", "pages.json")
    
    # Execute the appropriate function based on the command
    if args.blogger:
        from blogger_api_cli.blogger_test import blogger_test
        print("Running Blogger API test...")
        blogger_test(config, test_config)
        
    elif args.permission:
        from blogger_api_cli.permission_test import permission_test
        print("Running Blogger API permission test...")
        permission_test(config, test_config)
        
    elif args.xml_to_json:
        if not args.xml_file:
            print("Error: XML file path is required for XML to JSON conversion.")
            print("Use -f or --xml-file to specify the path to the XML blog backup file.")
            sys.exit(1)
            
        from blogger_api_cli.xml_to_json import xml_entries_to_json
        xml_path = args.xml_file
        posts_json = args.posts_json if args.posts_json else default_posts_json
        pages_json = args.pages_json if args.pages_json else default_pages_json
        print(f"Converting XML blog backup from {xml_path} to JSON...")
        if args.include_drafts:
            print("Including draft posts and pages in the output")
        xml_entries_to_json(xml_path, posts_json, pages_json, include_drafts=args.include_drafts)
    
    elif args.export_posts:
        from blogger_api_cli.export_search import export_posts
        print("Exporting posts via Blogger API...")
        export_posts(config, output_path=args.output)
    
    elif args.export_pages:
        from blogger_api_cli.export_search import export_pages
        print("Exporting pages via Blogger API...")
        export_pages(config, output_path=args.output)
    
    elif args.search:
        from blogger_api_cli.export_search import search_posts
        print(f"Searching for posts with query: {args.search}...")
        search_posts(config, args.search, max_results=args.max_results)
    
    elif args.get_blog:
        from blogger_api_cli.export_search import get_blog_info
        print("Retrieving blog information...")
        get_blog_info(config, output_path=args.output)


if __name__ == "__main__":
    main()
