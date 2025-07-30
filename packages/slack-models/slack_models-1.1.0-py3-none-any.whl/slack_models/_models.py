import enum
import typing

import pydantic

# Block Kit Models


class TextObject(pydantic.BaseModel):
    """A text object for formatting text in Slack Block Kit.

    Contains formatted text with type specification for plain text or
    markdown rendering. Used throughout Block Kit for displaying text
    content with optional emoji rendering and verbatim formatting.
    """

    type: typing.Literal['plain_text', 'mrkdwn']
    text: str
    emoji: bool | None = None
    verbatim: bool | None = None


class ConfirmationDialog(pydantic.BaseModel):
    """A confirmation dialog composition object.

    Defines a dialog that provides a confirmation step for interactive
    elements. Contains title, explanatory text, and button labels for
    confirm and deny actions.
    """

    title: TextObject
    text: TextObject
    confirm: TextObject
    deny: TextObject


class Option(pydantic.BaseModel):
    """An option object for use in select menus and multi-select menus.

    Represents a single selectable option containing display text and
    a value. Optionally includes a description for additional context.
    """

    text: TextObject
    value: str
    description: TextObject | None = None
    url: str | None = None


class OptionGroup(pydantic.BaseModel):
    """An option group object for organizing options in select menus.

    Groups related options together with a label for improved
    organization in select and multi-select menus.
    """

    label: TextObject
    options: list[Option]


class BaseBlockElement(pydantic.BaseModel):
    """Base class for all Block Kit elements.

    Contains common fields shared across all interactive elements
    including action identifier for handling interactions.
    """

    type: str
    action_id: str | None = None


class ButtonElement(BaseBlockElement):
    """A button element for user interaction.

    Interactive element that triggers an action when clicked. Can be
    styled as primary, danger, or default, and may include a URL for
    navigation or confirmation dialog for safety.
    """

    type: typing.Literal['button'] = 'button'
    text: TextObject
    value: str | None = None
    url: str | None = None
    style: typing.Literal['primary', 'danger'] | None = None
    confirm: ConfirmationDialog | None = None


class CheckboxesElement(BaseBlockElement):
    """A checkboxes element for multiple selections.

    Allows users to select multiple options from a list of checkboxes.
    Can have initial options selected and includes confirmation dialog
    support for safety.
    """

    type: typing.Literal['checkboxes'] = 'checkboxes'
    options: list[Option]
    initial_options: list[Option] | None = None
    confirm: ConfirmationDialog | None = None
    focus_on_load: bool | None = None


class DatePickerElement(BaseBlockElement):
    """A date picker element for selecting dates.

    Provides a calendar interface for users to select a date.
    Can have an initial date set and includes placeholder text
    and confirmation dialog support.
    """

    type: typing.Literal['datepicker'] = 'datepicker'
    initial_date: str | None = None
    confirm: ConfirmationDialog | None = None
    focus_on_load: bool | None = None
    placeholder: TextObject | None = None


class DatetimePickerElement(BaseBlockElement):
    """A datetime picker element for selecting date and time.

    Combines date and time selection in a single interface.
    Initial datetime is specified as Unix timestamp.
    """

    type: typing.Literal['datetimepicker'] = 'datetimepicker'
    initial_date_time: int | None = None
    confirm: ConfirmationDialog | None = None
    focus_on_load: bool | None = None


class EmailInputElement(BaseBlockElement):
    """An email input element for collecting email addresses.

    Text input specifically designed for email address collection
    with built-in validation and formatting.
    """

    type: typing.Literal['email_text_input'] = 'email_text_input'
    initial_value: str | None = None
    dispatch_action_config: dict | None = None
    focus_on_load: bool | None = None
    placeholder: TextObject | None = None


class ImageElement(pydantic.BaseModel):
    """An image element for displaying images in blocks.

    Displays an image with alternative text for accessibility.
    Can be used in various block types to enhance visual content.
    """

    type: typing.Literal['image'] = 'image'
    image_url: str
    alt_text: str


