"""
AgentMeter SDK - LangChain Integration Demonstration (v0.3.1)
============================================================

PURPOSE:
This example showcases how to integrate AgentMeter SDK v0.3.1 with LangChain agents
and function calls, demonstrating automatic usage tracking for LLM-based
applications with complex agent workflows.

SCENARIO:
We're building a LangChain-powered customer support agent that:
1. Uses LLM calls for understanding and generating responses (token-based billing)
2. Has access to various tools/functions (API request billing)
3. Offers premium analysis features (instant payments)

APPLICATION STRUCTURE:
- LangChain agents with custom tools
- Automatic token tracking via callbacks
- Function call metering for tool usage
- Premium feature gating with instant payments

PRICING MODEL:
1. LLM Token Usage: $0.000015 per input token, $0.000025 per output token
2. Tool Function Calls: $0.10 per function execution
3. Premium Analysis: $4.99 per detailed report

This demonstrates how AgentMeter v0.3.1 seamlessly integrates with LangChain's
callback system and tool framework for comprehensive usage tracking.
"""

import os
import time
import json
from typing import Dict, List, Any, Optional, Type
from agentmeter import AgentMeter, MeterEvent, MeterEventCreate

# Configuration
API_KEY = os.getenv("AGENTMETER_API_KEY", "your_api_key_here")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")

# LangChain imports with graceful fallback
try:
    from langchain.llms import OpenAI
    from langchain.chat_models import ChatOpenAI
    from langchain.agents import Tool, AgentExecutor, create_react_agent
    from langchain.prompts import PromptTemplate
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.schema import LLMResult, AgentAction, AgentFinish
    from langchain.tools import BaseTool
    from langchain import hub
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️  LangChain not installed. Install with: pip install langchain openai")


