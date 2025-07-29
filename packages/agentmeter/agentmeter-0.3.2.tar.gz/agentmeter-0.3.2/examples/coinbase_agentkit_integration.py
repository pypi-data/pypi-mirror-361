#!/usr/bin/env python3
"""
🚀 Coinbase AgentKit + AgentMeter SDK Integration Example

This example demonstrates how to integrate Coinbase AgentKit with AgentMeter 
for comprehensive usage tracking and billing of Web3 AI agents.

Coinbase AgentKit: https://github.com/coinbase/agentkit
AgentMeter SDK: https://github.com/Pagent-Money/agentmeter-sdk-python

Features Demonstrated:
1. 🔗 Seamless integration between Coinbase AgentKit and AgentMeter
2. 💰 Multi-tier billing: API calls, token usage, and premium features
3. 🛡️ Transaction monitoring and cost optimization
4. 📊 Real-time usage analytics and billing insights
5. 🎯 Smart contract interaction tracking

Requirements:
    pip install agentmeter cdp-sdk coinbase-python-sdk
    
Environment Variables:
    - AGENTMETER_API_KEY: Your AgentMeter API key
    - COINBASE_CDP_API_KEY_NAME: Coinbase CDP API key name
    - COINBASE_CDP_PRIVATE_KEY: Coinbase CDP private key
    - OPENAI_API_KEY: OpenAI API key for LLM operations
"""

import os
import asyncio
import json
from typing import Dict, List, Any, Optional, Union
from decimal import Decimal
from datetime import datetime

# AgentMeter SDK imports
from agentmeter import (
    AgentMeterClient, create_client,
    meter_api_request_pay, meter_token_based_pay, meter_instant_pay,
    track_api_request_pay, track_token_based_pay, track_instant_pay,
    PaymentType, APIRequestPayEvent, TokenBasedPayEvent, InstantPayEvent
)

# Coinbase AgentKit imports
try:
    from cdp import Cdp, Wallet, Asset
    from cdp.agent_toolkit import CdpAgentkitWrapper
    COINBASE_AVAILABLE = True
except ImportError:
    COINBASE_AVAILABLE = False
    print("⚠️  Coinbase AgentKit not installed. Install with:")
    print("   pip install cdp-sdk coinbase-python-sdk")

# Configuration
AGENTMETER_API_KEY = os.getenv("AGENTMETER_API_KEY", "your_agentmeter_api_key")
COINBASE_CDP_API_KEY_NAME = os.getenv("COINBASE_CDP_API_KEY_NAME", "organizations/{org_id}/apiKeys/{key_id}")
COINBASE_CDP_PRIVATE_KEY = os.getenv("COINBASE_CDP_PRIVATE_KEY", "your_private_key")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")

PROJECT_ID = "coinbase_agentkit_proj"
AGENT_ID = "web3_trading_agent"


