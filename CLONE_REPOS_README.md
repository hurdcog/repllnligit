# Repository Cloning Script

This document describes how to use the `clone_repos.py` script to clone all repositories listed in `llnl2do.tsv` and prepare them for integration into a monorepo.

## Overview

The `clone_repos.py` script automates the process of:
1. Reading repository URLs from a TSV file
2. Cloning each repository (shallow clone with depth=1 for efficiency)
3. Removing the `.git` directory from each cloned repository
4. Providing progress tracking and error reporting

## Usage

### Basic Usage

To clone all repositories from `llnl2do.tsv` into the default `cloned_repos` directory:

```bash
python3 clone_repos.py
```

### Custom TSV File and Output Directory

You can specify custom input and output paths:

```bash
python3 clone_repos.py <tsv_file> <output_directory>
```

Example:
```bash
python3 clone_repos.py llnl2do.tsv my_repos
```

## TSV File Format

The script expects a tab-separated values (TSV) file with the following format:

```
<repository_url>	<repository_name>	<description>	<language>
```

Only the first two columns (URL and name) are required. Example:

```
https://github.com/llnl/sundials	sundials	Official development repository...	C
https://github.com/llnl/UEDGE	UEDGE	2D fluid simulation...	Fortran
```

## Features

- **Shallow Clones**: Uses `git clone --depth 1` for faster cloning and reduced disk usage
- **Automatic Cleanup**: Removes `.git` directories automatically after cloning
- **Progress Tracking**: Shows progress for each repository being processed
- **Error Handling**: Reports failures with error messages
- **Resume Support**: Skips repositories that have already been cloned
- **Timeout Protection**: 5-minute timeout per repository to prevent hanging
- **Summary Report**: Displays a summary of successful and failed clones

## Output

The script creates a directory structure like:

```
cloned_repos/
├── sundials/
│   ├── src/
│   ├── examples/
│   └── ...
├── UEDGE/
│   ├── ...
└── RAJAPerf/
    └── ...
```

Note: No `.git` directories are present in the cloned repositories.

## Error Handling

If a repository fails to clone, the script:
- Logs the error message
- Continues with the next repository
- Provides a summary of all failures at the end

Common reasons for failures:
- Repository not found or is private
- Network connectivity issues
- Insufficient disk space
- Clone timeout (>5 minutes)

## Example Output

```
Reading repositories from llnl2do.tsv...
Found 633 repositories to clone.
[1/633] Processing sundials...
Cloning https://github.com/llnl/sundials to cloned_repos/sundials...
  ✓ Successfully cloned and cleaned sundials
[2/633] Processing UEDGE...
Cloning https://github.com/llnl/UEDGE to cloned_repos/UEDGE...
  ✓ Successfully cloned and cleaned UEDGE
...

======================================================================
SUMMARY
======================================================================
Total repositories: 633
Successfully cloned: 630
Failed: 3

Failed repositories:
  - private-repo: fatal: could not read Username
  - old-repo: Repository not found
  - large-repo: Timeout after 5 minutes
```

## Requirements

- Python 3.10 or higher
- Git command-line tool installed and available in PATH
- Sufficient disk space for all repositories
- Internet connection

## Disk Space Considerations

With 633 repositories, the total disk space required will vary significantly depending on repository sizes. Estimate at least 50-100 GB for all repositories, though this can vary widely.

To check available disk space before running:
```bash
df -h .
```

## Tips

1. **Test First**: Run on a small subset of repositories first to verify everything works:
   ```bash
   head -10 llnl2do.tsv > test.tsv
   python3 clone_repos.py test.tsv test_output
   ```

2. **Monitor Disk Space**: Use `df -h` periodically to monitor disk usage during cloning

3. **Resume After Interruption**: The script automatically skips already-cloned repositories, so you can safely re-run it if interrupted

4. **Parallel Cloning**: For faster cloning, consider splitting the TSV file and running multiple instances in parallel (not implemented in base script)

## Integration into Monorepo

After cloning, the repositories are ready for integration into a monorepo. Each directory contains:
- All source code and files from the repository
- No Git history (`.git` directory removed)
- Original directory structure preserved

You can now:
1. Review and organize the cloned repositories
2. Create a unified directory structure
3. Initialize a new Git repository for your monorepo
4. Add all cloned code as subdirectories or modules
