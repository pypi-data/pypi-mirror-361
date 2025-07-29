"""
AgentMeter SDK - MCP Server Metering Demonstration (v0.3.1)
===========================================================

PURPOSE:
This example demonstrates how to meter an MCP (Model Context Protocol) server
you build/deploy according to the demands of your business model using
AgentMeter SDK v0.3.1. It shows different approaches to track usage for MCP 
servers and tools.

SCENARIO:
We're building an MCP server that provides various AI-powered tools to clients.
The server offers different types of tools:
1. Basic utilities (file operations, calculations) - API request billing
2. AI processing tools (text analysis, generation) - Token-based billing
3. Premium services (advanced analytics, reports) - Instant payments

APPLICATION STRUCTURE:
- MCPServer: Main MCP server with tool registration
- MeteredTools: Collection of tools with different billing models
- UsageTracker: Tracks tool usage across all client sessions
- BillingManager: Manages different billing strategies per tool

PRICING MODEL:
1. Basic Tools: $0.02 per operation (file ops, calculations)
2. AI Tools: $0.000020 per input token, $0.000030 per output token
3. Premium Tools: $1.99-$9.99 per advanced operation
4. Bulk Operations: Discounted rates for batch processing

This demonstrates how to implement comprehensive usage tracking for
MCP servers using AgentMeter v0.3.1 while maintaining clean separation 
between tool logic and billing concerns.
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from agentmeter import AgentMeter, MeterEvent, MeterEventCreate

# Configuration
API_KEY = os.getenv("AGENTMETER_API_KEY", "your_api_key_here")

# MCP Protocol simulation (in real implementation, use official MCP library)
class MCPMessageType(Enum):
    INITIALIZE = "initialize"
    CALL_TOOL = "call_tool"
    LIST_TOOLS = "list_tools"
    GET_TOOL_INFO = "get_tool_info"


class BillingType(Enum):
    API_REQUEST = "api_request"
    TOKEN_BASED = "token_based"
    INSTANT_PAY = "instant_pay"


@dataclass
class MCPTool:
    """MCP Tool definition with billing configuration"""
    name: str
    description: str
    parameters: Dict[str, Any]
    billing_type: BillingType
    billing_config: Dict[str, Any]
    category: str = "utility"
    requires_premium: bool = False


@dataclass
class MCPRequest:
    """MCP Request message"""
    message_type: MCPMessageType
    tool_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    client_id: str = "default_client"
    session_id: str = "default_session"


@dataclass
class MCPResponse:
    """MCP Response message"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    usage_info: Optional[Dict[str, Any]] = None
    billing_info: Optional[Dict[str, Any]] = None


