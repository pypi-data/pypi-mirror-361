#!/usr/bin/env python3
"""
🔐secret & PII Scanner CLI Tool

A lightweight, extensible tool to automatically scan source code for hardcodedsecrets 
and personally identifiable information (PII) at commit time or during CI/CD pipeline execution.
"""

import sys
import os
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text
import datetime
import json

from .core.scanner import SecretScanner
from .core.config import Config
from .utils.git_utils import GitUtils
from .utils.report_generator import ReportGenerator
from .utils.pre_commit import PreCommitHook
from .utils.multi_project_scanner import MultiProjectScanner
from .utils.email_notifier import EmailNotifier
from .utils.platform_utils import (
    get_system_info,
    check_dependencies,
    get_installation_instructions
)

app = typer.Typer(
    name="secret-scanner",
    help="🔐 [bold blue]Secret & PII Scanner[/bold blue]\n\n"
         "Detect hardcodedsecrets and PII in source code.\n\n"
         "[bold green]Quick Start:[/bold green]\n"
         "secret-scanner scan .                    # Scan current directory\n"
         "secret-scanner scan . --output json      # Generate JSON report\n"
         "secret-scanner install-hook              # Install pre-commit hook\n\n"
         "[bold cyan]For detailed help:[/bold cyan]secret-scanner <command> --help",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True
)

console = Console()

