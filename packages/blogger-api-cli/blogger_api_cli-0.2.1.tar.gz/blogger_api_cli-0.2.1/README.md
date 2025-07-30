# Blogger CLI

A command-line interface for interacting with the Blogger API. This tool allows you to fetch posts, pages, and other data from your Blogger blog using Google's official API.

## Features
- Fetch posts and pages from your Blogger blog
- Export data to JSON
- Run tests to verify API access and configuration

## Getting Started

### 1. Create `config.json`
The CLI requires a `config.json` file for authentication and configuration. Create it according to the following structure:

```json
{
  "api_key": "YOUR_GOOGLE_API_KEY",
  "blog_id": "YOUR_BLOG_ID",
  "base_url": "https://www.googleapis.com/blogger/v3",
  "user_id": "self",
  "blog_url": "https://yourblog.blogspot.com/"
}
```
- `api_key`: Your Google API key (see below for instructions)
- `blog_id`: The numeric ID of your Blogger blog. To find your blog ID:
  1. Go to [Blogger](https://www.blogger.com/) and sign in.
  2. Select your blog.
  3. Look at the URL in your browser's address bar. It will look like:
     `https://www.blogger.com/blog/posts/XXXXXXXXXXXXXXX`
     The long number (XXXXXXXXXXXXXXX) is your blog ID.
  4. Alternatively, you can find your blog ID in the Blogger dashboard under **Settings > Basic > Blog ID**.
- `base_url`: (optional) The Blogger API base URL, usually `https://www.googleapis.com/blogger/v3`
- `user_id`: (optional) Use `self` for accessing your own blog
- `blog_url`: (optional) The public URL of your blog

### 2. How to Get a Google API Key
To use the Blogger CLI, you need a Google API key with access to the Blogger API. Follow these steps:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one).
3. In the left sidebar, navigate to **APIs & Services > Library**.
4. Search for "Blogger API v3" and click **Enable**.
5. Go to **APIs & Services > Credentials**.
6. Click **Create credentials** and select **API key**.
7. Copy the generated API key.
8. Paste the API key into your `config.json` file under the `api_key` field.

You may restrict the API key to specific referrers or IP addresses for security, but for development, you can leave it unrestricted. Make sure the API key is enabled for the Blogger API in your project.

> **Note:** The API key provided in this project is approved for **read-only** access. You can only fetch data, not modify it. For write access, you must request additional permissions from Google.

### 3. Usage
Run the CLI using:

```powershell
python -m blogger_api_cli [OPTIONS]
```

#### Main Options

- `-b`, `--blogger` : Run Blogger API test
- `-p`, `--permission` : Run Blogger API permission test
- `-x`, `--xml-to-json` : Convert XML blog backup entries to JSON
- `--export-posts` : Export posts via Blogger API
- `--export-pages` : Export pages via Blogger API
- `--search QUERY` : Search for posts in the blog
- `--get-blog` : Retrieve blog information using ID/URL from config.json

#### Additional Arguments

- `--post-id`, `--pid` : Post ID for testing
- `--page-id`, `--pgid` : Page ID for testing
- `-c`, `--comment-id` : Comment ID for testing
- `-u`, `--user-id` : User ID for testing
- `--test-post-title`, `-pt` : Title for test posts (default: "Test Post")
- `--test-page-title`, `-pg` : Title for test pages (default: "Test Page")
- `-t`, `--test-content` : Content for test posts/pages (default: "This is test content")

- `-f`, `--xml-file` : Path to the XML blog backup file (required for XML to JSON conversion)
- `--posts-json`, `-pj` : Path to save posts JSON
- `--pages-json`, `-gj` : Path to save pages JSON
- `--config-file`, `-cf` : Path to the config file
- `-o`, `--output` : Path to save the exported data

- `--max-results` : Maximum number of results to return for search (default: 10)
- `--include-drafts`, `-d` : Include draft posts and pages in the JSON output (for XML to JSON)

#### Example Commands

- Run Blogger API test:
  ```powershell
  python -m blogger_api_cli -b
  ```
- Run permission test:
  ```powershell
  python -m blogger_api_cli -p
  ```
- Convert XML to JSON:
  ```powershell
  python -m blogger_api_cli -x -f path/to/blog-export.xml --include-drafts
  ```
- Export posts:
  ```powershell
  python -m blogger_api_cli --export-posts -o my-posts.json
  ```
- Search for posts:
  ```powershell
  python -m blogger_api_cli --search "query" --max-results 20
  ```
- Get blog info:
  ```powershell
  python -m blogger_api_cli --get-blog -o blog-info.json
  ```

Refer to the code or use `--help` for more details on all options.

## Troubleshooting
- Ensure your `config.json` is present and correctly formatted
- Make sure your API key has access to the Blogger API
- For write access, you must request additional permissions from Google

## License
MIT
