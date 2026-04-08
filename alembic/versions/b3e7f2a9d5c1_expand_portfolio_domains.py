"""expand_portfolio_domains

Adds first-class structured fields to education, projects, blog_posts,
courses, and experiences tables, replacing previously metadata-only blobs
with typed columns and proper indexes.

Revision ID: b3e7f2a9d5c1
Revises: ff8c92764a89
Create Date: 2026-04-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b3e7f2a9d5c1'
down_revision = ('ff8c92764a89', 'a1b2c3d4e5f6')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # education
    # -------------------------------------------------------------------------
    # Institution
    op.add_column('education', sa.Column('institution', sa.String(255), nullable=False, server_default=''))
    op.add_column('education', sa.Column('institution_url', sa.String(2048), nullable=True))
    op.add_column('education', sa.Column('location', sa.String(255), nullable=True))
    # Programme
    op.add_column('education', sa.Column('degree_type', sa.String(50), nullable=False, server_default='bachelor'))
    op.add_column('education', sa.Column('field_of_study', sa.String(255), nullable=True))
    op.add_column('education', sa.Column('start_date', sa.Date(), nullable=True))
    op.add_column('education', sa.Column('end_date', sa.Date(), nullable=True))
    # Credential
    op.add_column('education', sa.Column('credential_id', sa.String(255), nullable=True))
    op.add_column('education', sa.Column('credential_url', sa.String(2048), nullable=True))
    op.add_column('education', sa.Column('grade', sa.String(50), nullable=True))
    op.add_column('education', sa.Column('honors', sa.String(255), nullable=True))
    # Academic extras (JSONB)
    op.add_column('education', sa.Column('relevant_coursework', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('education', sa.Column('activities', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('education', sa.Column('achievements', sa.JSON(), nullable=False, server_default='[]'))
    # Indexes
    op.create_index('ix_education_institution', 'education', ['institution'])
    op.create_index('ix_education_degree_type', 'education', ['degree_type'])
    op.create_index('ix_education_end_date', 'education', ['end_date'])
    # Remove server defaults so they are pure application-controlled after migration
    op.alter_column('education', 'institution', server_default=None)
    op.alter_column('education', 'degree_type', server_default=None)

    # -------------------------------------------------------------------------
    # projects
    # -------------------------------------------------------------------------
    # Classification
    op.add_column('projects', sa.Column('status', sa.String(50), nullable=False, server_default='completed'))
    op.add_column('projects', sa.Column('category', sa.String(50), nullable=True))
    op.add_column('projects', sa.Column('role', sa.String(255), nullable=True))
    # Timeline
    op.add_column('projects', sa.Column('start_date', sa.Date(), nullable=True))
    op.add_column('projects', sa.Column('end_date', sa.Date(), nullable=True))
    # Collaboration
    op.add_column('projects', sa.Column('team_size', sa.Integer(), nullable=True))
    op.add_column('projects', sa.Column('client', sa.String(255), nullable=True))
    # Tech stack (JSONB)
    op.add_column('projects', sa.Column('tech_stack', sa.JSON(), nullable=False, server_default='[]'))
    # Links
    op.add_column('projects', sa.Column('project_url', sa.String(2048), nullable=True))
    op.add_column('projects', sa.Column('repository_url', sa.String(2048), nullable=True))
    op.add_column('projects', sa.Column('documentation_url', sa.String(2048), nullable=True))
    op.add_column('projects', sa.Column('case_study_url', sa.String(2048), nullable=True))
    # Highlights (JSONB)
    op.add_column('projects', sa.Column('metrics', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('projects', sa.Column('features', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('projects', sa.Column('challenges', sa.JSON(), nullable=False, server_default='[]'))
    # Display
    op.add_column('projects', sa.Column('featured', sa.Boolean(), nullable=False, server_default='false'))
    # Indexes
    op.create_index('ix_projects_status', 'projects', ['status'])
    op.create_index('ix_projects_category', 'projects', ['category'])
    op.create_index('ix_projects_featured', 'projects', ['featured'])
    # Remove server defaults
    op.alter_column('projects', 'status', server_default=None)
    op.alter_column('projects', 'featured', server_default=None)
    op.alter_column('projects', 'tech_stack', server_default=None)
    op.alter_column('projects', 'metrics', server_default=None)
    op.alter_column('projects', 'features', server_default=None)
    op.alter_column('projects', 'challenges', server_default=None)

    # -------------------------------------------------------------------------
    # blog_posts
    # -------------------------------------------------------------------------
    # Structured content
    op.add_column('blog_posts', sa.Column('content_blocks', sa.JSON(), nullable=False, server_default='[]'))
    # Cover image
    op.add_column('blog_posts', sa.Column('cover_image_url', sa.String(2048), nullable=True))
    op.add_column('blog_posts', sa.Column('cover_image_alt', sa.String(255), nullable=True))
    op.add_column('blog_posts', sa.Column('cover_image_position', sa.String(20), nullable=False, server_default='center'))
    # Classification
    op.add_column('blog_posts', sa.Column('category', sa.String(100), nullable=True))
    op.add_column('blog_posts', sa.Column('tags', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('blog_posts', sa.Column('series', sa.String(255), nullable=True))
    op.add_column('blog_posts', sa.Column('series_order', sa.Integer(), nullable=True))
    # Reading experience
    op.add_column('blog_posts', sa.Column('reading_time_minutes', sa.Integer(), nullable=True))
    op.add_column('blog_posts', sa.Column('featured', sa.Boolean(), nullable=False, server_default='false'))
    # SEO
    op.add_column('blog_posts', sa.Column('seo_title', sa.String(60), nullable=True))
    op.add_column('blog_posts', sa.Column('seo_description', sa.String(160), nullable=True))
    op.add_column('blog_posts', sa.Column('canonical_url', sa.String(2048), nullable=True))
    op.add_column('blog_posts', sa.Column('og_image_url', sa.String(2048), nullable=True))
    # Indexes
    op.create_index('ix_blog_posts_category', 'blog_posts', ['category'])
    op.create_index('ix_blog_posts_series', 'blog_posts', ['series'])
    op.create_index('ix_blog_posts_featured', 'blog_posts', ['featured'])
    # Remove server defaults
    op.alter_column('blog_posts', 'cover_image_position', server_default=None)
    op.alter_column('blog_posts', 'featured', server_default=None)
    op.alter_column('blog_posts', 'content_blocks', server_default=None)
    op.alter_column('blog_posts', 'tags', server_default=None)

    # -------------------------------------------------------------------------
    # courses
    # -------------------------------------------------------------------------
    # Classification
    op.add_column('courses', sa.Column('is_certification', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('courses', sa.Column('category', sa.String(50), nullable=True))
    op.add_column('courses', sa.Column('level', sa.String(20), nullable=True))
    # Platform
    op.add_column('courses', sa.Column('platform', sa.String(255), nullable=True))
    op.add_column('courses', sa.Column('platform_url', sa.String(2048), nullable=True))
    op.add_column('courses', sa.Column('instructor', sa.String(255), nullable=True))
    op.add_column('courses', sa.Column('instructor_url', sa.String(2048), nullable=True))
    # Timeline
    op.add_column('courses', sa.Column('completion_date', sa.Date(), nullable=True))
    op.add_column('courses', sa.Column('expiration_date', sa.Date(), nullable=True))
    op.add_column('courses', sa.Column('duration_hours', sa.Integer(), nullable=True))
    # Credential
    op.add_column('courses', sa.Column('credential_id', sa.String(255), nullable=True))
    op.add_column('courses', sa.Column('certificate_url', sa.String(2048), nullable=True))
    op.add_column('courses', sa.Column('certificate_image_url', sa.String(2048), nullable=True))
    op.add_column('courses', sa.Column('badge_url', sa.String(2048), nullable=True))
    # Learning outcomes (JSONB)
    op.add_column('courses', sa.Column('skills_gained', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('courses', sa.Column('syllabus', sa.JSON(), nullable=False, server_default='[]'))
    # Indexes
    op.create_index('ix_courses_is_certification', 'courses', ['is_certification'])
    op.create_index('ix_courses_category', 'courses', ['category'])
    op.create_index('ix_courses_platform', 'courses', ['platform'])
    op.create_index('ix_courses_completion_date', 'courses', ['completion_date'])
    # Remove server defaults
    op.alter_column('courses', 'is_certification', server_default=None)
    op.alter_column('courses', 'skills_gained', server_default=None)
    op.alter_column('courses', 'syllabus', server_default=None)

    # -------------------------------------------------------------------------
    # experiences
    # -------------------------------------------------------------------------
    # Company
    op.add_column('experiences', sa.Column('company', sa.String(255), nullable=False, server_default=''))
    op.add_column('experiences', sa.Column('company_url', sa.String(2048), nullable=True))
    op.add_column('experiences', sa.Column('company_logo_url', sa.String(2048), nullable=True))
    op.add_column('experiences', sa.Column('location', sa.String(255), nullable=True))
    # Role details
    op.add_column('experiences', sa.Column('employment_type', sa.String(20), nullable=False, server_default='full_time'))
    op.add_column('experiences', sa.Column('work_mode', sa.String(10), nullable=True))
    op.add_column('experiences', sa.Column('department', sa.String(255), nullable=True))
    # Timeline
    op.add_column('experiences', sa.Column('start_date', sa.Date(), nullable=False, server_default='1970-01-01'))
    op.add_column('experiences', sa.Column('end_date', sa.Date(), nullable=True))
    op.add_column('experiences', sa.Column('is_current', sa.Boolean(), nullable=False, server_default='false'))
    # Tech stack & highlights (JSONB)
    op.add_column('experiences', sa.Column('tech_stack', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('experiences', sa.Column('responsibilities', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('experiences', sa.Column('achievements', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('experiences', sa.Column('related_projects', sa.JSON(), nullable=False, server_default='[]'))
    # References (JSONB)
    op.add_column('experiences', sa.Column('references', sa.JSON(), nullable=False, server_default='[]'))
    # Indexes
    op.create_index('ix_experiences_company', 'experiences', ['company'])
    op.create_index('ix_experiences_employment_type', 'experiences', ['employment_type'])
    op.create_index('ix_experiences_start_date', 'experiences', ['start_date'])
    op.create_index('ix_experiences_is_current', 'experiences', ['is_current'])
    # Remove server defaults
    op.alter_column('experiences', 'company', server_default=None)
    op.alter_column('experiences', 'employment_type', server_default=None)
    op.alter_column('experiences', 'start_date', server_default=None)
    op.alter_column('experiences', 'is_current', server_default=None)
    op.alter_column('experiences', 'tech_stack', server_default=None)
    op.alter_column('experiences', 'responsibilities', server_default=None)
    op.alter_column('experiences', 'achievements', server_default=None)
    op.alter_column('experiences', 'related_projects', server_default=None)
    op.alter_column('experiences', 'references', server_default=None)


def downgrade() -> None:
    # -------------------------------------------------------------------------
    # experiences
    # -------------------------------------------------------------------------
    op.drop_index('ix_experiences_is_current', table_name='experiences')
    op.drop_index('ix_experiences_start_date', table_name='experiences')
    op.drop_index('ix_experiences_employment_type', table_name='experiences')
    op.drop_index('ix_experiences_company', table_name='experiences')
    for col in ('references', 'related_projects', 'achievements', 'responsibilities',
                'tech_stack', 'is_current', 'end_date', 'start_date',
                'department', 'work_mode', 'employment_type',
                'location', 'company_logo_url', 'company_url', 'company'):
        op.drop_column('experiences', col)

    # -------------------------------------------------------------------------
    # courses
    # -------------------------------------------------------------------------
    op.drop_index('ix_courses_completion_date', table_name='courses')
    op.drop_index('ix_courses_platform', table_name='courses')
    op.drop_index('ix_courses_category', table_name='courses')
    op.drop_index('ix_courses_is_certification', table_name='courses')
    for col in ('syllabus', 'skills_gained', 'badge_url', 'certificate_image_url',
                'certificate_url', 'credential_id', 'duration_hours',
                'expiration_date', 'completion_date', 'instructor_url', 'instructor',
                'platform_url', 'platform', 'level', 'category', 'is_certification'):
        op.drop_column('courses', col)

    # -------------------------------------------------------------------------
    # blog_posts
    # -------------------------------------------------------------------------
    op.drop_index('ix_blog_posts_featured', table_name='blog_posts')
    op.drop_index('ix_blog_posts_series', table_name='blog_posts')
    op.drop_index('ix_blog_posts_category', table_name='blog_posts')
    for col in ('og_image_url', 'canonical_url', 'seo_description', 'seo_title',
                'featured', 'reading_time_minutes', 'series_order', 'series',
                'tags', 'category', 'cover_image_position', 'cover_image_alt',
                'cover_image_url', 'content_blocks'):
        op.drop_column('blog_posts', col)

    # -------------------------------------------------------------------------
    # projects
    # -------------------------------------------------------------------------
    op.drop_index('ix_projects_featured', table_name='projects')
    op.drop_index('ix_projects_category', table_name='projects')
    op.drop_index('ix_projects_status', table_name='projects')
    for col in ('featured', 'challenges', 'features', 'metrics',
                'case_study_url', 'documentation_url', 'repository_url', 'project_url',
                'tech_stack', 'client', 'team_size', 'end_date', 'start_date',
                'role', 'category', 'status'):
        op.drop_column('projects', col)

    # -------------------------------------------------------------------------
    # education
    # -------------------------------------------------------------------------
    op.drop_index('ix_education_end_date', table_name='education')
    op.drop_index('ix_education_degree_type', table_name='education')
    op.drop_index('ix_education_institution', table_name='education')
    for col in ('achievements', 'activities', 'relevant_coursework',
                'honors', 'grade', 'credential_url', 'credential_id',
                'end_date', 'start_date', 'field_of_study', 'degree_type',
                'location', 'institution_url', 'institution'):
        op.drop_column('education', col)
