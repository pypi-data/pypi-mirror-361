from typing import Any, Callable

import factory
import faker
from wagtail import blocks
from wagtail_factories.blocks import BlockFactory
from wagtail_factories.blocks import StreamFieldFactory as BaseStreamFieldFactory

fake = faker.Faker("en_AU")


class RichTextBlockFactory(BlockFactory):
    @classmethod
    def _build(cls, model_class, value=""):
        if not value:
            value = "".join(f"<p>{p}</p>" for p in fake.paragraphs(nb=3))
        block = model_class()
        return block.to_python(value)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._build(model_class, *args, **kwargs)

    class Meta:
        model = blocks.RichTextBlock


class StreamFieldFactory(BaseStreamFieldFactory):
    """
    Extension of wagtail_factories.blocks.StreamFieldFactory that doesn't require passing parameters
    """

    def evaluate(self, instance, step, extra):
        if not extra:
            possible_blocks = self.stream_block_factory._meta.base_declarations.keys()
            extra = {f"{index}": block_name for index, block_name in enumerate(possible_blocks)}
        return super().evaluate(instance, step, extra)


class ListLengthBlockFactory(factory.SubFactory):
    """
    Returns an n list of generated blocks, n may be an int or callable.
    Usage: ListLengthBlockFactory(SubblockFactory, length=10, block_args=["content.ContentPage"])
    """

    def __init__(self, factory, length: int | Callable = 1, block_args=None, **kwargs):
        self.length = length
        self.block_args = block_args or []
        super().__init__(factory, **kwargs)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        # TODO could be used with provided values then + (length - provided) generated appended
        return self.evaluate(None, None, kwds)

    def evaluate(self, instance, step, extra):
        subfactory = self.get_factory()
        ret_val = []
        length = self.length() if callable(self.length) else self.length
        for _ in range(length):
            # Very naive, assumes all default values
            ret_val.append(subfactory())

        list_block_def = blocks.list_block.ListBlock(subfactory._meta.model(*self.block_args))
        return blocks.list_block.ListValue(list_block_def, ret_val)

    class Meta:
        model = blocks.ListBlock
