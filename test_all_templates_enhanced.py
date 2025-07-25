#!/usr/bin/env python3
"""
Enhanced Template Compliance Test Suite
Tests all 4 vision board templates for structure compliance and personalization integration
"""

import os
import re
import json
from typing import Dict, List, Tuple, Any

def test_all_enhanced_templates():
    """Test all enhanced vision board templates for compliance and personalization"""
    print("🧪 TESTING ALL ENHANCED VISION BOARD TEMPLATES")
    print("=" * 60)
    
    # Template file mappings
    templates = {
        1: "VisionPrompt1_Enhanced.txt",
        2: "VisionPrompt2_Enhanced.txt", 
        3: "VisionPrompt3_Enhanced.txt",
        4: "VisionPrompt4_Enhanced.txt"
    }
    
    template_names = {
        1: "Disciplined Achiever",
        2: "Creative Visionary", 
        3: "Bold Success",
        4: "Mindful Balance"
    }
    
    overall_results = {
        "total_templates": len(templates),
        "templates_passed": 0,
        "total_checks": 0,
        "checks_passed": 0,
        "detailed_results": {}
    }
    
    for template_num, template_file in templates.items():
        print(f"\n🎯 TESTING TEMPLATE {template_num}: {template_names[template_num]}")
        print(f"📁 File: {template_file}")
        print("-" * 50)
        
        # Test this template
        results = test_single_template(template_num, template_file, template_names[template_num])
        overall_results["detailed_results"][template_num] = results
        overall_results["total_checks"] += results["total_checks"]
        overall_results["checks_passed"] += results["checks_passed"]
        
        if results["compliance_score"] >= 8:  # 80% threshold
            overall_results["templates_passed"] += 1
            print(f"✅ Template {template_num} PASSED ({results['checks_passed']}/{results['total_checks']} checks)")
        else:
            print(f"❌ Template {template_num} FAILED ({results['checks_passed']}/{results['total_checks']} checks)")
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 ENHANCED TEMPLATES TEST SUMMARY")
    print("=" * 60)
    
    success_rate = (overall_results["checks_passed"] / overall_results["total_checks"]) * 100
    template_success_rate = (overall_results["templates_passed"] / overall_results["total_templates"]) * 100
    
    print(f"🏆 Overall Success Rate: {success_rate:.1f}% ({overall_results['checks_passed']}/{overall_results['total_checks']} checks)")
    print(f"📈 Templates Passed: {template_success_rate:.1f}% ({overall_results['templates_passed']}/{overall_results['total_templates']} templates)")
    
    for template_num, results in overall_results["detailed_results"].items():
        template_name = template_names[template_num]
        score = results["compliance_score"]
        status = "✅ PASS" if score >= 8 else "❌ FAIL"
        print(f"   • Template {template_num} ({template_name}): {score}/10 {status}")
    
    if success_rate >= 90:
        print("\n🎉 EXCELLENT! All enhanced templates meet compliance standards!")
    elif success_rate >= 80:
        print("\n✅ GOOD! Enhanced templates show strong compliance!")
    else:
        print("\n⚠️ Some templates need additional enhancement")
    
    return overall_results