class NumberInputElement(BaseBlockElement):
    """A number input element for collecting numeric values.

    Specialized text input for numeric data with optional minimum
    and maximum value constraints and decimal precision control.
    """

    type: typing.Literal['number_input'] = 'number_input'
    is_decimal_allowed: bool
    initial_value: str | None = None
    min_value: str | None = None
    max_value: str | None = None
    dispatch_action_config: dict | None = None
    focus_on_load: bool | None = None
    placeholder: TextObject | None = None


class OverflowElement(BaseBlockElement):
    """An overflow menu element for additional actions.

    Displays a menu of options in a compact dropdown format.
    Useful for secondary actions that don't need prominent placement.
    """

    type: typing.Literal['overflow'] = 'overflow'
    options: list[Option]
    confirm: ConfirmationDialog | None = None


class PlainTextInputElement(BaseBlockElement):
    """A plain text input element for collecting text input.

    Basic text input field with support for single or multi-line input,
    length constraints, and input validation through dispatch actions.
    """

    type: typing.Literal['plain_text_input'] = 'plain_text_input'
    placeholder: TextObject | None = None
    initial_value: str | None = None
    multiline: bool | None = None
    min_length: int | None = None
    max_length: int | None = None
    dispatch_action_config: dict | None = None
    focus_on_load: bool | None = None


class RadioButtonsElement(BaseBlockElement):
    """A radio buttons element for single selection.

    Allows users to select one option from a list of radio buttons.
    Can have an initial option selected and confirmation dialog support.
    """

    type: typing.Literal['radio_buttons'] = 'radio_buttons'
    options: list[Option]
    initial_option: Option | None = None
    confirm: ConfirmationDialog | None = None
    focus_on_load: bool | None = None


class StaticSelectElement(BaseBlockElement):
    """A static select menu with predefined options.

    Select menu populated with a static list of options or option groups.
    Supports single selection with optional initial selection and
    confirmation dialog.
    """

    type: typing.Literal['static_select'] = 'static_select'
    placeholder: TextObject
    options: list[Option] | None = None
    option_groups: list[OptionGroup] | None = None
    initial_option: Option | None = None
    confirm: ConfirmationDialog | None = None
    focus_on_load: bool | None = None


class ExternalSelectElement(BaseBlockElement):
    """A select menu with externally loaded options.

    Select menu that loads options dynamically from an external source.
    Supports search functionality and minimum query length specification.
    """

    type: typing.Literal['external_select'] = 'external_select'
    placeholder: TextObject
    initial_option: Option | None = None
    min_query_length: int | None = None
    confirm: ConfirmationDialog | None = None
    focus_on_load: bool | None = None


class UsersSelectElement(BaseBlockElement):
    """A select menu populated with workspace users.

    Select menu automatically populated with users from the workspace.
    Supports initial user selection and confirmation dialog.
    """

    type: typing.Literal['users_select'] = 'users_select'
    placeholder: TextObject
    initial_user: str | None = None
    confirm: ConfirmationDialog | None = None
    focus_on_load: bool | None = None


class ConversationsSelectElement(BaseBlockElement):
    """A select menu populated with conversations.

    Select menu for selecting conversations (channels, DMs, etc.)
    with optional filtering and initial conversation selection.
    """

    type: typing.Literal['conversations_select'] = 'conversations_select'
    placeholder: TextObject
    initial_conversation: str | None = None
    default_to_current_conversation: bool | None = None
    confirm: ConfirmationDialog | None = None
    response_url_enabled: bool | None = None
    filter: dict | None = None
    focus_on_load: bool | None = None


class ChannelsSelectElement(BaseBlockElement):
    """A select menu populated with public channels.

    Select menu for selecting public channels from the workspace
    with optional initial channel selection and confirmation.
    """

    type: typing.Literal['channels_select'] = 'channels_select'
    placeholder: TextObject
    initial_channel: str | None = None
    confirm: ConfirmationDialog | None = None
    response_url_enabled: bool | None = None
    focus_on_load: bool | None = None