class AgentMeterLangChainCallback(BaseCallbackHandler):
    """
    Enhanced AgentMeter v0.3.1 callback for LangChain integration
    Automatically tracks token usage and costs for all LLM interactions
    """
    
    def __init__(
        self,
        meter: AgentMeter,
        token_meter_type_id: str,
        subject_id: str,
        input_token_price: float = 0.000015,
        output_token_price: float = 0.000025,
        enable_detailed_logging: bool = True
    ):
        super().__init__()
        self.meter = meter
        self.token_meter_type_id = token_meter_type_id
        self.subject_id = subject_id
        self.input_token_price = input_token_price
        self.output_token_price = output_token_price
        self.enable_detailed_logging = enable_detailed_logging
        
        # Track current operation
        self.current_operation = {}
        self.operation_count = 0
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """Called when LLM starts - track input tokens"""
        self.operation_count += 1
        
        if prompts:
            prompt_text = prompts[0]
            # Estimate input tokens (rough: 4 chars = 1 token)
            estimated_input_tokens = len(prompt_text) // 4
            
            self.current_operation = {
                "operation_id": self.operation_count,
                "model_name": serialized.get("name", "unknown"),
                "prompt_length": len(prompt_text),
                "estimated_input_tokens": estimated_input_tokens,
                "start_time": time.time(),
                "kwargs": kwargs
            }
            
            if self.enable_detailed_logging:
                print(f"🤖 LLM Start #{self.operation_count}: {estimated_input_tokens} input tokens estimated")
    
    def on_llm_end(self, response: LLMResult, **kwargs):
        """Called when LLM ends - track output tokens and record usage"""
        if not self.current_operation:
            return
        
        # Extract output text and estimate tokens
        output_text = ""
        if response.generations:
            for generation_list in response.generations:
                for generation in generation_list:
                    output_text += generation.text
        
        estimated_output_tokens = len(output_text) // 4
        
        # Get actual token usage if available (OpenAI provides this)
        actual_input_tokens = self.current_operation["estimated_input_tokens"]
        actual_output_tokens = estimated_output_tokens
        
        if hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            if token_usage:
                actual_input_tokens = token_usage.get('prompt_tokens', actual_input_tokens)
                actual_output_tokens = token_usage.get('completion_tokens', actual_output_tokens)
        
        # Calculate processing time
        processing_time = time.time() - self.current_operation["start_time"]
        
        # Calculate total cost
        total_cost = (actual_input_tokens * self.input_token_price) + (actual_output_tokens * self.output_token_price)
        
        # Record the usage with v0.3.1 architecture
        try:
            event = self.meter.meter_events.record(
                meter_type_id=self.token_meter_type_id,
                subject_id=self.subject_id,
                quantity=total_cost,
                metadata={
                    "operation_id": self.current_operation["operation_id"],
                    "model_name": self.current_operation["model_name"],
                    "processing_time": processing_time,
                    "prompt_length": self.current_operation["prompt_length"],
                    "response_length": len(output_text),
                    "input_tokens": actual_input_tokens,
                    "output_tokens": actual_output_tokens,
                    "input_token_price": self.input_token_price,
                    "output_token_price": self.output_token_price,
                    "langchain_callback": True
                }
            )
            
            if self.enable_detailed_logging:
                print(f"💰 LLM End #{self.current_operation['operation_id']}: "
                      f"${total_cost:.4f} ({actual_input_tokens}+{actual_output_tokens} tokens)")
                
        except Exception as e:
            print(f"❌ Failed to record LLM usage: {e}")
        
        # Clear current operation
        self.current_operation = {}
    
    def on_llm_error(self, error: Exception, **kwargs):
        """Called when LLM encounters an error"""
        if self.current_operation:
            print(f"❌ LLM Error #{self.current_operation['operation_id']}: {error}")
            
            # Still record input tokens for failed calls
            try:
                input_cost = self.current_operation["estimated_input_tokens"] * self.input_token_price
                
                self.meter.meter_events.record(
                    meter_type_id=self.token_meter_type_id,
                    subject_id=self.subject_id,
                    quantity=input_cost,
                    metadata={
                        "operation_id": self.current_operation["operation_id"],
                        "error": str(error),
                        "failed_call": True,
                        "input_tokens": self.current_operation["estimated_input_tokens"],
                        "output_tokens": 0
                    }
                )
            except Exception as track_error:
                print(f"❌ Failed to track error usage: {track_error}")
        
        self.current_operation = {}
    
    def on_agent_action(self, action: AgentAction, **kwargs):
        """Called when agent takes an action (tool usage)"""
        if self.enable_detailed_logging:
            print(f"🔧 Agent Action: {action.tool} with input: {action.tool_input}")
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs):
        """Called when agent finishes"""
        if self.enable_detailed_logging:
            print(f"✅ Agent Finished: {finish.return_values}")


