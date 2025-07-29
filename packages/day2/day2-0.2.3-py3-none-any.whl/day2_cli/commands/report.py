"""Reports commands for the MontyCloud DAY2 CLI."""

from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from day2.exceptions import Day2Error
from day2_cli.utils.context import get_enhanced_context, with_common_options
from day2_cli.utils.exit_codes import handle_error_with_exit
from day2_cli.utils.output_formatter import format_item_output

console = Console()


@click.group()
def report() -> None:
    """Reports commands."""


@report.command("get-details")
@click.argument("report-id")
@with_common_options(include_tenant_id=True)
def get_report_details(
    report_id: str,
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """Get details of a specific report.

    If --tenant-id is not provided, uses the default tenant configured with 'day2 profile create' or 'day2 auth login'.

    REPORT-ID: ID of the report to retrieve details for.
    """
    try:
        # Get enhanced context with tenant resolution
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        # Call the client method
        result = session.report.get_report_details(resolved_tenant_id, report_id)

        # Format timestamps
        created_at = (
            result.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if result.created_at
            else "N/A"
        )
        updated_at = (
            result.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            if result.updated_at
            else "N/A"
        )

        # Format and output the result
        report_data = {
            "ID": result.report_id,
            "Type": result.report_type,
            "Status": result.status,
            "Export Format": result.export_format,
            "Created At": created_at,
            "Updated At": updated_at,
            "Created By": result.created_by,
        }

        format_item_output(
            item=report_data,
            title=f"Report Details: {result.report_id}",
            format_override=output_format,
        )

    except Day2Error as e:
        handle_error_with_exit(e)


@report.command("get")
@click.argument("report-id")
@click.option(
    "--file-name", required=True, help="Desired name for the downloaded report file."
)
@with_common_options(include_tenant_id=True)
def get_report(
    report_id: str,
    file_name: str,
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> None:
    """Get the download URL for a specific report.

    If --tenant-id is not provided, uses the default tenant configured with 'day2 profile create' or 'day2 auth login'.

    REPORT-ID: ID of the report to retrieve.
    """
    try:
        # Get enhanced context with tenant resolution
        context = get_enhanced_context(
            output=output, profile=profile, tenant_id=tenant_id, require_tenant=True
        )
        session = context["session"]
        output_format = context["output_format"]
        resolved_tenant_id = context["tenant_id"]

        # Call the client method
        result = session.report.get_report(resolved_tenant_id, report_id, file_name)

        # Format and output the result
        report_data = {
            "download_url": result.download_url,
            "file_name": file_name,
        }

        if output_format == "json":
            # Output as JSON
            import json

            console.print(json.dumps(report_data, indent=2))
        else:
            # Output as table
            table = Table(show_header=False, box=None)
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green", overflow="fold")

            # Add rows to the table
            table.add_row("download_url", result.download_url)
            table.add_row("file_name", file_name)

            console.print(table)

    except Day2Error as e:
        handle_error_with_exit(e)
