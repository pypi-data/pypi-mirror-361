"""Comprehensive tests for Slack Block Kit models."""

import unittest

import pydantic

import slack_models


class TestTextObject(unittest.TestCase):
    """Test TextObject model."""

    def test_plain_text_object(self) -> None:
        """Test TextObject with plain text."""
        text_obj = slack_models.TextObject(
            type='plain_text', text='Hello, World!', emoji=True
        )

        self.assertEqual(text_obj.type, 'plain_text')
        self.assertEqual(text_obj.text, 'Hello, World!')
        self.assertTrue(text_obj.emoji)
        self.assertIsNone(text_obj.verbatim)

    def test_markdown_text_object(self) -> None:
        """Test TextObject with markdown."""
        text_obj = slack_models.TextObject(
            type='mrkdwn', text='*Bold text* and _italic text_', verbatim=True
        )

        self.assertEqual(text_obj.type, 'mrkdwn')
        self.assertEqual(text_obj.text, '*Bold text* and _italic text_')
        self.assertTrue(text_obj.verbatim)
        self.assertIsNone(text_obj.emoji)

    def test_text_object_minimal(self) -> None:
        """Test TextObject with minimal data."""
        text_obj = slack_models.TextObject(
            type='plain_text', text='Simple text'
        )

        self.assertEqual(text_obj.type, 'plain_text')
        self.assertEqual(text_obj.text, 'Simple text')
        self.assertIsNone(text_obj.emoji)
        self.assertIsNone(text_obj.verbatim)


class TestConfirmationDialog(unittest.TestCase):
    """Test ConfirmationDialog model."""

    def test_confirmation_dialog(self) -> None:
        """Test ConfirmationDialog creation."""
        dialog = slack_models.ConfirmationDialog(
            title=slack_models.TextObject(type='plain_text', text='Confirm'),
            text=slack_models.TextObject(
                type='plain_text', text='Are you sure?'
            ),
            confirm=slack_models.TextObject(type='plain_text', text='Yes'),
            deny=slack_models.TextObject(type='plain_text', text='No'),
        )

        self.assertEqual(dialog.title.text, 'Confirm')
        self.assertEqual(dialog.text.text, 'Are you sure?')
        self.assertEqual(dialog.confirm.text, 'Yes')
        self.assertEqual(dialog.deny.text, 'No')


class TestOption(unittest.TestCase):
    """Test Option model."""

    def test_option_with_description(self) -> None:
        """Test Option with description."""
        option = slack_models.Option(
            text=slack_models.TextObject(type='plain_text', text='Option 1'),
            value='option_1',
            description=slack_models.TextObject(
                type='plain_text', text='First option'
            ),
            url='https://example.com',
        )

        self.assertEqual(option.text.text, 'Option 1')
        self.assertEqual(option.value, 'option_1')
        self.assertEqual(option.description.text, 'First option')
        self.assertEqual(option.url, 'https://example.com')

    def test_option_minimal(self) -> None:
        """Test Option with minimal data."""
        option = slack_models.Option(
            text=slack_models.TextObject(type='plain_text', text='Simple'),
            value='simple',
        )

        self.assertEqual(option.text.text, 'Simple')
        self.assertEqual(option.value, 'simple')
        self.assertIsNone(option.description)
        self.assertIsNone(option.url)


class TestOptionGroup(unittest.TestCase):
    """Test OptionGroup model."""

    def test_option_group(self) -> None:
        """Test OptionGroup creation."""
        options = [
            slack_models.Option(
                text=slack_models.TextObject(
                    type='plain_text', text='Option 1'
                ),
                value='opt1',
            ),
            slack_models.Option(
                text=slack_models.TextObject(
                    type='plain_text', text='Option 2'
                ),
                value='opt2',
            ),
        ]

        group = slack_models.OptionGroup(
            label=slack_models.TextObject(type='plain_text', text='Group 1'),
            options=options,
        )

        self.assertEqual(group.label.text, 'Group 1')
        self.assertEqual(len(group.options), 2)
        self.assertEqual(group.options[0].value, 'opt1')
        self.assertEqual(group.options[1].value, 'opt2')


