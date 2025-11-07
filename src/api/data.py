import random
from datetime import UTC, datetime, timedelta

from .models import Comment, Forum, Post, User, UserWithPassword


def generate_id(seed: str) -> str:
    """Generate deterministic UUID from seed string using same algorithm as JS mock"""
    hash1 = 0
    hash2 = 0

    for char in seed:
        code = ord(char)
        hash1 = ((hash1 << 5) - hash1 + code) | 0
        hash2 = ((hash2 << 3) + hash2 + code) | 0

    # Convert to 32-bit signed integers (like JavaScript)
    if hash1 >= 0x80000000:
        hash1 = hash1 - 0x100000000
    if hash2 >= 0x80000000:
        hash2 = hash2 - 0x100000000

    # Convert to 32-bit unsigned for hex conversion
    hash1 = hash1 & 0xFFFFFFFF
    hash2 = hash2 & 0xFFFFFFFF

    # Convert to hex strings and pad to 8 characters
    hex1 = f"{hash1:08x}"
    hex2 = f"{hash2:08x}"

    # Build UUID v4 format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
    part1 = hex1[:8]
    part2 = hex2[:4]
    part3 = "4" + hex2[1:4]

    # Part 4: variant bits (10xx xxxx)
    variant_byte = 0x80 | (int(hex2[4:6], 16) & 0x3F)
    part4 = f"{variant_byte:02x}{hex2[6:8]}"

    # Part 5: remaining 12 characters
    part5 = (hex1[8:] + hex2[8:])[:12].ljust(12, "0")

    return f"{part1}-{part2}-{part3}-{part4}-{part5}"


def days_ago(days: int) -> datetime:
    """Return datetime N days ago"""
    return datetime.now(UTC) - timedelta(days=days)


# Initialize users
mock_users: list[UserWithPassword] = [
    UserWithPassword(id=generate_id("admin"), username="admin", password="admin", role="admin"),  # noqa: S106
    UserWithPassword(id=generate_id("user1"), username="user1", password="user1", role="user"),  # noqa: S106
    UserWithPassword(id=generate_id("alice"), username="alice", password="alice", role="user"),  # noqa: S106
    UserWithPassword(id=generate_id("bob"), username="bob", password="bob", role="user"),  # noqa: S106
]


# Initialize forums
mock_forums: list[Forum] = [
    # Technology
    Forum(
        id=generate_id("web-development"),
        slug="web-development",
        title="Web Development",
        description="Discuss web technologies, frameworks, and best practices",
        category="Technology",
    ),
    Forum(
        id=generate_id("artificial-intelligence"),
        slug="artificial-intelligence",
        title="Artificial Intelligence & ML",
        description="Machine learning, neural networks, and AI applications",
        category="Technology",
    ),
    Forum(
        id=generate_id("mobile-development"),
        slug="mobile-development",
        title="Mobile Development",
        description="iOS, Android, and cross-platform mobile development",
        category="Technology",
    ),
    # Science
    Forum(
        id=generate_id("physics"),
        slug="physics",
        title="Physics & Astronomy",
        description="Discuss physics theories, experiments, and space exploration",
        category="Science",
    ),
    Forum(
        id=generate_id("biology"),
        slug="biology",
        title="Biology & Life Sciences",
        description="Genetics, ecology, and the study of living organisms",
        category="Science",
    ),
    Forum(
        id=generate_id("chemistry"),
        slug="chemistry",
        title="Chemistry",
        description="Chemical reactions, molecular structures, and laboratory techniques",
        category="Science",
    ),
    # Art
    Forum(
        id=generate_id("digital-art"),
        slug="digital-art",
        title="Digital Art & Design",
        description="Digital painting, 3D modeling, and graphic design",
        category="Art",
    ),
    Forum(
        id=generate_id("traditional-art"),
        slug="traditional-art",
        title="Traditional Art",
        description="Painting, drawing, sculpture, and classical art forms",
        category="Art",
    ),
    Forum(
        id=generate_id("photography"),
        slug="photography",
        title="Photography",
        description="Camera techniques, composition, and photo editing",
        category="Art",
    ),
]


# Initialize posts
mock_posts: list[Post] = []

# Web development forum - 120 posts
web_dev_forum = next(f for f in mock_forums if f.slug == "web-development")
web_dev_topics = [
    "Getting Started with React Hooks",
    "TypeScript Best Practices in 2024",
    "Building RESTful APIs with FastAPI",
    "CSS Grid vs Flexbox: When to Use Each",
    "Understanding async/await in JavaScript",
    "Modern Authentication Patterns",
    "Optimizing Web Performance",
    "Introduction to Web Components",
    "State Management Solutions Compared",
    "Responsive Design Techniques",
]