def print_banner():
    """Print the tool banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🔐secret & PII Scanner                    ║
    ║                                                              ║
    ║  Detect hardcodedsecrets and PII in source code              ║
    ║  Shift-left security for modern development workflows        ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold blue"))

@app.command()
def scan(
    path: str = typer.Argument(
        ..., 
        help="[bold]Path to scan[/bold] - File, directory, or git repository to scan for secrets and PII",
        metavar="PATH"
    ),
    files: Optional[str] = typer.Option(
        None, 
        "--files", 
        "-f", 
        help="[bold]File patterns[/bold] - Comma-separated glob patterns (e.g., '*.py,*.js,*.env,*.yaml')"
    ),
    diff_only: bool = typer.Option(
        False, 
        "--diff-only", 
        "-d", 
        help="[bold]Git diff mode[/bold] - Scan only modified files (requires git repository)"
    ),
    output: str = typer.Option(
        "console", 
        "--output", 
        "-o", 
        help="[bold]Output format[/bold] - [green]console[/green] (default), [blue]json[/blue], [yellow]html[/yellow], [red]pdf[/red], [cyan]csv[/cyan], [magenta]xml[/magenta], [orange]sarif[/orange], [purple]junit[/purple]"
    ),
    report_path: Optional[str] = typer.Option(
        None,
        "--report-path",
        help="[bold]Report path[/bold] - Full path (including filename) for the output report. Overrides --report-name."
    ),
    report_name: Optional[str] = typer.Option(
        None,
        "--report-name",
        help="[bold]Report name[/bold] - Custom report filename (used in output directory or current directory)."
    ),
    config_file: Optional[str] = typer.Option(
        None, 
        "--config", 
        "-c", 
        help="[bold]Custom config[/bold] - Path to custom configuration file (.yaml/.yml)"
    ),
    exit_on_failure: bool = typer.Option(
        False, 
        "--exit-on-failure", 
        "-e", 
        help="[bold]CI/CD mode[/bold] - Exit with non-zero code ifsecrets found"
    ),
    verbose: bool = typer.Option(
        False, 
        "--verbose", 
        "-v", 
        help="[bold]Verbose mode[/bold] - Show detailed context and line numbers"
    ),
    quiet: bool = typer.Option(
        False, 
        "--quiet", 
        "-q", 
        help="[bold]Quiet mode[/bold] - Suppress all output except errors"
    ),
    max_file_size: Optional[int] = typer.Option(
        None,
        "--max-file-size",
        help="[bold]File size limit[/bold] - Maximum file size to scan in MB (default: 10MB)"
    ),
    context_lines: Optional[int] = typer.Option(
        None,
        "--context-lines",
        help="[bold]Context lines[/bold] - Number of lines around findings (default: 3)"
    ),
    max_workers: Optional[int] = typer.Option(
        None,
        "--max-workers",
        help="[bold]Worker threads[/bold] - Number of worker threads (default: auto-detect)"
    ),
    chunk_size: Optional[int] = typer.Option(
        None,
        "--chunk-size",
        help="[bold]Chunk size[/bold] - Files per thread batch (default: 10)"
    ),
    single_threaded: bool = typer.Option(
        False,
        "--single-threaded",
        help="[bold]Single thread[/bold] - Force single-threaded mode (for debugging)"
    ),
    thorough_scan: bool = typer.Option(
        False,
        "--thorough-scan",
        help="[bold]Thorough scan[/bold] - Disable exclude patterns and scan all files (may be slower)"
    ),
    show_skipped: bool = typer.Option(
        False,
        "--show-skipped",
        help="[bold]Show skipped[/bold] - Show files that are being skipped during scan"
    )
):
    """
    🔍 Scan for secrets and PII in source code
    
    [bold yellow]Examples:[/bold yellow]
    secret-scanner scan .                           # Scan current directory
    secret-scanner scan . --files "*.py,*.js"      # Scan specific file types
    secret-scanner scan . --diff-only              # Scan only modified files
    secret-scanner scan . --output json            # Generate JSON report
    
    [bold]File handling:[/bold]
    • Configurable maximum file size (default: 10MB)
    • Context lines around findings (default: 3 lines)
    • File pattern filtering for targeted scanning
    
    [bold]Scanning modes:[/bold]
    • --thorough-scan: Disable exclude patterns and scan all files
    • --show-skipped: Show files being skipped during scan
    • --single-threaded: Force single-threaded mode for debugging
    
    [bold]Debugging:[/bold]
    • --single-threaded for debugging threading issues
    • --verbose for detailed output
    • --quiet for minimal output
    
    [bold yellow]🔍 What it detects:[/bold yellow]
    
    [bold]Secrets & Credentials:[/bold]
    • API keys (AWS, Google, GitHub, Stripe, etc.)
    • Access tokens and OAuthsecrets
    • Database credentials and connection strings
    • Private keys and certificates
    • SSH keys and passwords
    
    [bold]PII (Personally Identifiable Information):[/bold]
    • Email addresses
    • Phone numbers (various formats)
    • Social Security Numbers (US)
    • Credit card numbers
    • IP addresses and MAC addresses
    
    [bold]High-entropy strings:[/bold]
    • Random-looking strings that might besecrets
    • Base64 encoded data
    • Hex strings and hashes
    
    [bold yellow]📁 Supported file types:[/bold yellow]
    
    [bold]Programming Languages:[/bold]
    • Python (.py, .pyc, .pyo)
    • JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
    • Java (.java, .class)
    • C/C++ (.c, .cpp, .h, .hpp)
    • Go (.go)
    • Rust (.rs)
    • PHP (.php)
    • Ruby (.rb)
    
    [bold]Configuration Files:[/bold]
    • YAML (.yaml, .yml)
    • JSON (.json)
    • XML (.xml)
    • INI (.ini, .cfg)
    • Environment files (.env, .env.local)
    
    [bold]Documentation & Scripts:[/bold]
    • Markdown (.md, .markdown)
    • HTML (.html, .htm)
    • CSS (.css, .scss, .less)
    • Shell scripts (.sh, .bash, .zsh)
    
    [bold yellow]📊 Output formats:[/bold yellow]
    
    [bold green]console[/bold green] (default):
    • Rich formatted output with colors and tables
    • Real-time progress indicators
    • Severity-based color coding
    • Context lines around findings
    
    [bold blue]json[/bold blue]:
    • Machine-readable format for CI/CD integration
    • Structured data for programmatic processing
    • Includes metadata and scan statistics
    
    [bold yellow]html[/bold yellow]:
    • Beautiful interactive web report
    • Search and filter functionality
    • Clickable file links
    • Severity-based styling
    
    [bold red]pdf[/bold red]:
    • Professional report for compliance/audit
    • Executive summary with statistics
    • Detailed findings with context
    • Email-ready format
    
    [bold cyan]csv[/bold cyan]:
    • Comma-separated values for spreadsheet import
    • Easy data analysis and filtering
    • Compatible with Excel, Google Sheets, etc.
    
    [bold magenta]xml[/bold magenta]:
    • Structured XML format for enterprise tools
    • Machine-readable with schema validation
    • Integration with XML-based systems
    
    [bold orange]sarif[/bold orange]:
    • SARIF format for security tool integration
    • Industry standard for static analysis results
    • Compatible with GitHub Security, Azure DevOps, etc.
    
    [bold purple]junit[/bold purple]:
    • JUnit XML format for CI/CD integration
    • Test failure reporting for build systems
    • Jenkins, GitLab CI, GitHub Actions compatible
    
    [bold yellow]⚡ Performance options:[/bold yellow]
    
    [bold]Multi-threading:[/bold]
    • Automatically uses optimal thread count based on CPU cores
    • Configurable with --max-workers (default: CPU cores + 4)
    • Adjustable chunk size with --chunk-size (default: 10 files per batch)
    
    [bold]File handling:[/bold]
    • Configurable maximum file size (default: 10MB)
    • Context lines around findings (default: 3 lines)
    • File pattern filtering for targeted scanning
    
    [bold]Debugging:[/bold]
    • --single-threaded for debugging threading issues
    • --verbose for detailed output
    • --quiet for minimal output
    
    [bold yellow]🔧 Configuration:[/bold yellow]
    
    Create a `.secret-scanner.yaml` file in your repository root:
    
    ```yaml
    patterns:
      - name: "Custom API Key"
        regex: "my_custom_key_[a-zA-Z0-9]{32}"
        severity: "high"
    
    exclude:
      - "*.log"
      - "node_modules/"
      - "vendor/"
    
    max_file_size: 10485760  # 10MB
    context_lines: 3
    max_workers: 8
    chunk_size: 10
    ```
    
    [bold yellow]💡 Pro Tips:[/bold yellow]
    
    • Use --diff-only for faster scans in git repositories
    • Combine --files with --diff-only for targeted scanning
    • Use --output json for CI/CD pipeline integration
    • Set --exit-on-failure to fail builds whensecrets are found
    • Use --max-workers to optimize for your system
    • Exclude large directories with configuration file
    • Use --thorough-scan to scan all files (no exclusions)
    • Use --show-skipped to see what files are being skipped
    • Combine --thorough-scan --show-skipped for complete visibility
    """
    if quiet:
        console.quiet = True
    
    if not quiet:
        print_banner()
    
    try:
        # Load configuration
        config = Config.load(config_file) if config_file else Config.load_default()
        
        # Override config with command line options
        if max_file_size:
            config.max_file_size = max_file_size * 1024 * 1024  # Convert MB to bytes
        if context_lines:
            config.context_lines = context_lines
        if max_workers:
            config.max_workers = max_workers
        if chunk_size:
            config.chunk_size = chunk_size
        if single_threaded:
            config.max_workers = 1
        
        # Handle thorough scan option
        if thorough_scan:
            config.exclude_patterns = []  # Disable all exclude patterns
            if not quiet:
                console.print("[yellow]🔍 Thorough scan enabled - scanning all files[/yellow]")
        
        # Handle show skipped option
        if show_skipped:
            config.show_skipped_files = True
            if not quiet:
                console.print("[cyan]📋 Will show skipped files during scan[/cyan]")
        
        # Initialize scanner
        scanner = SecretScanner(config)
        
        # Determine files to scan
        if diff_only:
            git_utils = GitUtils()
            files_to_scan = git_utils.get_modified_files(path)
            if not files_to_scan:
                console.print("[yellow]No modified files found in git diff[/yellow]")
                return
        else:
            files_to_scan = None
        
        # Perform scan
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            disable=quiet
        ) as progress:
            # Create progress tracking variables
            scan_task = None
            current_file_task = None
            total_findings = 0
            
            def progress_callback(file_path, findings_count, total_files=None, completed_files=None):
                nonlocal scan_task, current_file_task, total_findings
                
                # Initialize main scan task
                if scan_task is None and total_files is not None:
                    scan_task = progress.add_task(
                        f"Scanning {total_files} files for secrets and PII...", 
                        total=total_files
                    )
                
                # Update main progress
                if scan_task is not None and completed_files is not None:
                    progress.update(scan_task, completed=completed_files)
                
                # Update current file display
                if file_path is not None:
                    # Remove previous file task if exists
                    if current_file_task is not None:
                        progress.remove_task(current_file_task)
                    
                    # Create new file task
                    file_name = file_path.name if hasattr(file_path, 'name') else str(file_path)
                    current_file_task = progress.add_task(
                        f"📄 {file_name} ({findings_count} findings)",
                        total=None
                    )
                    
                    # Update total findings
                    total_findings += findings_count
                    
                    # Update main task description with findings count
                    if scan_task is not None:
                        progress.update(scan_task, description=f"Scanning {total_files} files for secrets and PII... ({total_findings} findings so far)")
            
            # Use the correct method based on what we're scanning
            if diff_only and files_to_scan:
                # Scan specific files from git diff
                results = scanner.scan_files(files_to_scan, progress_callback)
            else:
                # Scan directory or file
                path_obj = Path(path)
                if path_obj.is_file():
                    # For single file, just scan it directly
                    results = scanner.scan_file(path_obj)
                    if not quiet:
                        console.print(f"📄 Scanned {path_obj.name}")
                else:
                   results = scanner.scan_directory(
                        path_obj, 
                        file_patterns=files.split(',') if files else None,
                        progress_callback=progress_callback
                    )
            
            # Clean up progress display
            if current_file_task is not None:
                progress.remove_task(current_file_task)
            if scan_task is not None:
                progress.update(scan_task, completed=progress.tasks[scan_task].total)
        
        # Generate report
        report_generator = ReportGenerator()
        report_file_path = None
        if output == "console":
            report_generator.print_console_report(results, verbose=verbose)
        else:
            # Determine report file path
            if report_path:
                report_file_path = report_path
            else:
                if report_name:
                    report_file_path = report_name
                    if not os.path.isabs(report_file_path):
                        report_file_path = os.path.join(os.getcwd(), report_file_path)
                else:
                    ext = output.lower()
                    report_file_path = f"secret_scan_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            if output == "json":
                report_generator.save_json_report(results, report_file_path)
                console.print(f"[green]JSON report saved to: {report_file_path}[/green]")
            elif output == "html":
                report_generator.save_html_report(results, report_file_path)
                console.print(f"[green]HTML report saved to: {report_file_path}[/green]")
            elif output == "pdf":
                report_generator.save_pdf_report(results, report_file_path)
                console.print(f"[green]PDF report saved to: {report_file_path}[/green]")
            elif output == "csv":
                report_generator.save_csv_report(results, report_file_path)
                console.print(f"[green]CSV report saved to: {report_file_path}[/green]")
            elif output == "xml":
                report_generator.save_xml_report(results, report_file_path)
                console.print(f"[green]XML report saved to: {report_file_path}[/green]")
            elif output == "sarif":
                report_generator.save_sarif_report(results, report_file_path)
                console.print(f"[green]SARIF report saved to: {report_file_path}[/green]")
            elif output == "junit":
                report_generator.save_junit_report(results, report_file_path)
                console.print(f"[green]JUnit XML report saved to: {report_file_path}[/green]")
            else:
                console.print(f"[red]Unsupported output format: {output}[/red]")
                sys.exit(1)
        
        # Handle exit on failure
        if exit_on_failure and results:
            console.print(f"[red]Found {len(results)} potentialsecrets/PII. Exiting with failure.[/red]")
            sys.exit(1)
        
        if not quiet:
            if results:
                console.print(f"[yellow]⚠️  Found {len(results)} potentialsecrets/PII[/yellow]")
            else:
                console.print("[green]✅ Nosecrets or PII found![/green]")
    
    except Exception as e:
        console.print(f"[red]Error during scan: {str(e)}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)

@app.command()
def scan_multi(
    parent_directory: str = typer.Argument(
        ..., 
        help="[bold]Parent directory[/bold] - Directory containing multiple projects to scan",
        metavar="PARENT_DIR"
    ),
    project_patterns: Optional[str] = typer.Option(
        None, 
        "--project-patterns", 
        "-p", 
        help="[bold]Project patterns[/bold] - Comma-separated glob patterns to identify projects (e.g., '*,project-*')"
    ),
    exclude_patterns: Optional[str] = typer.Option(
        None, 
        "--exclude-patterns", 
        "-e", 
        help="[bold]Exclude patterns[/bold] - Comma-separated patterns to exclude from scanning"
    ),
    output_dir: Optional[str] = typer.Option(
        None, 
        "--output-dir", 
        "-o", 
        help="[bold]Output directory[/bold] - Directory to save reports (default: current directory)"
    ),
    report_path: Optional[str] = typer.Option(
        None,
        "--report-path",
        help="[bold]Report path[/bold] - Full path (including filename) for the summary report. Overrides --report-name."
    ),
    report_name: Optional[str] = typer.Option(
        None,
        "--report-name",
        help="[bold]Report name[/bold] - Custom summary report filename (used in output directory or current directory)."
    ),
    max_workers: Optional[int] = typer.Option(
        None,
        "--max-workers",
        help="[bold]Worker threads[/bold] - Maximum number of worker threads for project scanning"
    ),
    send_email: bool = typer.Option(
        False,
        "--send-email",
        help="[bold]Email notifications[/bold] - Send email notification with PDF report"
    ),
    email_config: Optional[str] = typer.Option(
        None,
        "--email-config",
        help="[bold]Email config[/bold] - Path to email configuration file (.json)"
    ),
    test_email: bool = typer.Option(
        False,
        "--test-email",
        help="[bold]Test email[/bold] - Test email configuration before scanning"
    ),
    config_file: Optional[str] = typer.Option(
        None, 
        "--config", 
        "-c", 
        help="[bold]Scanner config[/bold] - Path to custom scanner configuration file (.yaml/.yml)"
    ),
    verbose: bool = typer.Option(
        False, 
        "--verbose", 
        "-v", 
        help="[bold]Verbose mode[/bold] - Show detailed progress and statistics"
    ),
    quiet: bool = typer.Option(
        False, 
        "--quiet", 
        "-q", 
        help="[bold]Quiet mode[/bold] - Suppress all output except errors"
    )
):
    """
    🏢 Scan multiple projects in parallel
    
    [bold yellow]Examples:[/bold yellow]
    secret-scanner scan-multi /path/to/projects              # Scan all projects
    secret-scanner scan-multi /path/to/projects --project-patterns "project-*,web-*"
    secret-scanner scan-multi /path/to/projects --send-email --email-config email.json
    """
    if quiet:
        console.quiet = True
    
    if not quiet:
        print_banner()
    
    try:
        # Load configuration
        config = Config.load(config_file) if config_file else Config.load_default()
        
        # Override config with command line options
        if max_workers:
            config.max_workers = max_workers
        
        # Initialize multi-project scanner
        multi_scanner = MultiProjectScanner(
            parent_directory=parent_directory,
            scanner_config=config
        )
        
        # Parse patterns
        project_patterns_list = project_patterns.split(',') if project_patterns else None
        exclude_patterns_list = exclude_patterns.split(',') if exclude_patterns else None
        
        # Convert output_dir to Path if provided
        output_path = Path(output_dir) if output_dir else None
        
        # Load email config if provided
        email_config_dict = None
        if email_config:
            try:
                with open(email_config, 'r') as f:
                    email_config_dict = json.load(f)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load email config: {e}[/yellow]")
        
        # Test email configuration if requested
        if test_email and email_config_dict:
            console.print("[blue]Testing email configuration...[/blue]")
            test_notifier = EmailNotifier(email_config_dict)
            if test_notifier.test_connection():
                console.print("[green]✅ Email configuration test successful![/green]")
            else:
                console.print("[red]❌ Email configuration test failed![/red]")
                return
        
        # Perform multi-project scan
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            disable=quiet
        ) as progress:
            # Create progress tracking for multi-project scan
            multi_scan_task = None
            project_scan_task = None
            
            def multi_progress_callback(message, completed=None, total=None):
                nonlocal multi_scan_task, project_scan_task
                
                # Initialize main multi-scan task
                if multi_scan_task is None and total is not None:
                    multi_scan_task = progress.add_task(
                        "Multi-project scan", 
                        total=total
                    )
                
                # Update main progress
                if multi_scan_task is not None and completed is not None:
                    progress.update(multi_scan_task, completed=completed)
                
                # Update description with current message
                if multi_scan_task is not None:
                    progress.update(multi_scan_task, description=message)
            
            scan_results = multi_scanner.run_automated_scan(
                project_patterns=project_patterns_list,
                exclude_patterns=exclude_patterns_list,
                max_workers=max_workers,
                output_dir=output_path,
                send_email=send_email,
                progress_callback=multi_progress_callback,
                report_path=report_path,
                report_name=report_name
            )
            
            # Clean up progress display
            if multi_scan_task is not None:
                progress.update(multi_scan_task, completed=progress.tasks[multi_scan_task].total)
        
        if not quiet:
            results = scan_results['results']
            console.print(f"[green]✅ Multi-project scan completed![/green]")
            console.print(f"Scanned {results['projects_scanned']} projects")
            console.print(f"Found {results['total_findings']} total findings")
            
            if 'report_paths' in scan_results:
                report_paths = scan_results['report_paths']
                console.print(f"Reports saved to: {output_path or Path.cwd()}")
                for report_type, report_path in report_paths.items():
                    if report_type != 'project_pdfs':  # Skip individual project PDFs in summary
                        console.print(f"  - {report_type.upper()}: {report_path}")
    
    except Exception as e:
        console.print(f"[red]Error during multi-project scan: {str(e)}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)

@app.command()
def install_hook(
    repo_path: str = typer.Option(
        ".", 
        "--repo", 
        "-r", 
        help="[bold]Repository path[/bold] - Path to git repository (default: current directory)"
    ),
    force: bool = typer.Option(
        False, 
        "--force", 
        "-f", 
        help="[bold]Force install[/bold] - Overwrite existing pre-commit hook"
    ),
    global_hook: bool = typer.Option(
        False,
        "--global",
        "-g",
        help="[bold]Global hook[/bold] - Install as global git hook template for all repositories"
    )
):
    """
    🔗 Install pre-commit hook for automaticsecret scanning
    
    [bold yellow]Examples:[/bold yellow]
    secret-scanner install-hook                    # Install in current repository
    secret-scanner install-hook --repo /path/to/repo  # Install in specific repository
    secret-scanner install-hook --global           # Install for all repositories
    """
    try:
        hook_installer = PreCommitHook()
        success = hook_installer.install(
            repo_path=repo_path,
            force=force,
            global_hook=global_hook
        )
        
        if success:
            console.print("[green]✅ Pre-commit hook installed successfully![/green]")
            if global_hook:
                console.print("The hook is now available as a global template for all repositories.")
                console.print("New repositories will automatically get this hook when initialized.")
            else:
                console.print("The hook will now run before each commit in this repository.")
                console.print("To test it, try making a commit with a file containing 'password123'")
        else:
            console.print("[yellow]⚠️  Pre-commit hook installation skipped (already exists)[/yellow]")
            console.print("Use --force to overwrite the existing hook.")
    
    except Exception as e:
        console.print(f"[red]Error installing pre-commit hook: {str(e)}[/red]")
        sys.exit(1)

@app.command()
def uninstall_hook(
    repo_path: str = typer.Option(
        ".", 
        "--repo", 
        "-r", 
        help="[bold]Repository path[/bold] - Path to git repository (default: current directory)"
    )
):
    """
    🗑️ Uninstall pre-commit hook
    
    [bold yellow]Examples:[/bold yellow]
    secret-scanner uninstall-hook                    # Remove from current repository
    secret-scanner uninstall-hook --repo /path/to/repo  # Remove from specific repository
    """
    try:
        hook_installer = PreCommitHook()
        success = hook_installer.uninstall(repo_path)
        
        if success:
            console.print("[green]✅ Pre-commit hook uninstalled successfully![/green]")
        else:
            console.print("[yellow]⚠️  No pre-commit hook found to uninstall[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error uninstalling pre-commit hook: {str(e)}[/red]")
        sys.exit(1)

@app.command()
def init(
    path: str = typer.Option(
        ".", 
        "--path", 
        "-p", 
        help="[bold]Project path[/bold] - Path to initialize configuration (default: current directory)"
    ),
    force: bool = typer.Option(
        False, 
        "--force", 
        "-f", 
        help="[bold]Force overwrite[/bold] - Overwrite existing configuration file"
    )
):
    """
    ⚙️ Initialize configuration file
    
    [bold yellow]Examples:[/bold yellow]
    secret-scanner init                    # Create config in current directory
    secret-scanner init --path /path/to/project  # Create config in specific project
    secret-scanner init --force            # Overwrite existing config
    """
    try:
        config_path = Path(path) / ".secret-scanner.yaml"
        
        if config_path.exists() and not force:
            console.print("[yellow]Configuration file already exists. Use --force to overwrite.[/yellow]")
            return
        
        config = Config.create_default()
        config.save(config_path)
        
        console.print(f"[green]✅ Configuration file created: {config_path}[/green]")
        console.print("\nYou can now customize the patterns and settings in this file.")
        console.print("Run [bold]secret-scanner scan .[/bold] to test the configuration.")
    
    except Exception as e:
        console.print(f"[red]Error creating configuration: {str(e)}[/red]")
        sys.exit(1)

@app.command()
def test(
    pattern: str = typer.Argument(
        ..., 
        help="[bold]Regex pattern[/bold] - Regular expression pattern to test",
        metavar="PATTERN"
    ),
    text: str = typer.Argument(
        ..., 
        help="[bold]Test text[/bold] - Text to test against the pattern",
        metavar="TEXT"
    )
):
    """
    🧪 Test regex patterns for secret detection
    
    [bold yellow]Examples:[/bold yellow]
    secret-scanner test "api_key_[a-zA-Z0-9]{32}" "api_key_abc123def456ghi789jkl012mno345pqr678"
    secret-scanner test "password\\s*=\\s*['\"][^'\"]+['\"]" "password = 'secret123'"
    secret-scanner test "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b" "user@example.com"
    """
    try:
        import re
        
        console.print(f"[bold]Testing pattern:[/bold] {pattern}")
        console.print(f"[bold]Against text:[/bold] {text}")
        console.print()
        
        match = re.search(pattern, text)
        
        if match:
            console.print("[green]✅ Pattern matched![/green]")
            console.print(f"Matched text: '{match.group()}'")
            console.print(f"Start position: {match.start()}")
            console.print(f"End position: {match.end()}")
            
            # Show groups if any
            if match.groups():
                console.print("Groups:")
                for i, group in enumerate(match.groups(), 1):
                    console.print(f"  Group {i}: '{group}'")
        else:
            console.print("[red]❌ No match found[/red]")
    
    except re.error as e:
        console.print(f"[red]Invalid regex pattern: {str(e)}[/red]")
        console.print("Check your regex syntax and try again.")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@app.command()
def check_system():
    """
    🔍 Check system compatibility and dependencies
    
    [bold]Overview:[/bold]
    Verifies that your system meets the requirements for running thesecret & PII Scanner
    and checks the availability of all required dependencies.
    
    [bold yellow]🔍 What it checks:[/bold yellow]
    
    • [bold]Operating system:[/bold] Platform compatibility
    • [bold]Python version:[/bold] Python interpreter and version
    • [bold]Git availability:[/bold] Git command-line tool
    • [bold]PDF libraries:[/bold] WeasyPrint and ReportLab availability
    • [bold]File permissions:[/bold] Write access to necessary directories
    
    [bold yellow]💡 Usage:[/bold yellow]
    
    ```bash
  secret-scanner check-system
    ```
    
    [bold yellow]🔧 Troubleshooting:[/bold yellow]
    
    • Run this command after installation to verify setup
    • Use the output to identify missing dependencies
    • Follow the installation instructions if issues are found
    """
    console.print("[bold blue]🔍 System Compatibility Check[/bold blue]")
    console.print("=" * 50)
    
    # Get system information
    system_info = get_system_info()
    
    # Display system info
    console.print(f"\n[bold]System Information:[/bold]")
    console.print(f"  OS: {system_info['system']} {system_info['release']}")
    console.print(f"  Architecture: {system_info['machine']}")
    console.print(f"  Python: {system_info['python_version']} ({system_info['python_implementation']})")
    
    # Check dependencies
    dependencies = check_dependencies()
    
    console.print(f"\n[bold]Dependencies:[/bold]")
    
    # Python
    if dependencies['python']:
        console.print("  ✅ Python - Available")
    else:
        console.print("  ❌ Python - Not available")
    
    # Git
    if dependencies['git']:
        console.print("  ✅ Git - Available")
    else:
        console.print("  ❌ Git - Not available")
    
    # WeasyPrint
    if dependencies['weasyprint']:
        console.print("  ✅ WeasyPrint - Available (PDF generation)")
    else:
        console.print("  ⚠️  WeasyPrint - Not available (PDF generation limited)")
    
    # ReportLab
    if dependencies['reportlab']:
        console.print("  ✅ ReportLab - Available (PDF generation fallback)")
    else:
        console.print("  ⚠️  ReportLab - Not available (PDF generation limited)")
    
    # Overall status
    critical_deps = dependencies['python'] and dependencies['git']
    pdf_deps = dependencies['weasyprint'] or dependencies['reportlab']
    
    console.print(f"\n[bold]Overall Status:[/bold]")
    if critical_deps:
        console.print("  ✅ System is compatible for basic scanning")
        if pdf_deps:
            console.print("  ✅ PDF generation is available")
        else:
            console.print("  ⚠️  PDF generation is not available")
    else:
        console.print("  ❌ System has critical missing dependencies")
    
    # Installation instructions if needed
    if not critical_deps or not pdf_deps:
        console.print(f"\n[bold]Installation Instructions:[/bold]")
        console.print(get_installation_instructions())

@app.command()
def version():
    """
    📋 Show version information
    
    [bold]Overview:[/bold]
    Displays the current version of thesecret & PII Scanner tool along with
    additional information about features, capabilities, and system details.
    
    [bold yellow]📊 Version details:[/bold yellow]
    
    [bold]Tool version:[/bold] Shows the current release version
    [bold]Python version:[/bold] Shows the Python interpreter version
    [bold]Platform info:[/bold] Shows operating system and architecture
    [bold]Feature summary:[/bold] Lists key capabilities and supported formats
    
    [bold yellow]🔍 What you'll see:[/bold yellow]
    
    • [bold]Version number:[/bold] Current release version (e.g., 1.0.0)
    • [bold]Build information:[/bold] Build date and commit hash
    • [bold]Python compatibility:[/bold] Python version requirements
    • [bold]Supported platforms:[/bold] Operating systems and architectures
    • [bold]Feature list:[/bold] Key capabilities and detection patterns
    • [bold]Output formats:[/bold] Supported report formats
    • [bold]Integration options:[/bold] CI/CD and git hook support
    
    [bold yellow]💡 Usage:[/bold yellow]
    
    ```bash
  secret-scanner version
    ```
    
    [bold yellow]🔧 Troubleshooting:[/bold yellow]
    
    • Use this command to verify installation
    • Check version compatibility with your system
    • Verify feature availability
    • Report version information for bug reports
    """
    from . import __version__
    console.print(f"[bold blue]Secret & PII Scanner v{__version__}[/bold blue]")
    console.print("🔐 Detect hardcodedsecrets and PII in source code")
    console.print("📖 Documentation: https://github.com/your-org/secret-scanner")
    console.print("🐛 Report issues: https://github.com/your-org/secret-scanner/issues")

if __name__ == "__main__":
    app() 