def test_single_template(template_num: int, template_file: str, template_name: str) -> Dict[str, Any]:
    """Test a single template for compliance and personalization"""
    
    results = {
        "template_number": template_num,
        "template_name": template_name,
        "file_name": template_file,
        "total_checks": 10,
        "checks_passed": 0,
        "compliance_score": 0,
        "detailed_checks": {}
    }
    
    try:
        # Read template file
        if not os.path.exists(template_file):
            print(f"❌ Template file not found: {template_file}")
            return results
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📖 Template loaded: {len(content)} characters")
        
        # Test 1: Personalization placeholders
        check_1 = test_personalization_placeholders(content)
        results["detailed_checks"]["personalization_placeholders"] = check_1
        if check_1["passed"]:
            results["checks_passed"] += 1
        print(f"   1. Personalization Placeholders: {'✅' if check_1['passed'] else '❌'} ({check_1['found']}/{check_1['required']})")
        
        # Test 2: Template structure requirements
        check_2 = test_template_structure(content)
        results["detailed_checks"]["template_structure"] = check_2
        if check_2["passed"]:
            results["checks_passed"] += 1
        print(f"   2. Template Structure: {'✅' if check_2['passed'] else '❌'} ({check_2['found']}/{check_2['required']})")
        
        # Test 3: Sectional layout specifications
        check_3 = test_sectional_layout(content)
        results["detailed_checks"]["sectional_layout"] = check_3
        if check_3["passed"]:
            results["checks_passed"] += 1
        print(f"   3. Sectional Layout: {'✅' if check_3['passed'] else '❌'} ({check_3['found']}/{check_3['required']})")
        
        # Test 4: User data integration
        check_4 = test_user_data_integration(content)
        results["detailed_checks"]["user_data_integration"] = check_4
        if check_4["passed"]:
            results["checks_passed"] += 1
        print(f"   4. User Data Integration: {'✅' if check_4['passed'] else '❌'} ({check_4['found']}/{check_4['required']})")
        
        # Test 5: Visual style specifications
        check_5 = test_visual_style(content)
        results["detailed_checks"]["visual_style"] = check_5
        if check_5["passed"]:
            results["checks_passed"] += 1
        print(f"   5. Visual Style: {'✅' if check_5['passed'] else '❌'} ({check_5['found']}/{check_5['required']})")
        
        # Test 6: Technical requirements
        check_6 = test_technical_requirements(content)
        results["detailed_checks"]["technical_requirements"] = check_6
        if check_6["passed"]:
            results["checks_passed"] += 1
        print(f"   6. Technical Requirements: {'✅' if check_6['passed'] else '❌'} ({check_6['found']}/{check_6['required']})")
        
        # Test 7: Template adherence mentions
        check_7 = test_template_adherence(content, template_num)
        results["detailed_checks"]["template_adherence"] = check_7
        if check_7["passed"]:
            results["checks_passed"] += 1
        print(f"   7. Template Adherence: {'✅' if check_7['passed'] else '❌'} ({check_7['found']}/{check_7['required']})")
        
        # Test 8: Affirmation text overlays
        check_8 = test_affirmation_overlays(content)
        results["detailed_checks"]["affirmation_overlays"] = check_8
        if check_8["passed"]:
            results["checks_passed"] += 1
        print(f"   8. Affirmation Overlays: {'✅' if check_8['passed'] else '❌'} ({check_8['found']}/{check_8['required']})")
        
        # Test 9: Complete layout requirements
        check_9 = test_complete_layout(content)
        results["detailed_checks"]["complete_layout"] = check_9
        if check_9["passed"]:
            results["checks_passed"] += 1
        print(f"   9. Complete Layout: {'✅' if check_9['passed'] else '❌'} ({check_9['found']}/{check_9['required']})")
        
        # Test 10: Energy and aesthetic capture
        check_10 = test_energy_capture(content)
        results["detailed_checks"]["energy_capture"] = check_10
        if check_10["passed"]:
            results["checks_passed"] += 1
        print(f"  10. Energy Capture: {'✅' if check_10['passed'] else '❌'} ({check_10['found']}/{check_10['required']})")
        
        results["compliance_score"] = results["checks_passed"]
        
    except Exception as e:
        print(f"❌ Error testing template {template_num}: {e}")
    
    return results

def test_personalization_placeholders(content: str) -> Dict[str, Any]:
    """Test for personalization placeholder presence"""
    required_placeholders = [
        "USER_NAME", "USER_AGE", "USER_PERSONALITY", "USER_VALUES", "USER_GOALS",
        "USER_AESTHETIC", "USER_ENERGY", "EMOTIONAL_TONE", "VISUAL_ELEMENTS",
        "LIFESTYLE_ELEMENTS", "CORE_VALUES", "LIFE_ASPIRATIONS", "PERSONALITY_TRAITS"
    ]
    
    found_placeholders = []
    for placeholder in required_placeholders:
        if f"{{{placeholder}}}" in content:
            found_placeholders.append(placeholder)
    
    return {
        "passed": len(found_placeholders) >= 10,  # At least 10 of 13 placeholders
        "required": 10,
        "found": len(found_placeholders),
        "missing": [p for p in required_placeholders if p not in found_placeholders],
        "details": f"Found {len(found_placeholders)} personalization placeholders"
    }

def test_template_structure(content: str) -> Dict[str, Any]:
    """Test for template structure requirements"""
    structure_indicators = [
        "EXACT TEMPLATE STRUCTURE",
        "SECTIONAL LAYOUT",
        "Follow.*Template.*layout",
        "template adherence",
        "structure exactly"
    ]
    
    found_indicators = []
    for indicator in structure_indicators:
        if re.search(indicator, content, re.IGNORECASE):
            found_indicators.append(indicator)
    
    return {
        "passed": len(found_indicators) >= 2,
        "required": 2,
        "found": len(found_indicators),
        "details": f"Found {len(found_indicators)} structure requirements"
    }

def test_sectional_layout(content: str) -> Dict[str, Any]:
    """Test for sectional layout specifications"""
    section_indicators = [
        "UPPER LEFT", "UPPER CENTER", "UPPER RIGHT",
        "MIDDLE LEFT", "CENTER FOCUS", "MIDDLE RIGHT", 
        "LOWER", "rectangular sections", "asymmetrical"
    ]
    
    found_sections = []
    for section in section_indicators:
        if re.search(section, content, re.IGNORECASE):
            found_sections.append(section)
    
    return {
        "passed": len(found_sections) >= 5,
        "required": 5,
        "found": len(found_sections),
        "details": f"Found {len(found_sections)} sectional layout elements"
    }

def test_user_data_integration(content: str) -> Dict[str, Any]:
    """Test for user data integration requirements"""
    integration_phrases = [
        "USER DATA INTEGRATION",
        "user's authentic",
        "user's unique",
        "reflects.*user's",
        "user's journey",
        "authentically reflect"
    ]
    
    found_integration = []
    for phrase in integration_phrases:
        if re.search(phrase, content, re.IGNORECASE):
            found_integration.append(phrase)
    
    return {
        "passed": len(found_integration) >= 3,
        "required": 3,
        "found": len(found_integration),
        "details": f"Found {len(found_integration)} user integration elements"
    }

def test_visual_style(content: str) -> Dict[str, Any]:
    """Test for visual style specifications"""
    style_elements = [
        "Color Palette", "Mood", "Lighting", "Texture",
        "Typography", "aesthetic", "Background", "Visual"
    ]
    
    found_styles = []
    for element in style_elements:
        if re.search(element, content, re.IGNORECASE):
            found_styles.append(element)
    
    return {
        "passed": len(found_styles) >= 6,
        "required": 6,
        "found": len(found_styles),
        "details": f"Found {len(found_styles)} visual style elements"
    }

def test_technical_requirements(content: str) -> Dict[str, Any]:
    """Test for technical requirements"""
    tech_requirements = [
        "1024x1024", "margin", "FULLY visible", "no cropping",
        "Canvas", "completion", "perfectly readable", "edges"
    ]
    
    found_tech = []
    for req in tech_requirements:
        if re.search(req, content, re.IGNORECASE):
            found_tech.append(req)
    
    return {
        "passed": len(found_tech) >= 5,
        "required": 5,
        "found": len(found_tech),
        "details": f"Found {len(found_tech)} technical requirements"
    }

def test_template_adherence(content: str, template_num: int) -> Dict[str, Any]:
    """Test for template adherence mentions"""
    adherence_phrases = [
        f"VisionTemplate{template_num}",
        "template adherence",
        "follow.*template",
        "structure exactly",
        "layout precisely"
    ]
    
    found_adherence = []
    for phrase in adherence_phrases:
        if re.search(phrase, content, re.IGNORECASE):
            found_adherence.append(phrase)
    
    return {
        "passed": len(found_adherence) >= 2,
        "required": 2,
        "found": len(found_adherence),
        "details": f"Found {len(found_adherence)} template adherence mentions"
    }

def test_affirmation_overlays(content: str) -> Dict[str, Any]:
    """Test for affirmation text overlay specifications"""
    affirmation_indicators = [
        "AFFIRMATION.*TEXT.*OVERLAYS",
        "TEXT.*OVERLAYS",
        "affirmations",
        "phrases",
        "typography"
    ]
    
    found_affirmations = []
    for indicator in affirmation_indicators:
        if re.search(indicator, content, re.IGNORECASE):
            found_affirmations.append(indicator)
    
    return {
        "passed": len(found_affirmations) >= 2,
        "required": 2,
        "found": len(found_affirmations),
        "details": f"Found {len(found_affirmations)} affirmation elements"
    }

def test_complete_layout(content: str) -> Dict[str, Any]:
    """Test for complete layout requirements"""
    layout_requirements = [
        "COMPLETE.*vision board",
        "NO.*cut off",
        "FULLY VISIBLE",
        "no cropping",
        "every element",
        "complete.*viewable"
    ]
    
    found_layout = []
    for req in layout_requirements:
        if re.search(req, content, re.IGNORECASE):
            found_layout.append(req)
    
    return {
        "passed": len(found_layout) >= 3,
        "required": 3,
        "found": len(found_layout),
        "details": f"Found {len(found_layout)} complete layout requirements"
    }

def test_energy_capture(content: str) -> Dict[str, Any]:
    """Test for energy and aesthetic capture specifications"""
    energy_elements = [
        "ENERGY TO CAPTURE",
        "represents.*individual",
        "aesthetic should feel",
        "FINAL CHECK",
        "authentic.*representing"
    ]
    
    found_energy = []
    for element in energy_elements:
        if re.search(element, content, re.IGNORECASE):
            found_energy.append(element)
    
    return {
        "passed": len(found_energy) >= 2,
        "required": 2,
        "found": len(found_energy),
        "details": f"Found {len(found_energy)} energy capture elements"
    }

if __name__ == "__main__":
    test_all_enhanced_templates()
