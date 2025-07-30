import argparse
import requests
import sys
import re
import json
import os
from datetime import datetime
from uuid import uuid4

HISTORY_FILE = "url_history.json"

def is_valid_url(url):
    """Validate if the input is a proper URL."""
    regex = re.compile(
        r'^(?:http|https)://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def load_history():
    """Load URL history from JSON file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(entry):
    """Save a new entry to the URL history."""
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def shorten_url(url):
    """Shorten a URL using the TinyURL API and save to history."""
    if not is_valid_url(url):
        print("Error: Invalid URL. Please provide a valid URL (e.g., https://www.google.com).")
        sys.exit(1)
    
    api = f"http://tinyurl.com/api-create.php?url={url}"
    try:
        response = requests.get(api, timeout=5)
        if response.status_code == 200:
            short_url = response.text
            timestamp = datetime.now().strftime("%B %d, %Y %I:%M:%S %p")
            entry = {
                "id": str(uuid4()),
                "original_url": url,
                "short_url": short_url,
                "timestamp": timestamp
            }
            save_history(entry)
            print("Shortened URL Details:")
            print(f"  ID:           {entry['id']}")
            print(f"  Original URL: {url}")
            print(f"  Short URL:    {short_url}")
            print(f"  Timestamp:    {timestamp}")
        else:
            print(f"Error: Failed to shorten URL (Status code: {response.status_code}).")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to TinyURL API. Details: {e}")
        sys.exit(1)

def show_info():
    """Display information about the URL Shortener CLI tool."""
    print("""
URL Shortener CLI Tool
A simple command-line tool to shorten URLs.
Version : 2.0.0
License: MIT
Features:
- Shorten URLs with detailed output (`shorten` command)
- Validate URLs without shortening (`validate` command)
- View history of shortened URLs (`history` command)
- Batch shorten URLs from a file (`batch` command)
Use `zap --help` for more details.
    """)

def show_version():
    """Display the version of the URL Shortener CLI tool."""
    print("URL Shortener CLI Tool, version 2.0.0")

def show_history():
    """Display the history of shortened URLs."""
    history = load_history()
    if not history:
        print("No URL shortening history found.")
        return
    print("URL Shortening History:")
    for entry in history:
        print(f"  ID:           {entry['id']}")
        print(f"  Original URL: {entry['original_url']}")
        print(f"  Short URL:    {entry['short_url']}")
        print(f"  Timestamp:    {entry['timestamp']}")
        print("-" * 40)

def validate_url(url):
    """Validate a URL without shortening it."""
    if is_valid_url(url):
        print(f"URL is valid: {url}")
    else:
        print(f"URL is invalid: {url}")
        sys.exit(1)

def batch_shorten(file_path):
    """Shorten multiple URLs from a text file."""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    output_file = f"shortened_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(file_path, 'r') as f, open(output_file, 'w') as out:
        urls = [line.strip() for line in f if line.strip()]
        if not urls:
            print("Error: Input file is empty.")
            sys.exit(1)
        
        print(f"Processing {len(urls)} URLs...")
        for url in urls:
            if not is_valid_url(url):
                out.write(f"Invalid URL: {url}\n")
                continue
            try:
                api = f"http://tinyurl.com/api-create.php?url={url}"
                response = requests.get(api, timeout=5)
                if response.status_code == 200:
                    short_url = response.text
                    timestamp = datetime.now().strftime("%B %d, %Y %I:%M:%S %p")
                    entry = {
                        "id": str(uuid4()),
                        "original_url": url,
                        "short_url": short_url,
                        "timestamp": timestamp
                    }
                    save_history(entry)
                    out.write(f"Original: {url}, Short: {short_url}, Timestamp: {timestamp}\n")
                    print(f"Shortened: {url} -> {short_url}")
                else:
                    out.write(f"Failed to shorten: {url} (Status code: {response.status_code})\n")
            except requests.exceptions.RequestException as e:
                out.write(f"Failed to shorten: {url} (Error: {e})\n")
        print(f"Results saved to {output_file}")

class CustomHelpFormatter(argparse.HelpFormatter):
    """Custom formatter to show examples only for --help."""
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = "usage: "
        return super(CustomHelpFormatter, self).add_usage(usage, actions, groups, prefix)

    def format_help(self):
        help_text = super(CustomHelpFormatter, self).format_help()
        if '--help' in sys.argv or '-h' in sys.argv:
            help_text += """
Use Cases:
  zap shorten https://www.google.com    # Shorten a URL
  zap validate https://x.com           # Validate a URL
  zap history                          # View shortening history
  zap batch urls.txt                   # Shorten URLs from a file
  zap info                             # Show tool information
  zap version                          # Show tool version
"""
        return help_text

def main():
    parser = argparse.ArgumentParser(
        description="URL Shortener CLI Tool (Powered by TinyURL)",
        usage="%(prog)s <command> [options]",
        formatter_class=CustomHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Shorten command
    parser_shorten = subparsers.add_parser("shorten", help="Shorten a URL", description="Shorten a valid URL using TinyURL API. Example: zap shorten https://www.google.com")
    parser_shorten.add_argument("url", help="The URL to shorten (e.g., https://www.google.com)")

    # Info command
    subparsers.add_parser("info", help="Display information about the tool", description="Show details about the tool, including author and features. Example: zap info")

    # Version command
    subparsers.add_parser("version", help="Display the tool version", description="Show the current version of the tool. Example: zap version")

    # History command
    subparsers.add_parser("history", help="Display history of shortened URLs", description="Show previously shortened URLs with details. Example: zap history")

    # Validate command
    parser_validate = subparsers.add_parser("validate", help="Validate a URL without shortening", description="Check if a URL is valid. Example: zap validate https://x.com")
    parser_validate.add_argument("url", help="The URL to validate (e.g., https://x.com)")

    # Batch command
    parser_batch = subparsers.add_parser("batch", help="Shorten multiple URLs from a file", description="Shorten URLs listed in a text file (one per line). Example: zap batch urls.txt")
    parser_batch.add_argument("file", help="Path to a text file containing URLs (one per line)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "shorten":
        shorten_url(args.url)
    elif args.command == "info":
        show_info()
    elif args.command == "version":
        show_version()
    elif args.command == "history":
        show_history()
    elif args.command == "validate":
        validate_url(args.url)
    elif args.command == "batch":
        batch_shorten(args.file)

if __name__ == "__main__":
    main()