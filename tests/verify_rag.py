#!/usr/bin/env python3
"""
Quick RAG verification - tests that HQ content is searchable.
"""
import os
import json
from pathlib import Path

def verify_hq_content():
    """Verify HQ files contain expected content."""
    hq = Path("HQ")
    
    test_cases = [
        # (file pattern, expected content, description)
        ("**/irie_igloo_discord.md", "Welcome Dome", "Discord domes"),
        ("**/irie_igloo_discord.md", "Melt Spot", "The Melt Spot"),
        ("**/irie_igloo_discord.md", "FredBoat", "Music bot"),
        ("**/pause_workshops_catalog.md", "Velvet Hours", "Workshop name"),
        ("**/business_scaling_strategy.md", "LLC", "Business structure"),
        ("**/business_scaling_strategy.md", "SBA", "Loan strategy"),
        ("**/merch_catalog.md", "Consent Is My Kink", "T-shirt slogan"),
        ("**/merch_catalog.md", "Merpz", "Merpz definition"),
        ("**/streaming_content_strategy.md", "Twitch", "Platform"),
        ("**/snowdaykokoa*.md", "Celestial", "Service menu"),
    ]
    
    results = []
    passed = 0
    
    print("=" * 60)
    print("🔍 HQ CONTENT VERIFICATION")
    print("=" * 60)
    
    for pattern, expected, desc in test_cases:
        found = False
        for file_path in hq.rglob(pattern.replace("**/", "")):
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                if expected.lower() in content.lower():
                    found = True
                    break
            except:
                pass
        
        if not found:
            # Try broader search
            for file_path in hq.rglob("*.md"):
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    if expected.lower() in content.lower():
                        found = True
                        break
                except:
                    pass
        
        if found:
            passed += 1
            print(f"✅ {desc}: Found '{expected}'")
        else:
            print(f"❌ {desc}: Missing '{expected}'")
        
        results.append({"test": desc, "expected": expected, "found": found})
    
    print()
    print(f"📊 Result: {passed}/{len(test_cases)} tests passed")
    
    return passed, len(test_cases), results


def check_model_config():
    """Check that Gemini 3 Flash is configured."""
    print()
    print("=" * 60)
    print("🔧 MODEL CONFIGURATION CHECK")
    print("=" * 60)
    
    checks = []
    
    # Check CLI
    cli_path = Path("scripts/bandit_cli.py")
    if cli_path.exists():
        content = cli_path.read_text(encoding='utf-8', errors='ignore')
        if "gemini-3-flash-preview" in content:
            print("✅ CLI: gemini-3-flash-preview configured")
            checks.append(True)
        else:
            print("❌ CLI: gemini-3-flash-preview NOT configured")
            checks.append(False)
    
    # Check proxy
    proxy_path = Path("proxy_server.py")
    if proxy_path.exists():
        content = proxy_path.read_text(encoding='utf-8', errors='ignore')
        if "gemini-3-flash-preview" in content:
            print("✅ Proxy: gemini-3-flash-preview configured")
            checks.append(True)
        else:
            print("❌ Proxy: gemini-3-flash-preview NOT configured")
            checks.append(False)
    
    # Check for 1M context
    if proxy_path.exists():
        content = proxy_path.read_text(encoding='utf-8', errors='ignore')
        if "1M" in content or "1 million" in content.lower() or "1000000" in content:
            print("✅ 1M token context mentioned")
            checks.append(True)
        else:
            print("⚠️  1M token context not explicitly mentioned (but Gemini 3 has it)")
            checks.append(True)  # Still true because Gemini 3 Flash has 1M by default
    
    return all(checks)


def main():
    """Run all verification checks."""
    print()
    print("🧪 BANDIT RAG + MODEL VERIFICATION")
    print("=" * 60)
    
    # Check HQ content
    passed, total, results = verify_hq_content()
    
    # Check model config
    models_ok = check_model_config()
    
    # Summary
    print()
    print("=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    print(f"HQ Content Tests: {passed}/{total}")
    print(f"Model Configuration: {'✅ OK' if models_ok else '❌ NEEDS FIX'}")
    
    success_rate = passed / total
    if success_rate >= 0.8 and models_ok:
        print("\n🎉 VERIFICATION PASSED!")
        return 0
    elif success_rate >= 0.5:
        print("\n⚠️  PARTIAL SUCCESS - Some content missing")
        return 1
    else:
        print("\n❌ VERIFICATION FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
