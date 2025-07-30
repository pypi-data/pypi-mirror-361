import os
import sys
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

from forcode.docstring import run_docstring_generator
from forcode.readme import build_readme_writer_tool, run_recursive_readme_writer


def main():
    # Parse CLI args
    cli_args = {k.split('=')[0]: k.split('=')[1] for k in sys.argv[1:] if '=' in k}
    path_args = [arg for arg in sys.argv[1:] if '=' not in arg]
    target_dir = path_args[0] if path_args else os.getcwd()
    openai_key = cli_args.get("openai_key", None)
    if not openai_key:
        # Try loading .env from script directory first
        script_dir = Path(__file__).parent
        env_path = script_dir / '.env'
        if env_path.exists():
            load_dotenv(env_path)
        else:
            # Fallback to current working directory
            load_dotenv()
        openai_key = os.getenv("OPENAI_API_KEY")

    if not openai_key:
        print("ERROR: No OpenAI API key found. Use env var OPENAI_API_KEY or CLI like: forcode openai_key=sk-...")
        sys.exit(1)
    
    # Set environment variable for forgen to use
    os.environ["OPENAI_API_KEY"] = openai_key

    print(f"Scanning directory: {target_dir}")

    # Task selection
    print("\nSelect task:")
    print("  [1] Generate README.md files")
    print("  [2] Generate/Clean Docstrings")

    task = input("Enter choice (1 or 2): ").strip()

    if task == "2":
        print("\n=== DOCSTRING GENERATION MODE ===")
        
        # Detect top-level packages (same as README task)
        top_level_packages = []
        for entry in os.listdir(target_dir):
            full_path = os.path.join(target_dir, entry)
            if os.path.isdir(full_path) and not entry.startswith('.'):
                if os.path.isfile(os.path.join(full_path, '__init__.py')):
                    top_level_packages.append(entry)

        if not top_level_packages:
            print("No top-level Python packages found.")
            sys.exit(0)

        print("\nAvailable top-level packages:\n")
        for idx, pkg in enumerate(top_level_packages, 1):
            print(f"  [{idx}] {pkg}")

        selection = input(
            "\nEnter numbers of packages to process docstrings for (comma-separated, e.g., 1,3) or 'all': ").strip().lower()

        if selection == 'all':
            selected_packages = top_level_packages
        else:
            try:
                selected_indices = [int(i.strip()) - 1 for i in selection.split(',') if i.strip().isdigit()]
                selected_packages = [top_level_packages[i] for i in selected_indices if 0 <= i < len(top_level_packages)]
            except Exception as e:
                print(f"Invalid selection: {e}")
                sys.exit(1)

        if not selected_packages:
            print("No valid packages selected.")
            sys.exit(0)

        print(f"\nSelected packages: {', '.join(selected_packages)}")
        
        # Process only selected packages
        updated_files = []
        for package in selected_packages:
            pkg_path = os.path.join(target_dir, package)
            package_updated_files = run_docstring_generator(pkg_path, openai_key)
            updated_files.extend(package_updated_files)
        
        print(f"\n✅ Docstring generation completed. Updated {len(updated_files)} files:")
        for f in updated_files:
            print(f"  - {f}")
        return

    # Otherwise, proceed with README flow
    print("\n=== README GENERATION MODE ===")

    # Detect top-level packages
    top_level_packages = []
    for entry in os.listdir(target_dir):
        full_path = os.path.join(target_dir, entry)
        if os.path.isdir(full_path) and not entry.startswith('.'):
            if os.path.isfile(os.path.join(full_path, '__init__.py')):
                top_level_packages.append(entry)

    if not top_level_packages:
        print("No top-level Python packages found.")
        sys.exit(0)

    print("\nAvailable top-level packages:\n")
    for idx, pkg in enumerate(top_level_packages, 1):
        print(f"  [{idx}] {pkg}")

    selection = input(
        "\nEnter numbers of packages to generate READMEs for (comma-separated, e.g., 1,3) or 'all': ").strip().lower()

    if selection == 'all':
        selected_packages = top_level_packages
    else:
        try:
            selected_indices = [int(i.strip()) - 1 for i in selection.split(',') if i.strip().isdigit()]
            selected_packages = [top_level_packages[i] for i in selected_indices if 0 <= i < len(top_level_packages)]
        except Exception as e:
            print(f"Invalid selection: {e}")
            sys.exit(1)

    if not selected_packages:
        print("No valid packages selected.")
        sys.exit(0)

    print(f"\nSelected packages: {', '.join(selected_packages)}")

    # Gather files by package
    package_files = defaultdict(list)
    total_chars = 0

    for package in selected_packages:
        pkg_path = os.path.join(target_dir, package)
        for root, dirs, files in os.walk(pkg_path):
            dirs[:] = [d for d in dirs if
                       not d.startswith('.') and d not in {'__pycache__', 'venv', '.venv', 'dist', 'build'}]
            if '__init__.py' not in files:
                continue
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            contents = f.read()
                            package_files[root].append((full_path, contents))
                            total_chars += len(contents)
                    except Exception as e:
                        print(f"WARNING: Skipped {full_path}: {e}")

    print(f"\nFound {sum(len(v) for v in package_files.values())} Python files totaling {total_chars:,} characters.")
    confirm = input("Proceed with generation using OpenAI? [y/N] ").strip().lower()
    if confirm != 'y':
        print("Operation aborted.")
        return

    written_files = []
    for pkg_dir, files in package_files.items():
        print(f"\nProcessing package: {pkg_dir}")

        readme_path = os.path.join(pkg_dir, "README.md")
        existing_content = ""

        # Load existing README if present
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                existing_content = f.read().strip()

        combined_summary = existing_content

        for file_path, contents in files:
            print(f"  Summarizing {os.path.basename(file_path)}...")
            input_data = {"file_contents": contents}
            tool_instance = build_readme_writer_tool(openai_key)
            result = tool_instance.execute(input_data)
            generated = result.get("output") or result.get("summary") or ""
            combined_summary += f"\n\n---\n\n{generated.strip()}"

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(combined_summary.strip() + "\n")

        written_files.append(readme_path)

    print("\nSUCCESS: Generated/updated README.md files:")
    for file in written_files:
        print(f"  {file}")


if __name__ == "__main__":
    main()
