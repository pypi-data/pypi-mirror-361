import warnings
from enum import Enum


class PermissionEnum(str, Enum):
    ADD_REACTIONS = "add_reactions"
    ADMINISTRATOR = "administrator"
    ATTACH_FILES = "attach_files"
    BAN_MEMBERS = "ban_members"
    CHANGE_NICKNAME = "change_nickname"
    CONNECT = "connect"
    CREATE_EVENTS = "create_events"
    CREATE_EXPRESSIONS = "create_expressions"
    CREATE_INSTANT_INVITE = "create_instant_invite"
    CREATE_POLLS = "create_polls"
    CREATE_PRIVATE_THREADS = "create_private_threads"
    CREATE_PUBLIC_THREADS = "create_public_threads"
    DEAFEN_MEMBERS = "deafen_members"
    EMBED_LINKS = "embed_links"
    EXTERNAL_EMOJIS = "external_emojis"
    EXTERNAL_STICKERS = "external_stickers"
    KICK_MEMBERS = "kick_members"
    MANAGE_CHANNELS = "manage_channels"
    MANAGE_EMOJIS = "manage_emojis"
    MANAGE_EMOJIS_AND_STICKERS = "manage_emojis_and_stickers"
    MANAGE_EVENTS = "manage_events"
    MANAGE_EXPRESSIONS = "manage_expressions"
    MANAGE_GUILD = "manage_guild"
    MANAGE_MESSAGES = "manage_messages"
    MANAGE_NICKNAMES = "manage_nicknames"
    MANAGE_PERMISSIONS = "manage_permissions"
    MANAGE_ROLES = "manage_roles"
    MANAGE_THREADS = "manage_threads"
    MANAGE_WEBHOOKS = "manage_webhooks"
    MENTION_EVERYONE = "mention_everyone"
    MODERATE_MEMBERS = "moderate_members"
    MOVE_MEMBERS = "move_members"
    MUTE_MEMBERS = "mute_members"
    PRIORITY_SPEAKER = "priority_speaker"
    READ_MESSAGE_HISTORY = "read_message_history"
    READ_MESSAGES = "read_messages"
    REQUEST_TO_SPEAK = "request_to_speak"
    SEND_MESSAGES = "send_messages"
    SEND_MESSAGES_IN_THREADS = "send_messages_in_threads"
    SEND_POLLS = "send_polls"
    SEND_TTS_MESSAGES = "send_tts_messages"
    SEND_VOICE_MESSAGES = "send_voice_messages"
    SPEAK = "speak"
    STREAM = "stream"
    USE_APPLICATION_COMMANDS = "use_application_commands"
    USE_EMBEDDED_ACTIVITIES = "use_embedded_activities"
    USE_EXTERNAL_APPS = "use_external_apps"
    USE_EXTERNAL_EMOJIS = "use_external_emojis"
    USE_EXTERNAL_SOUNDS = "use_external_sounds"
    USE_EXTERNAL_STICKERS = "use_external_stickers"
    USE_SOUNDBOARD = "use_soundboard"
    USE_VOICE_ACTIVATION = "use_voice_activation"
    VALUE = "value"
    VIEW_AUDIT_LOG = "view_audit_log"
    VIEW_CHANNEL = "view_channel"
    VIEW_CREATOR_MONETIZATION_ANALYTICS = "view_creator_monetization_analytics"
    VIEW_GUILD_INSIGHTS = "view_guild_insights"

    def __new__(cls, value):
        warnings.warn(
            "`ModuBotDiscord.enums.permission.PermissionEnum` is deprecated, use `ModuBotDiscord.checks.permissions.Permission` instead",
            DeprecationWarning,
            stacklevel=2,
        )

        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj
