#!/usr/bin/env python
"""
Simple verification script to test schema extensions integration.

This script verifies that:
1. SchemaExtensions can be imported and initialized
2. VerbaManager includes schema_extensions
3. Collection names are correctly defined
4. All required methods are available
"""

import sys
from goldenverba.components.schema_extensions import SchemaExtensions
from goldenverba.verba_manager import VerbaManager


def verify_schema_extensions():
    """Verify SchemaExtensions class."""
    print("=" * 60)
    print("Verifying SchemaExtensions class...")
    print("=" * 60)
    
    try:
        se = SchemaExtensions()
        
        # Check collection names
        assert se.worklog_collection_name == "VERBA_WorkLog", "WorkLog collection name mismatch"
        assert se.skill_collection_name == "VERBA_Skill", "Skill collection name mismatch"
        assert se.resume_record_collection_name == "VERBA_ResumeRecord", "ResumeRecord collection name mismatch"
        print("✓ Collection names are correct")
        
        # Check methods exist
        assert hasattr(se, "verify_worklog_collection"), "Missing verify_worklog_collection method"
        assert hasattr(se, "verify_skill_collection"), "Missing verify_skill_collection method"
        assert hasattr(se, "verify_resume_record_collection"), "Missing verify_resume_record_collection method"
        assert hasattr(se, "initialize_all_collections"), "Missing initialize_all_collections method"
        assert hasattr(se, "delete_all_collections"), "Missing delete_all_collections method"
        print("✓ All required methods are present")
        
        print("\n✓ SchemaExtensions verification passed!\n")
        return True
        
    except Exception as e:
        print(f"\n✗ SchemaExtensions verification failed: {str(e)}\n")
        return False


def verify_verba_manager_integration():
    """Verify VerbaManager integration."""
    print("=" * 60)
    print("Verifying VerbaManager integration...")
    print("=" * 60)
    
    try:
        vm = VerbaManager()
        
        # Check schema_extensions attribute exists
        assert hasattr(vm, "schema_extensions"), "VerbaManager missing schema_extensions attribute"
        print("✓ VerbaManager has schema_extensions attribute")
        
        # Check it's the right type
        assert isinstance(vm.schema_extensions, SchemaExtensions), "schema_extensions is not a SchemaExtensions instance"
        print("✓ schema_extensions is correct type")
        
        # Check collection names are accessible
        assert vm.schema_extensions.worklog_collection_name == "VERBA_WorkLog"
        assert vm.schema_extensions.skill_collection_name == "VERBA_Skill"
        assert vm.schema_extensions.resume_record_collection_name == "VERBA_ResumeRecord"
        print("✓ Collection names accessible through VerbaManager")
        
        print("\n✓ VerbaManager integration verification passed!\n")
        return True
        
    except Exception as e:
        print(f"\n✗ VerbaManager integration verification failed: {str(e)}\n")
        return False


def main():
    """Run all verification tests."""
    print("\n" + "=" * 60)
    print("SCHEMA EXTENSIONS VERIFICATION")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run verifications
    results.append(verify_schema_extensions())
    results.append(verify_verba_manager_integration())
    
    # Summary
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All verifications passed successfully!")
        print("\nThe schema extensions are properly implemented and integrated.")
        print("\nNext steps:")
        print("  1. Start Weaviate (Local/Docker/Cloud)")
        print("  2. Connect through Verba")
        print("  3. Collections will be automatically created")
        return 0
    else:
        print("\n✗ Some verifications failed!")
        print("\nPlease review the errors above and fix the issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
