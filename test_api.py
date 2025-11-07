#!/usr/bin/env python3
"""Test script for Demo Forums API"""
import json
import urllib.request
from urllib.error import HTTPError


BASE_URL = "http://localhost:8000"


def make_request(method, url, data=None, headers=None):
    """Make HTTP request"""
    if headers is None:
        headers = {}

    if data is not None:
        data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))


print("=" * 60)
print("Testing Demo Forums API")
print("=" * 60)

# Test 1: Health check
print("\n1. Health Check")
status, data = make_request("GET", f"{BASE_URL}/")
print(f"Status: {status}")
print(f"Response: {data}")

# Test 2: Login
print("\n2. Login")
status, data = make_request(
    "POST",
    f"{BASE_URL}/api/auth/login",
    {"username": "admin", "password": "admin"}
)
print(f"Status: {status}")
print(f"Response: {data}")
token = data["authToken"]

# Test 3: Get Profile
print("\n3. Get Profile")
headers = {"Authorization": f"Bearer {token}"}
status, data = make_request("GET", f"{BASE_URL}/api/profile", headers=headers)
print(f"Status: {status}")
print(f"Response: {data}")

# Test 4: Get Forums
print("\n4. Get Forums")
status, forums = make_request("GET", f"{BASE_URL}/api/forums", headers=headers)
print(f"Status: {status}")
print(f"Found {len(forums)} forums")
print(f"First forum: {forums[0]['title']}")

# Test 5: Get Posts (web-development)
print("\n5. Get Posts from web-development forum")
status, posts_data = make_request("GET", f"{BASE_URL}/api/forums/web-development/posts?page=1&pageSize=5", headers=headers)
print(f"Status: {status}")
print(f"Total posts: {posts_data['totalCount']}")
print(f"Total pages: {posts_data['totalPages']}")
print(f"Posts on this page: {len(posts_data['items'])}")
if posts_data['items']:
    print(f"First post: {posts_data['items'][0]['title']}")

# Test 6: Get single post
print("\n6. Get Single Post")
status, post = make_request("GET", f"{BASE_URL}/api/forums/web-development/posts/1", headers=headers)
print(f"Status: {status}")
print(f"Post title: {post['title']}")
print(f"Post number: {post['number']}")

# Test 7: Get Comments
print("\n7. Get Comments for Post #1")
status, comments = make_request("GET", f"{BASE_URL}/api/forums/web-development/posts/1/comments", headers=headers)
print(f"Status: {status}")
print(f"Found {len(comments)} comments")

# Test 8: Create Post
print("\n8. Create New Post")
status, new_post = make_request(
    "POST",
    f"{BASE_URL}/api/forums/web-development/posts",
    {
        "title": "Test Post from API",
        "content": "This is a test post created via the API",
        "tags": ["test", "api"]
    },
    headers
)
print(f"Status: {status}")
print(f"Created post #{new_post['number']}: {new_post['title']}")

# Test 9: Create Comment
print("\n9. Create Comment on New Post")
status, new_comment = make_request(
    "POST",
    f"{BASE_URL}/api/forums/web-development/posts/{new_post['number']}/comments",
    {"content": "This is a test comment"},
    headers
)
print(f"Status: {status}")
print(f"Created comment: {new_comment['content']}")

# Test 10: Get Users
print("\n10. Get All Users")
status, users = make_request("GET", f"{BASE_URL}/api/users", headers=headers)
print(f"Status: {status}")
print(f"Found {len(users)} users")
for user in users:
    print(f"  - {user['username']} ({user['role']})")

# Test 11: Logout
print("\n11. Logout")
status, data = make_request("POST", f"{BASE_URL}/api/auth/logout", headers=headers)
print(f"Status: {status}")
print(f"Response: {data}")

# Test 12: Try to access after logout
print("\n12. Try to Access After Logout")
status, data = make_request("GET", f"{BASE_URL}/api/profile", headers=headers)
print(f"Status: {status}")
print(f"Response: {data}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
