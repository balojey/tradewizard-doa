#!/usr/bin/env python3
"""Quick verification script for polling agent fix."""

from nodes.dynamic_agent_selection import select_agents_by_market_type

def verify_fix():
    """Verify that polling agent is included in policy and geopolitical markets."""
    
    print("Testing polling agent inclusion fix...")
    print("=" * 60)
    
    # Test policy market
    policy_agents = select_agents_by_market_type('policy')
    print(f"\nPolicy market agents: {policy_agents}")
    policy_has_polling = 'polling_intelligence' in policy_agents
    print(f"✓ Policy includes polling_intelligence: {policy_has_polling}")
    
    # Test geopolitical market
    geo_agents = select_agents_by_market_type('geopolitical')
    print(f"\nGeopolitical market agents: {geo_agents}")
    geo_has_polling = 'polling_intelligence' in geo_agents
    print(f"✓ Geopolitical includes polling_intelligence: {geo_has_polling}")
    
    # Test that other agents are still included (preservation)
    print("\n" + "=" * 60)
    print("Preservation checks:")
    print(f"✓ Policy includes breaking_news: {'breaking_news' in policy_agents}")
    print(f"✓ Policy includes event_impact: {'event_impact' in policy_agents}")
    print(f"✓ Policy includes media_sentiment: {'media_sentiment' in policy_agents}")
    print(f"✓ Policy includes catalyst: {'catalyst' in policy_agents}")
    
    print(f"\n✓ Geopolitical includes breaking_news: {'breaking_news' in geo_agents}")
    print(f"✓ Geopolitical includes event_impact: {'event_impact' in geo_agents}")
    print(f"✓ Geopolitical includes media_sentiment: {'media_sentiment' in geo_agents}")
    print(f"✓ Geopolitical includes catalyst: {'catalyst' in geo_agents}")
    
    # Overall result
    print("\n" + "=" * 60)
    if policy_has_polling and geo_has_polling:
        print("✅ FIX VERIFIED: Polling agent is now included in both market types!")
        return True
    else:
        print("❌ FIX FAILED: Polling agent is missing!")
        return False

if __name__ == "__main__":
    success = verify_fix()
    exit(0 if success else 1)
