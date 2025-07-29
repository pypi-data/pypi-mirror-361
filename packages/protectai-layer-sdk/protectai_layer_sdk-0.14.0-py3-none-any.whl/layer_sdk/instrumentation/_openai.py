import json
from typing import Dict, List, Optional
from datetime import datetime, timezone
from dataclasses import asdict

import wrapt

from ._base import BaseInstrumentor
from .._utils import get_module_version, is_module_version_more_than
from ..logger import logger
from ..schemas import SessionActionKind, SessionActionError, SessionActionRequest, SessionActionScanner


class OpenAIInstrumentation(BaseInstrumentor):
    """Instrumentation class for OpenAI SDK."""

    def supports(self) -> bool:
        """Check if the OpenAI SDK is supported."""
        version_correct = is_module_version_more_than("openai", "1.40.0")

        if version_correct is None:
            return False

        return version_correct

    def instrument(self):
        """Instrument the OpenAI SDK."""
        self._instrument_chat_completion()
        self._instrument_embedding()
        self._instrument_moderation()

    def _extract_session_id(self, kwargs: dict) -> Optional[str]:
        return kwargs.get("extra_headers", {}).get("Layer-Session-Id")

    def _create_or_append(
            self,
            session_id: Optional[str],
            actions: List[SessionActionRequest],
    ) -> str:
        if session_id:
            for action in actions:
                self._layer.append_action(
                    session_id,
                    **asdict(action),
                )

                logger.debug(f"Appended {action.kind.value} action to '{session_id}' session")

            return session_id

        logger.debug(f"No session id was provided. "
                     f"Creating a new session with {len(actions)} actions")

        new_session_id = self._layer.create_session(
            attributes={
                "source": "instrumentation.openai",
                "openai.version": get_module_version("openai")
            },
            actions=actions,
        )

        return new_session_id

    def _process_completion_stream(self, session_id, start_time, result):
        attrs = {
            "stream": "true",
            "chunk.count": 0,
        }

        completion_content = ""
        completion_role = ""
        tool_calls_buffer: dict[int, dict] = {}
        for chunk in result:
            if len(chunk.choices) > 0:
                choice = chunk.choices[0]
                if not hasattr(choice, "delta"):
                    continue
                    
                if hasattr(choice.delta, "tool_calls") and choice.delta.tool_calls:
                    for tc in choice.delta.tool_calls:
                        idx = tc.index
                        
                        if tc.id is not None:
                            tool_calls_buffer[idx] = {
                                "id": tc.id,
                                "name": tc.function.name,
                                "arguments": ""
                            }

                        # append any argument‐string fragment
                        if tc.function.arguments:
                            buf = tool_calls_buffer.get(idx)
                            if buf:
                                buf["arguments"] += tc.function.arguments

                if hasattr(choice.delta, "content"):
                    content = choice.delta.content
                    if content:
                        completion_content += content

                if hasattr(choice.delta, "role"):
                    role = choice.delta.role
                    if role:
                        completion_role = role
                
                attrs["model.id"] = chunk.model
                attrs["chunk.count"] += 1

                yield chunk
                
        if completion_role and completion_content:
            self._create_or_append(session_id, [
                SessionActionRequest(
                    kind=SessionActionKind.COMPLETION_OUTPUT,
                    start_time=start_time,
                    end_time=datetime.now(timezone.utc),
                    attributes=attrs,
                    data={
                        "messages": [
                            {
                                "content": completion_content,
                                "role": completion_role,
                            }
                        ],
                    },
                )
            ])
        
        if len(tool_calls_buffer) > 0:
            tool_calls = []
            for idx, buf in tool_calls_buffer.items():
                try:
                    tool_calls.append({
                        "id": buf['id'],
                        "name": buf['name'],
                        "arguments": json.loads(buf['arguments']),
                    })
                except Exception:  # noqa: PERF203
                    # If the tool call hallucinates, we don't provide arguments
                    tool_calls.append({
                        "id": buf['id'],
                        "name": buf['name'],
                        "arguments": {},
                    })

            self._create_or_append(session_id, [
                SessionActionRequest(
                    kind=SessionActionKind.COMPLETION_TOOL_CALL,
                    start_time=start_time,
                    end_time=datetime.now(timezone.utc),
                    attributes=attrs,
                    data={
                        "tools": tool_calls,
                    },
                )
            ])
        
    def _get_completion_prompt_attributes(self, kwargs) -> Dict:
        attrs = {
            "model.id": kwargs.get("model"),
        }

        attr_keys = [
            "max_tokens",
            "temperature",
            "frequency_penalty",
            "max_completion_tokens",
            "n",
            "presence_penalty",
            "stop",
            "seed",
            "top_p",
            "user",
            "parallel_tool_calls",
            "stream",
        ]
        for key in attr_keys:
            if key not in kwargs or kwargs[key] is None:
                continue

            attrs[f"model.{key}"] = str(kwargs[key])

        attr_formatted_keys = [
            "tools",
            "metadata",
            "response_format",
            "modalities",
            "audio"
        ]
        for key in attr_formatted_keys:
            if key not in kwargs or kwargs[key] is None:
                continue

            try:
                attrs[f"model.{key}"] = json.dumps(kwargs[key])
            except Exception:
                continue
                
        return attrs
    
    def _get_completion_prompt_actions(self, kwargs) -> List[SessionActionRequest]:
        attrs = self._get_completion_prompt_attributes(kwargs)
        
        prompt_messages = []
        actions = []
        for message in kwargs.get("messages", []):
            if "content" not in message:
                prompt_messages = []  # Reset the prompt messages if we encounter it's a tool call
                continue
            
            if isinstance(message.get("content"), str):
                prompt_messages.append({
                    "role": message.get("role"),
                    "content": message.get("content"),
                    "name": message.get("name", ""),
                    "tool_call_id": message.get("tool_call_id", None),
                })

                continue

            content_items = []
            for content_part in message.content:
                content_type = content_part.get("type")
                if content_type == "input_audio":
                    content_items.append({
                        "type": "audio",
                        "audio_data": content_part.get("input_audio").get("data"),
                        "audio_format": content_part.get("input_audio").get("format"),
                    })
                    
                if content_type == "text":
                    content_items.append({
                        "type": "text",
                        "text": content_part.get("text"),
                    })
                    
                if content_type == "image_url":
                    content_items.append({
                        "type": "image_url",
                        "image_url": content_part.get("image_url").get("url"),
                    })
                    
                if content_type == "file":
                    content_items.append({
                        "type": "file",
                        "file_name": content_part.get("file").get("filename"),
                        "file_data": content_part.get("file").get("file_data"),
                    })
            
            actions.append(SessionActionRequest(
                kind=SessionActionKind.COMPLETION_PROMPT_ATTACHMENT,
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc),
                attributes=attrs,
                data={
                    "role": message.get("role"),
                    "name": message.get("name", ""),
                    "tool_call_id": message.get("tool_call_id", None),
                    "content": content_items,
                }
            ))

        if len(prompt_messages) > 0:
            actions.append(SessionActionRequest(
                kind=SessionActionKind.COMPLETION_PROMPT,
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc),
                attributes=attrs,
                data={
                    "messages": prompt_messages,
                },
            ))
            
        return actions
    
    def _get_completion_output(self, start_time, result) -> List[SessionActionRequest]:
        scanners = None
        messages = []
        tool_calls = []
        
        if result.usage is not None:
            scanners = [
                SessionActionScanner(
                    name="usage",
                    data={
                        "prompt_tokens": result.usage.prompt_tokens,
                        "completion_tokens": result.usage.completion_tokens,
                        "total_tokens": result.usage.total_tokens,
                    },
                )
            ]
            
        attrs = {
            "model.created": result.created,
            "model.id": result.model,
            "model.completion_id": result.id,
        }
        for choice in result.choices:            
            if choice.message.tool_calls is not None:
                try:
                    tool_calls.extend([{
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": json.loads(tool_call.function.arguments),
                    } for tool_call in choice.message.tool_calls])
                except Exception:
                    # If the tool call hallucinates, we don't provide arguments
                    tool_calls.extend([{
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": {},
                    } for tool_call in choice.message.tool_calls])
            
            if choice.message.content is not None:
                messages.append({
                    "content": choice.message.content,
                    "role": choice.message.role,
                })

        actions = []
        if len(messages) > 0:
            actions.append(SessionActionRequest(
                kind=SessionActionKind.COMPLETION_OUTPUT,
                start_time=start_time,
                end_time=datetime.now(timezone.utc),
                attributes=attrs,
                data={
                    "messages": messages,
                },
                scanners=scanners,
            ))
            
        if len(tool_calls) > 0:
            actions.append(SessionActionRequest(
                kind=SessionActionKind.COMPLETION_TOOL_CALL,
                start_time=start_time,
                end_time=datetime.now(timezone.utc),
                attributes=attrs,
                data={
                    "tools": tool_calls,
                },
                scanners=scanners,
            ))
        
        return actions

    def _instrument_chat_completion(self):
        @wrapt.patch_function_wrapper('openai.resources.chat.completions', 'Completions.create')
        def wrapper(wrapped, instance, args, kwargs):
            actions = self._get_completion_prompt_actions(kwargs)
            session_id = self._create_or_append(self._extract_session_id(kwargs), actions)

            result = None
            exception_to_raise = None
            start_time = datetime.now(timezone.utc)
            try:
                result = wrapped(*args, **kwargs)
            except Exception as e:
                exception_to_raise = e

            if exception_to_raise or result is None:
                self._create_or_append(session_id, [
                    SessionActionRequest(
                        kind=SessionActionKind.COMPLETION_OUTPUT,
                        start_time=start_time,
                        end_time=datetime.now(timezone.utc),
                        error=SessionActionError(message=str(exception_to_raise))
                    )
                ])

                raise exception_to_raise  # type: ignore

            is_stream = kwargs.get("stream", False)
            if is_stream:
                return self._process_completion_stream(session_id, start_time, result)

            self._create_or_append(session_id, self._get_completion_output(start_time, result))

            return result

    def _instrument_embedding(self):
        @wrapt.patch_function_wrapper('openai.resources.embeddings', 'Embeddings.create')
        def wrapped_embedding_create(wrapped, instance, args, kwargs):
            error = None
            exception_to_raise = None
            result = None

            start_time = datetime.now(timezone.utc)
            try:
                result = wrapped(*args, **kwargs)  # type: ignore
            except Exception as e:
                exception_to_raise = e
                error = SessionActionError(message=str(e))
            finally:
                end_time = datetime.now(timezone.utc)

            scanners = None
            if error is None:
                scanners = [
                    SessionActionScanner(
                        name="usage",
                        data={
                            "prompt_tokens": result.usage.prompt_tokens,  # type: ignore[reportOptionalMemberAccess]
                            "total_tokens": result.usage.total_tokens,  # type: ignore[reportOptionalMemberAccess]
                        },
                    )
                ]

            embedding_input = kwargs.get("input")
            if isinstance(embedding_input, str):
                embedding_input = [embedding_input]

            attributes = {
                "model.id": kwargs.get("model"),
                "model.encoding_format": kwargs.get("encoding_format", "float"),
            }

            if "user" in kwargs:
                attributes["model.user"] = kwargs.get("user")

            action = SessionActionRequest(
                kind=SessionActionKind.EMBEDDINGS,
                start_time=start_time,
                end_time=end_time,
                attributes=attributes,
                data={
                    "input": embedding_input,
                },
                scanners=scanners,
                error=error
            )

            self._create_or_append(self._extract_session_id(kwargs), [action])

            if exception_to_raise:
                raise exception_to_raise

            return result

    def _instrument_moderation(self):
        @wrapt.patch_function_wrapper('openai.resources.moderations', 'Moderations.create')
        def wrapped_moderation_create(wrapped, instance, args, kwargs):
            error = None
            exception_to_raise = None
            result = None

            start_time = datetime.now(timezone.utc)
            try:
                result = wrapped(*args, **kwargs)
            except Exception as e:
                exception_to_raise = e
                error = SessionActionError(message=str(e))
            finally:
                end_time = datetime.now(timezone.utc)

            scanners = None
            if error is None and len(result.results) > 0:  # type: ignore[reportOptionalMemberAccess]
                scanners = []
                for index, item in enumerate(result.results):  # type: ignore[reportOptionalMemberAccess]
                    scanners.append(SessionActionScanner(
                        name=f"openai_moderation_{index}",
                        data=item.categories.to_dict(),
                    ))

            moderation_input = kwargs.get("input")
            if isinstance(moderation_input, str):
                moderation_input = [moderation_input]

            action = SessionActionRequest(
                kind=SessionActionKind.MODERATION,
                start_time=start_time,
                end_time=end_time,
                attributes={
                    "model.id": kwargs.get("model", "text-moderation-latest"),
                },
                data={
                    "input": moderation_input,
                },
                scanners=scanners,
                error=error
            )

            self._create_or_append(self._extract_session_id(kwargs), [action])

            if exception_to_raise:
                raise exception_to_raise

            return result
