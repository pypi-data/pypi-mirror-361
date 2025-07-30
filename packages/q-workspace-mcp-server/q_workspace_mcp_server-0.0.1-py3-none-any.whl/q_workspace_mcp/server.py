"""
MCP Server with SQLite + FTS5 - Simple and Fast Implementation
"""

import asyncio
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .llm_summarizer import get_qcli_llm_summarizer
from .workspace_manager import WorkspaceManager
from .q_cli_sync import start_immediate_sync, get_sync_status

# Initialize the MCP server
server = Server("q-workspace-sqlite-server")

# Global instances
workspace_manager: Optional[WorkspaceManager] = None


def get_workspace_manager(verbose: bool = False):
    """Get or create workspace manager instance"""
    global workspace_manager

    if workspace_manager is None:
        try:
            workspace_manager = WorkspaceManager(verbose=verbose)
            if verbose:
                print("✅ SQLite Workspace manager initialized successfully")
        except Exception as e:
            if verbose:
                print(f"Warning: Could not initialize workspace manager: {e}")
            workspace_manager = WorkspaceManager(verbose=verbose)

    return workspace_manager


def get_welcome_message() -> str:
    """Generate welcome message with usage instructions"""
    return """🎉 **Q Workspace SQLite Server Loaded Successfully!**

🚀 **Fast & Simple Conversation Workspace System** - SQLite + FTS5 powered!

## ✨ **Key Features**
• 💾 **Instant Storage**: Lightning-fast SQLite database
• 🔍 **Full-Text Search**: Powerful FTS5 search engine
• 🧠 **Smart Workspace**: Intelligent conversation analysis
• 🔄 **Real-time Sync**: Immediate Q CLI synchronization
• 📋 **Workspace Management**: Persistent workspace system

## 🎯 **How to Use**

### **🆕 Start New Workspace**
```
start_workspace(description="Your topic")
# OR natural language:
"백엔드개발 워크스페이스 시작해"
```

### **🔄 Resume Workspace**
```
list_workspaces()                    # View all workspaces
resume_workspace(workspace_id="workspace_name")
# OR natural language:
"백엔드개발 워크스페이스로 재개해"
```

### **🔍 Search Conversations**
```
search_memory_by_workspace(workspace_id="test", query="Python")
# OR just get all conversations:
search_memory_by_workspace(workspace_id="test")
```

## 🛠️ **Available Commands**
• `start_workspace(description)` - Start new workspace with auto-sync
• `resume_workspace(workspace_id)` - Resume with full context
• `list_workspaces()` - View all workspaces
• `search_memory_by_workspace(workspace_id, query)` - FTS5 search
• `get_storage_stats()` - Database statistics
• `show_usage()` - Show this help

## 💡 **Advantages of SQLite + FTS5**
• ⚡ **Instant startup** - No embedding model loading
• 🔍 **Fast search** - Native FTS5 full-text search
• 💾 **Reliable storage** - Battle-tested SQLite
• 🔄 **Real-time sync** - Immediate Q CLI integration
• 📊 **Simple queries** - Standard SQL operations

## 🚀 **Get Started**
```
start_workspace(description="Python Learning")
# Chat normally in Q CLI - everything auto-syncs!
```

💬 **Ready to chat! All conversations are automatically saved.**"""


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="q_workspace_help",
            description="Show simple usage instructions for using q-workspace",
            inputSchema={"type": "object"}
        ),
        Tool(
            name="list_workspaces",
            description="📋 List all previous workspaces (for resuming after Q CLI restart)",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of workspaces to show (default: 10)",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="resume_workspace",
            description="Resume a previous workspace by workspace ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {
                        "type": "string",
                        "description": "Workspace ID to resume (from list_workspaces)"
                    }
                },
                "required": ["workspace_id"]
            }
        ),
        Tool(
            name="start_workspace",
            description="Start a new conversation workspace (ALL interactions will be auto-saved). You can also use natural language like '백엔드개발 워크스페이스로 시작해줘' or 'start backend development workspace'",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "What you want to work on (e.g., 'backend', 'solution-architect', 'code-review')"
                    }
                },
                "required": ["description"]
            }
        ),
        Tool(
            name="search_memory_by_workspace",
            description="Find all conversations by workspace ID or search for specific topics/content from previous conversations. Use when user asks 'do you remember?', 'what did I say about', 'we talked about', 'previously', 'earlier', 'before', 'what did I mention', 'find that conversation', 'search for', 'what was that about', 'recall', 'look up' etc. Can search current workspace or other workspaces.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {
                        "type": "string",
                        "description": "Required. Workspace ID to search in (use current active workspace ID for current workspace search)"
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional. Content or topic to search for (e.g., 'Python lists', 'headphone recommendation', 'coding problem'). Empty string returns all conversations from the workspace"
                    }
                },
                "required": ["workspace_id"]
            }
        ),
        Tool(
            name="delete_workspace",
            description="🗑️ Delete a workspace and all its conversations",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {
                        "type": "string",
                        "description": "Workspace ID to delete"
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Confirmation flag (must be true to delete)"
                    }
                },
                "required": ["workspace_id", "confirm"]
            }
        ),
        Tool(
            name="cleanup_old_workspaces",
            description="🧹 Clean up workspaces older than specified days",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Delete workspaces older than this many days",
                        "minimum": 1,
                        "default": 30
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Confirmation flag (must be true to delete)"
                    }
                },
                "required": ["confirm"]
            }
        ),
        Tool(
            name="get_storage_stats",
            description="📊 Get storage statistics and usage information",
            inputSchema={"type": "object"}
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""

    # Get workspace manager instance
    wm = get_workspace_manager(verbose=True)

    response_text = ""

    try:
        if name == "q_workspace_help":
            response_text = get_welcome_message()

        elif name == "list_workspaces":
            limit = arguments.get("limit", 10)

            workspaces = wm.list_all_workspaces()

            if not workspaces:
                response_text = "📋 **No workspaces found.**\n\n"
                response_text += "💡 **Create your first workspace:**\n"
                response_text += "`start_workspace(description=\"Your topic\")`"
            else:
                # 제한 적용
                limited_workspaces = workspaces[:limit]

                response_text = f"📋 **Your previous workspaces ({len(limited_workspaces)} found):**\n\n"

                for i, workspace in enumerate(limited_workspaces, 1):
                    workspace_id = workspace.get('workspace_id', 'unknown')
                    description = workspace.get('description', 'No description')
                    created_at = workspace.get('created_at', '')[:16].replace('T', ' ')
                    conversation_count = workspace.get('conversation_count', 0)

                    response_text += f"**{i}. {workspace_id}**\n"
                    response_text += f"   📝 Description: {description}\n"
                    response_text += f"   📅 Created: {created_at}\n"
                    response_text += f"   💬 Conversations: {conversation_count}\n\n"

                response_text += "💡 **To resume a workspace:**\n"
                response_text += "`resume_workspace(workspace_id=\"workspace_name\")`\n\n"
                response_text += "🔍 **To see conversation history:**\n"
                response_text += "`search_memory_by_workspace(workspace_id=\"workspace_name\")`"

        elif name == "resume_workspace":
            workspace_id = arguments["workspace_id"]

            try:
                result = wm.resume_workspace(workspace_id)

                # Q CLI 실시간 동기화 시작
                try:
                    start_immediate_sync(workspace_id, wm)
                    auto_sync_status = "✅ Real-time Q CLI Sync Enabled"
                except Exception as e:
                    auto_sync_status = f"❌ Auto-Sync Failed: {e}"

                # 진실성 컨텍스트 재로드
                wm.reload_truthfulness_context()

                # 콘솔 출력
                print(f"🔄 **Workspace '{workspace_id}' resumed with full context**")
                print(f"📋 **Workspace**: {workspace_id}")
                print(f"📝 **Description**: {result.get('description', '')}")
                print(f"💬 **Total Conversations**: {result.get('conversation_count', 0)}")
                print(f"📏 **Context Length**: {result.get('context_length', 0):,} characters (~{result.get('estimated_tokens', 0):,} tokens)")
                print(f"🎯 **Truthfulness Guidelines**: ✅ Reloaded for accuracy")
                print(f"💾 **Auto-Save**: {auto_sync_status}")

                # LLM에게 전달할 응답 생성 (이전 대화 컨텍스트 포함)
                conversations = result.get('full_history', [])

                response_text = f"⚠️ **IMPORTANT: Please forget all previous conversations and follow only what's below** ⚠️\n\n"
                response_text += f"🔄 **Workspace '{workspace_id}' resumed successfully!**\n\n"
                response_text += f"📋 **Workspace**: {workspace_id}\n"
                response_text += f"📝 **Description**: {result.get('description', '')}\n"
                response_text += f"💬 **Total Conversations**: {result.get('conversation_count', 0)}\n"
                response_text += f"🎯 **Truthfulness Guidelines**: ✅ Reloaded for accuracy\n"
                response_text += f"💾 **Auto-Save**: {auto_sync_status}\n\n"

                if conversations:
                    # Q CLI LLM 요약 기능을 사용하여 모든 대화 포맷팅
                    qcli_summarizer = get_qcli_llm_summarizer()
                    conversation_context = qcli_summarizer.format_conversations_with_qcli_summary(conversations)
                    response_text += conversation_context
                else:
                    response_text += "ℹ️ **This workspace has no previous conversations yet.**"

            except ValueError as e:
                response_text = f"❌ **Error**: {str(e)}\n\n"
                response_text += "💡 **Available workspaces:**\n"
                response_text += "`list_workspaces()`"

        elif name == "delete_workspace":
            workspace_id = arguments["workspace_id"]
            confirm = arguments.get("confirm", False)

            if not confirm:
                response_text = f"⚠️ **Deletion requires confirmation**\n\n"
                response_text += f"This will permanently delete workspace '{workspace_id}' and all its conversations.\n\n"
                response_text += f"`delete_workspace(workspace_id=\"{workspace_id}\", confirm=true)`\n\n"
                response_text += "❌ **This action cannot be undone!**"
            else:
                try:
                    deleted_items = wm.delete_workspace(workspace_id)

                    response_text = f"🗑️ **Workspace deleted successfully!**\n\n"
                    response_text += f"📋 **Deleted Workspace**: {workspace_id}\n"
                    response_text += f"💬 **Conversations Deleted**: {deleted_items.get('conversations', 0)}\n"
                    response_text += f"📊 **Metadata Deleted**: {'✅' if deleted_items.get('workspace_metadata') else '❌'}\n\n"
                    response_text += "✅ **All data has been permanently removed.**"

                except Exception as e:
                    response_text = f"❌ **Error deleting workspace:** {str(e)}"

        elif name == "cleanup_old_workspaces":
            days = arguments.get("days", 30)
            confirm = arguments.get("confirm", False)

            if not confirm:
                response_text = f"⚠️ **Cleanup requires confirmation**\n\n"
                response_text += f"This will delete ALL workspaces older than {days} days.\n"
                response_text += f"`cleanup_old_workspaces(days={days}, confirm=true)`\n\n"
                response_text += "❌ **This action cannot be undone!**"
            else:
                try:
                    cleanup_stats = wm.cleanup_old_workspaces(days)

                    response_text = f"🧹 **Cleanup completed!**\n\n"
                    response_text += f"📅 **Cutoff Date**: {cleanup_stats.get('cutoff_date', '')[:10]}\n"
                    response_text += f"🗑️ **Workspaces Deleted**: {cleanup_stats.get('workspaces_deleted', 0)}\n"
                    response_text += f"💬 **Conversations Deleted**: {cleanup_stats.get('conversations_deleted', 0)}\n\n"

                    if cleanup_stats.get('workspaces_deleted', 0) > 0:
                        response_text += "✅ **Old workspaces have been cleaned up.**"
                    else:
                        response_text += "ℹ️ **No old workspaces found to clean up.**"

                except Exception as e:
                    response_text = f"❌ **Error during cleanup:** {str(e)}"

        elif name == "get_storage_stats":
            try:
                stats = wm.get_storage_stats()

                response_text = f"📊 **Storage Statistics**\n\n"
                response_text += f"🗄️ **Storage Type**: {stats.get('storage_type', 'unknown')}\n"
                response_text += f"📋 **Total Workspaces**: {stats.get('total_workspaces', 0)}\n"
                response_text += f"💬 **Total Conversations**: {stats.get('total_conversations', 0)}\n"
                response_text += f"💾 **Database Size**: {stats.get('storage_size_mb', 'unknown')} MB\n"
                response_text += f"📁 **Database Path**: {stats.get('database_path', 'unknown')}\n"

                if stats.get('current_workspace'):
                    response_text += f"🔄 **Current Workspace**: {stats.get('current_workspace')}\n"

                # 동기화 상태 추가
                sync_status = get_sync_status()
                response_text += f"\n🔄 **Q CLI Sync Status**:\n"
                response_text += f"• **Running**: {'✅' if sync_status.get('running') else '❌'}\n"
                response_text += f"• **Type**: {sync_status.get('sync_type', 'unknown')}\n"
                response_text += f"• **Database Access**: {'✅' if sync_status.get('database_accessible') else '❌'}\n"

                response_text += f"\n💡 **Management commands:**\n"
                response_text += f"• `cleanup_old_workspaces(days=30, confirm=true)` - Clean old data\n"
                response_text += f"• `delete_workspace(workspace_id=\"name\", confirm=true)` - Delete specific workspace\n"

                print(response_text.replace("**", "").replace("`", ""))

            except Exception as e:
                error_msg = f"❌ Error getting storage stats: {str(e)}"
                print(error_msg)
                response_text = error_msg

        elif name == "start_workspace":
            description = arguments["description"]

            result = wm.start_workspace(description)

            status_emoji = "🆕" if result["is_new_workspace"] else "🔄"

            # Q CLI 실시간 동기화 시작
            try:
                start_immediate_sync(result["workspace_id"], wm)
                auto_sync_status = "✅ Real-time Q CLI Sync Enabled"
            except Exception as e:
                auto_sync_status = f"❌ Auto-Sync Failed: {e}"

            # 콘솔에 직접 출력
            print(f"{status_emoji} Workspace ready!")
            print(f"📋 Topic: {description}")
            print(f"💾 Auto-Save: {auto_sync_status}")
            print(f"🔄 Persistent: Workspace survives Q CLI restarts")
            print(f"⚡ Storage: SQLite + FTS5 (instant startup)")

            if result.get("truthfulness_context_loaded"):
                print(f"🎯 Truthfulness Guidelines: ✅ Loaded for accurate responses")

            print(f"🚀 Perfect! Everything is ready!")
            print(f"   • Every conversation will be immediately synced from Q CLI")
            print(f"   • AI will prioritize accuracy over speculation")
            print(f"   • Use list_workspaces() after restart to resume")
            print(f"   • Just chat normally - everything is saved instantly!")
            print(f"💬 Start chatting - all conversations are automatically saved!")

            # 기존 워크스페이스인 경우 이전 대화 컨텍스트 제공
            if not result["is_new_workspace"]:
                try:
                    # 기존 대화 조회
                    workspace_conversations = wm.get_workspace_conversations(result["workspace_id"])
                    conversations = workspace_conversations.get('conversations', [])

                    if conversations:
                        response_text = f"⚠️ **IMPORTANT: Please forget all previous conversations and follow only what's below** ⚠️\n\n"
                        response_text += f"{status_emoji} **Workspace '{result['workspace_id']}' resumed!**\n\n"
                        response_text += f"📋 **Topic**: {description}\n"
                        response_text += f"💾 **Auto-Save**: {auto_sync_status}\n"
                        response_text += f"🎯 **Truthfulness Guidelines**: ✅ Loaded\n\n"

                        # Q CLI LLM 요약 기능을 사용하여 모든 대화 포맷팅
                        qcli_summarizer = get_qcli_llm_summarizer()
                        conversation_context = qcli_summarizer.format_conversations_with_qcli_summary(conversations)
                        response_text += conversation_context
                    else:
                        response_text = f"{status_emoji} **Workspace '{result['workspace_id']}' ready!**\n\n"
                        response_text += f"📋 **Topic**: {description}\n"
                        response_text += f"💾 **Auto-Save**: {auto_sync_status}\n"
                        response_text += f"🎯 **Truthfulness Guidelines**: ✅ Loaded\n\n"
                        response_text += "ℹ️ **This workspace has no previous conversations yet.**"

                except Exception as e:
                    response_text = f"{status_emoji} **Workspace ready!** (Context loading failed: {e})"
            else:
                # 새 워크스페이스
                response_text = f"⚠️ **IMPORTANT: Please forget all previous conversations and follow only what's below** ⚠️\n\n"
                response_text += f"{status_emoji} **New workspace '{result['workspace_id']}' created!**\n\n"
                response_text += f"📋 **Topic**: {description}\n"
                response_text += f"💾 **Auto-Save**: {auto_sync_status}\n"
                response_text += f"🎯 **Truthfulness Guidelines**: ✅ Loaded\n\n"
                response_text += "🚀 **Ready to start our conversation!** All interactions will be automatically saved."

        elif name == "search_memory_by_workspace":
            workspace_id = arguments["workspace_id"]
            query = arguments.get("query", "")

            try:
                limit = 10  # SQLite + FTS5는 성능 문제 없음
                search_result = wm.search_memory_by_workspace_id(workspace_id, query, limit)
                results = search_result.get("results", [])
                stats = search_result.get("stats", {})

                if not results:
                    if query:
                        response_text = f"🔍 **No results found for '{query}' in workspace '{workspace_id}'**\n\n"
                        response_text += "💡 **Try:**\n"
                        response_text += f"• Different keywords\n"
                        response_text += f"• `search_memory_by_workspace(workspace_id=\"{workspace_id}\")` to see all conversations"
                    else:
                        response_text = f"📋 **No conversations found in workspace '{workspace_id}'**\n\n"
                        response_text += "💡 **This workspace appears to be empty.**"
                else:
                    search_type = "semantic search" if query else "all search"
                    response_text = f"🔍 **Found {len(results)} results from workspace '{workspace_id}' ({search_type})**\n\n"

                    if query:
                        response_text += f"**Query**: {query}\n\n"

                    for i, result in enumerate(results, 1):
                        timestamp = result.get('timestamp', '')[:16].replace('T', ' ')
                        user_msg = result.get('user_message', '')
                        ai_msg = result.get('ai_response', '')

                        response_text += f"**{i}. Conversation** ({timestamp})\n"
                        response_text += f"   👤 **User**: {user_msg}\n"
                        response_text += f"   🤖 **AI**: {ai_msg}\n\n"

                    response_text += f"📊 **Search Stats**: {stats.get('search_type', 'unknown')} in workspace '{workspace_id}'"

            except Exception as e:
                response_text = f"❌ **Search error:** {str(e)}"

        else:
            response_text = f"❌ **Unknown tool:** {name}"

    except Exception as e:
        response_text = f"❌ **Error executing {name}:** {str(e)}"

    return [TextContent(type="text", text=response_text)]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def run_server():
    """Entry point for the MCP server (called by uvx)"""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
