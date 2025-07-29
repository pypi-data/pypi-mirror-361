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

from bdtemplaterpostprocessor.default_post_process import default_post_process


def generate_template_from_files(
    template_file, replacements_file, keymap=None, post_process=default_post_process
):
    """
    Generate a template by replacing placeholders in the template file with
    values from the replacements file.

    :param template_file: Path to the template file containing placeholders.
    :param replacements_file: Path to the file containing replacement values.
    :param keymap: Optional list of keys to look for in the replacements file.
    :param post_process: Optional function to process the final output.
    :return: Processed output string with placeholders replaced.
    """
    try:
        # Read template file
        with open(template_file) as f:
            template = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Template file not found: {template_file}")
    except OSError as e:
        raise OSError(f"Error reading {template_file}: {e}")

    try:
        with open(replacements_file) as f:
            replacements = f.read()

    except FileNotFoundError:
        raise FileNotFoundError(f"Template file not found: {replacements_file}")
    except OSError as e:
        raise OSError(f"Error reading {replacements_file}: {e}")
    return generate_template(template, replacements, keymap, post_process)


def generate_template(
    template, replacements, keymap=None, post_process=default_post_process
):
    # Parse tfvars file
    tfdict = {}
    for line in replacements.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            try:
                key, value = line.split("=", 1)
                # Ensure special characters are preserved in values
                tfdict[key.strip()] = value.strip().strip('"')
            except ValueError:
                print(f"Warning: Skipping malformed line: {line}")
                continue

    # If tfdict is empty after parsing, log a warning to stderr
    if not tfdict:
        import sys

        print("Warning: Replacements content is invalid or empty.", file=sys.stderr)

    # Use all keys from tfdict if no keymap is provided
    if keymap is None:
        keymap = list(tfdict.keys())
    else:
        missing_keymap_keys = [key for key in keymap if key not in tfdict]
        if missing_keymap_keys:
            raise KeyError(
                f"Keys in keymap missing from tfvars: {', '.join(missing_keymap_keys)}"
            )

    # Initialize output with the template content
    output = template

    # Replace placeholders with values from tfvars
    for key_name in keymap:
        placeholder = f"@{key_name}@"
        if key_name in tfdict:
            output = output.replace(placeholder, tfdict[key_name])

    return post_process(output)


# FILL IN ANOTHER TEMPLATE
# WRITE ANOTHER TEMPLATE AS A SRESOURCE TO S3


def main(argv=None):
    """Main command-line interface for bdtemplater."""
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser(
        description=(
            "Generate templates by replacing placeholders with values from tfvars files"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                         # Use defaults:
                                                   # TEMPLATIZE.bdt and
                                                   # terraform.tfvars
  %(prog)s template.bdt myvars.tfvars              # Specify both files
  %(prog)s -t template.bdt -r vars.tfvars          # Use short options
  %(prog)s --template tpl.bdt --replacements t.txt # Long options
  %(prog)s -k project,env,bucket                   # Use custom keymap
  %(prog)s --keymap project,env,bucket             # Use custom keymap long option
  %(prog)s -o output.tf                            # Write output to file
  %(prog)s --output output.tf                      # Write output to file
  %(prog)s --post-process post.processor.func      # Run a post-processing function
  %(prog)s --import-module mymodule                # Import external module
                                                   # for post-processing
        """,
    )

    parser.add_argument(
        "template_file",
        nargs="?",
        default="TEMPLATIZE.bdt",
        help="Template file containing placeholders (default: TEMPLATIZE.bdt)",
    )

    parser.add_argument(
        "replacements_file",
        nargs="?",
        default="terraform.tfvars",
        help="File containing replacement values (default: terraform.tfvars)",
    )

    parser.add_argument(
        "-t",
        "--template",
        dest="template_file_alt",
        help="Template file (alternative to positional argument)",
    )

    parser.add_argument(
        "-r",
        "--replacements",
        dest="replacements_file_alt",
        help="Replacements file (alternative to positional argument)",
    )

    parser.add_argument(
        "-k",
        "--keymap",
        help="Comma-separated list of keys to look for in replacements file",
    )

    parser.add_argument(
        "--import-module",
        dest="import_module",
        help="Import external module for custom post-processing functions",
    )

    parser.add_argument(
        "--post-process",
        dest="post_process_func",
        default="default_post_process",
        help="Post-processing function name (default: default_post_process)",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        help="Output file path (default: print to stdout)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args(argv)

    # Use alternative arguments if provided
    template_file = args.template_file_alt or args.template_file
    replacements_file = args.replacements_file_alt or args.replacements_file

    if args.verbose:
        print(f"Template file: {template_file}", file=sys.stderr)
        print(f"Replacements file: {replacements_file}", file=sys.stderr)

    # Check if files exist
    if not os.path.exists(template_file):
        print(f"Error: Template file '{template_file}' not found", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(replacements_file):
        print(
            f"Error: Replacements file '{replacements_file}' not found", file=sys.stderr
        )
        sys.exit(1)

    # Parse keymap if provided
    keymap = None
    if args.keymap:
        keymap = [key.strip() for key in args.keymap.split(",") if key.strip()]
        if args.verbose:
            print(f"Using keymap: {keymap}", file=sys.stderr)

    # Handle post-processing function
    post_process_func = default_post_process

    if args.import_module:
        try:
            if args.verbose:
                print(f"Importing module: {args.import_module}", file=sys.stderr)

            # Add current directory to Python path for module imports
            original_path = sys.path.copy()
            if "." not in sys.path:
                sys.path.insert(0, ".")

            # Import the external module
            import importlib

            # Clear module from cache if it exists to ensure fresh import
            if args.import_module in sys.modules:
                del sys.modules[args.import_module]

            module = importlib.import_module(args.import_module)

            # Get the post-processing function from the module
            if hasattr(module, args.post_process_func):
                post_process_func = getattr(module, args.post_process_func)
                if args.verbose:
                    print(
                        f"Using post-processing function: {args.post_process_func} "
                        f"from {args.import_module}",
                        file=sys.stderr,
                    )
            else:
                print(
                    f"Warning: Function '{args.post_process_func}' not found in "
                    f"module '{args.import_module}', using default",
                    file=sys.stderr,
                )
                # Ensure the default post-processing function is used if the
                # specified function is invalid
                post_process_func = default_post_process

            # Restore original Python path
            sys.path = original_path

        except ImportError as e:
            print(
                f"Error: Could not import module '{args.import_module}': {e}",
                file=sys.stderr,
            )
            sys.exit(1)
        except Exception as e:
            print(
                f"Error: Problem with module '{args.import_module}': {e}",
                file=sys.stderr,
            )
            sys.exit(1)

    try:
        # Generate the template
        if args.verbose:
            print("Generating template...", file=sys.stderr)

        result = generate_template_from_files(
            template_file,
            replacements_file,
            keymap=keymap,
            post_process=post_process_func,
        )

        # Output the result
        if args.output_file:
            if args.verbose:
                print(f"Writing output to: {args.output_file}", file=sys.stderr)
            with open(args.output_file, "w") as f:
                f.write(result)
            if args.verbose:
                print(
                    f"Successfully wrote output to {args.output_file}", file=sys.stderr
                )
        else:
            print(result)

        if args.verbose:
            print("Template generation completed successfully", file=sys.stderr)

    except (OSError, FileNotFoundError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
