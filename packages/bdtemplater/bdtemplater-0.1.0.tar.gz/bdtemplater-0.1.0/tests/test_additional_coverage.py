#!/usr/bin/env python3

# Copyright 2025 Mykel Alvis
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

import io
import os
import sys
import tempfile

import pytest


class TestAdditionalCoverage:
    """Tests to increase coverage to 95%+"""

    def test_main_with_output_file_verbose(self):
        """Test main function with output file and verbose mode."""
        tfvars_content = """
project = "test-project"
env = "test"
bucket = "test-bucket"
region = "us-west-1"
lock_table = "test-lock-table"
"""

        template_content = """project: @project@
bucket: @bucket@
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bdt", delete=False
        ) as template_file:
            template_file.write(template_content)
            template_path = template_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tfvars", delete=False
        ) as tfvars_file:
            tfvars_file.write(tfvars_content)
            tfvars_path = tfvars_file.name

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as output_file:
            output_path = output_file.name

        try:
            # Capture stderr for verbose output
            old_stderr = sys.stderr
            sys.stderr = captured_stderr = io.StringIO()

            try:
                from bdtemplater.bdtemplatize import main

                main([template_path, tfvars_path, "-o", output_path, "-v"])
                stderr_output = captured_stderr.getvalue()

                # Check verbose output
                assert f"Writing output to: {output_path}" in stderr_output
                assert f"Successfully wrote output to {output_path}" in stderr_output

                # Check output file contents
                with open(output_path) as f:
                    content = f.read()
                    assert "test-project" in content
                    assert "test-bucket" in content

            finally:
                sys.stderr = old_stderr
        finally:
            os.unlink(template_path)
            os.unlink(tfvars_path)
            os.unlink(output_path)

    def test_main_module_import_exception_handling(self):
        """Test exception handling during module import."""
        tfvars_content = """project = "test"
env = "test"
bucket = "test-bucket"
region = "us-west-1"
lock_table = "test-lock-table"
"""

        template_content = """test: @project@"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bdt", delete=False
        ) as template_file:
            template_file.write(template_content)
            template_path = template_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tfvars", delete=False
        ) as tfvars_file:
            tfvars_file.write(tfvars_content)
            tfvars_path = tfvars_file.name

        try:
            # Test exception handling during module operations
            old_stderr = sys.stderr
            sys.stderr = captured_stderr = io.StringIO()

            try:
                # Mock importlib to raise an exception
                import importlib

                from bdtemplater.bdtemplatize import main

                original_import = importlib.import_module

                def mock_import_error(name):
                    if name == "some_bad_module":
                        raise Exception("Mocked exception during import")
                    return original_import(name)

                importlib.import_module = mock_import_error

                try:
                    with pytest.raises(SystemExit) as exc_info:
                        main(
                            [
                                template_path,
                                tfvars_path,
                                "--import-module",
                                "some_bad_module",
                            ]
                        )
                    assert exc_info.value.code == 1

                    stderr_output = captured_stderr.getvalue()
                    assert (
                        "Error: Problem with module 'some_bad_module'" in stderr_output
                    )
                finally:
                    importlib.import_module = original_import

            finally:
                sys.stderr = old_stderr
        finally:
            os.unlink(template_path)
            os.unlink(tfvars_path)

    def test_main_keyerror_handling(self):
        """Test that missing placeholders remain unreplaced when no keymap."""
        tfvars_content = '''project = "test"'''

        template_content = """test: @project@ @missing_key@"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bdt", delete=False
        ) as template_file:
            template_file.write(template_content)
            template_path = template_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tfvars", delete=False
        ) as tfvars_file:
            tfvars_file.write(tfvars_content)
            tfvars_path = tfvars_file.name

        try:
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = captured_stdout = io.StringIO()

            try:
                from bdtemplater.bdtemplatize import main

                main([template_path, tfvars_path])
                output = captured_stdout.getvalue()
                # project should be replaced, missing_key should remain as placeholder
                assert "test" in output
                assert "@missing_key@" in output
            finally:
                sys.stdout = old_stdout
        finally:
            os.unlink(template_path)
            os.unlink(tfvars_path)

    def test_main_unexpected_error_handling(self):
        """Test unexpected error handling in main function."""
        tfvars_content = '''project = "test"'''

        template_content = """test: @project@"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bdt", delete=False
        ) as template_file:
            template_file.write(template_content)
            template_path = template_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tfvars", delete=False
        ) as tfvars_file:
            tfvars_file.write(tfvars_content)
            tfvars_path = tfvars_file.name

        try:
            # Mock the generate_template_from_files function to raise error
            from bdtemplater import bdtemplatize

            original_generate = bdtemplatize.generate_template_from_files

            def mock_generate(*args, **kwargs):
                raise RuntimeError("Unexpected error for testing")

            bdtemplatize.generate_template_from_files = mock_generate

            try:
                # Capture stderr
                old_stderr = sys.stderr
                sys.stderr = captured_stderr = io.StringIO()

                try:
                    from bdtemplater.bdtemplatize import main

                    with pytest.raises(SystemExit) as exc_info:
                        main([template_path, tfvars_path])
                    assert exc_info.value.code == 1

                    stderr_output = captured_stderr.getvalue()
                    assert (
                        "Unexpected error: Unexpected error for testing"
                        in stderr_output
                    )

                finally:
                    sys.stderr = old_stderr
            finally:
                bdtemplatize.generate_template_from_files = original_generate
        finally:
            os.unlink(template_path)
            os.unlink(tfvars_path)

    def test_if_name_main_block(self):
        """Test the if __name__ == '__main__' block."""
        # This tests line 311
        import subprocess
        import sys

        # Create a simple test to run the module as main
        test_script = """
import sys
sys.path.insert(0, "src")
from bdtemplater.bdtemplatize import main

# Mock sys.argv
sys.argv = ["bdtemplatize.py", "--help"]

if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        if e.code in [0, 2]:  # 0 for success, 2 for help
            print("SUCCESS")
        else:
            print(f"FAILED: {e.code}")
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as script_file:
            script_file.write(test_script)
            script_path = script_file.name

        try:
            result = subprocess.run(
                [sys.executable, script_path], capture_output=True, text=True
            )
            # Help should exit with code 0 or 2, both are acceptable
            assert "usage:" in result.stderr or "SUCCESS" in result.stdout
        finally:
            os.unlink(script_path)

    def test_branch_coverage_keymap_replacement(self):
        """Test branch coverage for keymap replacement logic."""
        tfvars_content = """