class TimePickerElement(BaseBlockElement):
    """A time picker element for selecting time values.

    Provides an interface for users to select a time of day.
    Initial time is specified in HH:mm format.
    """

    type: typing.Literal['timepicker'] = 'timepicker'
    initial_time: str | None = None
    confirm: ConfirmationDialog | None = None
    focus_on_load: bool | None = None
    placeholder: TextObject | None = None


class URLInputElement(BaseBlockElement):
    """A URL input element for collecting web addresses.

    Text input specifically designed for URL collection with
    built-in validation and formatting for web addresses.
    """

    type: typing.Literal['url_text_input'] = 'url_text_input'
    initial_value: str | None = None
    dispatch_action_config: dict | None = None
    focus_on_load: bool | None = None
    placeholder: TextObject | None = None


class FileInputElement(BaseBlockElement):
    """A file input element for file uploads.

    Allows users to upload files with optional file type restrictions
    and maximum file count limits.
    """

    type: typing.Literal['file_input'] = 'file_input'
    filetypes: list[str] | None = None
    max_files: int | None = None


# Union type for all block elements
BlockElement = (
    ButtonElement
    | CheckboxesElement
    | DatePickerElement
    | DatetimePickerElement
    | EmailInputElement
    | ImageElement
    | NumberInputElement
    | OverflowElement
    | PlainTextInputElement
    | RadioButtonsElement
    | StaticSelectElement
    | ExternalSelectElement
    | UsersSelectElement
    | ConversationsSelectElement
    | ChannelsSelectElement
    | TimePickerElement
    | URLInputElement
    | FileInputElement
)


class BaseBlock(pydantic.BaseModel):
    """Base class for all Block Kit blocks.

    Contains common fields shared across all block types including
    block type and optional block identifier for referencing.
    """

    type: str
    block_id: str | None = None


class SectionBlock(BaseBlock):
    """A section block for displaying text and interactive elements.

    Basic block for displaying text content with optional interactive
    element (accessory). Supports both plain text and markdown formatting
    with multiple text field support.
    """

    type: typing.Literal['section'] = 'section'
    text: TextObject | None = None
    fields: list[TextObject] | None = None
    accessory: BlockElement | None = None


class DividerBlock(BaseBlock):
    """A divider block for visual separation.

    Simple block that displays a horizontal line to visually separate
    content sections. Requires no additional configuration.
    """

    type: typing.Literal['divider'] = 'divider'


class ImageBlock(BaseBlock):
    """An image block for displaying images.

    Displays an image with title and alternative text for accessibility.
    Images must be publicly accessible or use Slack-hosted URLs.
    """

    type: typing.Literal['image'] = 'image'
    image_url: str
    alt_text: str
    title: TextObject | None = None


class ActionsBlock(BaseBlock):
    """An actions block for interactive elements.

    Container for interactive elements like buttons, select menus,
    and other input elements. Can hold up to 25 elements in a
    horizontal layout.
    """

    type: typing.Literal['actions'] = 'actions'
    elements: list[BlockElement]


class ContextBlock(BaseBlock):
    """A context block for supplementary information.

    Displays contextual information using small text and images.
    Useful for metadata, timestamps, and supplementary details.
    """

    type: typing.Literal['context'] = 'context'
    elements: list[TextObject | ImageElement]


class InputBlock(BaseBlock):
    """An input block for collecting user input.

    Contains a single input element with label and optional hint text.
    Used in modals and app home surfaces for form-like interactions.
    """

    type: typing.Literal['input'] = 'input'
    label: TextObject
    element: BlockElement
    hint: TextObject | None = None
    optional: bool | None = None
    dispatch_action: bool | None = None


class FileBlock(BaseBlock):
    """A file block for displaying Slack files.

    Displays information about a Slack file including thumbnail,
    title, and metadata. Files must be shared in the workspace.
    """

    type: typing.Literal['file'] = 'file'
    external_id: str
    source: typing.Literal['remote'] = 'remote'


