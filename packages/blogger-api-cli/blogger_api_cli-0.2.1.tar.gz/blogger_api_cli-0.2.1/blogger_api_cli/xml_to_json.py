import xml.etree.ElementTree as ET
import os
import json

def xml_entries_to_json(xml_path, posts_json_path, pages_json_path, include_drafts=False):
    """
    Extracts <entry> elements from the XML, splits them into posts and pages by <category term>,
    and writes two JSON files with arrays of objects.
    
    Args:
        xml_path (str): Path to the XML blog backup file
        posts_json_path (str): Path to save posts JSON
        pages_json_path (str): Path to save pages JSON
        include_drafts (bool): Whether to include draft posts and pages (default: False)
    """
    if not os.path.exists(xml_path):
        print(f"File not found: {xml_path}")
        return
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    posts = []
    pages = []
    draft_posts = []
    draft_pages = []

    for entry in root.findall('atom:entry', ns):
        # Check if entry is a draft
        is_draft = False
        app_control = entry.find('{http://purl.org/atom/app#}control')
        if app_control is not None:
            app_draft = app_control.find('{http://purl.org/atom/app#}draft')
            if app_draft is not None and app_draft.text and app_draft.text.strip().lower() == 'yes':
                is_draft = True
                if not include_drafts:
                    continue

        entry_obj = {}
        # Basic fields with string handling
        for tag in ['id', 'title', 'content', 'published', 'updated']:
            el = entry.find(f'atom:{tag}', ns)
            if el is not None and el.text is not None:
                value = el.text
                if tag == 'id':
                    value = value.replace('\n', '').replace('\r', '').strip()
                else:
                    value = value.replace('\r\n', '\n').replace('\r', '\n')
                entry_obj[tag] = value
            else:
                entry_obj[tag] = None
        # Categories: check all for kind#post or kind#page
        categories = entry.findall('atom:category', ns)
        terms = [cat.attrib.get('term', '') for cat in categories]
        # Exclude kind#post and kind#page from categories
        non_kind_categories = [
            cat.attrib for cat in categories
            if not (cat.attrib.get('term', '').startswith('http://schemas.google.com/blogger/2008/kind#'))
        ]
        entry_obj['categories'] = non_kind_categories
        # category_term removed as requested
        # Links
        entry_obj['links'] = [
            {k: v for k, v in link.attrib.items()}
            for link in entry.findall('atom:link', ns)
        ]
        # Author
        author = entry.find('atom:author', ns)
        if author is not None:
            entry_obj['author'] = {child.tag.split('}')[-1]: child.text for child in author}
        else:
            entry_obj['author'] = None
        # Add draft status to entry object
        entry_obj['draft'] = is_draft
        
        # Sort into posts/pages
        if any('kind#post' in t for t in terms):
            if is_draft and include_drafts:
                draft_posts.append(entry_obj)
            elif not is_draft:
                posts.append(entry_obj)
        elif any('kind#page' in t for t in terms):
            if is_draft and include_drafts:
                draft_pages.append(entry_obj)
            elif not is_draft:
                pages.append(entry_obj)

    # Combine published and draft entries if include_drafts is True
    if include_drafts:
        total_posts = posts + draft_posts
        total_pages = pages + draft_pages
    else:
        total_posts = posts
        total_pages = pages

    # Write JSON files
    with open(posts_json_path, 'w', encoding='utf-8') as f:
        json.dump(total_posts, f, ensure_ascii=False, indent=2)
    with open(pages_json_path, 'w', encoding='utf-8') as f:
        json.dump(total_pages, f, ensure_ascii=False, indent=2)
    
    # Generate summary messages
    if include_drafts:
        print(f"Wrote {len(posts)} published posts and {len(draft_posts)} draft posts to {posts_json_path}")
        print(f"Wrote {len(pages)} published pages and {len(draft_pages)} draft pages to {pages_json_path}")
    else:
        print(f"Wrote {len(posts)} published posts to {posts_json_path}")
        print(f"Wrote {len(pages)} published pages to {pages_json_path}")
