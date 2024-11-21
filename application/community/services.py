from application.community.schemas import CommunityReadSchema, PostReadSchema
from application.post.schemas import CommunityShortReadSchema


async def update_author_from_community(community):
    community = CommunityReadSchema.model_validate(community)

    posts = []
    for post in community.posts:
        post = PostReadSchema.model_validate(post)
        post.author = CommunityShortReadSchema.model_validate(community)
        posts.append(post)

    community.posts = [PostReadSchema.model_validate(post) for post in posts] if posts else []

    return community