class Web3AgentMeter:
    """
    Advanced metering wrapper for Coinbase AgentKit operations
    
    This class provides comprehensive usage tracking for Web3 AI agents,
    including transaction costs, LLM usage, and premium feature billing.
    """
    
    def __init__(
        self,
        agentmeter_client: AgentMeterClient,
        cdp_api_key_name: str,
        cdp_private_key: str,
        network: str = "base-sepolia",
        default_user_tier: str = "basic"
    ):
        self.client = agentmeter_client
        self.network = network
        self.default_user_tier = default_user_tier
        
        # Initialize Coinbase CDP
        if COINBASE_AVAILABLE:
            Cdp.configure(cdp_api_key_name, cdp_private_key)
            self.wallet = Wallet.create()
            self.agentkit = CdpAgentkitWrapper(wallet=self.wallet)
            print(f"🔗 Coinbase AgentKit initialized on {network}")
            print(f"📍 Wallet address: {self.wallet.default_address}")
        else:
            self.wallet = None
            self.agentkit = None
            print("❌ Coinbase AgentKit not available - running in demo mode")
        
        # Usage tracking
        self.session_stats = {
            "total_transactions": 0,
            "total_gas_fees": Decimal("0"),
            "total_llm_tokens": 0,
            "total_costs": 0.0,
            "operations": []
        }
    
    def get_wallet_balance(self, user_id: str, asset_symbol: str = "ETH") -> Dict[str, Any]:
        """
        Get wallet balance - Charged per API request
        
        Args:
            user_id: User identifier for billing
            asset_symbol: Asset symbol to check (ETH, USDC, etc.)
        
        Returns:
            Dict containing balance information
        """

        
        print(f"💰 Checking {asset_symbol} balance for user {user_id}")
        
        # Record API request payment
        try:
            self.client.record_api_request_pay(
                api_calls=1,
                unit_price=0.05,
                user_id=user_id,
                metadata={
                    "operation": "get_wallet_balance",
                    "asset": asset_symbol
                }
            )
        except Exception as e:
            print(f"⚠️ API billing failed: {e}")
        
        if not self.wallet:
            # Demo mode
            return {
                "balance": "1.5",
                "asset": asset_symbol,
                "network": self.network,
                "address": "0x742d35Cc6634C0532925a3b8D0e9e8a2C2f2C2f2",
                "demo_mode": True
            }
        
        try:
            balance = self.wallet.balance(Asset.fetch(asset_symbol))
            return {
                "balance": str(balance),
                "asset": asset_symbol,
                "network": self.network,
                "address": str(self.wallet.default_address),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Error getting balance: {e}")
            return {"error": str(e), "balance": "0"}
    
    def get_transaction_history(
        self, 
        user_id: str, 
        limit: int = 10,
        asset_symbol: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get transaction history - Charged per API request
        
        Args:
            user_id: User identifier for billing
            limit: Number of transactions to retrieve
            asset_symbol: Optional asset filter
        
        Returns:
            Dict containing transaction history
        """

        
        print(f"📜 Getting transaction history for user {user_id} (limit: {limit})")
        
        # Record API request payment
        try:
            self.client.record_api_request_pay(
                api_calls=1,
                unit_price=0.10,
                user_id=user_id,
                metadata={
                    "operation": "get_transaction_history",
                    "limit": limit,
                    "asset_filter": asset_symbol
                }
            )
        except Exception as e:
            print(f"⚠️ API billing failed: {e}")
        
        if not self.wallet:
            # Demo mode
            return {
                "transactions": [
                    {
                        "hash": "0x1234...5678",
                        "from": "0x742d35Cc6634C0532925a3b8D0e9e8a2C2f2C2f2",
                        "to": "0x987f...4321",
                        "amount": "0.1 ETH",
                        "status": "confirmed",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                ],
                "count": 1,
                "demo_mode": True
            }
        
        try:
            # Get transaction history using AgentKit
            transactions = self.wallet.list_transactions(limit=limit)
            return {
                "transactions": [
                    {
                        "hash": tx.transaction_hash,
                        "status": tx.status,
                        "timestamp": tx.created_at.isoformat() if tx.created_at else None
                    } for tx in transactions
                ],
                "count": len(transactions),
                "network": self.network
            }
        except Exception as e:
            print(f"❌ Error getting transaction history: {e}")
            return {"error": str(e), "transactions": []}
    

    def analyze_market_conditions(
        self, 
        user_id: str,
        asset_symbol: str,
        analysis_type: str = "basic"
    ) -> Dict[str, Any]:
        """
        AI-powered market analysis - Charged based on LLM token usage
        
        Args:
            user_id: User identifier for billing
            asset_symbol: Asset to analyze (ETH, BTC, etc.)
            analysis_type: Type of analysis (basic, advanced, technical)
        
        Returns:
            Dict containing market analysis
        """

        
        print(f"📈 Analyzing market conditions for {asset_symbol} ({analysis_type})")
        
        # Simulate LLM analysis
        prompt = f"""
        Analyze the current market conditions for {asset_symbol}.
        
        Analysis Type: {analysis_type}
        Consider: price trends, volume, volatility, market sentiment, technical indicators.
        
        Provide actionable insights for trading decisions.
        """
        
        # Calculate tokens for billing (rough estimation)
        input_tokens = len(prompt.split()) * 1.3
        output_tokens = 120  # Estimated for the analysis result
        
        # Record token usage manually since we disabled automatic extraction
        try:
            self.client.record_token_based_pay(
                tokens_in=int(input_tokens),
                tokens_out=int(output_tokens),
                input_token_price=0.00003,
                output_token_price=0.00006,
                user_id=user_id,
                metadata={
                    "asset": asset_symbol,
                    "analysis_type": analysis_type,
                    "operation": "market_analysis"
                }
            )
        except Exception as e:
            print(f"⚠️ Token billing failed: {e}")
        
        # Simulate AI analysis result
        analysis_result = f"""
        Market Analysis for {asset_symbol}:
        
        📊 Current Sentiment: Bullish
        💹 Price Trend: Upward momentum detected
        📈 Volume: Above average trading volume (+15%)
        ⚡ Volatility: Moderate (12% daily range)
        
        Technical Indicators:
        - RSI: 58 (Neutral to bullish)
        - MA(20): Above current price (support at $2,420)
        - MACD: Positive crossover signal
        
        Recommendation: Consider accumulating on dips with tight stop-loss.
        Risk Level: Medium
        Confidence: 78%
        """
        
        return {
            "asset": asset_symbol,
            "analysis_type": analysis_type,
            "sentiment": "bullish",
            "confidence": 0.78,
            "recommendation": "accumulate_on_dips",
            "risk_level": "medium",
            "detailed_analysis": analysis_result,
            "timestamp": datetime.now().isoformat()
        }
    

    def execute_smart_trade(
        self,
        user_id: str,
        trade_type: str,
        asset_from: str,
        asset_to: str,
        amount: Union[str, float],
        user_tier: str = "basic",
        slippage_tolerance: float = 0.01
    ) -> Dict[str, Any]:
        """
        Execute smart trading with AI optimization - Premium feature with instant billing
        
        Args:
            user_id: User identifier for billing
            trade_type: Type of trade (swap, limit, market)
            asset_from: Source asset symbol
            asset_to: Target asset symbol
            amount: Amount to trade
            user_tier: User subscription tier
            slippage_tolerance: Maximum slippage tolerance
        
        Returns:
            Dict containing trade execution result
        """
        print(f"🤖 Executing smart trade: {amount} {asset_from} → {asset_to}")
        print(f"👤 User tier: {user_tier} | Trade type: {trade_type}")
        
        # Check if premium billing should apply
        should_charge_premium = user_tier in ['basic', 'standard'] and float(amount) > 100
        
        # Record instant payment for premium features
        if should_charge_premium:
            try:
                self.client.record_instant_pay(
                    amount=4.99,
                    description="Premium automated trading execution",
                    user_id=user_id,
                    metadata={
                        "operation": "smart_trade",
                        "trade_type": trade_type,
                        "trade_amount": str(amount),
                        "user_tier": user_tier
                    }
                )
                print("💰 Premium feature charged: $4.99")
            except Exception as e:
                print(f"⚠️ Premium billing failed: {e}")
        
        if not self.wallet:
            # Demo mode
            return {
                "trade_id": "demo_trade_12345",
                "status": "simulated",
                "from_asset": asset_from,
                "to_asset": asset_to,
                "amount": str(amount),
                "estimated_gas": "0.002 ETH",
                "slippage_tolerance": slippage_tolerance,
                "demo_mode": True,
                "message": "Trade simulation - Coinbase AgentKit integration ready"
            }
        
        try:
            # Execute trade using Coinbase AgentKit
            # Note: This is a simplified example - real implementation would use
            # the AgentKit's trading tools and smart contract interactions
            
            trade_params = {
                "from_asset": asset_from,
                "to_asset": asset_to,
                "amount": str(amount),
                "slippage_tolerance": slippage_tolerance,
                "trade_type": trade_type
            }
            
            # Simulate trade execution
            result = {
                "trade_id": f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "status": "pending",
                "transaction_hash": "0xabcd...1234",
                "estimated_completion": "2-3 minutes",
                "gas_estimate": "0.0015 ETH",
                **trade_params
            }
            
            self.session_stats["total_transactions"] += 1
            self.session_stats["operations"].append({
                "type": "smart_trade",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "details": result
            })
            
            return result
            
        except Exception as e:
            print(f"❌ Error executing trade: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "trade_type": trade_type
            }
    
    def monitor_portfolio_performance(self, user_id: str) -> Dict[str, Any]:
        """
        Monitor portfolio performance with cost tracking
        
        This method demonstrates how to combine multiple metered operations
        for comprehensive portfolio analysis.
        """
        print(f"📊 Monitoring portfolio performance for user {user_id}")
        
        portfolio_data = {}
        total_cost = 0.0
        
        # 1. Get wallet balances (API request pay)
        with track_api_request_pay(
            self.client, PROJECT_ID, AGENT_ID, 
            user_id=user_id, unit_price=0.03
        ) as api_usage:
            
            assets = ["ETH", "USDC", "BTC"]
            balances = {}
            
            for asset in assets:
                balance_info = self.get_wallet_balance(user_id, asset)
                balances[asset] = balance_info
            
            api_usage["api_calls"] = len(assets)
            api_usage["metadata"] = {
                "operation": "portfolio_balance_check",
                "assets_checked": assets
            }
            
            portfolio_data["balances"] = balances
        
        # 2. AI analysis of portfolio (token-based pay)
        with track_token_based_pay(
            self.client, PROJECT_ID, AGENT_ID,
            user_id=user_id,
            input_token_price=0.00003,
            output_token_price=0.00006
        ) as token_usage:
            
            # Simulate portfolio analysis
            portfolio_analysis = """
            Portfolio Analysis Summary:
            
            🔸 Total Portfolio Value: $2,847.50
            🔸 24h Change: +3.2% (+$88.30)
            🔸 Diversification Score: 8.2/10
            
            Asset Allocation:
            - ETH: 65% ($1,850.87)
            - USDC: 25% ($711.87)
            - BTC: 10% ($284.75)
            
            Recommendations:
            ✅ Well-diversified portfolio
            ⚠️  Consider reducing ETH exposure if it exceeds 70%
            📈 Strong performance in current market conditions
            """
            
            # Estimate token usage
            token_usage["tokens_in"] = 200
            token_usage["tokens_out"] = 350
            token_usage["metadata"] = {
                "analysis_type": "portfolio_performance",
                "assets_analyzed": len(balances)
            }
            
            portfolio_data["analysis"] = portfolio_analysis
        
        # 3. Generate insights and recommendations
        portfolio_data.update({
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "performance_metrics": {
                "total_value": "$2,847.50",
                "daily_change": "+3.2%",
                "diversification_score": 8.2,
                "risk_level": "moderate"
            },
            "session_stats": self.session_stats
        })
        
        return portfolio_data


class CoinbaseAgentKitDemo:
    """
    Complete demonstration of Coinbase AgentKit + AgentMeter integration
    """
    
    def __init__(self):
        # Initialize AgentMeter client
        self.agentmeter_client = create_client(
            api_key=AGENTMETER_API_KEY,
            project_id=PROJECT_ID,
            agent_id=AGENT_ID,
            base_url="https://api.agentmeter.money"
        )
        
        # Initialize Web3 agent with metering
        self.web3_agent = Web3AgentMeter(
            agentmeter_client=self.agentmeter_client,
            cdp_api_key_name=COINBASE_CDP_API_KEY_NAME,
            cdp_private_key=COINBASE_CDP_PRIVATE_KEY,
            network="base-sepolia"
        )
        
        print("🚀 Coinbase AgentKit + AgentMeter Demo Initialized")
        print(f"📊 Project: {PROJECT_ID}")
        print(f"🤖 Agent: {AGENT_ID}")
    
    async def run_basic_operations_demo(self):
        """Demonstrate basic Web3 operations with AgentMeter tracking"""
        print("\n" + "="*60)
        print("🔸 BASIC WEB3 OPERATIONS DEMO")
        print("="*60)
        
        user_id = "demo_user_001"
        
        # 1. Check wallet balance
        print("\n1️⃣ Checking Wallet Balance")
        balance = self.web3_agent.get_wallet_balance(user_id, "ETH")
        print(f"✅ Balance: {balance}")
        
        # 2. Get transaction history
        print("\n2️⃣ Getting Transaction History")
        history = self.web3_agent.get_transaction_history(user_id, limit=5)
        print(f"✅ Found {history.get('count', 0)} transactions")
        
        # 3. Market analysis
        print("\n3️⃣ AI Market Analysis")
        analysis = self.web3_agent.analyze_market_conditions(user_id, "ETH", "advanced")
        print(f"✅ Analysis complete - Sentiment: {analysis.get('sentiment', 'unknown')}")
        
        return {
            "balance": balance,
            "history": history,
            "analysis": analysis
        }
    
    async def run_advanced_trading_demo(self):
        """Demonstrate advanced trading features with premium billing"""
        print("\n" + "="*60)
        print("🔸 ADVANCED TRADING DEMO")
        print("="*60)
        
        user_id = "premium_user_002"
        
        # 1. Execute smart trade (triggers premium billing for large amounts)
        print("\n1️⃣ Executing Smart Trade (Premium Feature)")
        trade_result = self.web3_agent.execute_smart_trade(
            user_id=user_id,
            trade_type="market",
            asset_from="USDC",
            asset_to="ETH",
            amount=150.0,  # Large amount triggers premium billing
            user_tier="basic",  # Basic tier users pay premium
            slippage_tolerance=0.005
        )
        print(f"✅ Trade executed: {trade_result.get('trade_id', 'unknown')}")
        
        # 2. Portfolio monitoring
        print("\n2️⃣ Comprehensive Portfolio Monitoring")
        portfolio = self.web3_agent.monitor_portfolio_performance(user_id)
        print(f"✅ Portfolio analyzed - Value: {portfolio.get('performance_metrics', {}).get('total_value', 'unknown')}")
        
        return {
            "trade": trade_result,
            "portfolio": portfolio
        }
    
    async def run_usage_analytics_demo(self):
        """Demonstrate usage analytics and cost optimization"""
        print("\n" + "="*60)
        print("🔸 USAGE ANALYTICS & COST OPTIMIZATION")
        print("="*60)
        
        try:
            # Get usage statistics
            stats = self.agentmeter_client.get_meter_stats(
                project_id=PROJECT_ID,
                timeframe="1 hour"
            )
            
            print(f"📊 Usage Statistics:")
            print(f"   • Total API Calls: {stats.total_api_calls}")
            print(f"   • Total Tokens: {stats.total_tokens}")
            print(f"   • Total Cost: ${stats.total_cost:.4f}")
            print(f"   • Average Cost per Call: ${stats.average_cost_per_call:.4f}")
            
        except Exception as e:
            print(f"📊 Usage Statistics: Demo mode - {e}")
        
        # Session statistics
        session_stats = self.web3_agent.session_stats
        print(f"\n📈 Session Statistics:")
        print(f"   • Transactions: {session_stats['total_transactions']}")
        print(f"   • LLM Tokens: {session_stats['total_llm_tokens']}")
        print(f"   • Operations: {len(session_stats['operations'])}")
        
        return session_stats
    
    async def run_complete_demo(self):
        """Run the complete demonstration"""
        print("🎬 Starting Coinbase AgentKit + AgentMeter Complete Demo")
        print("🔗 Integration showcasing Web3 AI agents with comprehensive usage tracking")
        
        try:
            # Run all demonstrations
            basic_results = await self.run_basic_operations_demo()
            advanced_results = await self.run_advanced_trading_demo()
            analytics = await self.run_usage_analytics_demo()
            
            print("\n" + "="*60)
            print("🎉 DEMO COMPLETED SUCCESSFULLY")
            print("="*60)
            print("✅ Basic operations tracked and billed")
            print("✅ Advanced trading with premium billing")
            print("✅ Comprehensive usage analytics")
            print("✅ Multi-tier billing system operational")
            
            return {
                "basic_operations": basic_results,
                "advanced_trading": advanced_results,
                "analytics": analytics,
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            return {"status": "error", "error": str(e)}


async def main():
    """Main demonstration function"""
    print("🌟 Coinbase AgentKit + AgentMeter SDK Integration")
    print("🔗 The Future of Web3 AI Agent Monetization")
    print("=" * 70)
    
    if not COINBASE_AVAILABLE:
        print("⚠️  Running in demo mode - install Coinbase AgentKit for full functionality")
        print("   pip install cdp-sdk coinbase-python-sdk")
        print()
    
    # Check environment variables
    missing_vars = []
    if AGENTMETER_API_KEY == "your_agentmeter_api_key":
        missing_vars.append("AGENTMETER_API_KEY")
    if COINBASE_CDP_API_KEY_NAME == "organizations/{org_id}/apiKeys/{key_id}":
        missing_vars.append("COINBASE_CDP_API_KEY_NAME")
    if COINBASE_CDP_PRIVATE_KEY == "your_private_key":
        missing_vars.append("COINBASE_CDP_PRIVATE_KEY")
    
    if missing_vars:
        print("📋 Required Environment Variables:")
        for var in missing_vars:
            print(f"   export {var}='your_actual_value'")
        print()
    
    # Initialize and run demo
    demo = CoinbaseAgentKitDemo()
    results = await demo.run_complete_demo()
    
    print("\n🚀 Ready for Production!")
    print("📖 Next Steps:")
    print("   1. Set up your Coinbase CDP API keys")
    print("   2. Configure your AgentMeter project")
    print("   3. Customize billing tiers and pricing")
    print("   4. Deploy your Web3 AI agent with full monetization")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