class CustomerSupportTools:
    """
    Customer support tools with v0.3.1 AgentMeter integration
    """
    
    def __init__(self, meter: AgentMeter, api_meter_type_id: str):
        self.meter = meter
        self.api_meter_type_id = api_meter_type_id
    
    def record_api_usage(self, subject_id: str, tool_name: str, cost: float, metadata: dict = None):
        """Helper method to record API usage"""
        try:
            return self.meter.meter_events.record(
                meter_type_id=self.api_meter_type_id,
                subject_id=subject_id,
                quantity=cost,
                metadata={
                    "tool_name": tool_name,
                    **(metadata or {})
                }
            )
        except Exception as e:
            print(f"❌ Failed to record API usage for {tool_name}: {e}")
            return None

    def search_knowledge_base(self, query: str, subject_id: str = "default_user") -> str:
        """Search the customer support knowledge base"""
        print(f"🔍 Searching knowledge base for: {query}")
        
        # Record API usage
        self.record_api_usage(
            subject_id=subject_id,
            tool_name="search_knowledge_base",
            cost=0.10,
            metadata={"query_length": len(query)}
        )
        
        # Simulate knowledge base search
        knowledge_items = [
            "Password reset instructions: Visit settings > security > reset password",
            "Billing inquiries: Contact billing@company.com or call 1-800-BILLING",
            "Technical support: Use live chat or submit a ticket via support portal",
            "Account suspension: Check email for suspension notice and follow appeal process",
            "Feature requests: Submit via our public roadmap at roadmap.company.com"
        ]
        
        # Simple keyword matching
        relevant_items = [item for item in knowledge_items if any(word.lower() in item.lower() for word in query.split())]
        
        if relevant_items:
            return f"Found {len(relevant_items)} relevant articles:\n" + "\n".join(relevant_items)
        else:
            return "No specific articles found. Please contact human support for assistance."

    def check_user_account(self, user_email: str, subject_id: str = "default_user") -> str:
        """Check user account status and information"""
        print(f"👤 Checking account for: {user_email}")
        
        # Record API usage
        self.record_api_usage(
            subject_id=subject_id,
            tool_name="check_user_account",
            cost=0.15,
            metadata={"user_email": user_email}
        )
        
        # Simulate account lookup
        account_info = {
            "email": user_email,
            "status": "active",
            "plan": "pro",
            "last_login": "2024-01-15 14:30:00",
            "support_tickets": 2,
            "billing_status": "current"
        }
        
        return json.dumps(account_info, indent=2)

    def create_support_ticket(self, issue_description: str, priority: str = "normal", subject_id: str = "default_user") -> str:
        """Create a new support ticket"""
        print(f"🎫 Creating support ticket: {issue_description[:50]}...")
        
        # Record API usage
        self.record_api_usage(
            subject_id=subject_id,
            tool_name="create_support_ticket",
            cost=0.05,
            metadata={
                "priority": priority,
                "description_length": len(issue_description)
            }
        )
        
        ticket_id = f"TICKET-{int(time.time())}"
        return f"Support ticket {ticket_id} created successfully with priority: {priority}"
    
    def get_tools_list(self) -> List[Tool]:
        """Get LangChain Tool objects for all available tools"""
        return [
            Tool(
                name="search_knowledge_base",
                description="Search the customer support knowledge base for relevant articles and solutions",
                func=lambda query: self.search_knowledge_base(query)
            ),
            Tool(
                name="check_user_account", 
                description="Check user account status, plan details, and billing information",
                func=lambda email: self.check_user_account(email)
            ),
            Tool(
                name="create_support_ticket",
                description="Create a new support ticket for issues that require human assistance",
                func=lambda description: self.create_support_ticket(description)
            )
        ]


class PremiumAnalysisService:
    """
    Premium analysis service with instant payment integration
    """
    
    def __init__(self, meter: AgentMeter, instant_meter_type_id: str):
        self.meter = meter
        self.instant_meter_type_id = instant_meter_type_id
    
    def should_charge_for_analysis(self, *args, **kwargs):
        """Determine if we should charge for analysis (always True in this demo)"""
        return True

    def analyze_support_interaction(self, conversation_history: List[str], subject_id: str, detailed_analysis: bool = False) -> Dict[str, Any]:
        """
        Perform premium analysis of support interaction
        Charges $4.99 for detailed analysis
        """
        print(f"🔬 Performing premium analysis for {subject_id}")
        
        if detailed_analysis and self.should_charge_for_analysis():
            try:
                # Record instant payment
                self.meter.meter_events.record(
                    meter_type_id=self.instant_meter_type_id,
                    subject_id=subject_id,
                    quantity=4.99,
                    metadata={
                        "service": "premium_support_analytics",
                        "conversation_length": len(conversation_history),
                        "detailed_analysis": True
                    }
                )
                print("💳 Premium analysis payment of $4.99 recorded")
            except Exception as e:
                print(f"❌ Failed to record premium payment: {e}")
                return {"error": "Payment processing failed", "analysis": None}
        
        # Simulate comprehensive analysis
        analysis = {
            "conversation_summary": {
                "total_messages": len(conversation_history),
                "estimated_duration": len(conversation_history) * 2,  # 2 minutes per message
                "complexity_score": min(len(conversation_history) * 0.3, 10.0)
            },
            "sentiment_analysis": {
                "overall_sentiment": "neutral",
                "sentiment_progression": ["frustrated", "neutral", "satisfied"],
                "key_emotions": ["confusion", "relief", "appreciation"]
            },
            "topic_analysis": {
                "primary_topics": ["account_access", "billing_inquiry", "feature_request"],
                "resolution_status": "resolved",
                "escalation_recommended": False
            },
            "recommendations": {
                "follow_up_required": False,
                "knowledge_base_updates": [
                    "Add clearer password reset instructions",
                    "Improve billing FAQ section"
                ],
                "agent_feedback": "Excellent handling of multi-topic inquiry"
            }
        }
        
        if detailed_analysis:
            analysis.update({
                "detailed_metrics": {
                    "response_time_analysis": "Average 45 seconds per response",
                    "resolution_efficiency": "High - resolved in single session",
                    "customer_effort_score": 2.1,  # Low effort for customer
                    "agent_performance": "Excellent"
                },
                "advanced_insights": {
                    "customer_journey_stage": "retention",
                    "churn_risk": "low",
                    "upsell_opportunities": ["premium_support", "training_services"],
                    "satisfaction_prediction": 8.5
                },
                "comparative_analysis": {
                    "vs_similar_cases": "40% faster resolution",
                    "vs_team_average": "Above average satisfaction",
                    "industry_benchmark": "Top 25% performance"
                }
            })
        
        return analysis


