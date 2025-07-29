from assistant_stream.assistant_stream_chunk import (
    AssistantStreamChunk,
)
import json
from typing import AsyncGenerator
from assistant_stream.serialization.assistant_stream_response import (
    AssistantStreamResponse,
)
from assistant_stream.serialization.stream_encoder import StreamEncoder


class DataStreamEncoder(StreamEncoder):
    def __init__(self):
        pass

    def encode_chunk(self, chunk: AssistantStreamChunk) -> str:
        if chunk.type == "text-delta":
            return f"0:{json.dumps(chunk.text_delta)}\n"
        elif chunk.type == "reasoning-delta":
            return f"g:{json.dumps(chunk.reasoning_delta)}\n"
        elif chunk.type == "tool-call-begin":
            return f'b:{json.dumps({ "toolCallId": chunk.tool_call_id, "toolName": chunk.tool_name })}\n'
        elif chunk.type == "tool-call-delta":
            return f'c:{json.dumps({ "toolCallId": chunk.tool_call_id, "argsTextDelta": chunk.args_text_delta })}\n'
        elif chunk.type == "tool-result":
            res = {"toolCallId": chunk.tool_call_id, "result": chunk.result}
            if chunk.artifact is not None:
                res["artifact"] = chunk.artifact
            if chunk.is_error:
                res["isError"] = chunk.is_error
            return f"a:{json.dumps(res)}\n"
        elif chunk.type == "data":
            return f"2:{json.dumps([chunk.data])}\n"
        elif chunk.type == "error":
            return f"3:{json.dumps(chunk.error)}\n"
        elif chunk.type == "source":
            source_data = {
                "sourceType": chunk.source_type,
                "id": chunk.id,
                "url": chunk.url
            }
            if chunk.title is not None:
                source_data["title"] = chunk.title
            return f"h:{json.dumps(source_data)}\n"
        elif chunk.type == "update-state":
            return f"aui-state:{json.dumps(chunk.operations)}\n"

    def get_media_type(self) -> str:
        return "text/plain"

    async def encode_stream(
        self, stream: AsyncGenerator[AssistantStreamChunk, None]
    ) -> AsyncGenerator[str, None]:
        async for chunk in stream:
            encoded = self.encode_chunk(chunk)
            if encoded is None:
                continue
            yield encoded


class DataStreamResponse(AssistantStreamResponse):
    def __init__(
        self,
        stream: AsyncGenerator[AssistantStreamChunk, None],
    ):
        super().__init__(stream, DataStreamEncoder())
