"""
Preset service for managing preset information and selection.

This service centralizes all preset-related business logic,
reducing code duplication and improving maintainability.
"""

import logging
from typing import List, Dict, Any, Optional
from ..constants import DefaultValues, PresetCategories
from ..keyboards.presets import (
    get_preset_emoji,
    get_preset_display_name,
    get_preset_description,
    get_preset_examples,
)
from ..utils.error_handling import BotError

logger = logging.getLogger(__name__)


class PresetService:
    """
    Service for managing preset information and selection.

    This service handles all preset-related operations including
    retrieving preset information, formatting preset data, and
    managing preset categories.
    """

    def __init__(self, adapter):
        """
        Initialize the preset service.

        Args:
            adapter: AgentryLab Telegram adapter
        """
        self.adapter = adapter
        self._preset_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp: Optional[float] = None
        self._cache_ttl = 300  # 5 minutes cache TTL

    async def get_available_presets(self) -> List[str]:
        """
        Get list of available preset IDs.

        Returns:
            List of available preset IDs

        Raises:
            BotError: If presets cannot be retrieved
        """
        try:
            presets = self.adapter.get_available_presets()
            logger.debug(f"Retrieved {len(presets)} available presets")
            return presets
        except Exception as e:
            logger.error(f"Error retrieving available presets: {e}")
            raise BotError(f"Failed to retrieve available presets: {e}")

    async def get_preset_info_batch(
        self, preset_ids: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get information for multiple presets with error handling.

        Args:
            preset_ids: List of preset IDs

        Returns:
            Dictionary mapping preset IDs to their information

        Raises:
            BotError: If preset information cannot be retrieved
        """
        try:
            preset_info = {}
            for preset_id in preset_ids:
                preset_info[preset_id] = await self._get_single_preset_info(preset_id)

            logger.debug(f"Retrieved information for {len(preset_info)} presets")
            return preset_info
        except Exception as e:
            logger.error(f"Error retrieving preset information batch: {e}")
            raise BotError(f"Failed to retrieve preset information: {e}")

    async def get_preset_info(self, preset_id: str) -> Dict[str, Any]:
        """
        Get information for a single preset.

        Args:
            preset_id: Preset ID

        Returns:
            Dictionary with preset information

        Raises:
            BotError: If preset information cannot be retrieved
        """
        try:
            return await self._get_single_preset_info(preset_id)
        except Exception as e:
            logger.error(f"Error retrieving preset info for {preset_id}: {e}")
            raise BotError(
                f"Failed to retrieve preset information for {preset_id}: {e}"
            )

    async def get_preset_examples(self, preset_id: str) -> List[str]:
        """Expose examples via keyboard helper for callbacks."""
        try:
            from ..keyboards.presets import get_preset_examples

            return get_preset_examples(preset_id)
        except Exception as e:
            logger.error(f"Error retrieving examples for {preset_id}: {e}")
            return []

    async def _get_single_preset_info(self, preset_id: str) -> Dict[str, Any]:
        """
        Get information for a single preset with fallback.

        Args:
            preset_id: Preset ID

        Returns:
            Dictionary with preset information
        """
        try:
            # Try to get info from AgentryLab adapter
            info = self.adapter.get_preset_info(preset_id)

            return {
                "display_name": get_preset_display_name(preset_id),
                "description": get_preset_description(preset_id),
                "emoji": get_preset_emoji(preset_id),
                "category": info.get("category", PresetCategories.OTHER),
                "examples": get_preset_examples(preset_id),
                "metadata": info,
            }
        except Exception as e:
            logger.warning(f"Could not get info for preset {preset_id}: {e}")
            return self._get_fallback_preset_info(preset_id)

    def _get_fallback_preset_info(self, preset_id: str) -> Dict[str, Any]:
        """
        Get fallback preset information when AgentryLab info is unavailable.

        Args:
            preset_id: Preset ID

        Returns:
            Dictionary with fallback preset information
        """
        return {
            "display_name": get_preset_display_name(preset_id),
            "description": get_preset_description(preset_id),
            "emoji": get_preset_emoji(preset_id),
            "category": PresetCategories.OTHER,
            "examples": get_preset_examples(preset_id),
            "metadata": {},
        }

    def get_preset_categories(
        self, preset_info: Dict[str, Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        Group presets by category.

        Args:
            preset_info: Dictionary with preset information

        Returns:
            Dictionary mapping categories to lists of preset IDs
        """
        categories: Dict[str, List[str]] = {}

        for preset_id, info in preset_info.items():
            category = info.get("category", PresetCategories.OTHER)

            if category not in categories:
                categories[category] = []
            categories[category].append(preset_id)

        return categories

    def get_preset_display_info(
        self, preset_id: str, preset_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get display information for a preset.

        Args:
            preset_id: Preset ID
            preset_info: Preset information dictionary

        Returns:
            Dictionary with display information
        """
        return {
            "id": preset_id,
            "display_name": preset_info.get(
                "display_name", preset_id.replace("_", " ").title()
            ),
            "description": preset_info.get(
                "description", DefaultValues.DEFAULT_PRESET_DESCRIPTION
            ),
            "emoji": preset_info.get("emoji", DefaultValues.DEFAULT_PRESET_EMOJI),
            "category": preset_info.get(
                "category", DefaultValues.DEFAULT_PRESET_CATEGORY
            ),
            "examples": preset_info.get(
                "examples", [DefaultValues.DEFAULT_EXAMPLE_TOPIC]
            ),
        }

    def get_preset_examples_display(
        self, preset_id: str, preset_info: Dict[str, Any], max_examples: int = 5
    ) -> List[str]:
        """
        Get formatted examples for display.

        Args:
            preset_id: Preset ID
            preset_info: Preset information dictionary
            max_examples: Maximum number of examples to return

        Returns:
            List of formatted example strings
        """
        examples = preset_info.get("examples", [])
        if not examples:
            examples = [DefaultValues.DEFAULT_EXAMPLE_TOPIC]

        return examples[:max_examples]

    def validate_preset_id(self, preset_id: str, available_presets: List[str]) -> bool:
        """
        Validate that a preset ID is available.

        Args:
            preset_id: Preset ID to validate
            available_presets: List of available preset IDs

        Returns:
            True if preset ID is valid and available
        """
        return preset_id in available_presets

    def get_preset_summary(
        self, preset_info: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get summary information about all presets.

        Args:
            preset_info: Dictionary with preset information

        Returns:
            Dictionary with preset summary
        """
        total_presets = len(preset_info)
        categories = self.get_preset_categories(preset_info)

        return {
            "total_presets": total_presets,
            "categories": list(categories.keys()),
            "presets_by_category": {
                cat: len(presets) for cat, presets in categories.items()
            },
            "most_common_category": (
                max(categories.keys(), key=lambda k: len(categories[k]))
                if categories
                else None
            ),
        }

    def search_presets(
        self, query: str, preset_info: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """
        Search presets by name or description.

        Args:
            query: Search query
            preset_info: Dictionary with preset information

        Returns:
            List of matching preset IDs
        """
        query_lower = query.lower()
        matches = []

        for preset_id, info in preset_info.items():
            # Search in display name
            if query_lower in info.get("display_name", "").lower():
                matches.append(preset_id)
                continue

            # Search in description
            if query_lower in info.get("description", "").lower():
                matches.append(preset_id)
                continue

            # Search in examples
            examples = info.get("examples", [])
            if any(query_lower in example.lower() for example in examples):
                matches.append(preset_id)
                continue

        return matches

    def get_preset_recommendations(
        self, user_preferences: Dict[str, Any], preset_info: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """
        Get preset recommendations based on user preferences.

        Args:
            user_preferences: User preference dictionary
            preset_info: Dictionary with preset information

        Returns:
            List of recommended preset IDs
        """
        recommendations = []

        # Get preferred category
        preferred_category = user_preferences.get("preferred_category")
        if preferred_category:
            categories = self.get_preset_categories(preset_info)
            if preferred_category in categories:
                recommendations.extend(categories[preferred_category])

        # Get recently used presets
        recently_used = user_preferences.get("recently_used", [])
        for preset_id in recently_used:
            if preset_id in preset_info and preset_id not in recommendations:
                recommendations.append(preset_id)

        # Add popular presets if no specific preferences
        if not recommendations:
            # Add presets from most common category
            categories = self.get_preset_categories(preset_info)
            if categories:
                most_common = max(categories.keys(), key=lambda k: len(categories[k]))
                recommendations.extend(categories[most_common][:3])

        return recommendations[:5]  # Limit to 5 recommendations

    def get_preset_statistics(
        self, preset_info: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get statistics about presets.

        Args:
            preset_info: Dictionary with preset information

        Returns:
            Dictionary with preset statistics
        """
        total_presets = len(preset_info)
        categories = self.get_preset_categories(preset_info)

        # Count examples
        total_examples = sum(
            len(info.get("examples", [])) for info in preset_info.values()
        )
        avg_examples = total_examples / total_presets if total_presets > 0 else 0

        # Count emojis
        emoji_counts: Dict[str, int] = {}
        for info in preset_info.values():
            emoji = info.get("emoji", "🤖")
            emoji_counts[emoji] = emoji_counts.get(emoji, 0) + 1

        return {
            "total_presets": total_presets,
            "total_categories": len(categories),
            "total_examples": total_examples,
            "average_examples_per_preset": round(avg_examples, 2),
            "most_common_emoji": (
                max(emoji_counts.keys(), key=lambda k: emoji_counts[k])
                if emoji_counts
                else "🤖"
            ),
            "emoji_distribution": emoji_counts,
            "category_distribution": {
                cat: len(presets) for cat, presets in categories.items()
            },
        }

    def format_preset_list(
        self, preset_info: Dict[str, Dict[str, Any]], max_per_category: int = 10
    ) -> str:
        """
        Format preset list for display.

        Args:
            preset_info: Dictionary with preset information
            max_per_category: Maximum presets per category to display

        Returns:
            Formatted preset list string
        """
        categories = self.get_preset_categories(preset_info)

        if not categories:
            return "No presets available."

        formatted_list = "**Available Presets:**\n\n"

        for category, preset_ids in categories.items():
            formatted_list += f"📁 **{category}**\n"

            for preset_id in preset_ids[:max_per_category]:
                info = preset_info[preset_id]
                emoji = info.get("emoji", "🤖")
                display_name = info.get(
                    "display_name", preset_id.replace("_", " ").title()
                )
                formatted_list += f"  {emoji} {display_name}\n"

            if len(preset_ids) > max_per_category:
                formatted_list += (
                    f"  ... and {len(preset_ids) - max_per_category} more\n"
                )

            formatted_list += "\n"

        return formatted_list

    def clear_cache(self) -> None:
        """Clear the preset information cache."""
        self._preset_cache.clear()
        self._cache_timestamp = None
        logger.debug("Cleared preset information cache")

    def is_cache_valid(self) -> bool:
        """
        Check if the cache is still valid.

        Returns:
            True if cache is valid
        """
        if not self._cache_timestamp:
            return False

        import time

        return (time.time() - self._cache_timestamp) < self._cache_ttl