class HeaderBlock(BaseBlock):
    """A header block for section titles.

    Displays large text intended as a section header. Text is always
    rendered in plain text format for consistent styling.
    """

    type: typing.Literal['header'] = 'header'
    text: TextObject


class VideoBlock(BaseBlock):
    """A video block for embedding video content.

    Embeds video content from supported platforms with metadata
    including title, description, and provider information.
    """

    type: typing.Literal['video'] = 'video'
    video_url: str
    thumbnail_url: str
    alt_text: str
    title: TextObject
    title_url: str | None = None
    description: TextObject | None = None
    provider_icon_url: str | None = None
    provider_name: str | None = None


# Rich text blocks and elements
class RichTextElement(pydantic.BaseModel):
    """Base class for rich text elements."""

    type: str


class RichTextSection(RichTextElement):
    """A rich text section containing formatted text elements."""

    type: typing.Literal['rich_text_section'] = 'rich_text_section'
    elements: list[dict]


class RichTextList(RichTextElement):
    """A rich text list (ordered or unordered)."""

    type: typing.Literal['rich_text_list'] = 'rich_text_list'
    style: typing.Literal['ordered', 'bullet']
    elements: list[dict]
    indent: int | None = None
    border: int | None = None


class RichTextQuote(RichTextElement):
    """A rich text quote block."""

    type: typing.Literal['rich_text_quote'] = 'rich_text_quote'
    elements: list[dict]
    border: int | None = None


class RichTextPreformatted(RichTextElement):
    """A rich text preformatted block."""

    type: typing.Literal['rich_text_preformatted'] = 'rich_text_preformatted'
    elements: list[dict]
    border: int | None = None


class RichTextBlock(BaseBlock):
    """A rich text block for complex text formatting.

    Supports advanced text formatting including lists, quotes,
    preformatted text, and inline formatting like bold, italic,
    and links.
    """

    type: typing.Literal['rich_text'] = 'rich_text'
    elements: list[
        RichTextSection | RichTextList | RichTextQuote | RichTextPreformatted
    ]


# Union type for all blocks
Block = (
    SectionBlock
    | DividerBlock
    | ImageBlock
    | ActionsBlock
    | ContextBlock
    | InputBlock
    | FileBlock
    | HeaderBlock
    | VideoBlock
    | RichTextBlock
)

# Event Models


class EventSubType(enum.StrEnum):
    assistant_app_thread = 'assistant_app_thread'
    bot_message = 'bot_message'
    channel_archive = 'channel_archive'
    channel_convert_to_private = 'channel_convert_to_private'
    channel_convert_to_public = 'channel_convert_to_public'
    channel_join = 'channel_join'
    channel_leave = 'channel_leave'
    channel_name = 'channel_name'
    channel_posting_permissions = 'channel_posting_permissions'
    channel_purpose = 'channel_purpose'
    channel_topic = 'channel_topic'
    channel_unarchive = 'channel_unarchive'
    document_mention = 'document_mention'
    ekm_access_denied = 'ekm_access_denied'
    file_share = 'file_share'
    message_changed = 'message_changed'
    message_deleted = 'message_deleted'
    me_message = 'me_message'
    reminder_add = 'reminder_add'
    thread_broadcast = 'thread_broadcast'


class Channel(pydantic.BaseModel):
    """A legacy object that contains information about a workspace channel.

    Represents a communication space within Slack containing metadata like
    channel ID, name, creation timestamp, creator, and membership status.
    Includes details such as whether the channel is archived, general,
    shared, or private, and tracks information like last read message,
    unread message count, and channel topic/purpose.

    Note: This is different from private channels (which are group objects).
    """

    id: str
    name: str = ''
    is_channel: bool | None = None
    created: int | None = None
    creator: str | None = None
    is_archived: bool = False
    is_general: bool | None = None
    name_normalized: str | None = None
    is_shared: bool | None = None
    is_org_shared: bool = False
    is_member: bool | None = None
    is_private: bool | None = None
    is_mpim: bool | None = None
    is_im: bool = False
    last_read: str | None = None
    latest: dict | None = None
    unread_count: int = 0
    unread_count_display: int = 0
    members: list[str] | None = None
    topic: dict | None = None
    purpose: dict | None = None
    previous_names: list[str] | None = None


class UserProfile(pydantic.BaseModel):
    """Contains detailed profile information for a Slack user.

    Stores both standard and custom profile fields including user status,
    contact information, display names, and profile images. Profile
    composition can vary and not all fields will be present for every user.
    """

    title: str | None = None
    phone: str | None = None
    skype: str | None = None
    email: str | None = None
    real_name: str | None = None
    display_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    real_name_normalized: str | None = None
    display_name_normalized: str | None = None
    fields: list[dict] | None = None
    status_text: str | None = None
    status_emoji: str | None = None
    status_expiration: int | None = None
    avatar_hash: str | None = None
    always_active: bool | None = False
    image_original: str | None = None
    image_24: str | None = None
    image_32: str | None = None
    image_48: str | None = None
    image_72: str | None = None
    image_192: str | None = None
    image_512: str | None = None
    image_1024: str | None = None
    status_text_canonical: str | None = None
    team: str | None = None


class EnterpriseUser(pydantic.BaseModel):
    """Contains Enterprise Grid-specific user information.

    Provides details about a user's enterprise identity including
    enterprise ID, name, administrative roles, and team memberships
    within the Enterprise Grid structure.
    """

    enterprise_id: str
    enterprise_name: str
    is_admin: bool
    is_owner: bool
    teams: list[str] | None = None


class User(pydantic.BaseModel):
    """A comprehensive representation of a Slack workspace user.

    Provides detailed information about a user within a Slack workspace,
    including profile details, workspace roles, and account settings.
    Contains workspace-specific information and may include Enterprise Grid
    user data. User object composition can vary and not all fields will be
    present for every user.
    """

    id: str
    team_id: str | None = None
    name: str | None = None
    deleted: bool = False
    color: str | None = None
    real_name: str | None = None
    tz: str | None = None
    tz_label: str | None = None
    tz_offset: int | None = None
    profile: UserProfile | None = None
    is_bot: bool = False
    is_admin: bool = False
    is_owner: bool = False
    is_primary_owner: bool = False
    is_restricted: bool = False
    is_ultra_restricted: bool = False
    is_app_user: bool = False
    enterprise_user: EnterpriseUser | None = None
    updated: int | None = None
    is_email_confirmed: bool | None = None
    who_can_share_contact_card: str | None = None

    @property
    def display_name(self) -> str:
        """Return the name to display"""
        if not self.profile:
            return self.name or self.id
        return (
            self.profile.display_name
            or self.profile.first_name
            or self.name
            or self.id
        )


class File(pydantic.BaseModel, extra='ignore'):
    """A file object contains information about a file shared with a workspace.

    Represents a file shared within a Slack workspace, including unique
    identifier, creation timestamp, file metadata like name, type, and size,
    user who uploaded the file, sharing information, and thumbnail/preview
    URLs.

    Authentication is required to access file URLs.

    """

    id: str
    name: str
    title: str
    mimetype: str
    size: int
    mode: str
    url_private: str
    url_private_download: str | None = None


class FileContent(pydantic.BaseModel):
    """Represents downloaded file content with MIME type information.

    Contains the actual file data (as bytes) along with its MIME type,
    used for processing file attachments from Slack messages.
    """

    mimetype: str
    content: str | bytes


class Reaction(pydantic.BaseModel):
    """Represents an emoji reaction on a Slack message.

    Contains the reaction emoji name, count of users who reacted,
    and list of user IDs who added this reaction to the message.
    """

    name: str
    count: int
    users: list[str]


class MessageItem(pydantic.BaseModel):
    """Represents an item referenced in a Slack event.

    Used in reaction events to identify the target item (message, file,
    or file comment) that was reacted to. Contains the item type,
    channel/location, and timestamp information.
    """

    type: str = 'message'
    channel: str
    ts: str
    thread_ts: str | None = None


