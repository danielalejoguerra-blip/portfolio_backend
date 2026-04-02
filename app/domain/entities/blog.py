"""
Blog post entity for portfolio blog domain.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from app.domain.entities.content_base import ContentMetadata


@dataclass(frozen=True)
class ContentBlock:
	"""
	A single block in the structured content of a blog post.

	Allows full control over image placement and rich editorial layouts.

	block_type values:
	  text      – Markdown/HTML prose
	  image     – Standalone image with optional caption
	  gallery   – Multiple images in a grid
	  code      – Syntax-highlighted code snippet
	  callout   – Highlighted note / warning / tip box
	  video     – Embedded video (URL)
	  divider   – Visual section separator
	  quote     – Pull-quote / blockquote

	image_position (for block_type="image"):
	  inline     – Full-width inside the article flow
	  left       – Floated left with text wrap
	  right      – Floated right with text wrap
	  center     – Centered, narrower than full-width
	  background – Used as a section background
	"""
	block_type: str                      # text | image | gallery | code | …
	content: Optional[str] = None        # Markdown text / code / quote text
	image_url: Optional[str] = None
	image_position: Optional[str] = None # inline | left | right | center | background
	image_alt: Optional[str] = None
	caption: Optional[str] = None
	language: Optional[str] = None       # For code blocks: python, js, etc.
	callout_type: Optional[str] = None   # info | warning | tip | danger
	video_url: Optional[str] = None
	# Gallery images: [{"url": "...", "alt": "...", "caption": "..."}]
	gallery_items: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class BlogPost:
	"""
	Blog post entity for articles and publications.

	Supports both simple Markdown ``content`` and a rich ``content_blocks``
	structure when fine-grained control over image placement is needed.
	They are mutually exclusive — prefer ``content_blocks`` for new posts.
	"""
	# ── Identity ─────────────────────────────────────────────────────────────
	id: int
	title: str
	slug: str
	description: Optional[str]          # Excerpt / summary (≤ 500 chars)
	content: Optional[str]              # Plain Markdown fallback
	# Structured content blocks with full image-position control
	content_blocks: list[dict[str, Any]]

	# ── Cover image ──────────────────────────────────────────────────────────
	cover_image_url: Optional[str]      # Hero / thumbnail URL
	cover_image_alt: Optional[str]      # Accessibility alt text
	# CSS object-position equivalent: center | top | bottom | left | right
	cover_image_position: str

	# ── Classification ───────────────────────────────────────────────────────
	category: Optional[str]             # tutorial | opinion | case_study | news | …
	tags: list[str]                     # Topic tags for filtering
	series: Optional[str]               # Series / collection name
	series_order: Optional[int]         # Order within the series (1-based)

	# ── Reading experience ────────────────────────────────────────────────────
	reading_time_minutes: Optional[int] # Auto-calculated or manually set
	featured: bool                      # Pin to homepage / hero carousel

	# ── SEO ──────────────────────────────────────────────────────────────────
	seo_title: Optional[str]            # Override <title> tag (≤ 60 chars)
	seo_description: Optional[str]      # Override meta description (≤ 160 chars)
	canonical_url: Optional[str]        # Original URL when cross-posting
	og_image_url: Optional[str]         # Open Graph image override

	# ── Media ────────────────────────────────────────────────────────────────
	images: list[str]                   # Additional media library for the post

	# ── Publishing ───────────────────────────────────────────────────────────
	visible: bool
	published_at: Optional[datetime]    # Scheduled publishing datetime

	# ── Meta / i18n ──────────────────────────────────────────────────────────
	metadata: ContentMetadata
	created_at: datetime
	updated_at: datetime
	deleted_at: Optional[datetime] = None
	translations: dict = field(default_factory=dict)

	@property
	def is_deleted(self) -> bool:
		return self.deleted_at is not None

	@property
	def is_published(self) -> bool:
		if self.is_deleted or not self.visible:
			return False
		if self.published_at is None:
			return True
		return self.published_at <= datetime.now(self.published_at.tzinfo)

	@property
	def status(self) -> str:
		"""Derive publication status from visible and published_at fields."""
		if not self.visible:
			return "draft"
		if self.published_at is not None:
			now = datetime.now(self.published_at.tzinfo)
			if self.published_at > now:
				return "scheduled"
		return "published"