class TestButtonElement(unittest.TestCase):
    """Test ButtonElement model."""

    def test_button_element_full(self) -> None:
        """Test ButtonElement with all fields."""
        button = slack_models.ButtonElement(
            action_id='button_1',
            text=slack_models.TextObject(type='plain_text', text='Click me'),
            value='click_value',
            url='https://example.com',
            style='primary',
            confirm=slack_models.ConfirmationDialog(
                title=slack_models.TextObject(
                    type='plain_text', text='Confirm'
                ),
                text=slack_models.TextObject(type='plain_text', text='Sure?'),
                confirm=slack_models.TextObject(type='plain_text', text='Yes'),
                deny=slack_models.TextObject(type='plain_text', text='No'),
            ),
        )

        self.assertEqual(button.type, 'button')
        self.assertEqual(button.action_id, 'button_1')
        self.assertEqual(button.text.text, 'Click me')
        self.assertEqual(button.value, 'click_value')
        self.assertEqual(button.url, 'https://example.com')
        self.assertEqual(button.style, 'primary')
        self.assertIsNotNone(button.confirm)

    def test_button_element_minimal(self) -> None:
        """Test ButtonElement with minimal data."""
        button = slack_models.ButtonElement(
            text=slack_models.TextObject(type='plain_text', text='Button')
        )

        self.assertEqual(button.type, 'button')
        self.assertEqual(button.text.text, 'Button')
        self.assertIsNone(button.action_id)
        self.assertIsNone(button.value)
        self.assertIsNone(button.url)
        self.assertIsNone(button.style)
        self.assertIsNone(button.confirm)


class TestCheckboxesElement(unittest.TestCase):
    """Test CheckboxesElement model."""

    def test_checkboxes_element(self) -> None:
        """Test CheckboxesElement creation."""
        options = [
            slack_models.Option(
                text=slack_models.TextObject(
                    type='plain_text', text='Option 1'
                ),
                value='opt1',
            ),
            slack_models.Option(
                text=slack_models.TextObject(
                    type='plain_text', text='Option 2'
                ),
                value='opt2',
            ),
        ]

        checkboxes = slack_models.CheckboxesElement(
            action_id='checkboxes_1',
            options=options,
            initial_options=[options[0]],
            focus_on_load=True,
        )

        self.assertEqual(checkboxes.type, 'checkboxes')
        self.assertEqual(checkboxes.action_id, 'checkboxes_1')
        self.assertEqual(len(checkboxes.options), 2)
        self.assertEqual(len(checkboxes.initial_options), 1)
        self.assertTrue(checkboxes.focus_on_load)


class TestDatePickerElement(unittest.TestCase):
    """Test DatePickerElement model."""

    def test_date_picker_element(self) -> None:
        """Test DatePickerElement creation."""
        date_picker = slack_models.DatePickerElement(
            action_id='date_1',
            initial_date='2023-12-25',
            placeholder=slack_models.TextObject(
                type='plain_text', text='Select a date'
            ),
            focus_on_load=True,
        )

        self.assertEqual(date_picker.type, 'datepicker')
        self.assertEqual(date_picker.action_id, 'date_1')
        self.assertEqual(date_picker.initial_date, '2023-12-25')
        self.assertEqual(date_picker.placeholder.text, 'Select a date')
        self.assertTrue(date_picker.focus_on_load)


class TestImageElement(unittest.TestCase):
    """Test ImageElement model."""

    def test_image_element(self) -> None:
        """Test ImageElement creation."""
        image = slack_models.ImageElement(
            image_url='https://example.com/image.png', alt_text='Example image'
        )

        self.assertEqual(image.type, 'image')
        self.assertEqual(image.image_url, 'https://example.com/image.png')
        self.assertEqual(image.alt_text, 'Example image')


class TestPlainTextInputElement(unittest.TestCase):
    """Test PlainTextInputElement model."""

    def test_plain_text_input_element(self) -> None:
        """Test PlainTextInputElement creation."""
        text_input = slack_models.PlainTextInputElement(
            action_id='text_input_1',
            placeholder=slack_models.TextObject(
                type='plain_text', text='Enter text'
            ),
            initial_value='Default text',
            multiline=True,
            min_length=10,
            max_length=500,
            focus_on_load=True,
        )

        self.assertEqual(text_input.type, 'plain_text_input')
        self.assertEqual(text_input.action_id, 'text_input_1')
        self.assertEqual(text_input.placeholder.text, 'Enter text')
        self.assertEqual(text_input.initial_value, 'Default text')
        self.assertTrue(text_input.multiline)
        self.assertEqual(text_input.min_length, 10)
        self.assertEqual(text_input.max_length, 500)
        self.assertTrue(text_input.focus_on_load)


