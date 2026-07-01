# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import uuid

import google.auth
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, Artifact, Message, Role, TaskArtifactUpdateEvent, TaskState, TaskStatus, TaskStatusUpdateEvent
from a2a.server.agent_execution import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils.constants import (
    AGENT_CARD_WELL_KNOWN_PATH,
    EXTENDED_AGENT_CARD_PATH,
)
from fastapi import FastAPI
from google.adk.a2a.executor.a2a_agent_executor import A2aAgentExecutor
from google.adk.a2a.converters.utils import _get_adk_metadata_key
from google.adk.artifacts import GcsArtifactService, InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.cloud import logging as google_cloud_logging
from google.genai import types as genai_types
from a2a import types as a2a_types
from a2ui.schema.constants import VERSION_0_8
from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.parser.streaming import A2uiStreamParser
from a2ui.parser.response_part import ResponsePart
from a2ui.a2a.parts import create_a2ui_part as _original_create_a2ui_part
from a2ui.a2a.extension import get_a2ui_agent_extension

from .agent import app as adk_app

def convert_a2a_request_to_adk_run_args(request: RequestContext) -> dict:
    user_id = f'A2A_USER_{request.context_id}'
    if request.call_context and request.call_context.user and request.call_context.user.user_name:
        user_id = request.call_context.user.user_name
    parts = []
    if request.message and request.message.parts:
        for p in request.message.parts:
            if hasattr(p, 'root') and isinstance(p.root, a2a_types.TextPart):
                parts.append(genai_types.Part.from_text(text=p.root.text))
            else:
                parts.append(genai_types.Part.from_text(text=str(p)))
    return {
        'user_id': user_id,
        'session_id': request.context_id,
        'new_message': genai_types.Content(role='user', parts=parts),
        'run_config': None,
    }

os.environ["OTEL_PYTHON_DISABLED_INSTRUMENTATIONS"] = "httpx"

try:
    _, project_id = google.auth.default()
    logging_client = google_cloud_logging.Client()
    logger = logging_client.logger(__name__)
except Exception:
    logger = logging.getLogger(__name__)

logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")
artifact_service = (
    GcsArtifactService(bucket_name=logs_bucket_name)
    if logs_bucket_name
    else InMemoryArtifactService()
)

runner = Runner(
    app=adk_app,
    artifact_service=artifact_service,
    session_service=InMemorySessionService(),
)

a2ui_schema_manager = A2uiSchemaManager(version=VERSION_0_8, catalogs=[BasicCatalog.get_config(version=VERSION_0_8)])
a2ui_selected_catalog = a2ui_schema_manager.get_selected_catalog()

def clean_a2ui_dict(d):
    """
    再帰的に辞書を走査し、A2UI (v0.8) の標準スキーマに含まれない非標準プロパティ（'styles'など）
    を検出して根こそぎ完全消去するクレンジングフィルター。
    """
    if isinstance(d, dict):
        if "styles" in d:
            del d["styles"]
        for k, v in list(d.items()):
            clean_a2ui_dict(v)
    elif isinstance(d, list):
        for item in d:
            clean_a2ui_dict(item)