for i in range(120):
    topic = web_dev_topics[i % len(web_dev_topics)]
    iteration = i // len(web_dev_topics)
    if iteration > 0:
        topic = f"{topic} - Part {iteration + 1}"

    created_at = days_ago(120 - i)
    updated_at = None
    if random.random() < 0.7:
        updated_at = created_at + timedelta(days=random.randint(0, 5))

    mock_posts.append(
        Post(
            id=generate_id(f"post-{i + 1}"),
            forumId=web_dev_forum.id,
            number=i + 1,
            title=topic,
            content=f"This is the content for post about {topic.lower()}.",
            tags=["discussion", "question"] if i % 2 == 0 else ["tutorial", "guide"],
            authorId=mock_users[i % len(mock_users)].id,
            createdAt=created_at,
            updatedAt=updated_at,
        )
    )

# Other forums - 5 posts each
forum_topics = {
    "artificial-intelligence": [
        "Neural Networks Fundamentals",
        "Deep Learning Frameworks Comparison",
        "Natural Language Processing Basics",
        "Computer Vision Applications",
        "Reinforcement Learning Introduction",
    ],
    "mobile-development": [
        "React Native vs Flutter",
        "iOS App Architecture Patterns",
        "Android Jetpack Compose Guide",
        "Mobile App Performance Optimization",
        "Cross-Platform Development Tips",
    ],
    "physics": [
        "Quantum Mechanics Introduction",
        "Black Holes and Event Horizons",
        "String Theory Explained",
        "Particle Physics Discoveries",
        "Cosmology and the Big Bang",
    ],
    "biology": [
        "CRISPR Gene Editing Technology",
        "Evolution and Natural Selection",
        "Cellular Biology Basics",
        "Ecosystems and Biodiversity",
        "Genetics and Heredity",
    ],
    "chemistry": [
        "Organic Chemistry Fundamentals",
        "Chemical Bonding Explained",
        "Periodic Table Trends",
        "Reaction Kinetics",
        "Laboratory Safety Best Practices",
    ],
    "digital-art": [
        "Digital Painting Techniques",
        "3D Modeling for Beginners",
        "Graphic Design Principles",
        "Color Theory in Digital Art",
        "Creating Game Assets",
    ],
    "traditional-art": [
        "Oil Painting Basics",
        "Drawing Fundamentals",
        "Sculpture Techniques",
        "Watercolor Methods",
        "Art History Overview",
    ],
    "photography": [
        "Camera Settings Guide",
        "Composition Rules",
        "Portrait Photography Tips",
        "Landscape Photography",
        "Photo Editing Workflow",
    ],
}

post_number = 121
days_offset = [60, 50, 40, 30, 20]

for forum in mock_forums:
    if forum.slug == "web-development":
        continue

    topics = forum_topics.get(forum.slug, [])
    for i, topic in enumerate(topics):
        created_at = days_ago(days_offset[i])
        updated_at = None
        if random.random() < 0.8:
            updated_at = created_at + timedelta(days=random.randint(0, 3))

        mock_posts.append(
            Post(
                id=generate_id(f"post-{post_number}"),
                forumId=forum.id,
                number=i + 1,
                title=topic,
                content=f"This is the content for post about {topic.lower()}.",
                tags=["discussion"] if i % 2 == 0 else ["guide"],
                authorId=mock_users[i % len(mock_users)].id,
                createdAt=created_at,
                updatedAt=updated_at,
            )
        )
        post_number += 1


# Initialize comments
mock_comments: list[Comment] = []

comment_templates = [
    "Great post! Thanks for sharing.",
    "I have a question about this...",
    "This is very helpful, thank you!",
    "Could you elaborate on this point?",
    "I disagree with this approach.",
    "Excellent explanation!",
    "This doesn't work for me.",
    "Can you provide more examples?",
    "Very informative, thanks!",
    "I'm having trouble understanding this.",
    "This is exactly what I needed!",
    "What about edge cases?",
    "Great tutorial!",
    "This saved me hours of work.",
    "Could you clarify this section?",
    "I found a better solution.",
    "Thanks for the detailed post!",
    "This is outdated information.",
    "Brilliant explanation!",
    "I have a follow-up question.",
]

comment_id = 1
for post in mock_posts:
    num_comments = random.randint(0, 5)
    for i in range(num_comments):
        post_age = (datetime.now(UTC) - post.createdAt).days
        comment_age = random.randint(0, min(post_age, 30))
        created_at = post.createdAt + timedelta(days=comment_age)
        updated_at = None
        if random.random() < 0.9:
            updated_at = created_at + timedelta(days=random.randint(0, 2))

        mock_comments.append(
            Comment(
                id=generate_id(f"comment-{comment_id}"),
                postId=post.id,
                content=comment_templates[i % len(comment_templates)],
                authorId=mock_users[random.randint(0, len(mock_users) - 1)].id,
                createdAt=created_at,
                updatedAt=updated_at,
            )
        )
        comment_id += 1


# Session storage
sessions: dict[str, User] = {}