class TestStaticSelectElement(unittest.TestCase):
    """Test StaticSelectElement model."""

    def test_static_select_with_options(self) -> None:
        """Test StaticSelectElement with options."""
        options = [
            slack_models.Option(
                text=slack_models.TextObject(
                    type='plain_text', text='Option 1'
                ),
                value='opt1',
            ),
            slack_models.Option(
                text=slack_models.TextObject(
                    type='plain_text', text='Option 2'
                ),
                value='opt2',
            ),
        ]

        select = slack_models.StaticSelectElement(
            action_id='select_1',
            placeholder=slack_models.TextObject(
                type='plain_text', text='Choose an option'
            ),
            options=options,
            initial_option=options[0],
        )

        self.assertEqual(select.type, 'static_select')
        self.assertEqual(select.action_id, 'select_1')
        self.assertEqual(select.placeholder.text, 'Choose an option')
        self.assertEqual(len(select.options), 2)
        self.assertEqual(select.initial_option.value, 'opt1')
        self.assertIsNone(select.option_groups)

    def test_static_select_with_option_groups(self) -> None:
        """Test StaticSelectElement with option groups."""
        options1 = [
            slack_models.Option(
                text=slack_models.TextObject(
                    type='plain_text', text='Option 1'
                ),
                value='opt1',
            )
        ]
        options2 = [
            slack_models.Option(
                text=slack_models.TextObject(
                    type='plain_text', text='Option 2'
                ),
                value='opt2',
            )
        ]

        option_groups = [
            slack_models.OptionGroup(
                label=slack_models.TextObject(
                    type='plain_text', text='Group 1'
                ),
                options=options1,
            ),
            slack_models.OptionGroup(
                label=slack_models.TextObject(
                    type='plain_text', text='Group 2'
                ),
                options=options2,
            ),
        ]

        select = slack_models.StaticSelectElement(
            placeholder=slack_models.TextObject(
                type='plain_text', text='Choose from groups'
            ),
            option_groups=option_groups,
        )

        self.assertEqual(select.type, 'static_select')
        self.assertEqual(len(select.option_groups), 2)
        self.assertIsNone(select.options)


class TestSectionBlock(unittest.TestCase):
    """Test SectionBlock model."""

    def test_section_block_with_text(self) -> None:
        """Test SectionBlock with text only."""
        section = slack_models.SectionBlock(
            block_id='section_1',
            text=slack_models.TextObject(
                type='mrkdwn', text='This is a *section* block.'
            ),
        )

        self.assertEqual(section.type, 'section')
        self.assertEqual(section.block_id, 'section_1')
        self.assertEqual(section.text.text, 'This is a *section* block.')
        self.assertIsNone(section.fields)
        self.assertIsNone(section.accessory)

    def test_section_block_with_fields(self) -> None:
        """Test SectionBlock with fields."""
        fields = [
            slack_models.TextObject(type='mrkdwn', text='*Field 1*'),
            slack_models.TextObject(type='mrkdwn', text='*Field 2*'),
        ]

        section = slack_models.SectionBlock(
            text=slack_models.TextObject(
                type='mrkdwn', text='Section with fields'
            ),
            fields=fields,
        )

        self.assertEqual(section.type, 'section')
        self.assertEqual(len(section.fields), 2)
        self.assertEqual(section.fields[0].text, '*Field 1*')

    def test_section_block_with_accessory(self) -> None:
        """Test SectionBlock with accessory element."""
        button = slack_models.ButtonElement(
            action_id='button_1',
            text=slack_models.TextObject(type='plain_text', text='Click'),
        )

        section = slack_models.SectionBlock(
            text=slack_models.TextObject(
                type='mrkdwn', text='Section with button'
            ),
            accessory=button,
        )

        self.assertEqual(section.type, 'section')
        self.assertIsInstance(section.accessory, slack_models.ButtonElement)
        self.assertEqual(section.accessory.text.text, 'Click')


class TestDividerBlock(unittest.TestCase):
    """Test DividerBlock model."""

    def test_divider_block(self) -> None:
        """Test DividerBlock creation."""
        divider = slack_models.DividerBlock(block_id='divider_1')

        self.assertEqual(divider.type, 'divider')
        self.assertEqual(divider.block_id, 'divider_1')


