#!/usr/bin/env python3
"""
Test suite for commands List vs Dict compatibility fix.
Author: Dr. Alex Rivera
Date: July 4, 2025
"""

import sys
import warnings
from pathlib import Path

# Add the TCP module to the path
tcp_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(tcp_path))

from tcp.core.descriptors import (
    CapabilityDescriptor, 
    CommandDescriptor, 
    ParameterDescriptor,
    ParameterType,
    FormatDescriptor,
    FormatType
)


class TestCommandsCompatibility:
    """Test backward compatibility for commands field."""
    
    def test_list_format_unchanged(self):
        """Test that List format continues to work as before."""
        print("\n[TEST] List format (current behavior)...")
        
        # Create commands as a list
        commands = [
            CommandDescriptor(
                name="search",
                description="Search for patterns",
                parameters=[
                    ParameterDescriptor(
                        name="pattern",
                        type=ParameterType.STRING,
                        required=True,
                        description="Pattern to search"
                    )
                ]
            ),
            CommandDescriptor(
                name="count",
                description="Count occurrences",
                parameters=[]
            )
        ]
        
        # Create descriptor with list
        descriptor = CapabilityDescriptor(
            name="grep",
            version="1.0.0",
            commands=commands
        )
        
        # Verify commands is still a list
        assert isinstance(descriptor.commands, list), "Commands should remain a list"
        assert len(descriptor.commands) == 2, "Should have 2 commands"
        assert descriptor.commands[0].name == "search", "First command should be 'search'"
        assert descriptor.commands[1].name == "count", "Second command should be 'count'"
        
        # Test get_command
        search_cmd = descriptor.get_command("search")
        assert search_cmd is not None, "Should find 'search' command"
        assert search_cmd.name == "search", "Found command should be 'search'"
        
        # Test add_command
        new_cmd = CommandDescriptor(name="list", description="List matches")
        descriptor.add_command(new_cmd)
        assert len(descriptor.commands) == 3, "Should have 3 commands after adding"
        
        print("✓ List format test passed")
        return True
    
    def test_dict_format_with_warning(self):
        """Test that Dict format works but emits deprecation warning."""
        print("\n[TEST] Dict format (deprecated behavior)...")
        
        # Create commands as a dict
        commands_dict = {
            "search": CommandDescriptor(
                name="search",
                description="Search for patterns",
                parameters=[
                    ParameterDescriptor(
                        name="pattern",
                        type=ParameterType.STRING,
                        required=True
                    )
                ]
            ),
            "count": CommandDescriptor(
                name="count",
                description="Count occurrences"
            )
        }
        
        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Create descriptor with dict
            descriptor = CapabilityDescriptor(
                name="grep",
                version="1.0.0",
                commands=commands_dict
            )
            
            # Verify warning was issued
            assert len(w) == 1, "Should emit exactly one warning"
            assert issubclass(w[0].category, DeprecationWarning), "Should be DeprecationWarning"
            assert "Dict format for commands is deprecated" in str(w[0].message)
            print(f"✓ Deprecation warning emitted: {w[0].message}")
        
        # Verify commands was converted to list
        assert isinstance(descriptor.commands, list), "Commands should be converted to list"
        assert len(descriptor.commands) == 2, "Should have 2 commands"
        
        # Commands should be preserved (order may vary)
        command_names = {cmd.name for cmd in descriptor.commands}
        assert command_names == {"search", "count"}, "All commands should be preserved"
        
        # Test get_command still works
        search_cmd = descriptor.get_command("search")
        assert search_cmd is not None, "Should find 'search' command"
        assert search_cmd.description == "Search for patterns"
        
        print("✓ Dict format test passed with deprecation warning")
        return True
    
    def test_binary_generator_compatibility(self):
        """Test that binary generator works with both formats."""
        print("\n[TEST] Binary generator compatibility...")
        
        from tcp.generators.binary import BinaryGenerator
        
        generator = BinaryGenerator()
        
        # Test with List format
        list_descriptor = CapabilityDescriptor(
            name="test_list",
            version="1.0.0",
            commands=[
                CommandDescriptor(name="cmd1"),
                CommandDescriptor(name="cmd2")
            ]
        )
        
        try:
            binary_list = generator.generate(list_descriptor)
            assert len(binary_list) == 20, "Binary descriptor should be 20 bytes"
            print("✓ Binary generator works with List format")
        except Exception as e:
            print(f"✗ Binary generator failed with List: {e}")
            return False
        
        # Test with Dict format (should work after conversion)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Suppress deprecation warning for this test
            
            dict_descriptor = CapabilityDescriptor(
                name="test_dict",
                version="1.0.0",
                commands={
                    "cmd1": CommandDescriptor(name="cmd1"),
                    "cmd2": CommandDescriptor(name="cmd2")
                }
            )
        
        try:
            binary_dict = generator.generate(dict_descriptor)
            assert len(binary_dict) == 20, "Binary descriptor should be 20 bytes"
            print("✓ Binary generator works with Dict format (after conversion)")
        except Exception as e:
            print(f"✗ Binary generator failed with Dict: {e}")
            return False
        
        return True
    
    def test_iteration_safety(self):
        """Test that iteration over commands works correctly."""
        print("\n[TEST] Iteration safety...")
        
        # Test List format iteration
        list_descriptor = CapabilityDescriptor(
            name="test",
            version="1.0.0",
            commands=[
                CommandDescriptor(name=f"cmd{i}") for i in range(3)
            ]
        )
        
        list_names = [cmd.name for cmd in list_descriptor.commands]
        assert list_names == ["cmd0", "cmd1", "cmd2"], "List iteration should work"
        print("✓ List iteration works correctly")
        
        # Test Dict format iteration (after conversion)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            dict_descriptor = CapabilityDescriptor(
                name="test",
                version="1.0.0",
                commands={
                    f"cmd{i}": CommandDescriptor(name=f"cmd{i}") for i in range(3)
                }
            )
        
        dict_names = [cmd.name for cmd in dict_descriptor.commands]
        assert len(dict_names) == 3, "Should have all 3 commands"
        assert all(name.startswith("cmd") for name in dict_names), "All commands preserved"
        print("✓ Dict iteration works correctly after conversion")
        
        return True
    
    def test_performance_metrics(self):
        """Test performance of both formats."""
        print("\n[TEST] Performance comparison...")
        
        import time
        
        # Create large command sets
        num_commands = 1000
        
        # Test List format performance
        list_commands = [
            CommandDescriptor(name=f"cmd_{i}", description=f"Command {i}")
            for i in range(num_commands)
        ]
        
        start = time.perf_counter()
        list_descriptor = CapabilityDescriptor(
            name="perf_test",
            version="1.0.0",
            commands=list_commands
        )
        list_time = time.perf_counter() - start
        
        # Test Dict format performance
        dict_commands = {
            f"cmd_{i}": CommandDescriptor(name=f"cmd_{i}", description=f"Command {i}")
            for i in range(num_commands)
        }
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            start = time.perf_counter()
            dict_descriptor = CapabilityDescriptor(
                name="perf_test",
                version="1.0.0",
                commands=dict_commands
            )
            dict_time = time.perf_counter() - start
        
        print(f"✓ List format: {list_time*1000:.2f}ms for {num_commands} commands")
        print(f"✓ Dict format: {dict_time*1000:.2f}ms for {num_commands} commands (includes conversion)")
        print(f"✓ Overhead: {(dict_time - list_time)*1000:.2f}ms ({(dict_time/list_time - 1)*100:.1f}%)")
        
        # Verify no significant performance regression 
        # For small absolute times (<1ms), percentage can be misleading
        # Allow 2x overhead or 1ms absolute difference, whichever is more lenient
        overhead_ok = (dict_time < list_time * 2.0) or (dict_time - list_time < 0.001)
        assert overhead_ok, f"Dict conversion overhead too high: {dict_time-list_time:.3f}s"
        
        return True
    
    def run_all_tests(self):
        """Run all compatibility tests."""
        print("=" * 60)
        print("Commands List vs Dict Compatibility Test Suite")
        print("Dr. Alex Rivera - TCP Research Consortium")
        print("=" * 60)
        
        tests = [
            self.test_list_format_unchanged,
            self.test_dict_format_with_warning,
            self.test_binary_generator_compatibility,
            self.test_iteration_safety,
            self.test_performance_metrics
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"✗ {test.__name__} failed with exception: {e}")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"Test Results: {passed} passed, {failed} failed")
        print("=" * 60)
        
        return failed == 0


if __name__ == "__main__":
    tester = TestCommandsCompatibility()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All tests passed! The fix is ready for production.")
        print("\nNext steps:")
        print("1. Run full TCP test suite")
        print("2. Notify Yuki for performance benchmarking")
        print("3. Create migration documentation")
        print("4. Schedule code review")
    else:
        print("\n❌ Some tests failed. Please review the implementation.")
        sys.exit(1)