class MessageEdited(pydantic.BaseModel):
    """Contains metadata about a message edit.

    Tracks who edited the message and when the edit occurred,
    used in message events to indicate post-creation modifications.
    """

    user: str
    ts: str


class Authorization(pydantic.BaseModel):
    """Contains authorization information for a Slack webhook event.

    Provides details about the app installation including enterprise ID,
    team ID, user ID, and installation type. Used by Events API to
    identify the authorization context for the event.
    """

    enterprise_id: str | None = None
    team_id: str
    user_id: str
    is_bot: bool
    is_enterprise_install: bool


class BaseSlackEvent(pydantic.BaseModel):
    """Base class for all Slack event types.

    Contains common fields shared across all Slack events including
    event type, timestamp, and event timestamp.
    All specific event types inherit from this base class.
    """

    type: str
    ts: str | None = None
    event_ts: str | None = None


class MessageEvent(BaseSlackEvent):
    """A message was sent to a channel.

    Delivered when a message is posted to a channel, containing details
    like channel ID, user ID, message text, and timestamp. Can have
    various subtypes and may include additional properties like stars,
    pins, reactions, and file attachments.
    """

    type: typing.Literal['message'] = 'message'
    ts: str
    channel: str | None = None
    text: str | None = None
    user: str | None = None
    thread_ts: str | None = None
    subtype: str | None = None
    bot_id: str | None = None
    blocks: list[Block] | None = None
    channel_type: str | None = None
    edited: MessageEdited | None = None
    files: list[File] | None = None
    message: typing.Self | None = None
    reactions: list[Reaction] | None = None
    is_starred: bool | None = None
    pinned_to: list[str] | None = None
    parent_user_id: str | None = None
    reply_count: int | None = None
    reply_users: list[str] | None = None
    reply_users_count: int | None = None
    latest_reply: str | None = None
    hidden: bool | None = None
    deleted_ts: str | None = None


class AppMentionEvent(BaseSlackEvent):
    """Subscribe to message events that directly mention your app.

    Allows a Slack app to receive messages where the app is explicitly
    mentioned. Requires the app_mentions:read scope and only includes
    messages where the app is directly mentioned, not direct messages
    to the app.
    """

    type: typing.Literal['app_mention'] = 'app_mention'
    channel: str
    user: str
    text: str
    ts: str
    thread_ts: str | None = None
    event_ts: str


class ReactionAddedEvent(BaseSlackEvent):
    """A member has added an emoji reaction to an item.

    Sent when a user adds an emoji reaction to a message, file, or other
    item. Includes details about who added the reaction, what emoji was
    used, and which item was reacted to. Requires the reactions:read scope.
    """

    type: typing.Literal['reaction_added'] = 'reaction_added'
    user: str
    reaction: str
    item: MessageItem
    item_user: str | None = None
    event_ts: str


class ReactionRemovedEvent(BaseSlackEvent):
    """A reaction is removed from an item.

    Triggered when a user removes an emoji reaction from a message, file,
    or other item. Includes details about who removed the reaction, what
    emoji was removed, and which item was affected. Requires the
    reactions:read scope.
    """

    type: typing.Literal['reaction_removed'] = 'reaction_removed'
    user: str
    reaction: str
    item: MessageItem
    item_user: str | None = None
    event_ts: str


class TeamJoinEvent(BaseSlackEvent):
    """A new member has joined the team.

    Sent to all connections for a workspace when a new member joins,
    helping clients update their local cache of members. Includes
    user object with details about the new team member. Requires
    the users:read scope.
    """

    type: typing.Literal['team_join'] = 'team_join'
    user: User  # Full user object - override base class string type
    event_ts: str


class FileCreatedEvent(BaseSlackEvent):
    """A file was created.

    Sent when a user uploads a file to Slack. Contains file details
    and user information. When a file is shared with workspace members,
    a separate file_shared event is also sent. Requires the files:read
    scope.
    """

    type: typing.Literal['file_created'] = 'file_created'
    file_id: str
    file: dict  # Full file object
    user_id: str
    event_ts: str