class AdkAgentToA2AExecutor(A2aAgentExecutor):
    async def _handle_request(self, context: RequestContext, event_queue: EventQueue) -> None:
        runner = await self._resolve_runner()
        run_args = convert_a2a_request_to_adk_run_args(context)

        session_id = run_args['session_id']
        user_id = run_args['user_id']
        session = await runner.session_service.get_session(app_name=runner.app_name, user_id=user_id, session_id=session_id)
        
        token = None
        if hasattr(context, 'call_context') and context.call_context:
            call_context_state = context.call_context.state if hasattr(context.call_context, 'state') else {}
            if isinstance(call_context_state, dict) and 'headers' in call_context_state:
                headers = call_context_state['headers']
                if 'authorization' in headers:
                    auth_header = headers['authorization']
                    if auth_header.startswith("Bearer "):
                        token = auth_header[7:]
        if token:
            import builtins
            builtins._workspace_oauth_token = token
            
        if session is None:
            session = await runner.session_service.create_session(app_name=runner.app_name, user_id=user_id, session_id=session_id)
        else:
            run_args['session_id'] = session.id

        # 進捗ローディングカード（ヘッドバンドドロイド君ロゴ付き）の送信
        try:
            progress_items = [
                {
                    "beginRendering": {
                        "surfaceId": "slideexpert-progress-surface",
                        "root": "progress-card-root"
                    }
                },
                {
                    "surfaceUpdate": {
                        "surfaceId": "slideexpert-progress-surface",
                        "components": [
                            {
                                "id": "progress-card-root",
                                "component": {
                                    "Card": {
                                        "child": "progress-col"
                                    }
                                }
                            },
                            {
                                "id": "progress-col",
                                "component": {
                                    "Column": {
                                        "children": {
                                            "explicitList": [
                                                "progress-logo",
                                                "progress-title",
                                                "progress-spinner-text"
                                            ]
                                        }
                                    }
                                }
                            },
                            {
                                "id": "progress-logo",
                                "component": {
                                    "Image": {
                                        "url": "https://storage.googleapis.com/agentspace-469000-agentlogo/slideexpert-icon.png",
                                        "altText": { "literalString": "SlideExpert Logo" },
                                        "fit": "contain"
                                    }
                                }
                            },
                            {
                                "id": "progress-title",
                                "component": {
                                    "Text": {
                                        "text": { "literalString": "SlideExpert" },
                                        "usageHint": "h2"
                                    }
                                }
                            },
                            {
                                "id": "progress-spinner-text",
                                "component": {
                                    "Text": {
                                        "text": { "literalString": "⏳ Googleスライド資料をプロフェッショナルに作成しています。少々お待ちください..." },
                                        "usageHint": "body"
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
            
            progress_parts = []
            for item in progress_items:
                progress_parts.append(_original_create_a2ui_part(item))
                
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=context.task_id,
                    context_id=context.context_id,
                    status=TaskStatus(
                        state=TaskState.working,
                        message=Message(
                            message_id=str(uuid.uuid4()),
                            role=Role.agent,
                            parts=progress_parts
                        ),
                        timestamp=datetime.now(timezone.utc).isoformat()
                    ),
                    final=False
                )
            )
        except Exception as e:
            print(f"[PROGRESS CARD ERROR] Failed to send progress card: {e}")
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=context.task_id,
                    status=TaskStatus(state=TaskState.working, timestamp=datetime.now(timezone.utc).isoformat()),
                    context_id=context.context_id,
                    final=False,
                )
            )

        import re
        artifact_text_parts = []
        artifact_media_parts = []
        progress_deleted = False

        async for adk_event in runner.run_async(**run_args):
            content = getattr(adk_event, 'content', None)
            if content and hasattr(content, 'parts'):
                for part in content.parts:
                    if part.text:
                        print(f"[RAW LLM RESP] Length: {len(part.text)}")
                        print(f"[RAW LLM RESP] --- BEGIN ---\n{part.text}\n--- END ---")
                        
                        # 1. 正規表現による A2UI タグの自前抽出 (100% 確実)
                        _matches = re.findall(r'<a2ui[-_]json>(.*?)</a2ui[-_]json>', part.text, re.DOTALL)
                        # A2UIタグを含まない純粋な平文テキストのみを抽出する
                        _plain = re.sub(r'<a2ui[-_]json>.*?</a2ui[-_]json>', '', part.text, flags=re.DOTALL).strip()
                        
                        # プレーンテキストがあれば最終テキストパートに蓄積
                        if _plain:
                            # 進捗ログ絵文字はアーティファクトから隠し、思考領域のみに留める
                            is_progress_log = any(_plain.strip().startswith(emoji) for emoji in ["📊", "🎨", "🏁", "🔍", "🛠️", "⚡", "📌", "⚠️", "⏳"]) or "作成中..." in _plain or "進行中" in _plain
                            text_part = a2a_types.Part(root=a2a_types.TextPart(text=_plain))
                            if not is_progress_log:
                                artifact_text_parts.append(text_part)
                            print(f"[PARSER TEXT] Plain text handled: {_plain[:100]}...")

                        # 抽出した A2UI カードオブジェクトを処理
                        real_media_parts = []
                        if _matches and not progress_deleted:
                            try:
                                delete_part = _original_create_a2ui_part({
                                    "deleteSurface": {
                                        "surfaceId": "slideexpert-progress-surface"
                                    }
                                })
                                real_media_parts.append(delete_part)
                                progress_deleted = True
                                print("[PARSER A2UI] Queued auto-deletion of progress card for intermediate card rendering.")
                            except Exception as ex:
                                print(f"[PARSER A2UI ERROR] Failed to create auto-delete part: {ex}")
                        for _m in _matches:
                            try:
                                import json
                                # 生文字列段階で非標準プロパティ "styles" をお掃除
                                _m_clean = re.sub(r'"styles"\s*:\s*\{[^{}]*?\}\s*,?', '', _m)
                                _parsed = json.loads(_m_clean)
                                _items = _parsed if isinstance(_parsed, list) else [_parsed]
                                for _item in _items:
                                    if isinstance(_item, dict):
                                        # 再帰的お掃除の徹底適用
                                        clean_a2ui_dict(_item)
                                        ui_part = _original_create_a2ui_part(_item)
                                        artifact_media_parts.append(ui_part)
                                        real_media_parts.append(ui_part)
                                        print(f"[PARSER A2UI] Successfully created A2UI component: {_item.get('surfaceId')}")
                            except Exception as ex:
                                print(f"[PARSER A2UI ERROR] Failed to parse A2UI JSON: {ex}")

                        # カードがあれば、リアルタイムの画面描画を促すために即座に作業中イベントで送り出す
                        if real_media_parts:
                            await event_queue.enqueue_event(
                                TaskStatusUpdateEvent(
                                    task_id=context.task_id,
                                    context_id=context.context_id,
                                    status=TaskStatus(
                                        state=TaskState.working,
                                        message=Message(message_id=str(uuid.uuid4()), role=Role.agent, parts=real_media_parts),
                                        timestamp=datetime.now(timezone.utc).isoformat(),
                                    ),
                                    final=False
                                )
                            )

        # 最終成果物を送る前に、進捗カードがまだ消去されていなければ消去コマンドを追加
        if not progress_deleted:
            try:
                delete_progress_part = _original_create_a2ui_part({
                    "deleteSurface": {
                        "surfaceId": "slideexpert-progress-surface"
                    }
                })
                artifact_media_parts.insert(0, delete_progress_part)
                progress_deleted = True
            except Exception as e:
                print(f"[DELETE PROGRESS CARD ERROR] Failed to create deleteSurface part: {e}")
        artifact_parts = artifact_text_parts + artifact_media_parts
        print(f"[FINAL ARTIFACTS] Total parts: {len(artifact_parts)} (Text: {len(artifact_text_parts)}, Media: {len(artifact_media_parts)})")
        if artifact_parts:
            await event_queue.enqueue_event(
                TaskArtifactUpdateEvent(
                    task_id=context.task_id,
                    last_chunk=True,
                    context_id=context.context_id,
                    artifact=Artifact(artifact_id=str(uuid.uuid4()), parts=artifact_parts),
                )
            )
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=context.task_id,
                    status=TaskStatus(state=TaskState.completed, timestamp=datetime.now(timezone.utc).isoformat()),
                    context_id=context.context_id,
                    final=True,
                )
            )

request_handler = DefaultRequestHandler(agent_executor=AdkAgentToA2AExecutor(runner=runner, use_legacy=True), task_store=InMemoryTaskStore())

A2A_RPC_PATH = f"/a2a/{adk_app.name}"

def _build_static_agent_card() -> AgentCard:
    a2ui_extension = get_a2ui_agent_extension(version="0.8", supported_catalog_ids=a2ui_schema_manager.supported_catalog_ids)
    return AgentCard(
        name="SlideExpert",
        description="Googleブランドの美学に基づき、プロフェッショナルな日本ビジネススタイルのGoogle Slides資料を作成します。",
        url=f"https://google-slide-agent-989491130286.us-east1.run.app{A2A_RPC_PATH}",
        version="0.1.0",
        icon_url="https://storage.googleapis.com/agentspace-469000-agentlogo/slideexpert-icon.png",
        capabilities=AgentCapabilities(streaming=True, extensions=[a2ui_extension]),
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/plain", "application/json"],
        skills=[],
    )

@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncIterator[None]:
    agent_card = _build_static_agent_card()
    a2a_app = A2AFastAPIApplication(agent_card=agent_card, http_handler=request_handler)
    a2a_app.add_routes_to_app(
        app_instance,
        agent_card_url=f"{A2A_RPC_PATH}{AGENT_CARD_WELL_KNOWN_PATH}",
        rpc_url=A2A_RPC_PATH,
        extended_agent_card_url=f"{A2A_RPC_PATH}{EXTENDED_AGENT_CARD_PATH}",
    )
    yield

app = FastAPI(title="SlideExpert", description="API for interacting with SlideExpert", lifespan=lifespan)

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import builtins

class TokenExtractionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = None
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        if token:
            builtins._workspace_oauth_token = token
            request.state.oauth_token = token
        return await call_next(request)

app.add_middleware(TokenExtractionMiddleware)
