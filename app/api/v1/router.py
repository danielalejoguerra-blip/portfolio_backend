from fastapi import APIRouter

from app.api.v1.endpoints import (
	analytics,
	auth,
	blog,
	courses,
	education,
	experience,
	personal_info,
	projects,
	skills,
	users,
)

api_router = APIRouter()

# Auth & Users
api_router.include_router(auth.router)
api_router.include_router(users.router)

# Content domains
api_router.include_router(projects.router)
api_router.include_router(blog.router)
api_router.include_router(courses.router)
api_router.include_router(education.router)
api_router.include_router(experience.router)
api_router.include_router(personal_info.router)
api_router.include_router(skills.router)

# Analytics
api_router.include_router(analytics.router)
