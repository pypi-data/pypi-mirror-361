"""Define custom Discord client for discordproxy."""

import logging

import discord

logger = logging.getLogger(__name__)


class DiscordClient(discord.Client):
    """Custom sub-class for handling Discord events"""

    async def on_connect(self):
        """Handle on_connect event."""
        logger.info("%s has connected to Discord", self.user.name)

    async def on_ready(self):
        """Handle on_ready event."""
        logger.info("%s as logged in successfully", self.user.name)

    async def on_disconnect(self):
        """Handle on_disconnect event."""
        logger.info("Client has disconnected from Discord")
