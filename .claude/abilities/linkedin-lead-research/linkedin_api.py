#!/usr/bin/env python3
"""
LinkedIn API Helper for Claude Code Skill
Self-contained LinkedIn profile enrichment tool.
Wraps the RapidAPI professional-network-data endpoints for easy use.
"""

import os
import sys
import json
import time
import random
import re
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone

import requests

# API Configuration
RAPIDAPI_HOST = "professional-network-data.p.rapidapi.com"
RAPIDAPI_BASE_URL = f"https://{RAPIDAPI_HOST}"

# Skill directory (where this script is located)
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE_PATH = os.path.join(SKILL_DIR, ".env")


def get_api_key() -> str:
    """Get RapidAPI key from environment or local .env file."""
    # First check environment variable
    env_key = os.environ.get("RAPIDAPI_KEY")
    if env_key:
        return env_key

    # Try to load from skill's local .env file
    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('RAPIDAPI_KEY='):
                    key = line.split('=', 1)[1].strip()
                    # Remove quotes if present
                    key = key.strip('"').strip("'")
                    if key:
                        return key

    # Fallback to hardcoded key
    return "a45f6d315fmsh9421f84897ba7ddp15659fjsn3eb60906b0db"


def extract_username_from_url(url: str) -> Optional[str]:
    """Extract LinkedIn username from profile URL.

    Args:
        url: LinkedIn profile URL (e.g., https://www.linkedin.com/in/username/)

    Returns:
        Username string or None if not found
    """
    if not url:
        return None
    url = url.strip()
    if not url:
        return None

    # Remove query params and fragments
    cleaned = re.sub(r"[?#].*$", "", url)
    match = re.search(r"/in/([^/]+)", cleaned)
    if match:
        username = match.group(1).strip()
        return username or None
    return None


class LinkedInAPI:
    """LinkedIn API client using RapidAPI professional-network-data."""

    def __init__(self, api_key: Optional[str] = None, sleep_between_requests: float = 0.3, max_retries: int = 5):
        """Initialize API client.

        Args:
            api_key: RapidAPI key (defaults to reading from env/config)
            sleep_between_requests: Delay between requests in seconds
            max_retries: Maximum retry attempts for failed requests
        """
        self.api_key = api_key or get_api_key()
        self.host = RAPIDAPI_HOST
        self.base_url = RAPIDAPI_BASE_URL
        self.sleep_between_requests = sleep_between_requests
        self.max_retries = max_retries

    def _headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "x-rapidapi-host": self.host,
            "x-rapidapi-key": self.api_key,
        }

    def _request_with_backoff(self, path: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make API request with exponential backoff retry logic.

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            Response data as dict or None on failure
        """
        url = f"{self.base_url}{path}"
        username = params.get('username', 'unknown')
        attempt = 0

        while True:
            attempt += 1
            try:
                resp = requests.get(url, headers=self._headers(), params=params, timeout=30)
            except requests.RequestException as e:
                if attempt >= self.max_retries:
                    print(f"Request failed for {username} at {path}: {e}", file=sys.stderr)
                    return None
                backoff = (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                time.sleep(backoff)
                continue

            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if isinstance(data, dict) and not data:
                        print(f"Empty response for {username} at {path}", file=sys.stderr)
                except ValueError as e:
                    print(f"Invalid JSON for {username} at {path}: {e}", file=sys.stderr)
                    data = None
                time.sleep(self.sleep_between_requests)
                return data

            if resp.status_code in (429, 500, 502, 503, 504):
                if attempt >= self.max_retries:
                    print(f"Max retries reached for {username} at {path} (status {resp.status_code})", file=sys.stderr)
                    return None
                retry_after = resp.headers.get("Retry-After")
                if retry_after:
                    try:
                        delay = float(retry_after)
                    except ValueError:
                        delay = (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                else:
                    delay = (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                time.sleep(delay)
                continue

            print(f"Unexpected status {resp.status_code} for {username} at {path}", file=sys.stderr)
            return None

    def get_profile_basic(self, username: str) -> Optional[Dict[str, Any]]:
        """Get basic profile information.

        Args:
            username: LinkedIn username

        Returns:
            Profile data including name, headline, location, summary
        """
        return self._request_with_backoff(path="/", params={"username": username})

    def get_recent_activity_time(self, username: str) -> Optional[Dict[str, Any]]:
        """Get recent activity timestamp.

        Args:
            username: LinkedIn username

        Returns:
            Recent activity data with timestamp
        """
        return self._request_with_backoff(
            path="/get-profile-recent-activity-time",
            params={"username": username}
        )

    def get_top_position(self, username: str) -> Optional[Dict[str, Any]]:
        """Get current/top position.

        Args:
            username: LinkedIn username

        Returns:
            Position data with title, company, dates
        """
        return self._request_with_backoff(
            path="/profiles/positions/top",
            params={"username": username}
        )

    def get_profile_posts(self, username: str, start: int = 0, posted_after: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get user posts.

        Args:
            username: LinkedIn username
            start: Pagination offset (0, 50, 100, etc.)
            posted_after: Filter posts after this date (format: YYYY-MM-DD HH:MM:SS)

        Returns:
            Posts data with text, dates, engagement metrics
        """
        params = {"username": username, "start": start}
        if posted_after:
            params["postedAt"] = posted_after
        return self._request_with_backoff(
            path="/get-profile-posts",
            params=params
        )

    def get_profile_comments(self, username: str) -> Optional[Dict[str, Any]]:
        """Get profile comments.

        Args:
            username: LinkedIn username

        Returns:
            Comments data with text, dates, post URLs
        """
        return self._request_with_backoff(
            path="/get-profile-comments",
            params={"username": username}
        )

    def enrich_profile(self, username: str, recent_days: int = 30) -> Dict[str, Any]:
        """Enrich profile with all available data.

        Args:
            username: LinkedIn username
            recent_days: Number of days to look back for recent activity

        Returns:
            Comprehensive profile data
        """
        # Get all data
        profile = self.get_profile_basic(username)
        activity = self.get_recent_activity_time(username)
        position = self.get_top_position(username)

        # Calculate date filter for posts
        posted_after = (datetime.now(timezone.utc) - timedelta(days=recent_days)).strftime("%Y-%m-%d %H:%M:%S")
        posts = self.get_profile_posts(username, start=0, posted_after=posted_after)
        comments = self.get_profile_comments(username)

        # Structure the result
        result = {
            "username": username,
            "fetchedAt": datetime.now(timezone.utc).isoformat(),
            "basic_profile": self._extract_basic_fields(profile) if profile else {},
            "top_position": self._extract_top_position(position) if position else {},
            "recent_activity": self._extract_activity(activity) if activity else {},
            "recent_posts": self._extract_posts(posts, recent_days) if posts else [],
            "recent_comments": self._extract_comments(comments, recent_days) if comments else [],
        }

        return result

    def _extract_basic_fields(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize basic profile fields."""
        if not profile:
            return {}

        fields_map = {
            "username": ["username", "publicId", "public_id", "vanityName"],
            "full_name": ["fullName", "name", "formattedName", "firstName", "lastName"],
            "first_name": ["firstName"],
            "last_name": ["lastName"],
            "headline": ["headline"],
            "location": ["location", "locationName"],
            "profile_url": ["publicProfileUrl", "url", "profileUrl"],
            "summary": ["summary", "about", "description"],
        }

        result = {}
        for out_key, in_keys in fields_map.items():
            for k in in_keys:
                if k in profile and profile[k] not in (None, ""):
                    result[out_key] = profile[k]
                    break

        # Handle geo data
        if "geo" in profile and isinstance(profile["geo"], dict):
            geo = profile["geo"]
            if geo.get("full"):
                result["location"] = geo["full"]
            elif geo.get("city") and geo.get("country"):
                result["location"] = f"{geo['city']}, {geo['country']}"
            result["geo"] = geo

        return result

    def _extract_top_position(self, position_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Extract top position information."""
        if not position_data:
            return None

        # Handle wrapped responses
        for key in ("data", "result", "topPosition", "position"):
            if key in position_data:
                position_data = position_data[key]
                break

        if isinstance(position_data, list) and position_data:
            position_data = position_data[0]

        if isinstance(position_data, dict):
            fields = ["title", "company", "companyName", "location", "startDate", "endDate", "isCurrent"]
            filtered = {k: position_data.get(k) for k in fields if k in position_data}
            if "companyName" in filtered and "company" not in filtered:
                filtered["company"] = filtered.pop("companyName")
            return filtered

        return None

    def _extract_activity(self, activity_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract activity timestamp."""
        if not activity_data:
            return {}

        if activity_data.get("success") and activity_data.get("data"):
            data = activity_data["data"]
            if data.get("timestamp"):
                return {"last_active": data["timestamp"]}
            elif data.get("date"):
                return {"last_active": data["date"]}

        return {}

    def _extract_posts(self, posts_data: Optional[Dict[str, Any]], recent_days: int) -> list:
        """Extract posts from API response."""
        if not posts_data:
            return []

        candidates = []
        if isinstance(posts_data, list):
            candidates = posts_data
        elif isinstance(posts_data, dict):
            if posts_data.get("success") and "data" in posts_data:
                data = posts_data["data"]
                candidates = data if isinstance(data, list) else data.get("posts", [])
            else:
                for key in ("posts", "data", "items"):
                    if isinstance(posts_data.get(key), list):
                        candidates = posts_data[key]
                        break

        posts = []
        for item in candidates:
            if isinstance(item, dict):
                posts.append({
                    "text": item.get("text", ""),
                    "createdAt": item.get("postedDate", item.get("createdAt", "")),
                    "url": item.get("url", ""),
                    "likeCount": item.get("likeCount", 0),
                    "commentCount": item.get("commentCount", 0),
                })

        return posts

    def _extract_comments(self, comments_data: Optional[Dict[str, Any]], recent_days: int) -> list:
        """Extract comments from API response."""
        if not comments_data:
            return []

        candidates = []
        if isinstance(comments_data, list):
            candidates = comments_data
        elif isinstance(comments_data, dict):
            if comments_data.get("success") and "data" in comments_data:
                data = comments_data["data"]
                candidates = data if isinstance(data, list) else data.get("comments", [])
            else:
                for key in ("comments", "data", "items"):
                    if isinstance(comments_data.get(key), list):
                        candidates = comments_data[key]
                        break

        comments = []
        for item in candidates:
            if isinstance(item, dict):
                comments.append({
                    "text": item.get("text", ""),
                    "createdAt": item.get("commentedDate", item.get("createdAt", "")),
                    "postUrl": item.get("postUrl", ""),
                })

        return comments


def main():
    """CLI interface for the LinkedIn API."""
    if len(sys.argv) < 2:
        print("Usage: linkedin_api.py <command> [args...]")
        print("\nCommands:")
        print("  profile <username>           - Get basic profile")
        print("  activity <username>          - Get recent activity")
        print("  position <username>          - Get top position")
        print("  posts <username> [days]      - Get recent posts")
        print("  comments <username>          - Get recent comments")
        print("  enrich <username> [days]     - Get all data (default 30 days)")
        print("  extract-username <url>       - Extract username from LinkedIn URL")
        sys.exit(1)

    command = sys.argv[1]
    api = LinkedInAPI()

    if command == "extract-username":
        if len(sys.argv) < 3:
            print("Error: URL required", file=sys.stderr)
            sys.exit(1)
        username = extract_username_from_url(sys.argv[2])
        print(json.dumps({"username": username}, indent=2))

    elif command == "profile":
        if len(sys.argv) < 3:
            print("Error: Username required", file=sys.stderr)
            sys.exit(1)
        result = api.get_profile_basic(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == "activity":
        if len(sys.argv) < 3:
            print("Error: Username required", file=sys.stderr)
            sys.exit(1)
        result = api.get_recent_activity_time(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == "position":
        if len(sys.argv) < 3:
            print("Error: Username required", file=sys.stderr)
            sys.exit(1)
        result = api.get_top_position(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == "posts":
        if len(sys.argv) < 3:
            print("Error: Username required", file=sys.stderr)
            sys.exit(1)
        username = sys.argv[2]
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        posted_after = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        result = api.get_profile_posts(username, start=0, posted_after=posted_after)
        print(json.dumps(result, indent=2))

    elif command == "comments":
        if len(sys.argv) < 3:
            print("Error: Username required", file=sys.stderr)
            sys.exit(1)
        result = api.get_profile_comments(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == "enrich":
        if len(sys.argv) < 3:
            print("Error: Username required", file=sys.stderr)
            sys.exit(1)
        username = sys.argv[2]
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        result = api.enrich_profile(username, recent_days=days)
        print(json.dumps(result, indent=2))

    else:
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