class TestImageBlock(unittest.TestCase):
    """Test ImageBlock model."""

    def test_image_block(self) -> None:
        """Test ImageBlock creation."""
        image_block = slack_models.ImageBlock(
            block_id='image_1',
            image_url='https://example.com/image.png',
            alt_text='Example image',
            title=slack_models.TextObject(
                type='plain_text', text='Image Title'
            ),
        )

        self.assertEqual(image_block.type, 'image')
        self.assertEqual(image_block.block_id, 'image_1')
        self.assertEqual(
            image_block.image_url, 'https://example.com/image.png'
        )
        self.assertEqual(image_block.alt_text, 'Example image')
        self.assertEqual(image_block.title.text, 'Image Title')


class TestActionsBlock(unittest.TestCase):
    """Test ActionsBlock model."""

    def test_actions_block(self) -> None:
        """Test ActionsBlock creation."""
        elements = [
            slack_models.ButtonElement(
                action_id='button_1',
                text=slack_models.TextObject(
                    type='plain_text', text='Button 1'
                ),
            ),
            slack_models.ButtonElement(
                action_id='button_2',
                text=slack_models.TextObject(
                    type='plain_text', text='Button 2'
                ),
            ),
        ]

        actions = slack_models.ActionsBlock(
            block_id='actions_1', elements=elements
        )

        self.assertEqual(actions.type, 'actions')
        self.assertEqual(actions.block_id, 'actions_1')
        self.assertEqual(len(actions.elements), 2)
        self.assertIsInstance(actions.elements[0], slack_models.ButtonElement)


class TestContextBlock(unittest.TestCase):
    """Test ContextBlock model."""

    def test_context_block(self) -> None:
        """Test ContextBlock creation."""
        elements = [
            slack_models.TextObject(type='mrkdwn', text='Context information'),
            slack_models.ImageElement(
                image_url='https://example.com/icon.png', alt_text='Icon'
            ),
        ]

        context = slack_models.ContextBlock(
            block_id='context_1', elements=elements
        )

        self.assertEqual(context.type, 'context')
        self.assertEqual(context.block_id, 'context_1')
        self.assertEqual(len(context.elements), 2)
        self.assertIsInstance(context.elements[0], slack_models.TextObject)
        self.assertIsInstance(context.elements[1], slack_models.ImageElement)


class TestInputBlock(unittest.TestCase):
    """Test InputBlock model."""

    def test_input_block(self) -> None:
        """Test InputBlock creation."""
        text_input = slack_models.PlainTextInputElement(
            action_id='input_1',
            placeholder=slack_models.TextObject(
                type='plain_text', text='Enter your name'
            ),
        )

        input_block = slack_models.InputBlock(
            block_id='input_block_1',
            label=slack_models.TextObject(type='plain_text', text='Name'),
            element=text_input,
            hint=slack_models.TextObject(
                type='plain_text', text='Please enter your full name'
            ),
            optional=True,
            dispatch_action=True,
        )

        self.assertEqual(input_block.type, 'input')
        self.assertEqual(input_block.block_id, 'input_block_1')
        self.assertEqual(input_block.label.text, 'Name')
        self.assertIsInstance(
            input_block.element, slack_models.PlainTextInputElement
        )
        self.assertEqual(input_block.hint.text, 'Please enter your full name')
        self.assertTrue(input_block.optional)
        self.assertTrue(input_block.dispatch_action)


class TestHeaderBlock(unittest.TestCase):
    """Test HeaderBlock model."""

    def test_header_block(self) -> None:
        """Test HeaderBlock creation."""
        header = slack_models.HeaderBlock(
            block_id='header_1',
            text=slack_models.TextObject(
                type='plain_text', text='Header Text'
            ),
        )

        self.assertEqual(header.type, 'header')
        self.assertEqual(header.block_id, 'header_1')
        self.assertEqual(header.text.text, 'Header Text')


class TestFileBlock(unittest.TestCase):
    """Test FileBlock model."""

    def test_file_block(self) -> None:
        """Test FileBlock creation."""
        file_block = slack_models.FileBlock(
            block_id='file_1', external_id='external_file_123'
        )

        self.assertEqual(file_block.type, 'file')
        self.assertEqual(file_block.block_id, 'file_1')
        self.assertEqual(file_block.external_id, 'external_file_123')
        self.assertEqual(file_block.source, 'remote')


