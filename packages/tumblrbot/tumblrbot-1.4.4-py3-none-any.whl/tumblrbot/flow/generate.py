from random import random

import rich

from tumblrbot.utils.common import FlowClass, PreviewLive
from tumblrbot.utils.models import Post


class DraftGenerator(FlowClass):
    def create_drafts(self) -> None:
        message = f"View drafts here: https://tumblr.com/blog/{self.config.upload_blog_identifier}/drafts"

        with PreviewLive() as live:
            for i in live.progress.track(range(self.config.draft_count), description="Generating drafts..."):
                try:
                    post = self.generate_post()
                    self.tumblr.create_post(self.config.upload_blog_identifier, post)
                    live.custom_update(post)
                except BaseException as exception:
                    exception.add_note(f"📉 An error occurred! Generated {i} draft(s) before failing. {message}")
                    raise

        rich.print(f":chart_increasing: [bold green]Generated {self.config.draft_count} draft(s).[/] {message}")

    def generate_post(self) -> Post:
        content = self.generate_content()
        post = Post(
            content=[content],
            state="draft",
        )
        if tags := self.generate_tags(content):
            post.tags = tags.tags
        return post

    def generate_content(self) -> Post.Block:
        content = self.openai.responses.create(
            input=self.config.user_message,
            instructions=self.config.developer_message,
            model=self.config.fine_tuned_model,
        ).output_text

        return Post.Block(type="text", text=content)

    def generate_tags(self, content: Post.Block) -> Post | None:
        if random() < self.config.tags_chance:  # noqa: S311
            return self.openai.responses.parse(
                text_format=Post,
                input=f"Extract the most important subjects from the following text:\n\n{content.text}",
                instructions="You are an advanced text summarization tool. You return the requested data to the user as a list of comma-separated strings.",
                model=self.config.base_model,
                temperature=0.5,
            ).output_parsed

        return None