class LangChainAgentMeterDemo:
    """
    Comprehensive demonstration of LangChain + AgentMeter v0.3.1 integration
    """
    
    def __init__(self, api_key: str, openai_api_key: str):
        self.meter = AgentMeter(api_key=api_key)
        self.openai_api_key = openai_api_key
        
        # Initialize meter types (in real app, these would be created once)
        self.setup_meter_types()
        
        # Initialize services
        self.support_tools = CustomerSupportTools(self.meter, self.api_meter_type_id)
        self.premium_service = PremiumAnalysisService(self.meter, self.instant_meter_type_id)
    
    def setup_meter_types(self):
        """Setup required meter types"""
        try:
            # Create meter types for different billing models
            token_meter = self.meter.meter_types.create(
                name="LLM Token Usage",
                description="Token-based billing for LLM API calls"
            )
            self.token_meter_type_id = token_meter.id
            
            api_meter = self.meter.meter_types.create(
                name="API Tool Calls",
                description="Fixed price billing for tool/function calls"
            )
            self.api_meter_type_id = api_meter.id
            
            instant_meter = self.meter.meter_types.create(
                name="Premium Services",
                description="Instant payment for premium features"
            )
            self.instant_meter_type_id = instant_meter.id
            
            print("✅ Meter types created successfully")
            
        except Exception as e:
            print(f"⚠️ Error creating meter types (they may already exist): {e}")
            # Use default IDs if creation fails
            self.token_meter_type_id = "default_token_meter"
            self.api_meter_type_id = "default_api_meter"
            self.instant_meter_type_id = "default_instant_meter"
    
    def create_customer_support_agent(self):
        """Create a LangChain agent with AgentMeter callback integration"""
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is required for this demo")
        
        # Initialize LLM with AgentMeter callback
        callback = AgentMeterLangChainCallback(
            meter=self.meter,
            token_meter_type_id=self.token_meter_type_id,
            subject_id="langchain_agent"
        )
        
        llm = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            temperature=0.7,
            callbacks=[callback]
        )
        
        # Get tools from our support tools
        tools = self.support_tools.get_tools_list()
        
        # Create agent prompt
        prompt = PromptTemplate.from_template("""
        You are a helpful customer support agent. Use the available tools to assist users with their inquiries.
        
        Available tools: {tool_names}
        
        User question: {input}
        
        Think step by step and use tools when needed to provide accurate information.
        
        {agent_scratchpad}
        """)
        
        # Create and return agent
        agent = create_react_agent(llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=3)
    
    def demonstrate_basic_interaction(self, agent_executor, user_query: str, user_id: str):
        """Demonstrate basic agent interaction with usage tracking"""
        print(f"\n{'='*60}")
        print(f"🎯 Basic Interaction Demo - User: {user_id}")
        print(f"Query: {user_query}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            result = agent_executor.invoke({"input": user_query})
            processing_time = time.time() - start_time
            
            print(f"\n✅ Agent Response:")
            print(result.get("output", "No output"))
            print(f"\n⏱️ Processing time: {processing_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            print(f"❌ Error during interaction: {e}")
            return None
    
    def demonstrate_premium_analysis(self, conversation_history: List[str], user_id: str):
        """Demonstrate premium analysis with instant payment"""
        print(f"\n{'='*60}")
        print(f"💎 Premium Analysis Demo - User: {user_id}")
        print(f"{'='*60}")
        
        analysis = self.premium_service.analyze_support_interaction(
            conversation_history=conversation_history,
            subject_id=user_id,
            detailed_analysis=True
        )
        
        print("\n📊 Premium Analysis Results:")
        print(json.dumps(analysis, indent=2))
        return analysis
    
    def demonstrate_usage_monitoring(self, user_id: str):
        """Demonstrate usage monitoring and analytics"""
        print(f"\n{'='*60}")
        print(f"📈 Usage Monitoring Demo - User: {user_id}")
        print(f"{'='*60}")
        
        try:
            # Get usage analytics
            events = self.meter.meter_events.list(subject_id=user_id, limit=10)
            
            if events:
                print(f"📋 Recent Usage Events for {user_id}:")
                total_cost = 0
                for event in events:
                    print(f"  • {event.created_at}: ${event.quantity:.4f} - {event.metadata.get('tool_name', 'Unknown')}")
                    total_cost += event.quantity
                
                print(f"\n💰 Total Usage Cost: ${total_cost:.4f}")
            else:
                print(f"No usage events found for {user_id}")
                
        except Exception as e:
            print(f"❌ Error fetching usage data: {e}")
    
    def run_comprehensive_demo(self):
        """Run a comprehensive demonstration of all features"""
        print("🚀 Starting LangChain + AgentMeter v0.3.1 Integration Demo")
        print("=" * 70)
        
        if not LANGCHAIN_AVAILABLE:
            print("❌ LangChain not available. Please install: pip install langchain openai")
            return
        
        try:
            # Create agent
            print("🤖 Creating customer support agent...")
            agent_executor = self.create_customer_support_agent()
            
            # Demo scenarios
            demo_user = "demo_user_001"
            
            # Scenario 1: Basic support query
            result1 = self.demonstrate_basic_interaction(
                agent_executor,
                "I forgot my password and can't access my account. Can you help?",
                demo_user
            )
            
            # Scenario 2: Account information query
            result2 = self.demonstrate_basic_interaction(
                agent_executor,
                "Can you check my account status for user@example.com?",
                demo_user
            )
            
            # Scenario 3: Create support ticket
            result3 = self.demonstrate_basic_interaction(
                agent_executor,
                "I'm having issues with billing charges that seem incorrect. Please create a ticket.",
                demo_user
            )
            
            # Build conversation history for premium analysis
            conversation_history = [
                "User: I forgot my password and can't access my account",
                "Agent: I can help you with that. Let me search our knowledge base...",
                result1.get("output", "") if result1 else "",
                "User: Can you also check my account status?",
                "Agent: Sure! Let me look that up for you...",
                result2.get("output", "") if result2 else "",
                "User: Thanks! One more thing - I need to report a billing issue",
                "Agent: I'll create a support ticket for that...",
                result3.get("output", "") if result3 else ""
            ]
            
            # Scenario 4: Premium analysis
            self.demonstrate_premium_analysis(conversation_history, demo_user)
            
            # Scenario 5: Usage monitoring
            self.demonstrate_usage_monitoring(demo_user)
            
            print("\n🎉 Demo completed successfully!")
            print("Check your AgentMeter dashboard to see all recorded usage and costs.")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()


def main():
    """
    Main function to run the LangChain + AgentMeter integration demo
    """
    # Verify configuration
    if API_KEY == "your_api_key_here":
        print("❌ Please set your AGENTMETER_API_KEY environment variable")
        return
    
    if OPENAI_API_KEY == "your_openai_api_key":
        print("❌ Please set your OPENAI_API_KEY environment variable")
        return
    
    # Run demo
    demo = LangChainAgentMeterDemo(API_KEY, OPENAI_API_KEY)
    demo.run_comprehensive_demo()


if __name__ == "__main__":
    main() 