"""
Context Manager v1.0 - Final Production Release
Fixes final critical issues from executive review:
C-1: Monkey-patch recursion fixed
C-2: ExtendedContent forward reference fixed
C-3: LRU cache key explosion fixed
C-4: Unused compression cache removed
+ High-priority improvements and polish
"""

from __future__ import annotations  # C-2 FIX: Enables postponed evaluation

import asyncio
import atexit
import inspect
import json
import logging
import os
import threading
import time
import uuid
from abc import ABC, abstractmethod
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    Callable,
    Protocol,
    Literal,
)
from datetime import datetime
from enum import Enum
import importlib.metadata as importlib_metadata

# Hard dependencies - fail fast if missing
try:
    from pydantic import BaseModel, Field, ConfigDict

    PYDANTIC_VERSION = 2
except ImportError:
    raise ImportError(
        "managed-context requires pydantic>=2.7. Install with: pip install 'pydantic>=2.7'"
    )

try:
    import tiktoken
except ImportError:
    raise ImportError(
        "managed-context requires tiktoken>=0.6.0. Install with: pip install 'tiktoken>=0.6.0'"
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Module exports - minimal public surface
__all__ = [
    "ManagedContext",
    "managed_openai_client",
    "managed_anthropic_client",
    "patch_openai",
    "patch_anthropic",
    "create_context_store",
    "load_converters",
    "register_converter",
    "MCPMessage",
    "Role",
    "ContextCompressionError",
]


# === Custom Exceptions ===


class ContextCompressionError(Exception):
    """Raised when compression fails and cannot be recovered."""

    pass


# === Module-level cache for token encodings (C-3 FIX) ===

_ENCODING_CACHE = {}
_CACHE_LOCK = threading.Lock()


def _get_encoding(model: str):
    """Module-level encoding cache to avoid per-instance cache misses."""
    with _CACHE_LOCK:
        if model not in _ENCODING_CACHE:
            try:
                _ENCODING_CACHE[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                _ENCODING_CACHE[model] = tiktoken.get_encoding("cl100k_base")
        return _ENCODING_CACHE[model]


# === MCP-Compliant Core Types ===


class Role(str, Enum):
    """Message roles following MCP with provider extensions."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    FUNCTION = "function"
    DEVELOPER = "developer"


class TextContent(BaseModel):
    """Text content block following MCP specification."""

    model_config = ConfigDict(
        extra="allow",
        validate_default=False,
        validate_assignment=False,
        populate_by_name=True,
    )

    type: Literal["text"] = "text"
    text: str
    annotations: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = Field(None, alias="_meta")


class ImageContent(BaseModel):
    """Image content block following MCP specification."""

    model_config = ConfigDict(
        extra="allow",
        validate_default=False,
        validate_assignment=False,
        populate_by_name=True,
    )

    type: Literal["image"] = "image"
    data: str
    mimeType: str
    annotations: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = Field(None, alias="_meta")


class AudioContent(BaseModel):
    """Audio content block following MCP specification."""

    model_config = ConfigDict(
        extra="allow",
        validate_default=False,
        validate_assignment=False,
        populate_by_name=True,
    )

    type: Literal["audio"] = "audio"
    data: str
    mimeType: str
    annotations: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = Field(None, alias="_meta")


class VideoContent(BaseModel):
    """Video content block - future MCP extension."""

    model_config = ConfigDict(
        extra="allow",
        validate_default=False,
        validate_assignment=False,
        populate_by_name=True,
    )

    type: Literal["video"] = "video"
    data: str
    mimeType: str
    annotations: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = Field(None, alias="_meta")


class ToolUseContent(BaseModel):
    """Tool use content block - extension to MCP."""

    model_config = ConfigDict(
        extra="allow",
        validate_default=False,
        validate_assignment=False,
        populate_by_name=True,
    )

    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: Dict[str, Any]
    annotations: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = Field(None, alias="_meta")


class ToolResultContent(BaseModel):
    """Tool result content block - extension to MCP."""

    model_config = ConfigDict(
        extra="allow",
        validate_default=False,
        validate_assignment=False,
        populate_by_name=True,
    )

    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str
    content: Union[str, List[Dict[str, Any]]]
    is_error: bool = False
    annotations: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = Field(None, alias="_meta")


class EmbeddedResource(BaseModel):
    """Embedded resource following MCP specification."""

    model_config = ConfigDict(
        extra="allow",
        validate_default=False,
        validate_assignment=False,
        populate_by_name=True,
    )

    type: Literal["resource"] = "resource"
    resource: Dict[str, Any]
    annotations: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = Field(None, alias="_meta")


class ThinkingContent(BaseModel):
    """Anthropic thinking block - maps to special text content."""

    model_config = ConfigDict(
        extra="allow",
        validate_default=False,
        validate_assignment=False,
        populate_by_name=True,
    )

    type: Literal["thinking"] = "thinking"
    thinking: str
    signature: Optional[str] = None
    annotations: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = Field(None, alias="_meta")


class ExtendedContent(TextContent):
    """
    Extended content that inherits from TextContent to maintain type compatibility.
    Stores multiple content blocks in _meta while appearing as a single text block.
    """

    model_config = ConfigDict(
        extra="allow", validate_default=False, validate_assignment=False
    )

    type: Literal["text"] = "text"

    @classmethod
    def from_blocks(cls, blocks: List[ContentBlock]) -> ExtendedContent:
        """Create from multiple content blocks."""
        if len(blocks) == 1 and isinstance(blocks[0], (TextContent, ExtendedContent)):
            # Optimization: avoid unnecessary wrapper for single text blocks
            return (
                blocks[0]
                if isinstance(blocks[0], ExtendedContent)
                else cls(
                    text=blocks[0].text,
                    annotations=blocks[0].annotations,
                    meta=blocks[0].meta,
                )
            )

        text_parts = []
        chunks = []

        for block in blocks:
            chunks.append(block.model_dump())

            if isinstance(block, TextContent):
                text_parts.append(block.text)
            elif isinstance(block, ToolResultContent) and isinstance(
                block.content, str
            ):
                text_parts.append(block.content)
            elif isinstance(block, ToolUseContent):
                text_parts.append(f"[Tool: {block.name}]")
            elif isinstance(block, ImageContent):
                text_parts.append(f"[Image: {block.mimeType}]")
            elif isinstance(block, AudioContent):
                text_parts.append(f"[Audio: {block.mimeType}]")
            elif isinstance(block, VideoContent):
                text_parts.append(f"[Video: {block.mimeType}]")
            elif isinstance(block, ThinkingContent):
                text_parts.append(f"[Thinking: {block.thinking[:50]}...]")
            elif isinstance(block, EmbeddedResource):
                text_parts.append("[Resource]")

        return cls(
            text="\n".join(text_parts), meta={"_chunks": chunks} if chunks else None
        )

    def to_blocks(self) -> List[ContentBlock]:
        """Convert back to content blocks."""
        if not self.meta or "_chunks" not in self.meta:
            return [TextContent(text=self.text)]

        chunks = self.meta["_chunks"]
        blocks = []

        for chunk in chunks:
            block_type = chunk.get("type")
            try:
                if block_type == "text":
                    blocks.append(TextContent(**chunk))
                elif block_type == "image":
                    blocks.append(ImageContent(**chunk))
                elif block_type == "audio":
                    blocks.append(AudioContent(**chunk))
                elif block_type == "video":
                    blocks.append(VideoContent(**chunk))
                elif block_type == "tool_use":
                    blocks.append(ToolUseContent(**chunk))
                elif block_type == "tool_result":
                    blocks.append(ToolResultContent(**chunk))
                elif block_type == "resource":
                    blocks.append(EmbeddedResource(**chunk))
                elif block_type == "thinking":
                    blocks.append(ThinkingContent(**chunk))
                else:
                    # Preserve unknown types in meta
                    blocks.append(
                        TextContent(
                            text=f"[Unknown block: {block_type}]",
                            meta={"original_block": chunk, "original_type": block_type},
                        )
                    )
            except Exception as e:
                logger.warning(f"Failed to reconstruct block {block_type}: {e}")
                blocks.append(TextContent(text=f"[Reconstruction error: {block_type}]"))

        return blocks


# Content block union - now defined after ExtendedContent
ContentBlock = Union[
    TextContent,
    ImageContent,
    AudioContent,
    VideoContent,
    ToolUseContent,
    ToolResultContent,
    EmbeddedResource,
    ThinkingContent,
    ExtendedContent,
]


class MCPMessage(BaseModel):
    """MCP-compliant message with single content field."""

    model_config = ConfigDict(
        extra="allow", validate_default=False, validate_assignment=False
    )

    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: Role
    content: ContentBlock
    timestamp: datetime = Field(default_factory=datetime.now)
    priority: int = 1
    compressed: bool = False
    token_counts: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Provider-specific extensions
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    refusal: Optional[str] = None

    @property
    def content_blocks(self) -> List[ContentBlock]:
        """Get all content blocks (single or multiple)."""
        if isinstance(self.content, ExtendedContent):
            return self.content.to_blocks()
        else:
            return [self.content]

    @property
    def text_content(self) -> str:
        """Extract all text content."""
        if isinstance(self.content, (TextContent, ExtendedContent)):
            return self.content.text
        elif isinstance(self.content, ToolResultContent) and isinstance(
            self.content.content, str
        ):
            return self.content.content
        elif isinstance(self.content, ThinkingContent):
            return self.content.thinking
        else:
            return str(self.content)

    @property
    def has_multimodal_content(self) -> bool:
        """Check if message contains non-text content."""
        blocks = self.content_blocks
        return any(
            not isinstance(block, (TextContent, ThinkingContent)) for block in blocks
        )

    def get_token_count(self, model: str) -> int:
        """Get token count for specific model."""
        return self.token_counts.get(model, 0)

    def set_token_count(self, model: str, count: int):
        """Set token count for specific model."""
        self.token_counts[model] = count

    @classmethod
    def from_text(cls, role: Union[Role, str], text: str, **kwargs) -> MCPMessage:
        """Create simple text message."""
        if isinstance(role, str):
            role = Role(role)

        return cls(role=role, content=TextContent(text=text), **kwargs)

    @classmethod
    def from_blocks(
        cls, role: Union[Role, str], blocks: List[ContentBlock], **kwargs
    ) -> MCPMessage:
        """Create message from multiple content blocks."""
        if isinstance(role, str):
            role = Role(role)

        if len(blocks) == 1:
            content = blocks[0]
        else:
            content = ExtendedContent.from_blocks(blocks)

        return cls(role=role, content=content, **kwargs)

    def safe_copy(self) -> MCPMessage:
        """Safe copy that preserves all fields including message_id."""
        return self.__class__.model_validate(self.model_dump(mode="python"))


# === Token Estimation ===


class TokenEstimator(Protocol):
    """Protocol for token estimation strategies."""

    def estimate(self, message: MCPMessage, model: str) -> int:
        """Estimate token count for message."""
        ...


class TiktokenEstimator:
    """Default tiktoken-based estimator with module-level caching."""

    def estimate(self, message: MCPMessage, model: str) -> int:
        """Estimate tokens using tiktoken with shared cache."""
        encoding = _get_encoding(model)  # C-3 FIX: Use module-level cache

        tokens = 4  # Base overhead
        tokens += len(encoding.encode(message.role.value))

        text_content = message.text_content
        if text_content:
            tokens += len(encoding.encode(text_content))

        # Configurable overhead for multimodal content
        if message.has_multimodal_content:
            tokens += len(message.content_blocks) * 5

        return max(tokens, 1)


class OpenAITokenEstimator:
    """OpenAI-specific token estimation with configurable overheads."""

    # Empirically measured costs - user-overridable
    VISION_COSTS = {
        "gpt-4-vision-preview": {"base": 85, "high_detail": 170},
        "gpt-4o": {"base": 85, "high_detail": 170},
        "gpt-4o-2024-08-06": {"base": 85, "high_detail": 170},
    }

    def __init__(
        self,
        vision_costs: Optional[Dict[str, Dict[str, int]]] = None,
        token_overhead_per_image: int = 85,
        token_overhead_per_audio: int = 25,
        token_overhead_per_tool_call: int = 20,
    ):
        self.base_estimator = TiktokenEstimator()
        self.vision_costs = vision_costs or self.VISION_COSTS
        self.token_overhead_per_image = token_overhead_per_image
        self.token_overhead_per_audio = token_overhead_per_audio
        self.token_overhead_per_tool_call = token_overhead_per_tool_call

    def estimate(self, message: MCPMessage, model: str) -> int:
        """Estimate with OpenAI-specific costs and configurable overheads."""
        tokens = self.base_estimator.estimate(message, model)

        # Add vision costs if model supports it
        vision_costs = self.vision_costs.get(
            model,
            {
                "base": self.token_overhead_per_image,
                "high_detail": self.token_overhead_per_image * 2,
            },
        )

        for block in message.content_blocks:
            if isinstance(block, ImageContent):
                # Check for detail preference in meta
                detail = "base"
                if block.meta and "detail" in block.meta:
                    detail = block.meta["detail"]
                tokens += vision_costs.get(detail, vision_costs["base"])
            elif isinstance(block, AudioContent):
                tokens += self.token_overhead_per_audio
            elif isinstance(block, VideoContent):
                tokens += self.token_overhead_per_image * 10  # Rough estimate
            elif isinstance(block, ToolUseContent):
                tokens += self.token_overhead_per_tool_call
                # Add tokens for tool input JSON
                tool_input_text = json.dumps(block.input)
                encoding = _get_encoding(model)
                tokens += len(encoding.encode(tool_input_text))

        return tokens


# === Message Converter Protocol ===


class MessageConverter(Protocol):
    """Protocol for provider message converters."""

    def from_provider_format(self, message: Any) -> MCPMessage:
        """Convert provider message to internal format."""
        ...

    def to_provider_format(self, message: MCPMessage) -> Any:
        """Convert internal message to provider format."""
        ...

    def get_provider_name(self) -> str:
        """Get provider name."""
        ...

    def get_token_estimator(self) -> TokenEstimator:
        """Get provider-specific token estimator."""
        ...


# === Provider Converters ===


class OpenAIConverter:
    """OpenAI message converter with full spec compliance."""

    SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    SUPPORTED_AUDIO_FORMATS = {"wav", "mp3", "aac", "flac", "opus", "pcm16"}

    def __init__(
        self,
        vision_costs: Optional[Dict[str, Dict[str, int]]] = None,
        **estimator_kwargs,
    ):
        self.vision_costs = vision_costs
        self.estimator_kwargs = estimator_kwargs

    def get_provider_name(self) -> str:
        return "openai"

    def get_token_estimator(self) -> TokenEstimator:
        return OpenAITokenEstimator(self.vision_costs, **self.estimator_kwargs)

    def from_provider_format(self, message: Dict[str, Any]) -> MCPMessage:
        """Convert OpenAI message to internal format."""
        if "role" not in message:
            raise ValueError("Message missing required 'role' field")

        role = Role(message["role"])
        content_blocks = []

        # Handle content
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            content_blocks.append(TextContent(text=content))
        elif isinstance(content, list):
            content_blocks.extend(self._convert_content_list(content))

        # Handle tool calls
        tool_calls = message.get("tool_calls", [])
        for tool_call in tool_calls:
            try:
                function_data = tool_call.get("function", {})
                arguments = function_data.get("arguments", "{}")

                try:
                    parsed_args = (
                        json.loads(arguments)
                        if isinstance(arguments, str)
                        else arguments
                    )
                except json.JSONDecodeError:
                    parsed_args = {"raw_arguments": arguments}

                content_blocks.append(
                    ToolUseContent(
                        id=tool_call.get("id", ""),
                        name=function_data.get("name", ""),
                        input=parsed_args,
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to convert tool call: {e}")

        # Handle legacy function calls
        function_call = message.get("function_call")
        if function_call:
            try:
                arguments = function_call.get("arguments", "{}")
                parsed_args = (
                    json.loads(arguments) if isinstance(arguments, str) else arguments
                )

                content_blocks.append(
                    ToolUseContent(
                        id=f"func_{int(time.time())}",
                        name=function_call.get("name", ""),
                        input=parsed_args,
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to convert function call: {e}")

        # Create message
        if not content_blocks:
            return MCPMessage.from_text(role, "")
        elif len(content_blocks) == 1:
            return MCPMessage(
                role=role,
                content=content_blocks[0],
                name=message.get("name"),
                tool_call_id=message.get("tool_call_id"),
                refusal=message.get("refusal"),
            )
        else:
            return MCPMessage(
                role=role,
                content=ExtendedContent.from_blocks(content_blocks),
                name=message.get("name"),
                tool_call_id=message.get("tool_call_id"),
                refusal=message.get("refusal"),
            )

    def _convert_content_list(
        self, content_list: List[Dict[str, Any]]
    ) -> List[ContentBlock]:
        """Convert OpenAI content list."""
        blocks = []

        for part in content_list:
            part_type = part.get("type", "text")

            if part_type == "text":
                text = part.get("text", "")
                if text.strip():
                    blocks.append(TextContent(text=text))

            elif part_type == "image_url":
                image_url = part.get("image_url", {}).get("url", "")
                detail = part.get("image_url", {}).get("detail", "auto")
                if image_url:
                    blocks.extend(self._convert_image_url(image_url, detail))

            elif part_type == "input_audio":
                audio_data = part.get("input_audio", {})
                if audio_data.get("data"):
                    blocks.append(self._convert_audio_data(audio_data))

            elif part_type == "refusal":
                refusal_text = part.get("refusal", "")
                if refusal_text:
                    blocks.append(TextContent(text=f"[Refusal: {refusal_text}]"))

            else:
                # Handle unknown types by preserving in meta
                blocks.append(
                    TextContent(
                        text=f"[Unknown content type: {part_type}]",
                        meta={"original_block": part, "original_type": part_type},
                    )
                )

        return blocks

    def _convert_image_url(
        self, image_url: str, detail: str = "auto"
    ) -> List[ContentBlock]:
        """Convert image URL to content blocks."""
        if image_url.startswith("data:"):
            try:
                header, data = image_url.split(";base64,", 1)
                mime_type = header.replace("data:", "")

                if mime_type in self.SUPPORTED_IMAGE_TYPES:
                    return [
                        ImageContent(
                            data=data,
                            mimeType=mime_type,
                            meta={"detail": detail},  # Preserve detail setting
                        )
                    ]
                else:
                    return [TextContent(text=f"[Unsupported image: {mime_type}]")]
            except ValueError:
                return [TextContent(text="[Malformed image URL]")]
        else:
            # MCP-compliant URL reference
            return [
                EmbeddedResource(
                    resource={"uri": image_url, "mimeType": "image/jpeg"},
                    meta={"origin": "image_url", "detail": detail},
                )
            ]

    def _convert_audio_data(self, audio_data: Dict[str, Any]) -> AudioContent:
        """Convert audio data."""
        format_name = audio_data.get("format", "wav")
        return AudioContent(
            data=audio_data.get("data", ""), mimeType=f"audio/{format_name}"
        )

    def to_provider_format(self, message: MCPMessage) -> Dict[str, Any]:
        """Convert internal message to OpenAI format with strict compliance."""
        # Fix: Tool messages must have string content and "tool" role
        if message.tool_call_id:
            return {
                "role": "tool",
                "tool_call_id": message.tool_call_id,
                "content": str(message.text_content or "No result"),  # Must be string
            }

        role = message.role.value
        msg = {"role": role}

        # Get all content blocks
        content_blocks = message.content_blocks

        # Handle simple text case
        text_blocks = [
            b
            for b in content_blocks
            if isinstance(b, (TextContent, ExtendedContent, ThinkingContent))
        ]
        if (
            len(content_blocks) == 1
            and len(text_blocks) == 1
            and not message.has_multimodal_content
        ):
            if isinstance(text_blocks[0], ThinkingContent):
                msg["content"] = f"[Thinking] {text_blocks[0].thinking}"
            else:
                msg["content"] = text_blocks[0].text
        else:
            # Complex content
            content_parts = []
            tool_calls = []

            for block in content_blocks:
                if (
                    isinstance(block, (TextContent, ExtendedContent))
                    and block.text.strip()
                ):
                    content_parts.append({"type": "text", "text": block.text})

                elif isinstance(block, ThinkingContent):
                    content_parts.append(
                        {"type": "text", "text": f"[Thinking] {block.thinking}"}
                    )

                elif isinstance(block, ImageContent):
                    if block.mimeType in self.SUPPORTED_IMAGE_TYPES:
                        image_url_obj = {
                            "url": f"data:{block.mimeType};base64,{block.data}"
                        }
                        # Restore detail if preserved
                        if block.meta and "detail" in block.meta:
                            image_url_obj["detail"] = block.meta["detail"]
                        content_parts.append(
                            {"type": "image_url", "image_url": image_url_obj}
                        )

                elif isinstance(block, AudioContent):
                    format_name = block.mimeType.split("/")[-1]
                    if format_name in self.SUPPORTED_AUDIO_FORMATS:
                        content_parts.append(
                            {
                                "type": "input_audio",
                                "input_audio": {
                                    "data": block.data,
                                    "format": format_name,
                                },
                            }
                        )

                elif isinstance(block, ToolUseContent):
                    tool_calls.append(
                        {
                            "id": block.id,
                            "type": "function",
                            "function": {
                                "name": block.name,
                                "arguments": json.dumps(block.input),
                            },
                        }
                    )

                elif isinstance(block, EmbeddedResource):
                    # Convert resource back to appropriate format
                    resource = block.resource
                    if resource.get("mimeType", "").startswith("image/"):
                        if "uri" in resource:
                            detail = (
                                block.meta.get("detail", "auto")
                                if block.meta
                                else "auto"
                            )
                            content_parts.append(
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": resource["uri"],
                                        "detail": detail,
                                    },
                                }
                            )

            if content_parts:
                msg["content"] = content_parts
            elif not tool_calls:
                msg["content"] = ""

            if tool_calls and role == "assistant":
                msg["tool_calls"] = tool_calls

        # Add optional fields
        if message.name:
            msg["name"] = message.name
        if message.refusal and role == "assistant":
            msg["refusal"] = message.refusal

        return msg


class AnthropicConverter:
    """Anthropic message converter with thinking blocks support."""

    SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

    def get_provider_name(self) -> str:
        return "anthropic"

    def get_token_estimator(self) -> TokenEstimator:
        return TiktokenEstimator()

    def from_provider_format(self, message: Dict[str, Any]) -> MCPMessage:
        """Convert Anthropic message to internal format."""
        if "role" not in message:
            raise ValueError("Message missing required 'role' field")

        role = Role(message["role"])
        content_blocks = []

        content = message.get("content")
        if isinstance(content, str) and content.strip():
            content_blocks.append(TextContent(text=content))
        elif isinstance(content, list):
            content_blocks.extend(self._convert_content_list(content))

        if not content_blocks:
            return MCPMessage.from_text(role, "")
        elif len(content_blocks) == 1:
            return MCPMessage(role=role, content=content_blocks[0])
        else:
            return MCPMessage(
                role=role, content=ExtendedContent.from_blocks(content_blocks)
            )

    def _convert_content_list(
        self, content_list: List[Dict[str, Any]]
    ) -> List[ContentBlock]:
        """Convert Anthropic content list."""
        blocks = []

        for block_data in content_list:
            block_type = block_data.get("type", "text")

            if block_type == "text":
                text = block_data.get("text", "")
                if text.strip():
                    blocks.append(TextContent(text=text))

            elif block_type == "image":
                source = block_data.get("source", {})
                if source.get("type") == "base64":
                    blocks.append(
                        ImageContent(
                            data=source.get("data", ""),
                            mimeType=source.get("media_type", "image/jpeg"),
                        )
                    )
                elif source.get("type") == "url":
                    # Handle URL-based images
                    blocks.append(
                        EmbeddedResource(
                            resource={
                                "uri": source.get("url", ""),
                                "mimeType": source.get("media_type", "image/jpeg"),
                            },
                            meta={"origin": "anthropic_image_url"},
                        )
                    )

            elif block_type == "tool_use":
                blocks.append(
                    ToolUseContent(
                        id=block_data.get("id", ""),
                        name=block_data.get("name", ""),
                        input=block_data.get("input", {}),
                    )
                )

            elif block_type == "tool_result":
                blocks.append(
                    ToolResultContent(
                        tool_use_id=block_data.get("tool_use_id", ""),
                        content=block_data.get("content", ""),
                        is_error=block_data.get("is_error", False),
                    )
                )

            elif block_type == "thinking":
                blocks.append(
                    ThinkingContent(
                        thinking=block_data.get("thinking", ""),
                        signature=block_data.get("signature", ""),
                    )
                )

            elif block_type == "redacted_thinking":
                blocks.append(
                    ThinkingContent(
                        thinking="[Redacted thinking]",
                        signature=block_data.get("signature", ""),
                        meta={"redacted": True},
                    )
                )

            else:
                # Handle unknown types
                blocks.append(
                    TextContent(
                        text=f"[Unknown block type: {block_type}]",
                        meta={
                            "original_block": block_data,
                            "original_type": block_type,
                        },
                    )
                )

        return blocks

    def to_provider_format(self, message: MCPMessage) -> Dict[str, Any]:
        """Convert internal message to Anthropic format."""
        msg = {"role": message.role.value}

        content_blocks = message.content_blocks
        text_blocks = [
            b
            for b in content_blocks
            if isinstance(b, (TextContent, ExtendedContent, ThinkingContent))
        ]

        if (
            len(content_blocks) == 1
            and len(text_blocks) == 1
            and not message.has_multimodal_content
        ):
            if isinstance(text_blocks[0], ThinkingContent):
                msg["content"] = [
                    {"type": "thinking", "thinking": text_blocks[0].thinking}
                ]
            else:
                msg["content"] = text_blocks[0].text
        else:
            content_parts = []

            for block in content_blocks:
                if (
                    isinstance(block, (TextContent, ExtendedContent))
                    and block.text.strip()
                ):
                    content_parts.append({"type": "text", "text": block.text})

                elif isinstance(block, ThinkingContent):
                    if block.meta and block.meta.get("redacted"):
                        content_parts.append(
                            {
                                "type": "redacted_thinking",
                                "signature": block.signature or "",
                            }
                        )
                    else:
                        content_parts.append(
                            {
                                "type": "thinking",
                                "thinking": block.thinking,
                                "signature": block.signature or "",
                            }
                        )

                elif isinstance(block, ImageContent):
                    if block.mimeType in self.SUPPORTED_IMAGE_TYPES:
                        content_parts.append(
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": block.mimeType,
                                    "data": block.data,
                                },
                            }
                        )

                elif isinstance(block, ToolUseContent):
                    content_parts.append(
                        {
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        }
                    )

                elif isinstance(block, ToolResultContent):
                    content_parts.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.tool_use_id,
                            "content": block.content,
                            "is_error": block.is_error,
                        }
                    )

                elif isinstance(block, EmbeddedResource):
                    # Convert resource back if it's an image URL
                    if block.meta and block.meta.get("origin") == "anthropic_image_url":
                        resource = block.resource
                        content_parts.append(
                            {
                                "type": "image",
                                "source": {
                                    "type": "url",
                                    "url": resource.get("uri", ""),
                                    "media_type": resource.get(
                                        "mimeType", "image/jpeg"
                                    ),
                                },
                            }
                        )

            msg["content"] = content_parts or [{"type": "text", "text": ""}]

        return msg


# === Plugin Registry ===

_CONVERTER_REGISTRY = {}
_TOKEN_ESTIMATOR_REGISTRY = {}


def register_converter(name: str, converter_class: type):
    """Register a converter class with duplicate checking."""
    if name in _CONVERTER_REGISTRY:
        logger.warning(f"Overriding existing converter registration: {name}")
    _CONVERTER_REGISTRY[name] = converter_class


def register_token_estimator(name: str, estimator_class: type):
    """Register a token estimator class with duplicate checking."""
    if name in _TOKEN_ESTIMATOR_REGISTRY:
        logger.warning(f"Overriding existing token estimator registration: {name}")
    _TOKEN_ESTIMATOR_REGISTRY[name] = estimator_class


def load_converters() -> Dict[str, MessageConverter]:
    """Load converters from entry points and registry."""
    converters = {}

    # Load from entry points
    try:
        entry_points = importlib_metadata.entry_points(
            group="managed_context.converters"
        )
        for ep in entry_points:
            try:
                converter_class = ep.load()
                converters[ep.name] = converter_class()
                logger.info(f"Loaded converter plugin: {ep.name}")
            except Exception as e:
                logger.warning(f"Failed to load converter {ep.name}: {e}")
    except Exception as e:
        logger.warning(f"Failed to load entry points: {e}")

    # Load from direct registry (check for conflicts)
    for name, converter_class in _CONVERTER_REGISTRY.items():
        if name in converters:
            logger.warning(f"Entry point converter {name} overridden by registry")
        try:
            converters[name] = converter_class()
        except Exception as e:
            logger.warning(f"Failed to instantiate converter {name}: {e}")

    # Add built-in converters as fallback
    converters.setdefault("openai", OpenAIConverter())
    converters.setdefault("anthropic", AnthropicConverter())

    return converters


def load_token_estimators() -> Dict[str, TokenEstimator]:
    """Load token estimators from entry points and registry."""
    estimators = {}

    # Load from entry points
    try:
        entry_points = importlib_metadata.entry_points(
            group="managed_context.token_estimators"
        )
        for ep in entry_points:
            try:
                estimator_class = ep.load()
                estimators[ep.name] = estimator_class()
            except Exception as e:
                logger.warning(f"Failed to load token estimator {ep.name}: {e}")
    except Exception as e:
        logger.warning(f"Failed to load token estimator entry points: {e}")

    # Load from direct registry
    for name, estimator_class in _TOKEN_ESTIMATOR_REGISTRY.items():
        if name in estimators:
            logger.warning(f"Entry point estimator {name} overridden by registry")
        try:
            estimators[name] = estimator_class()
        except Exception as e:
            logger.warning(f"Failed to instantiate token estimator {name}: {e}")

    # Add built-in estimators with namespaced names
    estimators.setdefault("builtin_tiktoken", TiktokenEstimator())
    estimators.setdefault("builtin_openai", OpenAITokenEstimator())

    return estimators


# Register built-in components
register_converter("builtin_openai", OpenAIConverter)
register_converter("builtin_anthropic", AnthropicConverter)
register_token_estimator("builtin_tiktoken", TiktokenEstimator)
register_token_estimator("builtin_openai_vision", OpenAITokenEstimator)


# === Compression Strategy ===


class CompressionStrategy(ABC):
    """Abstract compression strategy."""

    @abstractmethod
    async def compress_messages(
        self, messages: List[MCPMessage], target_tokens: int, model: str
    ) -> List[MCPMessage]:
        """Compress messages to target token count."""
        ...


class LLMCompressionStrategy(CompressionStrategy):
    """LLM-based compression with timeout handling and error bubbling."""

    def __init__(
        self,
        client_factory: Callable,
        converter: MessageConverter,
        compress_fn: Optional[Callable[[str], Union[str, Callable]]] = None,
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        self.client_factory = client_factory
        self.converter = converter
        self.compress_fn = compress_fn
        self.timeout = timeout
        self.max_retries = max_retries

    async def compress_messages(
        self, messages: List[MCPMessage], target_tokens: int, model: str
    ) -> List[MCPMessage]:
        """Compress messages using LLM."""
        if not messages:
            return messages

        try:
            # Sort by priority and timestamp
            sorted_messages = sorted(
                messages,
                key=lambda m: (m.priority, m.timestamp.timestamp()),
                reverse=True,
            )

            # Determine what to keep vs compress
            keep_messages = []
            compress_messages = []

            estimator = self.converter.get_token_estimator()
            current_tokens = 0
            reserve_tokens = int(target_tokens * 0.3)

            for msg in sorted_messages:
                msg_tokens = estimator.estimate(msg, model)
                if current_tokens + msg_tokens <= target_tokens - reserve_tokens:
                    keep_messages.append(msg)
                    current_tokens += msg_tokens
                else:
                    compress_messages.append(msg)

            # Compress overflow messages
            if compress_messages:
                try:
                    compressed_msg = await self._compress_batch(
                        compress_messages, model
                    )
                    return [compressed_msg] + keep_messages
                except Exception as e:
                    # Bubble up compression errors with context
                    raise ContextCompressionError(
                        f"Failed to compress {len(compress_messages)} messages"
                    ) from e

            return keep_messages

        except ContextCompressionError:
            raise  # Re-raise compression errors
        except Exception as e:
            logger.error(f"Compression strategy error: {e}")
            # Fallback: return recent messages
            return sorted(messages, key=lambda m: m.timestamp, reverse=True)[:3]

    async def _compress_batch(
        self, messages: List[MCPMessage], model: str
    ) -> MCPMessage:
        """Compress a batch of messages."""
        conversation = self._format_conversation(messages)

        prompt = f"""Compress this conversation into a concise summary preserving key facts, context, and decisions:

{conversation}

Summary:"""

        try:
            # Use custom compression function if provided
            if self.compress_fn:
                if inspect.iscoroutinefunction(self.compress_fn):
                    response_text = await self.compress_fn(prompt)
                else:
                    response_text = self.compress_fn(prompt)
            else:
                # Use client for compression with retries
                response_text = await self._make_api_call_with_retry(prompt, model)

            return MCPMessage.from_text(
                Role.SYSTEM,
                f"[COMPRESSED] {response_text}",
                priority=2,
                compressed=True,
                metadata={
                    "original_count": len(messages),
                    "compressed_at": datetime.now().isoformat(),
                    "original_ids": [msg.message_id for msg in messages],
                },
            )

        except Exception as e:
            logger.error(f"LLM compression failed: {e}")
            # Create fallback summary
            recent = sorted(messages, key=lambda m: m.timestamp, reverse=True)[:2]
            summary = "; ".join(
                f"{m.role.value}: {m.text_content[:50]}" for m in recent
            )

            return MCPMessage.from_text(
                Role.SYSTEM, f"[FALLBACK] Recent: {summary}", compressed=True
            )

    def _format_conversation(self, messages: List[MCPMessage]) -> str:
        """Format messages for compression."""
        parts = []
        for msg in sorted(messages, key=lambda m: m.timestamp):
            content = msg.text_content
            if len(content) > 200:
                content = content[:200] + "..."
            parts.append(f"{msg.role.value.upper()}: {content}")
        return "\n".join(parts)

    async def _make_api_call_with_retry(self, prompt: str, model: str) -> str:
        """Make API call with timeout and retry logic."""
        for attempt in range(self.max_retries + 1):
            try:
                return await asyncio.wait_for(
                    self._make_api_call(prompt, model), timeout=self.timeout
                )
            except asyncio.TimeoutError:
                if attempt == self.max_retries:
                    raise ContextCompressionError(
                        f"Compression timed out after {self.timeout}s"
                    )
                logger.warning(
                    f"Compression call timed out, retry {attempt + 1}/{self.max_retries}"
                )
                await asyncio.sleep(2**attempt)  # Exponential backoff
            except Exception as e:
                if attempt == self.max_retries:
                    raise ContextCompressionError(
                        f"Compression failed after {self.max_retries + 1} attempts"
                    ) from e
                logger.warning(
                    f"Compression call failed, retry {attempt + 1}/{self.max_retries}: {e}"
                )
                await asyncio.sleep(2**attempt)

    async def _make_api_call(self, prompt: str, model: str) -> str:
        """Make API call for compression."""
        provider_name = self.converter.get_provider_name()

        if provider_name == "openai":
            return await self._call_openai(prompt, model)
        elif provider_name == "anthropic":
            return await self._call_anthropic(prompt, model)
        else:
            raise NotImplementedError(
                f"Compression not implemented for provider: {provider_name}"
            )

    async def _call_openai(self, prompt: str, model: str) -> str:
        """Call OpenAI API for compression."""
        try:
            client = self.client_factory()
            create_method = client.chat.completions.create

            if inspect.iscoroutinefunction(create_method):
                response = await create_method(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.1,
                )
            else:
                response = create_method(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.1,
                )

            return response.choices[0].message.content or "No response"

        except Exception as e:
            logger.error(f"OpenAI compression call failed: {e}")
            raise

    async def _call_anthropic(self, prompt: str, model: str) -> str:
        """Call Anthropic API for compression."""
        try:
            client = self.client_factory()
            create_method = client.messages.create

            if inspect.iscoroutinefunction(create_method):
                response = await create_method(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                )
            else:
                response = create_method(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                )

            if response.content and len(response.content) > 0:
                return response.content[0].text
            return "No response"

        except Exception as e:
            logger.error(f"Anthropic compression call failed: {e}")
            raise


# === Context Store Interface ===


class ContextStore(ABC):
    """Abstract interface for persistent context storage."""

    @abstractmethod
    async def save_messages(self, context_id: str, messages: List[MCPMessage]) -> None:
        """Save messages for a context."""
        ...

    @abstractmethod
    async def load_messages(self, context_id: str) -> List[MCPMessage]:
        """Load messages for a context."""
        ...

    @abstractmethod
    async def delete_context(self, context_id: str) -> None:
        """Delete a context."""
        ...


class InMemoryContextStore(ContextStore):
    """In-memory context store for development/testing."""

    def __init__(self):
        self._contexts: Dict[str, List[MCPMessage]] = {}
        self._lock = asyncio.Lock()

    async def save_messages(self, context_id: str, messages: List[MCPMessage]) -> None:
        async with self._lock:
            # Use safe_copy to preserve all fields
            self._contexts[context_id] = [msg.safe_copy() for msg in messages]

    async def load_messages(self, context_id: str) -> List[MCPMessage]:
        async with self._lock:
            messages = self._contexts.get(context_id, [])
            return [msg.safe_copy() for msg in messages]

    async def delete_context(self, context_id: str) -> None:
        async with self._lock:
            self._contexts.pop(context_id, None)


# === Managed Context Core ===


class ManagedContext:
    """
    Core context manager with race-safe merge-on-commit.

    Thread safety contract:
    - All methods are thread-safe except shutdown()
    - shutdown() must NOT be called concurrently with other methods
    - Callers MUST invoke shutdown() at process exit to clean up background threads
    """

    def __init__(
        self,
        max_tokens: int = 4000,
        compression_threshold: float = 0.8,
        model: str = "gpt-3.5-turbo",
        converter: Optional[MessageConverter] = None,
        compression_strategy: Optional[CompressionStrategy] = None,
        background_compression: bool = True,
        context_store: Optional[ContextStore] = None,
        context_id: Optional[str] = None,
    ):
        self.max_tokens = max_tokens
        self.compression_threshold = compression_threshold
        self.model = model
        self.converter = converter
        self.compression_strategy = compression_strategy
        self.background_compression = background_compression
        self.context_store = context_store
        self.context_id = context_id or f"ctx_{int(time.time())}_{id(self)}"

        self.messages: List[MCPMessage] = []
        self._lock = threading.RLock()
        self._shutdown_event = threading.Event()
        self._background_task = None
        self._loop = None  # Dedicated event loop for background thread

        # Statistics - only real failures
        self.stats = {
            "total_messages": 0,
            "compressions": 0,
            "tokens_saved": 0,
            "real_errors": 0,
            "compression_errors": 0,  # Track compression-specific errors
        }

        # Always start background task if enabled
        if background_compression:
            self._start_background_compression()

    @classmethod
    def openai(
        cls, client, model: str = "gpt-4", max_tokens: int = 4000, **kwargs
    ) -> tuple[ManagedContext, Any]:
        """
        Convenience constructor for OpenAI clients.
        Returns (context, wrapped_client) tuple for easy access to both.
        """
        converters = load_converters()
        converter = converters.get("openai") or converters.get("builtin_openai")
        if not converter:
            raise ValueError("OpenAI converter not available")

        context = cls(max_tokens=max_tokens, model=model, converter=converter, **kwargs)

        # Set up compression strategy
        if context.compression_strategy is None:

            def client_factory():
                return client

            strategy = LLMCompressionStrategy(client_factory, converter)
            context.set_compression_strategy(strategy)

        wrapped_client = ManagedOpenAIClient(client, context)

        return context, wrapped_client

    @classmethod
    def anthropic(
        cls,
        client,
        model: str = "claude-3-sonnet-20240229",
        max_tokens: int = 4000,
        **kwargs,
    ) -> tuple[ManagedContext, Any]:
        """
        Convenience constructor for Anthropic clients.
        Returns (context, wrapped_client) tuple for easy access to both.
        """
        converters = load_converters()
        converter = converters.get("anthropic") or converters.get("builtin_anthropic")
        if not converter:
            raise ValueError("Anthropic converter not available")

        context = cls(max_tokens=max_tokens, model=model, converter=converter, **kwargs)

        # Set up compression strategy
        if context.compression_strategy is None:

            def client_factory():
                return client

            strategy = LLMCompressionStrategy(client_factory, converter)
            context.set_compression_strategy(strategy)

        wrapped_client = ManagedAnthropicClient(client, context)

        return context, wrapped_client

    def _start_background_compression(self):
        """Start background compression with dedicated event loop."""
        self._background_task = threading.Thread(
            target=self._compression_loop, daemon=True, name="context-compression"
        )
        self._background_task.start()

    def _compression_loop(self):
        """Background compression loop with proper event loop management."""
        # Create dedicated event loop (Python 3.13 compatible)
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            while not self._shutdown_event.wait(timeout=10):
                try:
                    # Check if we have a compression strategy and should compress
                    if self.compression_strategy and self._should_compress():
                        self._loop.run_until_complete(self._compress_if_needed())
                except ContextCompressionError as e:
                    logger.error(f"Background compression error: {e}")
                    self.stats["compression_errors"] += 1
                except Exception as e:
                    logger.error(f"Background compression failed: {e}")
                    self.stats["real_errors"] += 1
        finally:
            # Clean up event loop
            if self._loop and not self._loop.is_closed():
                self._loop.close()

    def set_compression_strategy(self, strategy: CompressionStrategy):
        """Set compression strategy after initialization."""
        self.compression_strategy = strategy
        # Background task will pick it up on next iteration

    def add_message(self, message: MCPMessage):
        """Add message with proper token counting."""
        with self._lock:
            # Calculate token count for current model
            if self.converter:
                estimator = self.converter.get_token_estimator()
                token_count = estimator.estimate(message, self.model)
                message.set_token_count(self.model, token_count)

            self.messages.append(message)
            self.stats["total_messages"] += 1

    def add_provider_message(self, message: Any):
        """Add provider-format message."""
        if not self.converter:
            raise ValueError("No converter available")

        try:
            mcp_message = self.converter.from_provider_format(message)
            self.add_message(mcp_message)
        except Exception as e:
            logger.error(f"Failed to convert provider message: {e}")
            self.stats["real_errors"] += 1
            raise

    def get_messages(self) -> List[Any]:
        """Get messages in provider format."""
        if not self.converter:
            raise ValueError("No converter available")

        with self._lock:
            return [self.converter.to_provider_format(msg) for msg in self.messages]

    def get_token_count(self) -> int:
        """Get current token count."""
        with self._lock:
            return sum(msg.get_token_count(self.model) for msg in self.messages)

    def _should_compress(self) -> bool:
        """Check if compression is needed."""
        current_tokens = self.get_token_count()
        return current_tokens > (self.max_tokens * self.compression_threshold)

    async def _compress_if_needed(self):
        """Compress with race-safe merge-on-commit to prevent message loss."""
        # Step 1: Snapshot messages and their IDs
        with self._lock:
            if not self._should_compress():
                return

            messages_snapshot = [msg.safe_copy() for msg in self.messages]
            snapshot_ids = {msg.message_id for msg in messages_snapshot}
            current_tokens = self.get_token_count()

        # Step 2: Compress without holding lock
        target_tokens = int(self.max_tokens * 0.6)

        try:
            compressed_messages = await self.compression_strategy.compress_messages(
                messages_snapshot, target_tokens, self.model
            )

            # Step 3: Race-safe merge-on-commit
            with self._lock:
                # Find messages added during compression (not in snapshot)
                new_messages = [
                    msg for msg in self.messages if msg.message_id not in snapshot_ids
                ]

                if new_messages:
                    logger.info(
                        f"Merging {len(new_messages)} messages added during compression"
                    )
                    # Merge: new messages + compressed results
                    self.messages = new_messages + compressed_messages
                else:
                    # No new messages, safe to replace
                    self.messages = compressed_messages

                # Update stats
                self.stats["compressions"] += 1
                new_tokens = self.get_token_count()
                self.stats["tokens_saved"] += current_tokens - new_tokens

                logger.info(
                    f"Compression complete: {current_tokens} -> {new_tokens} tokens"
                )

        except ContextCompressionError as e:
            logger.error(f"Compression failed: {e}")
            self.stats["compression_errors"] += 1
            # Don't raise - let background loop continue
        except Exception as e:
            logger.error(f"Compression error: {e}")
            self.stats["real_errors"] += 1

    def shutdown(self):
        """
        Shutdown gracefully. MUST be called at process exit.

        Thread-safety contract: No other methods should be called
        concurrently with shutdown().
        """
        logger.info("Shutting down context manager")
        self._shutdown_event.set()

        if self._background_task:
            self._background_task.join(timeout=10)
            if self._background_task.is_alive():
                logger.warning(
                    "Background task failed to stop - may keep interpreter alive"
                )


# === Proxy Pattern Client Wrappers ===


class ManagedOpenAIClient:
    """Proxy wrapper for OpenAI client with proper API surface."""

    def __init__(self, client, context: ManagedContext):
        self._client = client
        self._context = context

        # C-1 FIX: Capture original method before any patching
        self._original_create = client.chat.completions.create

        # Create proper nested attribute structure
        self.chat = self._create_chat_wrapper()

    def _create_chat_wrapper(self):
        """Create chat wrapper that maintains OpenAI API structure."""

        class ChatWrapper:
            def __init__(self, client, context, original_create):
                self._client = client
                self._context = context
                self._original_create = original_create
                self.completions = self._create_completions_wrapper()

            def _create_completions_wrapper(self):
                class CompletionsWrapper:
                    def __init__(self, client, context, original_create):
                        self._client = client
                        self._context = context
                        self._original_create = original_create

                        # Single method that handles both sync and async
                        if inspect.iscoroutinefunction(original_create):
                            self.create = self._async_create
                        else:
                            self.create = self._sync_create

                    def _sync_create(self, *args, **kwargs):
                        """Synchronous create method."""
                        # Add input messages to context
                        messages = kwargs.get("messages", [])
                        for msg in messages:
                            self._context.add_provider_message(msg)

                        # Use managed messages
                        kwargs["messages"] = self._context.get_messages()

                        # C-1 FIX: Call original method directly, not through client
                        response = self._original_create(*args, **kwargs)

                        # Add response to context
                        self._add_response_to_context(response)

                        return response

                    async def _async_create(self, *args, **kwargs):
                        """Asynchronous create method."""
                        # Add input messages to context
                        messages = kwargs.get("messages", [])
                        for msg in messages:
                            self._context.add_provider_message(msg)

                        # Use managed messages
                        kwargs["messages"] = self._context.get_messages()

                        # C-1 FIX: Call original method directly, not through client
                        response = await self._original_create(*args, **kwargs)

                        # Add response to context
                        self._add_response_to_context(response)

                        return response

                    def _add_response_to_context(self, response):
                        """Add response to context."""
                        try:
                            if hasattr(response, "choices") and response.choices:
                                choice = response.choices[0]
                                if hasattr(choice, "message"):
                                    message = choice.message
                                    response_message = {"role": "assistant"}

                                    if hasattr(message, "content") and message.content:
                                        response_message["content"] = message.content

                                    if (
                                        hasattr(message, "tool_calls")
                                        and message.tool_calls
                                    ):
                                        response_message["tool_calls"] = [
                                            {
                                                "id": tc.id,
                                                "type": tc.type,
                                                "function": {
                                                    "name": tc.function.name,
                                                    "arguments": tc.function.arguments,
                                                },
                                            }
                                            for tc in message.tool_calls
                                        ]

                                    if hasattr(message, "refusal") and message.refusal:
                                        response_message["refusal"] = message.refusal

                                    self._context.add_provider_message(response_message)

                        except Exception as e:
                            logger.warning(
                                f"Failed to add OpenAI response to context: {e}"
                            )

                return CompletionsWrapper(
                    self._client, self._context, self._original_create
                )

        return ChatWrapper(self._client, self._context, self._original_create)

    # Convenience method for backward compatibility
    def chat_completions_create(self, *args, **kwargs):
        """Flat method for convenience."""
        return self.chat.completions.create(*args, **kwargs)

    def __getattr__(self, name):
        """Delegate other attributes to wrapped client."""
        return getattr(self._client, name)


class ManagedAnthropicClient:
    """Proxy wrapper for Anthropic client."""

    def __init__(self, client, context: ManagedContext):
        self._client = client
        self._context = context

        # C-1 FIX: Capture original method before any patching
        self._original_create = client.messages.create

        self.messages = self._create_messages_wrapper()

    def _create_messages_wrapper(self):
        """Create messages wrapper."""

        class MessagesWrapper:
            def __init__(self, client, context, original_create):
                self._client = client
                self._context = context
                self._original_create = original_create

                # Handle both sync and async
                if inspect.iscoroutinefunction(original_create):
                    self.create = self._async_create
                else:
                    self.create = self._sync_create

            def _sync_create(self, *args, **kwargs):
                """Synchronous create."""
                # Add input messages to context
                messages = kwargs.get("messages", [])
                for msg in messages:
                    self._context.add_provider_message(msg)

                # Use managed messages
                kwargs["messages"] = self._context.get_messages()

                # C-1 FIX: Call original method directly
                response = self._original_create(*args, **kwargs)
                self._add_response_to_context(response)
                return response

            async def _async_create(self, *args, **kwargs):
                """Asynchronous create."""
                # Add input messages to context
                messages = kwargs.get("messages", [])
                for msg in messages:
                    self._context.add_provider_message(msg)

                # Use managed messages
                kwargs["messages"] = self._context.get_messages()

                # C-1 FIX: Call original method directly
                response = await self._original_create(*args, **kwargs)
                self._add_response_to_context(response)
                return response

            def _add_response_to_context(self, response):
                """Add Anthropic response to context."""
                try:
                    if hasattr(response, "content"):
                        response_msg = {"role": "assistant", "content": []}
                        for block in response.content:
                            if hasattr(block, "type") and block.type == "text":
                                response_msg["content"].append(
                                    {"type": "text", "text": block.text}
                                )
                            elif hasattr(block, "type") and block.type == "tool_use":
                                response_msg["content"].append(
                                    {
                                        "type": "tool_use",
                                        "id": block.id,
                                        "name": block.name,
                                        "input": block.input,
                                    }
                                )

                        if (
                            len(response_msg["content"]) == 1
                            and response_msg["content"][0]["type"] == "text"
                        ):
                            response_msg["content"] = response_msg["content"][0]["text"]

                        self._context.add_provider_message(response_msg)

                except Exception as e:
                    logger.warning(f"Failed to add Anthropic response to context: {e}")

        return MessagesWrapper(self._client, self._context, self._original_create)

    def __getattr__(self, name):
        """Delegate other attributes to wrapped client."""
        return getattr(self._client, name)


# === Factory Functions with Plugin Support ===


def managed_openai_client(client, **kwargs):
    """Create managed OpenAI client using plugin registry."""
    converters = load_converters()
    converter = converters.get("openai") or converters.get("builtin_openai")
    if not converter:
        raise ValueError("OpenAI converter not available in plugin registry")

    context = ManagedContext(converter=converter, **kwargs)

    # Set compression strategy after context creation
    if context.compression_strategy is None:

        def client_factory():
            return client

        strategy = LLMCompressionStrategy(client_factory, converter)
        context.set_compression_strategy(strategy)

    return ManagedOpenAIClient(client, context)


def managed_anthropic_client(client, **kwargs):
    """Create managed Anthropic client using plugin registry."""
    converters = load_converters()
    converter = converters.get("anthropic") or converters.get("builtin_anthropic")
    if not converter:
        raise ValueError("Anthropic converter not available in plugin registry")

    context = ManagedContext(converter=converter, **kwargs)

    # Set compression strategy after context creation
    if context.compression_strategy is None:

        def client_factory():
            return client

        strategy = LLMCompressionStrategy(client_factory, converter)
        context.set_compression_strategy(strategy)

    return ManagedAnthropicClient(client, context)


# === Monkey-Patch Facade (C-1 FIXED) ===


def patch_openai(client, **ctx_kwargs) -> ManagedContext:
    """
    Monkey-patch OpenAI client in-place for opt-in compatibility.

    WARNING: This modifies the client globally. Use managed_openai_client()
    for safer isolation.

    Returns the ManagedContext for access to stats and control.
    """
    converters = load_converters()
    converter = converters.get("openai") or converters.get("builtin_openai")
    if not converter:
        raise ValueError("OpenAI converter not available")

    # Create context
    context = ManagedContext(converter=converter, **ctx_kwargs)

    # Set up compression strategy
    if context.compression_strategy is None:

        def client_factory():
            return client

        strategy = LLMCompressionStrategy(client_factory, converter)
        context.set_compression_strategy(strategy)

    # Store original method
    original_create = client.chat.completions.create

    def patched_create(*args, **kwargs):
        """Patched create method that intercepts calls."""
        # Add input messages to context
        messages = kwargs.get("messages", [])
        for msg in messages:
            context.add_provider_message(msg)

        # Use managed messages
        kwargs["messages"] = context.get_messages()

        # Call original method
        if inspect.iscoroutinefunction(original_create):

            async def async_wrapper():
                response = await original_create(*args, **kwargs)
                _add_openai_response_to_context(response, context)
                return response

            return async_wrapper()
        else:
            response = original_create(*args, **kwargs)
            _add_openai_response_to_context(response, context)
            return response

    # Replace method
    client.chat.completions.create = patched_create

    return context


def patch_anthropic(client, **ctx_kwargs) -> ManagedContext:
    """
    Monkey-patch Anthropic client in-place for opt-in compatibility.

    WARNING: This modifies the client globally. Use managed_anthropic_client()
    for safer isolation.

    Returns the ManagedContext for access to stats and control.
    """
    converters = load_converters()
    converter = converters.get("anthropic") or converters.get("builtin_anthropic")
    if not converter:
        raise ValueError("Anthropic converter not available")

    # Create context
    context = ManagedContext(converter=converter, **ctx_kwargs)

    # Set up compression strategy
    if context.compression_strategy is None:

        def client_factory():
            return client

        strategy = LLMCompressionStrategy(client_factory, converter)
        context.set_compression_strategy(strategy)

    # Store original method
    original_create = client.messages.create

    def patched_create(*args, **kwargs):
        """Patched create method that intercepts calls."""
        # Add input messages to context
        messages = kwargs.get("messages", [])
        for msg in messages:
            context.add_provider_message(msg)

        # Use managed messages
        kwargs["messages"] = context.get_messages()

        # Call original method
        if inspect.iscoroutinefunction(original_create):

            async def async_wrapper():
                response = await original_create(*args, **kwargs)
                _add_anthropic_response_to_context(response, context)
                return response

            return async_wrapper()
        else:
            response = original_create(*args, **kwargs)
            _add_anthropic_response_to_context(response, context)
            return response

    # Replace method
    client.messages.create = patched_create

    return context


def _add_openai_response_to_context(response, context: ManagedContext):
    """Helper to add OpenAI response to context."""
    try:
        if hasattr(response, "choices") and response.choices:
            choice = response.choices[0]
            if hasattr(choice, "message"):
                message = choice.message
                response_message = {"role": "assistant"}

                if hasattr(message, "content") and message.content:
                    response_message["content"] = message.content

                if hasattr(message, "tool_calls") and message.tool_calls:
                    response_message["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in message.tool_calls
                    ]

                if hasattr(message, "refusal") and message.refusal:
                    response_message["refusal"] = message.refusal

                context.add_provider_message(response_message)

    except Exception as e:
        logger.warning(f"Failed to add OpenAI response to context: {e}")


def _add_anthropic_response_to_context(response, context: ManagedContext):
    """Helper to add Anthropic response to context."""
    try:
        if hasattr(response, "content"):
            response_msg = {"role": "assistant", "content": []}
            for block in response.content:
                if hasattr(block, "type") and block.type == "text":
                    response_msg["content"].append({"type": "text", "text": block.text})
                elif hasattr(block, "type") and block.type == "tool_use":
                    response_msg["content"].append(
                        {
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        }
                    )

            if (
                len(response_msg["content"]) == 1
                and response_msg["content"][0]["type"] == "text"
            ):
                response_msg["content"] = response_msg["content"][0]["text"]

            context.add_provider_message(response_msg)

    except Exception as e:
        logger.warning(f"Failed to add Anthropic response to context: {e}")


# === Persistence Support ===


class FileContextStore(ContextStore):
    """File-based context store using JSON."""

    def __init__(self, base_path: str = "./contexts"):
        import os

        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        self._lock = asyncio.Lock()

    def _get_context_path(self, context_id: str) -> str:
        import os

        return os.path.join(self.base_path, f"{context_id}.json")

    async def save_messages(self, context_id: str, messages: List[MCPMessage]) -> None:
        async with self._lock:
            try:
                data = {
                    "context_id": context_id,
                    "saved_at": datetime.now().isoformat(),
                    "messages": [msg.model_dump(mode="json") for msg in messages],
                }

                path = self._get_context_path(context_id)
                with open(path, "w") as f:
                    json.dump(data, f, indent=2)

            except Exception as e:
                logger.error(f"Failed to save context {context_id}: {e}")
                raise

    async def load_messages(self, context_id: str) -> List[MCPMessage]:
        async with self._lock:
            try:
                path = self._get_context_path(context_id)

                if not os.path.exists(path):
                    return []

                with open(path, "r") as f:
                    data = json.load(f)

                messages = []
                for msg_data in data.get("messages", []):
                    try:
                        messages.append(MCPMessage.model_validate(msg_data))
                    except Exception as e:
                        logger.warning(f"Failed to load message: {e}")

                return messages

            except Exception as e:
                logger.error(f"Failed to load context {context_id}: {e}")
                return []

    async def delete_context(self, context_id: str) -> None:
        async with self._lock:
            try:
                import os

                path = self._get_context_path(context_id)
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                logger.error(f"Failed to delete context {context_id}: {e}")


# Update the factory function
def create_context_store(store_type: str, **config) -> ContextStore:
    """Factory for creating context stores."""
    if store_type == "memory":
        return InMemoryContextStore()
    elif store_type == "file":
        return FileContextStore(**config)
    else:
        raise ValueError(f"Unknown store type: {store_type}")


# === Module Cleanup ===

# Global registry of contexts for cleanup
_ACTIVE_CONTEXTS = set()


def _register_context(context: ManagedContext):
    """Register context for cleanup."""
    _ACTIVE_CONTEXTS.add(context)


def _unregister_context(context: ManagedContext):
    """Unregister context."""
    _ACTIVE_CONTEXTS.discard(context)


def _cleanup_all_contexts():
    """Cleanup all active contexts."""
    for context in list(_ACTIVE_CONTEXTS):
        try:
            context.shutdown()
        except Exception as e:
            logger.warning(f"Failed to shutdown context: {e}")
    _ACTIVE_CONTEXTS.clear()


# Register cleanup at module level
atexit.register(_cleanup_all_contexts)

# Update ManagedContext to register/unregister itself
original_init = ManagedContext.__init__


def patched_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    _register_context(self)


def patched_shutdown(self):
    """Enhanced shutdown that unregisters context."""
    try:
        self._shutdown_event.set()

        if self._background_task:
            self._background_task.join(timeout=10)
            if self._background_task.is_alive():
                logger.warning(
                    "Background task failed to stop - may keep interpreter alive"
                )
    finally:
        _unregister_context(self)


ManagedContext.__init__ = patched_init
ManagedContext.shutdown = patched_shutdown


# === Version and Metadata ===

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Managed context for LLM APIs with automatic compression"
