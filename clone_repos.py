#!/usr/bin/env python3
"""
Script to clone repositories from llnl2do.tsv and remove .git directories.
This prepares the repos as native code for integration into a monorepo.
"""

import shutil
import subprocess
import sys
from pathlib import Path


# Constants
ERROR_MESSAGE_MAX_LENGTH = 100


def parse_tsv(tsv_file):
    """Parse the TSV file and extract repository information."""
    repos = []
    with open(tsv_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                url = parts[0]
                name = parts[1]
                # Skip header row if it doesn't look like a URL
                if line_num == 1 and not url.startswith(('http://', 'https://', 'git@')):
                    continue
                repos.append((url, name))
    return repos


def clone_repo(url, dest_path):
    """Clone a repository to the specified destination."""
    try:
        print(f"Cloning {url} to {dest_path}...")
        result = subprocess.run(
            ['git', 'clone', '--depth', '1', url, str(dest_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per repo
        )
        if result.returncode == 0:
            return True, None
        else:
            return False, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout after 5 minutes"
    except Exception as e:
        return False, str(e)


def remove_git_dir(repo_path):
    """Remove the .git directory from a cloned repository."""
    git_dir = repo_path / '.git'
    if git_dir.exists():
        try:
            shutil.rmtree(git_dir)
            return True
        except Exception as e:
            print(f"Warning: Could not remove .git directory from {repo_path}: {e}")
            return False
    return True


def main():
    """Main function to orchestrate the cloning process."""
    # Parse command line arguments
    tsv_file = 'llnl2do.tsv'
    output_dir = 'cloned_repos'
    
    if len(sys.argv) > 1:
        tsv_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Check if TSV file exists
    if not Path(tsv_file).exists():
        print(f"Error: TSV file '{tsv_file}' not found.")
        print(f"Please ensure the file exists and try again.")
        return 1
    
    # Parse TSV file
    print(f"Reading repositories from {tsv_file}...")
    try:
        repos = parse_tsv(tsv_file)
    except Exception as e:
        print(f"Error reading TSV file: {e}")
        return 1
    print(f"Found {len(repos)} repositories to clone.")
    
    # Track results
    success_count = 0
    failed_repos = []
    
    # Clone each repository
    for i, (url, name) in enumerate(repos, 1):
        dest_path = output_path / name
        
        # Skip if already exists
        if dest_path.exists():
            print(f"[{i}/{len(repos)}] Skipping {name} (already exists)")
            success_count += 1
            continue
        
        # Clone the repository
        print(f"[{i}/{len(repos)}] Processing {name}...")
        success, error = clone_repo(url, dest_path)
        
        if success:
            # Remove .git directory
            if remove_git_dir(dest_path):
                print(f"  ✓ Successfully cloned and cleaned {name}")
                success_count += 1
            else:
                print(f"  ⚠ Cloned {name} but failed to remove .git directory")
                success_count += 1
        else:
            print(f"  ✗ Failed to clone {name}: {error}")
            failed_repos.append((name, error))
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total repositories: {len(repos)}")
    print(f"Successfully cloned: {success_count}")
    print(f"Failed: {len(failed_repos)}")
    
    if failed_repos:
        print("\nFailed repositories:")
        for name, error in failed_repos:
            print(f"  - {name}: {error[:ERROR_MESSAGE_MAX_LENGTH]}")
    
    return 0 if len(failed_repos) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