class MeteredMCPTools:
    """
    Collection of MCP tools with integrated AgentMeter v0.3.1 billing
    Each tool demonstrates different billing approaches
    """
    
    def __init__(self, meter: AgentMeter, meter_type_ids: Dict[str, str]):
        self.meter = meter
        self.meter_type_ids = meter_type_ids  # Maps billing_type to meter_type_id
        self.tools_registry = {}
        self._register_all_tools()
    
    def _register_all_tools(self):
        """Register all available tools with their billing configurations"""
        
        # Basic utility tools - API request billing
        self.tools_registry.update({
            "file_read": MCPTool(
                name="file_read",
                description="Read contents of a file",
                parameters={"filename": {"type": "string", "required": True}},
                billing_type=BillingType.API_REQUEST,
                billing_config={"unit_price": 0.02},
                category="file_operations"
            ),
            "file_write": MCPTool(
                name="file_write", 
                description="Write content to a file",
                parameters={"filename": {"type": "string", "required": True}, "content": {"type": "string", "required": True}},
                billing_type=BillingType.API_REQUEST,
                billing_config={"unit_price": 0.03},
                category="file_operations"
            ),
            "calculator": MCPTool(
                name="calculator",
                description="Perform mathematical calculations",
                parameters={"expression": {"type": "string", "required": True}},
                billing_type=BillingType.API_REQUEST,
                billing_config={"unit_price": 0.01},
                category="utility"
            ),
            "url_fetch": MCPTool(
                name="url_fetch",
                description="Fetch content from a URL",
                parameters={"url": {"type": "string", "required": True}},
                billing_type=BillingType.API_REQUEST,
                billing_config={"unit_price": 0.05},
                category="network"
            )
        })
        
        # AI processing tools - Token-based billing
        self.tools_registry.update({
            "text_analyze": MCPTool(
                name="text_analyze",
                description="Analyze text for sentiment, topics, and insights",
                parameters={"text": {"type": "string", "required": True}, "analysis_type": {"type": "string", "default": "basic"}},
                billing_type=BillingType.TOKEN_BASED,
                billing_config={"input_token_price": 0.000020, "output_token_price": 0.000030},
                category="ai_processing"
            ),
            "text_generate": MCPTool(
                name="text_generate",
                description="Generate text based on prompts",
                parameters={"prompt": {"type": "string", "required": True}, "max_length": {"type": "integer", "default": 500}},
                billing_type=BillingType.TOKEN_BASED,
                billing_config={"input_token_price": 0.000025, "output_token_price": 0.000040},
                category="ai_processing"
            ),
            "text_translate": MCPTool(
                name="text_translate",
                description="Translate text between languages",
                parameters={"text": {"type": "string", "required": True}, "target_language": {"type": "string", "required": True}},
                billing_type=BillingType.TOKEN_BASED,
                billing_config={"input_token_price": 0.000015, "output_token_price": 0.000020},
                category="ai_processing"
            ),
            "code_analyze": MCPTool(
                name="code_analyze",
                description="Analyze code for quality, security, and best practices",
                parameters={"code": {"type": "string", "required": True}, "language": {"type": "string", "required": True}},
                billing_type=BillingType.TOKEN_BASED,
                billing_config={"input_token_price": 0.000030, "output_token_price": 0.000050},
                category="ai_processing"
            )
        })
        
        # Premium tools - Instant payment billing
        self.tools_registry.update({
            "advanced_analytics": MCPTool(
                name="advanced_analytics",
                description="Generate comprehensive analytics reports",
                parameters={"data": {"type": "array", "required": True}, "report_type": {"type": "string", "default": "standard"}},
                billing_type=BillingType.INSTANT_PAY,
                billing_config={"amount": 1.99, "description": "Advanced Analytics Report"},
                category="premium",
                requires_premium=True
            ),
            "ai_consultation": MCPTool(
                name="ai_consultation",
                description="Get expert AI consultation and recommendations",
                parameters={"topic": {"type": "string", "required": True}, "detail_level": {"type": "string", "default": "standard"}},
                billing_type=BillingType.INSTANT_PAY,
                billing_config={"amount": 4.99, "description": "AI Expert Consultation"},
                category="premium",
                requires_premium=True
            ),
            "custom_model_training": MCPTool(
                name="custom_model_training",
                description="Train a custom AI model for specific tasks",
                parameters={"training_data": {"type": "array", "required": True}, "model_type": {"type": "string", "required": True}},
                billing_type=BillingType.INSTANT_PAY,
                billing_config={"amount": 9.99, "description": "Custom Model Training"},
                category="premium",
                requires_premium=True
            )
        })
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars = 1 token)"""
        return max(1, len(text) // 4)
    
    async def record_usage(self, tool: MCPTool, subject_id: str, metadata: Dict[str, Any] = None) -> Optional[MeterEvent]:
        """Record usage for a tool based on its billing type"""
        try:
            meter_type_id = self.meter_type_ids.get(tool.billing_type.value)
            if not meter_type_id:
                print(f"⚠️ No meter type ID found for billing type: {tool.billing_type.value}")
                return None
            
            # Calculate quantity based on billing type
            quantity = 0.0
            if tool.billing_type == BillingType.API_REQUEST:
                quantity = tool.billing_config["unit_price"]
            elif tool.billing_type == BillingType.TOKEN_BASED:
                input_tokens = metadata.get("input_tokens", 0)
                output_tokens = metadata.get("output_tokens", 0)
                input_cost = input_tokens * tool.billing_config["input_token_price"]
                output_cost = output_tokens * tool.billing_config["output_token_price"]
                quantity = input_cost + output_cost
            elif tool.billing_type == BillingType.INSTANT_PAY:
                quantity = tool.billing_config["amount"]
            
            # Record the event
            event = self.meter.meter_events.record(
                meter_type_id=meter_type_id,
                subject_id=subject_id,
                quantity=quantity,
                metadata={
                    "tool_name": tool.name,
                    "billing_type": tool.billing_type.value,
                    "category": tool.category,
                    **(metadata or {})
                }
            )
            
            print(f"💰 Recorded ${quantity:.4f} for {tool.name} (subject: {subject_id})")
            return event
            
        except Exception as e:
            print(f"❌ Failed to record usage for {tool.name}: {e}")
            return None

    async def execute_file_read(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute file read operation with billing"""
        tool = self.tools_registry["file_read"]
        filename = parameters.get("filename", "")
        
        print(f"📖 Reading file: {filename}")
        
        try:
            # Simulate file read operation
            await asyncio.sleep(0.1)
            
            # Mock file content based on filename
            content_map = {
                "config.json": '{"api_key": "example_key", "environment": "production"}',
                "data.csv": "name,age,city\nJohn,30,NYC\nJane,25,LA\nBob,35,Chicago",
                "README.md": "# Project Documentation\n\nThis is a sample project.\n\n## Features\n- Feature 1\n- Feature 2",
                "logs.txt": "2024-01-15 10:30:00 - INFO: Application started\n2024-01-15 10:31:00 - DEBUG: Processing request"
            }
            
            file_content = content_map.get(filename, f"Sample content for {filename}")
            file_size = len(file_content)
            
            # Record usage
            await self.record_usage(
                tool=tool,
                subject_id=user_id,
                metadata={
                    "filename": filename,
                    "file_size": file_size,
                    "operation": "read"
                }
            )
            
            return {
                "success": True,
                "content": file_content,
                "metadata": {
                    "filename": filename,
                    "size": file_size,
                    "operation": "file_read"
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_file_write(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute file write operation with billing"""
        tool = self.tools_registry["file_write"]
        filename = parameters.get("filename", "")
        content = parameters.get("content", "")
        
        print(f"✍️ Writing to file: {filename} ({len(content)} chars)")
        
        try:
            # Simulate file write operation
            await asyncio.sleep(0.2)
            
            # Record usage
            await self.record_usage(
                tool=tool,
                subject_id=user_id,
                metadata={
                    "filename": filename,
                    "content_size": len(content),
                    "operation": "write"
                }
            )
            
            return {
                "success": True,
                "message": f"Successfully wrote {len(content)} characters to {filename}",
                "metadata": {
                    "filename": filename,
                    "size": len(content),
                    "operation": "file_write"
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_calculator(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute calculation with billing"""
        tool = self.tools_registry["calculator"]
        expression = parameters.get("expression", "")
        
        print(f"🧮 Calculating: {expression}")
        
        try:
            # Simulate calculation processing
            await asyncio.sleep(0.1)
            
            # Simple expression evaluation (in production, use a secure math parser)
            safe_expression = expression.replace(" ", "")
            
            # Basic calculation simulation
            if "+" in safe_expression:
                parts = safe_expression.split("+")
                result = sum(float(p) for p in parts)
            elif "-" in safe_expression:
                parts = safe_expression.split("-")
                result = float(parts[0]) - sum(float(p) for p in parts[1:])
            elif "*" in safe_expression:
                parts = safe_expression.split("*")
                result = 1
                for p in parts:
                    result *= float(p)
            elif "/" in safe_expression:
                parts = safe_expression.split("/")
                result = float(parts[0])
                for p in parts[1:]:
                    result /= float(p)
            else:
                result = float(safe_expression)
            
            # Record usage
            await self.record_usage(
                tool=tool,
                subject_id=user_id,
                metadata={
                    "expression": expression,
                    "result": result,
                    "operation": "calculation"
                }
            )
            
            return {
                "success": True,
                "result": result,
                "expression": expression,
                "metadata": {
                    "operation": "calculator",
                    "complexity": len(expression)
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Calculation error: {str(e)}"}

    async def execute_text_analyze(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute text analysis with token-based billing"""
        tool = self.tools_registry["text_analyze"]
        text = parameters.get("text", "")
        analysis_type = parameters.get("analysis_type", "basic")
        
        print(f"🔍 Analyzing text: {text[:50]}...")
        
        try:
            # Simulate AI processing
            await asyncio.sleep(1.0)
            
            # Estimate tokens
            input_tokens = self.estimate_tokens(text)
            
            # Generate analysis result
            analysis_result = {
                "sentiment": "positive" if "good" in text.lower() or "great" in text.lower() else "neutral",
                "topics": ["technology", "business"] if "tech" in text.lower() else ["general"],
                "word_count": len(text.split()),
                "reading_level": "intermediate",
                "key_phrases": text.split()[:3]
            }
            
            if analysis_type == "detailed":
                analysis_result.update({
                    "emotions": ["confidence", "optimism"],
                    "intent": "informational",
                    "complexity_score": min(len(text) / 100, 10.0)
                })
            
            # Estimate output tokens
            output_text = json.dumps(analysis_result)
            output_tokens = self.estimate_tokens(output_text)
            
            # Record usage
            await self.record_usage(
                tool=tool,
                subject_id=user_id,
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "analysis_type": analysis_type,
                    "text_length": len(text),
                    "operation": "text_analysis"
                }
            )
            
            return {
                "success": True,
                "analysis": analysis_result,
                "metadata": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "operation": "text_analyze"
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_text_generate(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute text generation with token-based billing"""
        tool = self.tools_registry["text_generate"]
        prompt = parameters.get("prompt", "")
        max_length = parameters.get("max_length", 500)
        
        print(f"✍️ Generating text from prompt: {prompt[:50]}...")
        
        try:
            # Simulate AI text generation
            await asyncio.sleep(1.5)
            
            # Estimate input tokens
            input_tokens = self.estimate_tokens(prompt)
            
            # Generate mock response
            generated_text = f"Based on your request '{prompt}', here's a comprehensive response that addresses your needs. " \
                           f"This generated content provides detailed information and insights relevant to your query. " \
                           f"The content is tailored to be informative and helpful for your specific use case."
            
            # Limit to max_length characters
            if len(generated_text) > max_length:
                generated_text = generated_text[:max_length] + "..."
            
            # Estimate output tokens
            output_tokens = self.estimate_tokens(generated_text)
            
            # Record usage
            await self.record_usage(
                tool=tool,
                subject_id=user_id,
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "prompt_length": len(prompt),
                    "max_length": max_length,
                    "operation": "text_generation"
                }
            )
            
            return {
                "success": True,
                "generated_text": generated_text,
                "metadata": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "operation": "text_generate"
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_advanced_analytics(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute advanced analytics with instant payment billing"""
        tool = self.tools_registry["advanced_analytics"]
        data = parameters.get("data", [])
        report_type = parameters.get("report_type", "standard")
        
        print(f"📊 Generating advanced analytics report: {report_type}")
        
        try:
            # Simulate complex analytics processing
            await asyncio.sleep(2.0)
            
            # Record usage (instant payment)
            await self.record_usage(
                tool=tool,
                subject_id=user_id,
                metadata={
                    "report_type": report_type,
                    "data_points": len(data),
                    "operation": "advanced_analytics"
                }
            )
            
            # Generate analytics report
            analytics_report = {
                "report_type": report_type,
                "data_summary": {
                    "total_records": len(data),
                    "data_quality_score": 8.7,
                    "completeness": "94%"
                },
                "insights": [
                    "Strong correlation between variables A and B",
                    "Seasonal trends detected in the data",
                    "Outliers identified in 3% of records"
                ],
                "recommendations": [
                    "Consider data cleaning for outlier records",
                    "Implement trend-based forecasting",
                    "Regular monitoring recommended"
                ],
                "visualizations": {
                    "charts_generated": 5,
                    "dashboard_url": "https://analytics.example.com/report/12345"
                }
            }
            
            return {
                "success": True,
                "report": analytics_report,
                "metadata": {
                    "cost": tool.billing_config["amount"],
                    "operation": "advanced_analytics"
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute a tool by name"""
        if tool_name not in self.tools_registry:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}
        
        # Route to appropriate execution method
        execution_map = {
            "file_read": self.execute_file_read,
            "file_write": self.execute_file_write,
            "calculator": self.execute_calculator,
            "text_analyze": self.execute_text_analyze,
            "text_generate": self.execute_text_generate,
            "advanced_analytics": self.execute_advanced_analytics,
            # Add more tool executors as needed
        }
        
        executor = execution_map.get(tool_name)
        if executor:
            return await executor(parameters, user_id)
        else:
            return {
                "success": False,
                "error": f"Executor not implemented for tool '{tool_name}'"
            }


class MCPServerUsageTracker:
    """
    Track usage across all MCP server sessions and clients
    """
    
    def __init__(self, meter: AgentMeter):
        self.meter = meter
        self.active_sessions = {}
        self.client_stats = {}
    
    def start_session(self, client_id: str, session_id: str, user_id: str):
        """Start tracking a new client session"""
        session_key = f"{client_id}:{session_id}"
        self.active_sessions[session_key] = {
            "client_id": client_id,
            "session_id": session_id,
            "user_id": user_id,
            "start_time": time.time(),
            "tool_calls": 0,
            "total_cost": 0.0,
            "tools_used": set()
        }
        
        # Initialize client stats if needed
        if client_id not in self.client_stats:
            self.client_stats[client_id] = {
                "total_sessions": 0,
                "total_cost": 0.0,
                "favorite_tools": {},
                "first_seen": time.time()
            }
        
        self.client_stats[client_id]["total_sessions"] += 1
        print(f"📊 Started session {session_id} for client {client_id}")
    
    def record_tool_usage(self, client_id: str, session_id: str, tool_name: str, result: Dict[str, Any]):
        """Record tool usage in session tracking"""
        session_key = f"{client_id}:{session_id}"
        
        if session_key in self.active_sessions:
            session = self.active_sessions[session_key]
            session["tool_calls"] += 1
            session["tools_used"].add(tool_name)
            
            # Extract cost if available
            if "metadata" in result and "cost" in result["metadata"]:
                cost = result["metadata"]["cost"]
                session["total_cost"] += cost
                self.client_stats[client_id]["total_cost"] += cost
            
            # Update favorite tools
            if tool_name not in self.client_stats[client_id]["favorite_tools"]:
                self.client_stats[client_id]["favorite_tools"][tool_name] = 0
            self.client_stats[client_id]["favorite_tools"][tool_name] += 1
    
    def end_session(self, client_id: str, session_id: str):
        """End a session and generate summary"""
        session_key = f"{client_id}:{session_id}"
        
        if session_key in self.active_sessions:
            session = self.active_sessions[session_key]
            duration = time.time() - session["start_time"]
            
            print(f"📋 Session {session_id} ended:")
            print(f"   Duration: {duration:.1f}s")
            print(f"   Tool calls: {session['tool_calls']}")
            print(f"   Tools used: {', '.join(session['tools_used'])}")
            print(f"   Total cost: ${session['total_cost']:.4f}")
            
            # Clean up
            del self.active_sessions[session_key]
            
            return {
                "session_id": session_id,
                "duration": duration,
                "tool_calls": session["tool_calls"],
                "tools_used": list(session["tools_used"]),
                "total_cost": session["total_cost"]
            }
        
        return None
    
    def get_client_analytics(self, client_id: str) -> Dict[str, Any]:
        """Get analytics for a specific client"""
        if client_id not in self.client_stats:
            return {"error": "Client not found"}
        
        stats = self.client_stats[client_id]
        
        # Find most used tool
        favorite_tool = max(stats["favorite_tools"].items(), key=lambda x: x[1]) if stats["favorite_tools"] else ("none", 0)
        
        return {
            "client_id": client_id,
            "total_sessions": stats["total_sessions"],
            "total_cost": stats["total_cost"],
            "favorite_tool": favorite_tool[0],
            "favorite_tool_usage": favorite_tool[1],
            "tools_tried": len(stats["favorite_tools"]),
            "customer_since": time.strftime("%Y-%m-%d", time.localtime(stats["first_seen"])),
            "average_cost_per_session": stats["total_cost"] / max(stats["total_sessions"], 1)
        }


class AgentMeterMCPServer:
    """
    Main MCP Server with AgentMeter v0.3.1 integration
    """
    
    def __init__(self, meter: AgentMeter):
        self.meter = meter
        self.setup_meter_types()
        self.tools = MeteredMCPTools(meter, self.meter_type_ids)
        self.usage_tracker = MCPServerUsageTracker(meter)
        self.is_initialized = False
    
    def setup_meter_types(self):
        """Setup required meter types for different billing models"""
        try:
            # Create meter types for different billing models
            api_meter = self.meter.meter_types.create(
                name="MCP API Requests",
                description="Fixed price billing for basic tool operations"
            )
            
            token_meter = self.meter.meter_types.create(
                name="MCP Token Usage", 
                description="Token-based billing for AI processing tools"
            )
            
            instant_meter = self.meter.meter_types.create(
                name="MCP Premium Services",
                description="Instant payment for premium tools and services"
            )
            
            self.meter_type_ids = {
                "api_request": api_meter.id,
                "token_based": token_meter.id,
                "instant_pay": instant_meter.id
            }
            
            print("✅ MCP meter types created successfully")
            
        except Exception as e:
            print(f"⚠️ Error creating meter types (they may already exist): {e}")
            # Use default IDs if creation fails
            self.meter_type_ids = {
                "api_request": "default_api_meter",
                "token_based": "default_token_meter", 
                "instant_pay": "default_instant_meter"
            }

    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle incoming MCP requests"""
        try:
            if request.message_type == MCPMessageType.INITIALIZE:
                return await self._handle_initialize(request)
            elif request.message_type == MCPMessageType.LIST_TOOLS:
                return await self._handle_list_tools(request)
            elif request.message_type == MCPMessageType.GET_TOOL_INFO:
                return await self._handle_get_tool_info(request)
            elif request.message_type == MCPMessageType.CALL_TOOL:
                return await self._handle_call_tool(request)
            else:
                return MCPResponse(
                    success=False,
                    error=f"Unknown message type: {request.message_type}"
                )
        
        except Exception as e:
            return MCPResponse(
                success=False,
                error=f"Server error: {str(e)}"
            )

    async def _handle_initialize(self, request: MCPRequest) -> MCPResponse:
        """Handle MCP initialization"""
        self.is_initialized = True
        
        return MCPResponse(
            success=True,
            result={
                "protocol_version": "1.0",
                "server_name": "AgentMeter MCP Server",
                "server_version": "0.3.1",
                "capabilities": {
                    "tools": True,
                    "billing": True,
                    "usage_tracking": True
                },
                "billing_info": {
                    "supported_types": ["api_request", "token_based", "instant_pay"],
                    "currency": "USD"
                }
            }
        )

    async def _handle_list_tools(self, request: MCPRequest) -> MCPResponse:
        """Handle tool listing request"""
        if not self.is_initialized:
            return MCPResponse(success=False, error="Server not initialized")
        
        tools_list = []
        for tool_name, tool in self.tools.tools_registry.items():
            tools_list.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "category": tool.category,
                "billing_type": tool.billing_type.value,
                "billing_config": tool.billing_config,
                "requires_premium": tool.requires_premium
            })
        
        return MCPResponse(
            success=True,
            result={
                "tools": tools_list,
                "total_count": len(tools_list)
            }
        )

    async def _handle_get_tool_info(self, request: MCPRequest) -> MCPResponse:
        """Handle tool info request"""
        if not self.is_initialized:
            return MCPResponse(success=False, error="Server not initialized")
        
        tool_name = request.tool_name
        if not tool_name or tool_name not in self.tools.tools_registry:
            return MCPResponse(success=False, error=f"Tool '{tool_name}' not found")
        
        tool = self.tools.tools_registry[tool_name]
        
        return MCPResponse(
            success=True,
            result={
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "category": tool.category,
                "billing_type": tool.billing_type.value,
                "billing_config": tool.billing_config,
                "requires_premium": tool.requires_premium,
                "usage_examples": self._get_tool_examples(tool_name)
            }
        )

    async def _handle_call_tool(self, request: MCPRequest) -> MCPResponse:
        """Handle tool execution request"""
        if not self.is_initialized:
            return MCPResponse(success=False, error="Server not initialized")
        
        tool_name = request.tool_name
        if not tool_name:
            return MCPResponse(success=False, error="Tool name required")
        
        # Start session tracking if not already started
        user_id = request.parameters.get("user_id", request.client_id)
        if f"{request.client_id}:{request.session_id}" not in self.usage_tracker.active_sessions:
            self.usage_tracker.start_session(request.client_id, request.session_id, user_id)
        
        # Execute the tool
        result = await self.tools.execute_tool(
            tool_name=tool_name,
            parameters=request.parameters or {},
            user_id=user_id
        )
        
        # Track usage
        self.usage_tracker.record_tool_usage(
            client_id=request.client_id,
            session_id=request.session_id,
            tool_name=tool_name,
            result=result
        )
        
        return MCPResponse(
            success=result.get("success", False),
            result=result.get("result") if result.get("success") else None,
            error=result.get("error") if not result.get("success") else None,
            usage_info=result.get("metadata"),
            billing_info=result.get("billing_info")
        )

    def _get_tool_examples(self, tool_name: str) -> List[Dict[str, Any]]:
        """Get usage examples for a tool"""
        examples_map = {
            "file_read": [
                {"parameters": {"filename": "config.json"}, "description": "Read configuration file"},
                {"parameters": {"filename": "data.csv"}, "description": "Read CSV data file"}
            ],
            "calculator": [
                {"parameters": {"expression": "25 + 17"}, "description": "Simple addition"},
                {"parameters": {"expression": "100 * 0.15"}, "description": "Calculate percentage"}
            ],
            "text_analyze": [
                {"parameters": {"text": "This product is amazing!", "analysis_type": "basic"}, "description": "Basic sentiment analysis"}
            ]
        }
        return examples_map.get(tool_name, [])

    def get_server_analytics(self) -> Dict[str, Any]:
        """Get overall server analytics"""
        total_clients = len(self.usage_tracker.client_stats)
        total_cost = sum(stats["total_cost"] for stats in self.usage_tracker.client_stats.values())
        total_sessions = sum(stats["total_sessions"] for stats in self.usage_tracker.client_stats.values())
        
        return {
            "server_stats": {
                "total_clients": total_clients,
                "total_sessions": total_sessions,
                "total_revenue": total_cost,
                "active_sessions": len(self.usage_tracker.active_sessions)
            },
            "tool_popularity": self._get_tool_popularity(),
            "revenue_breakdown": self._get_revenue_breakdown()
        }
    
    def _get_tool_popularity(self) -> Dict[str, int]:
        """Get tool usage statistics"""
        tool_counts = {}
        for stats in self.usage_tracker.client_stats.values():
            for tool, count in stats["favorite_tools"].items():
                tool_counts[tool] = tool_counts.get(tool, 0) + count
        return dict(sorted(tool_counts.items(), key=lambda x: x[1], reverse=True))
    
    def _get_revenue_breakdown(self) -> Dict[str, float]:
        """Get revenue breakdown by tool category"""
        # This would be more sophisticated in a real implementation
        return {
            "file_operations": 0.12,
            "ai_processing": 0.45,
            "premium_services": 15.97,
            "utility": 0.03
        }


async def demonstrate_mcp_server_usage():
    """Comprehensive demonstration of MCP server with AgentMeter integration"""
    print("🚀 Starting MCP Server + AgentMeter v0.3.1 Integration Demo")
    print("=" * 70)
    
    # Create AgentMeter client
    meter = AgentMeter(api_key=API_KEY)
    
    # Create MCP server
    print("🏗️ Initializing MCP server with AgentMeter integration...")
    mcp_server = AgentMeterMCPServer(meter)
    
    # Initialize server
    init_request = MCPRequest(message_type=MCPMessageType.INITIALIZE)
    init_response = await mcp_server.handle_request(init_request)
    print(f"✅ Server initialized: {init_response.success}")
    
    # Demo client sessions
    demo_clients = ["client_001", "client_002", "client_003"]
    
    for client_id in demo_clients:
        print(f"\n{'='*50}")
        print(f"🔄 Demonstrating session for {client_id}")
        print(f"{'='*50}")
        
        session_id = f"session_{int(time.time())}"
        
        # List available tools
        list_request = MCPRequest(
            message_type=MCPMessageType.LIST_TOOLS,
            client_id=client_id,
            session_id=session_id
        )
        list_response = await mcp_server.handle_request(list_request)
        print(f"📋 Available tools: {len(list_response.result['tools'])}")
        
        # Demo different tool types for each client
        demo_scenarios = {
            "client_001": [
                ("file_read", {"filename": "config.json", "user_id": "user_001"}),
                ("calculator", {"expression": "150 * 0.18", "user_id": "user_001"}),
            ],
            "client_002": [
                ("text_analyze", {"text": "This is an excellent product with great features!", "analysis_type": "detailed", "user_id": "user_002"}),
                ("text_generate", {"prompt": "Write a product description", "max_length": 200, "user_id": "user_002"}),
            ],
            "client_003": [
                ("file_write", {"filename": "output.txt", "content": "Generated report data", "user_id": "user_003"}),
                ("advanced_analytics", {"data": [1, 2, 3, 4, 5], "report_type": "comprehensive", "user_id": "user_003"}),
            ]
        }
        
        # Execute tools for this client
        for tool_name, parameters in demo_scenarios.get(client_id, []):
            print(f"\n🔧 Executing {tool_name}...")
            
            call_request = MCPRequest(
                message_type=MCPMessageType.CALL_TOOL,
                tool_name=tool_name,
                parameters=parameters,
                client_id=client_id,
                session_id=session_id
            )
            
            call_response = await mcp_server.handle_request(call_request)
            
            if call_response.success:
                print(f"✅ {tool_name} executed successfully")
                if call_response.usage_info:
                    print(f"   📊 Usage: {call_response.usage_info}")
            else:
                print(f"❌ {tool_name} failed: {call_response.error}")
        
        # End session and show summary
        session_summary = mcp_server.usage_tracker.end_session(client_id, session_id)
        if session_summary:
            print(f"\n📈 Session Summary:")
            print(f"   Tools used: {len(session_summary['tools_used'])}")
            print(f"   Total calls: {session_summary['tool_calls']}")
            print(f"   Total cost: ${session_summary['total_cost']:.4f}")
        
        # Small delay between clients
        await asyncio.sleep(0.5)
    
    # Show overall analytics
    print(f"\n{'='*70}")
    print("📊 MCP SERVER ANALYTICS")
    print(f"{'='*70}")
    
    server_analytics = mcp_server.get_server_analytics()
    print(f"Total clients served: {server_analytics['server_stats']['total_clients']}")
    print(f"Total sessions: {server_analytics['server_stats']['total_sessions']}")
    print(f"Total revenue: ${server_analytics['server_stats']['total_revenue']:.4f}")
    
    print(f"\n🏆 Most popular tools:")
    for tool, count in list(server_analytics['tool_popularity'].items())[:3]:
        print(f"   {tool}: {count} uses")
    
    print(f"\n💰 Revenue by category:")
    for category, revenue in server_analytics['revenue_breakdown'].items():
        print(f"   {category}: ${revenue:.2f}")
    
    # Show individual client analytics
    print(f"\n{'='*50}")
    print("👥 INDIVIDUAL CLIENT ANALYTICS")
    print(f"{'='*50}")
    
    for client_id in demo_clients:
        analytics = mcp_server.usage_tracker.get_client_analytics(client_id)
        if "error" not in analytics:
            print(f"\n{client_id}:")
            print(f"   Sessions: {analytics['total_sessions']}")
            print(f"   Total cost: ${analytics['total_cost']:.4f}")
            print(f"   Favorite tool: {analytics['favorite_tool']}")
            print(f"   Tools tried: {analytics['tools_tried']}")
    
    print(f"\n🎉 MCP Server demonstration completed!")
    print("Check your AgentMeter dashboard to see all recorded usage and revenue.")


async def main():
    """Main function to run the MCP server demonstration"""
    if API_KEY == "your_api_key_here":
        print("❌ Please set your AGENTMETER_API_KEY environment variable")
        return
    
    await demonstrate_mcp_server_usage()


if __name__ == "__main__":
    asyncio.run(main()) 