class TestVideoBlock(unittest.TestCase):
    """Test VideoBlock model."""

    def test_video_block(self) -> None:
        """Test VideoBlock creation."""
        video = slack_models.VideoBlock(
            block_id='video_1',
            video_url='https://example.com/video.mp4',
            thumbnail_url='https://example.com/thumbnail.png',
            alt_text='Example video',
            title=slack_models.TextObject(
                type='plain_text', text='Video Title'
            ),
            title_url='https://example.com/video-page',
            description=slack_models.TextObject(
                type='plain_text', text='Video description'
            ),
            provider_icon_url='https://example.com/provider-icon.png',
            provider_name='Example Provider',
        )

        self.assertEqual(video.type, 'video')
        self.assertEqual(video.block_id, 'video_1')
        self.assertEqual(video.video_url, 'https://example.com/video.mp4')
        self.assertEqual(
            video.thumbnail_url, 'https://example.com/thumbnail.png'
        )
        self.assertEqual(video.alt_text, 'Example video')
        self.assertEqual(video.title.text, 'Video Title')
        self.assertEqual(video.title_url, 'https://example.com/video-page')
        self.assertEqual(video.description.text, 'Video description')
        self.assertEqual(
            video.provider_icon_url, 'https://example.com/provider-icon.png'
        )
        self.assertEqual(video.provider_name, 'Example Provider')


class TestRichTextBlock(unittest.TestCase):
    """Test RichTextBlock model."""

    def test_rich_text_block(self) -> None:
        """Test RichTextBlock creation."""
        rich_text_section = slack_models.RichTextSection(
            elements=[{'type': 'text', 'text': 'Hello, world!'}]
        )

        rich_text_list = slack_models.RichTextList(
            style='bullet',
            elements=[{'type': 'rich_text_section', 'elements': []}],
            indent=1,
        )

        rich_text = slack_models.RichTextBlock(
            block_id='rich_text_1',
            elements=[rich_text_section, rich_text_list],
        )

        self.assertEqual(rich_text.type, 'rich_text')
        self.assertEqual(rich_text.block_id, 'rich_text_1')
        self.assertEqual(len(rich_text.elements), 2)
        self.assertIsInstance(
            rich_text.elements[0], slack_models.RichTextSection
        )
        self.assertIsInstance(rich_text.elements[1], slack_models.RichTextList)
        self.assertEqual(rich_text.elements[1].style, 'bullet')


class TestUnionTypes(unittest.TestCase):
    """Test union types for blocks and elements."""

    def test_block_element_union(self) -> None:
        """Test BlockElement union type validation."""
        # Test that ButtonElement is valid BlockElement
        button = slack_models.ButtonElement(
            text=slack_models.TextObject(type='plain_text', text='Button')
        )
        self.assertIsInstance(button, slack_models.BaseBlockElement)

        # Test that ImageElement is valid BlockElement
        image = slack_models.ImageElement(
            image_url='https://example.com/image.png', alt_text='Image'
        )
        # Note: ImageElement doesn't inherit from BaseBlockElement
        self.assertIsInstance(image, slack_models.ImageElement)

    def test_block_union(self) -> None:
        """Test Block union type validation."""
        # Test various block types
        section = slack_models.SectionBlock(
            text=slack_models.TextObject(type='plain_text', text='Section')
        )
        self.assertIsInstance(section, slack_models.BaseBlock)

        divider = slack_models.DividerBlock()
        self.assertIsInstance(divider, slack_models.BaseBlock)

        actions = slack_models.ActionsBlock(
            elements=[
                slack_models.ButtonElement(
                    text=slack_models.TextObject(
                        type='plain_text', text='Button'
                    )
                )
            ]
        )
        self.assertIsInstance(actions, slack_models.BaseBlock)


class TestValidationErrors(unittest.TestCase):
    """Test validation error cases."""

    def test_invalid_text_object_type(self) -> None:
        """Test invalid text object type."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.TextObject(
                type='invalid_type',  # Invalid type
                text='Text',
            )

    def test_missing_required_fields(self) -> None:
        """Test missing required fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.ButtonElement()  # Missing required 'text' field

        with self.assertRaises(pydantic.ValidationError):
            slack_models.Option(value='value')  # Missing required 'text' field

    def test_invalid_button_style(self) -> None:
        """Test invalid button style."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.ButtonElement(
                text=slack_models.TextObject(type='plain_text', text='Button'),
                style='invalid_style',  # Invalid style
            )

    def test_invalid_rich_text_list_style(self) -> None:
        """Test invalid rich text list style."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.RichTextList(
                style='invalid_style',  # Invalid style
                elements=[],
            )


if __name__ == '__main__':
    unittest.main()