class FileDeletedEvent(BaseSlackEvent):
    """A file was deleted.

    Sent to all connected clients in a workspace when a file is deleted.
    Contains only the file ID, not a full file object. Not raised if
    file removal is due to workspace's file retention policy. Requires
    the files:read scope.
    """

    type: typing.Literal['file_deleted'] = 'file_deleted'
    file_id: str
    user_id: str
    event_ts: str


class ChannelCreatedEvent(BaseSlackEvent):
    """A channel was created.

    Sent when a new channel is created in a workspace to help clients
    update their local cache of non-joined channels. Includes channel
    metadata such as ID, name, creation timestamp, and creator.
    Requires the channels:read scope.
    """

    type: typing.Literal['channel_created'] = 'channel_created'
    channel: dict  # Full channel object
    event_ts: str


class ChannelDeletedEvent(BaseSlackEvent):
    """A channel was deleted.

    Sent to all connections for a workspace when a channel is deleted
    to help clients update their local cache of non-joined channels.
    Contains the deleted channel's ID. Requires the channels:read scope.
    """

    type: typing.Literal['channel_deleted'] = 'channel_deleted'
    channel: str  # Channel ID
    event_ts: str


class ChannelRenameEvent(BaseSlackEvent):
    """A channel was renamed.

    Sent to all workspace connections when a channel is renamed,
    allowing clients to update their local list of channels.
    Contains the channel's new ID, name, and creation timestamp.
    Requires the channels:read scope.
    """

    type: typing.Literal['channel_rename'] = 'channel_rename'
    channel: dict  # Channel object with new name
    event_ts: str


# Union type for all possible events
SlackEvent = (
    MessageEvent
    | AppMentionEvent
    | ReactionAddedEvent
    | ReactionRemovedEvent
    | TeamJoinEvent
    | FileCreatedEvent
    | FileDeletedEvent
    | ChannelCreatedEvent
    | ChannelDeletedEvent
    | ChannelRenameEvent
)


class SlackEventCallback(pydantic.BaseModel):
    """Event callback payload from Slack Events API.

    Standard envelope for event notifications sent via HTTP endpoint.
    Contains authentication token, workspace identifier, app identifier,
    event details, and authorization context. Events are delivered with
    a 3-second response timeout and include retry mechanisms.
    """

    token: str
    team_id: str
    api_app_id: str
    event: SlackEvent
    type: typing.Literal['event_callback'] = 'event_callback'
    event_id: str
    event_time: int
    event_context: str | None = None
    authorizations: list[Authorization] | None = None

    model_config = pydantic.ConfigDict(extra='allow')


class SlackUrlVerification(pydantic.BaseModel):
    """URL verification challenge from Slack.

    Sent during Events API endpoint setup to verify endpoint ownership.
    Contains a challenge string that must be echoed back in the response
    to complete the verification process.
    """

    token: str
    challenge: str
    type: typing.Literal['url_verification'] = 'url_verification'


class SlackAppRateLimited(pydantic.BaseModel):
    """App rate limited notification from Slack.

    Sent when an app exceeds the Events API rate limit of 30,000 events
    per workspace per hour. Contains the minute-based rate limit count
    and workspace/app identifiers.
    """

    token: str
    team_id: str
    minute_rate_limited: int
    api_app_id: str
    type: typing.Literal['app_rate_limited'] = 'app_rate_limited'


# Union type for all possible webhook payloads
SlackWebhookPayload = (
    SlackEventCallback | SlackUrlVerification | SlackAppRateLimited
)

EVENT_MAP = {
    'message': MessageEvent,
    'app_mention': AppMentionEvent,
    'reaction_added': ReactionAddedEvent,
    'reaction_removed': ReactionRemovedEvent,
    'team_join': TeamJoinEvent,
    'file_created': FileCreatedEvent,
    'file_deleted': FileDeletedEvent,
    'channel_created': ChannelCreatedEvent,
    'channel_deleted': ChannelDeletedEvent,
    'channel_rename': ChannelRenameEvent,
}