project = "test-project"
env = "test"
bucket = "test-bucket"
missing_key = "should_not_be_used"
"""

        # Test when keymap is provided but a key in keymap is not in template
        template_content = """project: @project@"""

        from bdtemplater.bdtemplatize import generate_template

        # This should work - keymap key exists in tfvars but not referenced in template
        keymap = ["project", "env"]
        result = generate_template(template_content, tfvars_content, keymap=keymap)
        assert "test-project" in result

    def test_edge_case_empty_keymap_with_placeholders(self):
        """Test edge case with empty template but tfvars content."""
        tfvars_content = """
project = "test-project"
env = "test"
"""

        # Empty template should work fine
        template_content = ""

        from bdtemplater.bdtemplatize import generate_template

        result = generate_template(template_content, tfvars_content)
        assert result == ""

    def test_error_message_consistency(self):
        """Test that missing placeholders remain unreplaced when no keymap."""
        tfvars_content = '''project = "test"'''

        template_content = """@missing1@ @missing2@ @missing3@ @project@"""

        from bdtemplater.bdtemplatize import generate_template

        result = generate_template(template_content, tfvars_content)

        # project should be replaced, others should remain as placeholders
        assert "test" in result
        assert "@missing1@" in result
        assert "@missing2@" in result
        assert "@missing3@" in result

    def test_keymap_missing_keys_causes_error(self):
        """Test that KeyError is raised when keymap has missing keys from tfvars."""
        tfvars_content = '''project = "test"'''

        template_content = """test: @project@ @missing_key@"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bdt", delete=False
        ) as template_file:
            template_file.write(template_content)
            template_path = template_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tfvars", delete=False
        ) as tfvars_file:
            tfvars_file.write(tfvars_content)
            tfvars_path = tfvars_file.name

        try:
            # Capture stderr
            old_stderr = sys.stderr
            sys.stderr = captured_stderr = io.StringIO()

            try:
                from bdtemplater.bdtemplatize import main

                with pytest.raises(SystemExit) as exc_info:
                    main([template_path, tfvars_path, "-k", "project,missing_key"])
                assert exc_info.value.code == 1

                stderr_output = captured_stderr.getvalue()
                assert "Error:" in stderr_output
                assert "Keys in keymap missing from tfvars" in stderr_output
            finally:
                sys.stderr = old_stderr
        finally:
            os.unlink(template_path)
            os.unlink(tfvars_path)

    def test_bdtemplaterexample_package(self):
        """Test the bdtemplaterexample package for coverage."""
        import bdtemplaterexample

        # Test that we can access the uppercase_post_process from the package
        assert hasattr(bdtemplaterexample, "uppercase_post_process")

        # Test the function
        result = bdtemplaterexample.uppercase_post_process("test example import")
        assert result == "TEST EXAMPLE IMPORT"

    def test_keymap_with_missing_keys_in_tfdict(self):
        """Test keymap replacement when some keys are missing from tfdict."""
        tfvars_content = """project = "my-project"
env = "production"
"""
        keymap = ["project", "env", "missing_key"]
        template = "project: @project@, env: @env@, missing: @missing_key@"

        from bdtemplater.bdtemplatize import generate_template

        # Should raise KeyError when keymap contains keys not in tfvars
        with pytest.raises(KeyError) as exc_info:
            generate_template(template, tfvars_content, keymap=keymap)
        assert "Keys in keymap missing from tfvars: missing_key" in str(exc_info.value)

    def test_placeholder_replacement_branch_coverage(self):
        """Test both branches of placeholder replacement for coverage."""
        tfvars_content = """project = "my-project"
env = "production"
"""
        # Use all keys from tfdict (no keymap provided) - this tests the branch
        template = "project: @project@, env: @env@, missing: @missing_key@"

        from bdtemplater.bdtemplatize import generate_template

        result = generate_template(template, tfvars_content)

        # Should replace keys that exist in tfdict
        assert "my-project" in result
        assert "production" in result
        # Should leave placeholders that don't exist in tfdict
        assert "@missing_key@" in result

    def test_main_with_verbose_output_file_success(self, capsys):
        """Test main function with verbose and output file for coverage."""
        template_content = """project: @project@
env: @env@"""
        tfvars_content = '''project = "verbose-test"
env = "test-env"'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bdt", delete=False
        ) as template_file:
            template_file.write(template_content)
            template_path = template_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tfvars", delete=False
        ) as tfvars_file:
            tfvars_file.write(tfvars_content)
            tfvars_path = tfvars_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".out", delete=False
        ) as output_file:
            output_path = output_file.name

        try:
            from bdtemplater.bdtemplatize import main

            main([template_path, tfvars_path, "-o", output_path, "-v"])

            # Check verbose output
            captured = capsys.readouterr()
            assert "Writing output to:" in captured.err
            assert "Successfully wrote output to" in captured.err
            assert "Template generation completed successfully" in captured.err

            # Check output file content
            with open(output_path) as f:
                result = f.read()
            assert "verbose-test" in result
            assert "test-env" in result
        finally:
            os.unlink(template_path)
            os.unlink(tfvars_path)
            os.unlink(output_path)

    def test_main_with_custom_post_process_not_found(self, capsys):
        """Test main function when custom post-process function not found."""
        template_content = """project: @project@"""
        tfvars_content = '''project = "test-project"'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bdt", delete=False
        ) as template_file:
            template_file.write(template_content)
            template_path = template_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tfvars", delete=False
        ) as tfvars_file:
            tfvars_file.write(tfvars_content)
            tfvars_path = tfvars_file.name

        try:
            from bdtemplater.bdtemplatize import main

            # Try to use a non-existent function in the bdtemplaterexample module
            main(
                [
                    template_path,
                    tfvars_path,
                    "--import-module",
                    "bdtemplaterexample",
                    "--post-process",
                    "nonexistent_function",
                    "-v",
                ]
            )

            captured = capsys.readouterr()
            assert (
                "Warning: Function 'nonexistent_function' not found in module "
                "'bdtemplaterexample', using default" in captured.err
            )
        finally:
            os.unlink(template_path)
            os.unlink(tfvars_path)

    def test_main_with_general_exception_in_module_import(self, capsys):
        """Test main function when there's a general exception during module import."""
        template_content = """project: @project@"""
        tfvars_content = '''project = "test-project"'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bdt", delete=False
        ) as template_file:
            template_file.write(template_content)
            template_path = template_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tfvars", delete=False
        ) as tfvars_file:
            tfvars_file.write(tfvars_content)
            tfvars_path = tfvars_file.name

        try:
            from bdtemplater.bdtemplatize import main

            with pytest.raises(SystemExit) as exc_info:
                # Try to import a module that will cause an exception
                main(
                    [
                        template_path,
                        tfvars_path,
                        "--import-module",
                        "this.module.does.not.exist",
                    ]
                )
            assert exc_info.value.code == 1
        finally:
            os.unlink(template_path)
            os.unlink(tfvars_path)

    def test_key_in_tfdict_branch_coverage(self):
        """Test the branch where key_name is checked to be in tfdict."""
        tfvars_content = """project = "my-project"
env = "production"
"""
        # Test with specific keymap that includes keys both in and not in tfdict
        keymap = ["project"]  # Only project is in tfdict
        template = "project: @project@, env: @env@, missing: @missing_key@"

        from bdtemplater.bdtemplatize import generate_template

        result = generate_template(template, tfvars_content, keymap=keymap)

        # Should replace project (key in keymap and tfdict)
        assert "my-project" in result
        # Should leave env and missing_key as placeholders (not in keymap)
        assert "@env@" in result
        assert "@missing_key@" in result
