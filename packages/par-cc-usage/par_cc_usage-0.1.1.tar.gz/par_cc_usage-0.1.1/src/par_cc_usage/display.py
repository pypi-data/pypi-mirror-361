"""Display components for par_cc_usage monitor mode."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

from .models import Project, Session, UsageSnapshot
from .token_calculator import format_token_count, get_model_display_name
from .utils import format_datetime, format_time_range


class MonitorDisplay:
    """Display component for monitor mode."""

    def __init__(
        self, console: Console | None = None, show_sessions: bool = False, time_format: str = "24h", config: Any = None
    ) -> None:
        """Initialize display.

        Args:
            console: Rich console instance
            show_sessions: Whether to show the sessions panel
            time_format: Time format ('12h' or '24h')
            config: Configuration object
        """
        self.console = console or Console()
        self.layout = Layout()
        self.show_sessions = show_sessions
        self.time_format = time_format
        self.config = config
        self.show_tool_usage = config and config.display.show_tool_usage if config else True
        self._setup_layout(show_sessions)

    def _strip_project_name(self, project_name: str) -> str:
        """Strip configured prefixes from project name."""
        if not self.config or not self.config.display.project_name_prefixes:
            return project_name

        for prefix in self.config.display.project_name_prefixes:
            if project_name.startswith(prefix):
                return project_name[len(prefix) :]
        return project_name

    def _setup_layout(self, show_sessions: bool = False) -> None:
        """Set up the display layout."""
        if show_sessions:
            if self.show_tool_usage:
                self.layout.split_column(
                    Layout(name="header", size=3),
                    Layout(name="block_progress", size=3),
                    Layout(name="progress", size=6),
                    Layout(name="tool_usage", size=7),
                    Layout(name="sessions"),
                )
            else:
                self.layout.split_column(
                    Layout(name="header", size=3),
                    Layout(name="block_progress", size=3),
                    Layout(name="progress", size=6),
                    Layout(name="sessions"),
                )
        else:
            if self.show_tool_usage:
                self.layout.split_column(
                    Layout(name="header", size=3),
                    Layout(name="block_progress", size=3),
                    Layout(name="progress", size=6),
                    Layout(name="tool_usage", size=7),
                )
            else:
                self.layout.split_column(
                    Layout(name="header", size=3),
                    Layout(name="block_progress", size=3),
                    Layout(name="progress", size=6),
                )

    def _create_header(self, snapshot: UsageSnapshot) -> Panel:
        """Create header panel.

        Args:
            snapshot: Usage snapshot

        Returns:
            Header panel
        """
        active_projects = len(snapshot.active_projects)
        active_sessions = snapshot.active_session_count
        # Use the configured timezone from snapshot
        current_time = format_datetime(snapshot.timestamp, self.time_format)

        header_text = Text()
        header_text.append(f"Active Projects: {active_projects}", style="bold #00FF00")
        header_text.append("  │  ", style="dim")
        header_text.append(f"Active Sessions: {active_sessions}", style="bold #00FFFF")
        header_text.append("\n")
        header_text.append(f"Current Time: {current_time}", style="dim")

        return Panel(
            header_text,
            title="PAR Claude Code Usage Monitor",
            border_style="#4169E1",
        )

    def _create_block_progress(self, snapshot: UsageSnapshot) -> Panel:
        """Create progress bar for current 5-hour block.

        Args:
            snapshot: Usage snapshot

        Returns:
            Block progress panel
        """
        # Get current time in the snapshot's timezone
        current_time = snapshot.timestamp

        # Find the unified block start time to show progress for
        unified_block_start = snapshot.unified_block_start_time

        if unified_block_start:
            # Use the unified block start time (most recently active session)
            block_start = unified_block_start
            # Ensure it's in the same timezone as current_time for display
            if block_start.tzinfo != current_time.tzinfo:
                block_start = block_start.astimezone(current_time.tzinfo)
        else:
            # No active blocks, show current hour block
            block_start = current_time.replace(minute=0, second=0, microsecond=0)

        block_end = block_start + timedelta(hours=5)

        # Calculate progress through the block
        elapsed = (current_time - block_start).total_seconds()
        total = (block_end - block_start).total_seconds()
        progress_percent = (elapsed / total) * 100

        # Calculate time remaining
        remaining = block_end - current_time
        hours_left = int(remaining.total_seconds() // 3600)
        minutes_left = int((remaining.total_seconds() % 3600) // 60)

        # Create progress bar
        progress = Progress(
            TextColumn("Block Progress"),
            BarColumn(bar_width=25),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn(format_time_range(block_start, block_end, self.time_format)),
            TextColumn(f"({hours_left}h {minutes_left}m left)", style="bold #FFFF00"),
            console=self.console,
            expand=False,
        )
        progress.add_task("Block", total=100, completed=int(progress_percent))

        block_info = progress

        return Panel(
            block_info,
            border_style="#0000FF",
            height=3,
        )

    def _get_model_emoji(self, model: str) -> str:
        """Get emoji for model type.

        Args:
            model: Model name

        Returns:
            Emoji string
        """
        if "opus" in model.lower():
            return "🚀"
        elif "sonnet" in model.lower():
            return "⚡"
        elif "haiku" in model.lower():
            return "💨"
        elif "claude" in model.lower():
            return "🤖"
        elif "gpt" in model.lower():
            return "🧠"
        elif "llama" in model.lower():
            return "🦙"
        else:
            return "❓"

    def _create_model_displays(
        self, model_tokens: dict[str, int], model_interruptions: dict[str, int] | None = None
    ) -> list[Text]:
        """Create model token displays.

        Args:
            model_tokens: Token count by model
            model_interruptions: Interruption count by model (optional)

        Returns:
            List of formatted model displays
        """
        model_displays: list[Text] = []
        for model, tokens in sorted(model_tokens.items()):
            display_name = get_model_display_name(model)
            emoji = self._get_model_emoji(model)

            model_text = Text()
            model_text.append(f"{emoji} {display_name:8}", style="bold")
            model_text.append(f"{format_token_count(tokens):>12}", style="#FFFF00")

            # Add interruption count if interruption data exists (always show, even if 0)
            if model_interruptions is not None:
                interruption_count = model_interruptions.get(model, 0)
                # Green for 0 interruptions (good), red for actual interruptions (warning)
                color = "#00FF00" if interruption_count == 0 else "#FF6B6B"
                model_text.append(f"  ({interruption_count} Interrupted)", style=color)

            model_displays.append(model_text)
        return model_displays

    def _get_progress_colors(self, percentage: float, total_tokens: int, base_limit: int) -> tuple[str, str]:
        """Get progress bar colors based on percentage.

        Args:
            percentage: Usage percentage
            total_tokens: Current token count
            base_limit: Base token limit

        Returns:
            Tuple of (bar_color, text_style)
        """
        # Determine color based on percentage thresholds
        if percentage >= 90:
            bar_color = "#FF0000"  # red
            text_style = "bold #FF0000"
        elif percentage >= 75:
            bar_color = "#FFA500"  # orange
            text_style = "bold #FFA500"
        elif percentage >= 50:
            bar_color = "#FFFF00"  # yellow
            text_style = "bold #FFFF00"
        else:
            bar_color = "#00FF00"  # green
            text_style = "bold"

        # Add warning color if over original limit (overrides percentage colors)
        if total_tokens > base_limit:
            text_style = "bold #FF0000"  # red

        return bar_color, text_style

    def _get_fallback_tool_data(self, snapshot: UsageSnapshot) -> tuple[dict[str, int], int]:
        """Get fallback tool data from all active blocks."""
        tool_counts = {}
        total_tool_calls = 0
        for project in snapshot.projects.values():
            for session in project.sessions.values():
                for block in session.blocks:
                    if block.is_active:
                        for tool, count in block.tool_call_counts.items():
                            tool_counts[tool] = tool_counts.get(tool, 0) + count
                        total_tool_calls += block.total_tool_calls
        return tool_counts, total_tool_calls

    def _create_progress_bars(self, snapshot: UsageSnapshot) -> Panel:
        """Create progress bars for token usage.

        Args:
            snapshot: Usage snapshot

        Returns:
            Progress panel
        """
        # Get token usage by model for unified block only
        model_tokens = snapshot.unified_block_tokens_by_model()
        total_tokens = snapshot.unified_block_tokens()
        model_interruptions = snapshot.unified_block_interruptions_by_model()

        # If no unified block data, fall back to all active tokens and models
        if not model_tokens and total_tokens == 0:
            model_tokens = snapshot.tokens_by_model()
            total_tokens = snapshot.active_tokens
            model_interruptions = snapshot.interruptions_by_model()

        # Ensure limit is at least as high as current usage
        base_limit = snapshot.total_limit or 500_000
        total_limit = max(base_limit, total_tokens)

        # Create per-model token displays (no progress bars)
        from rich.console import Group
        from rich.progress import BarColumn, Progress, TextColumn

        model_displays = self._create_model_displays(model_tokens, model_interruptions)

        # Calculate burn rate and estimated total usage
        burn_rate_text = self._calculate_burn_rate(snapshot, total_tokens, total_limit)

        # Total progress bar with color based on percentage
        percentage = (total_tokens / total_limit) * 100
        bar_color, text_style = self._get_progress_colors(percentage, total_tokens, base_limit)

        total_progress = Progress(
            TextColumn("📊 Total   ", style=text_style),
            BarColumn(bar_width=25, complete_style=bar_color, finished_style=bar_color),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn(
                f"{format_token_count(total_tokens):>8} / {format_token_count(total_limit)}",
                style=text_style,
            ),
            console=self.console,
            expand=False,
        )
        total_progress.add_task("Total", total=total_limit, completed=total_tokens)

        # Combine model displays, total progress bar, and burn rate
        all_displays = []
        if model_displays:
            all_displays.extend(model_displays)
        all_displays.extend([total_progress, burn_rate_text])

        all_progress = Group(*all_displays)

        return Panel(
            all_progress,
            title="Token Usage by Model",
            border_style="#FFFF00",
        )

    def _create_tool_usage_table(self, snapshot: UsageSnapshot) -> Table:
        """Create tool usage table with dynamic sizing and column distribution.

        Args:
            snapshot: Usage snapshot

        Returns:
            Tool usage table with optimized layout
        """
        from rich.table import Table

        # Create table for tool usage
        table = Table(
            show_header=False,
            show_lines=False,
            expand=True,
            title="Tool Use",
            border_style="#FF9900",
        )

        # Only show tool usage if enabled
        if not (self.config and self.config.display.show_tool_usage):
            table.add_column("Status", style="dim italic")
            table.add_row("Tool usage display disabled")
            return table

        # Get tool usage data
        tool_counts = snapshot.unified_block_tool_usage()
        total_tool_calls = snapshot.unified_block_total_tool_calls()

        if not tool_counts:
            # Show empty table when no tools are used
            table.add_column("Status", style="dim italic")
            table.add_row("No tool usage in current block")
            return table

        # Sort tools by usage count (highest first), then by name (case-insensitive)
        sorted_tools = sorted(tool_counts.items(), key=lambda x: (-x[1], x[0].lower()))

        # Use fixed 3-column layout
        num_tools = len(sorted_tools)
        max_rows = 8  # Maximum table height (excluding total row)
        num_cols = 3  # Always use 3 columns

        # Limit tools to fit in 3-column layout with max_rows
        max_tools = max_rows * num_cols
        if num_tools > max_tools:
            sorted_tools = sorted_tools[:max_tools]

        # Add columns based on calculated layout
        for _col in range(num_cols):
            table.add_column("Tool", style="#FF9900", no_wrap=False)
            table.add_column("Count", justify="right", style="#FFFF00", width=6)

        # Calculate tools per column for even distribution
        tools_per_col = (len(sorted_tools) + num_cols - 1) // num_cols  # Ceiling division

        # Distribute tools into columns
        tool_columns = []
        for col in range(num_cols):
            start_idx = col * tools_per_col
            end_idx = min(start_idx + tools_per_col, len(sorted_tools))
            tool_columns.append(sorted_tools[start_idx:end_idx])

        # Calculate actual number of rows needed
        actual_rows = max(len(col) for col in tool_columns) if tool_columns else 0

        # Arrange tools in rows
        for row in range(actual_rows):
            row_data = []
            for col in range(num_cols):
                if row < len(tool_columns[col]):
                    tool_name, tool_count = tool_columns[col][row]
                    row_data.extend([f"🔧 {tool_name}", f"{tool_count:,}"])
                else:
                    row_data.extend(["", ""])  # Empty cells

            table.add_row(*row_data)

        # Add total row if there are tool calls
        if total_tool_calls > 0:
            total_row = ["📊 Total", f"{total_tool_calls:,}"]
            # Fill remaining columns with empty strings
            total_row.extend([""] * ((num_cols - 1) * 2))
            table.add_row(*total_row, style="bold")

        return table

    def _calculate_tool_usage_height(self, snapshot: UsageSnapshot) -> int:
        """Calculate the optimal height for the tool usage section.

        Args:
            snapshot: Usage snapshot

        Returns:
            Height for tool usage layout (minimum 3, maximum 10)
        """
        if not (self.config and self.config.display.show_tool_usage):
            return 3  # Minimum height for disabled message

        tool_counts = snapshot.unified_block_tool_usage()

        if not tool_counts:
            return 3  # Minimum height for empty message

        num_tools = len(tool_counts)
        max_table_rows = 8  # Maximum data rows
        num_cols = 3  # Fixed 3-column layout

        # Calculate actual rows needed for 3-column layout
        tools_per_col = (num_tools + num_cols - 1) // num_cols
        actual_rows = min(tools_per_col, max_table_rows)

        # Add space for table borders and total row
        # Top border: 1, Data rows: actual_rows, Total row: 1, Bottom border: 1
        return min(actual_rows + 4, 10)  # Cap at 10 total height (8 data rows + 2 overhead)

    def _calculate_burn_rate(self, snapshot: UsageSnapshot, total_tokens: int, total_limit: int) -> Text:
        """Calculate burn rate and estimated total usage.

        Args:
            snapshot: Usage snapshot
            total_tokens: Current total token usage
            total_limit: Token limit

        Returns:
            Formatted text with burn rate and estimate
        """
        # Get unified block start time
        block_start = snapshot.unified_block_start_time
        if not block_start:
            return Text("No active block", style="dim")

        # Calculate elapsed time
        elapsed_seconds = (snapshot.timestamp - block_start).total_seconds()
        elapsed_minutes = elapsed_seconds / 60

        # Avoid division by zero
        if elapsed_minutes < 0.1:  # Less than 6 seconds
            return Text("Burn rate: calculating...", style="dim")

        # Calculate burn rate (tokens per minute)
        burn_rate_per_minute = total_tokens / elapsed_minutes

        # Calculate burn rate per hour for estimation
        burn_rate_per_hour = burn_rate_per_minute * 60

        # Calculate estimated total usage for the full 5-hour block
        estimated_total = burn_rate_per_hour * 5.0

        # Calculate ETA to token limit
        remaining_tokens = total_limit - total_tokens
        eta_display, eta_before_block_end = self._calculate_eta_display(
            snapshot, total_tokens, total_limit, burn_rate_per_minute
        )

        # Determine color based on percentage of limit
        percentage = (estimated_total / total_limit) * 100
        if percentage >= 100:
            color = "bold #FF0000"  # red
        elif percentage >= 95:
            color = "bold #FFA500"  # orange
        else:
            color = "bold #00FF00"  # green

        # Format the display
        burn_rate_text = Text()
        burn_rate_text.append("🔥 Burn    ", style="bold")
        burn_rate_text.append(f"{format_token_count(int(burn_rate_per_minute)):>8}/m", style="#00FFFF")
        burn_rate_text.append("  Est: ", style="dim")
        burn_rate_text.append(f"{format_token_count(int(estimated_total)):>8}", style=color)
        burn_rate_text.append(f" ({percentage:>3.0f}%)", style=color)

        # Add time until limit
        if remaining_tokens > 0:
            burn_rate_text.append("  ETA: ", style="dim")
            if burn_rate_per_minute > 0:
                # Color ETA red if it's before block end (urgent), otherwise cyan (less urgent)
                eta_style = "#FF0000" if eta_before_block_end else "#00FFFF"
                burn_rate_text.append(eta_display, style=eta_style)
            else:
                burn_rate_text.append("∞", style="#00FF00")

        return burn_rate_text

    def _calculate_eta_display(
        self, snapshot: UsageSnapshot, total_tokens: int, total_limit: int, burn_rate_per_minute: float
    ) -> tuple[str, bool]:
        """Calculate ETA display string with block end time capping.

        Returns:
            Tuple of (display_string, eta_before_block_end)
        """
        remaining_tokens = total_limit - total_tokens
        if burn_rate_per_minute <= 0 or remaining_tokens <= 0:
            return "N/A", False

        minutes_until_limit = remaining_tokens / burn_rate_per_minute

        # Calculate actual time when limit will be reached
        eta_time = snapshot.timestamp + timedelta(minutes=minutes_until_limit)

        # Check if ETA is before block end time (for styling purposes)
        block_end_time = snapshot.unified_block_end_time
        eta_before_block_end = False

        if block_end_time:
            # ETA is before block end if it's less than the block end time
            eta_before_block_end = eta_time < block_end_time

        # Format time remaining and actual time
        total_minutes = int(minutes_until_limit)
        hours = total_minutes // 60
        minutes = total_minutes % 60

        if hours > 0:
            time_remaining = f"{hours}h {minutes}m"
        else:
            time_remaining = f"{minutes}m"

        # Format ETA time based on display settings
        if self.time_format == "12h":
            eta_clock = eta_time.strftime("%I:%M %p")
        else:
            eta_clock = eta_time.strftime("%H:%M")

        # Combine duration and clock time
        return f"{time_remaining} ({eta_clock})", eta_before_block_end

    def _create_sessions_table(self, snapshot: UsageSnapshot) -> Panel:
        """Create active sessions table.

        Args:
            snapshot: Usage snapshot

        Returns:
            Sessions panel
        """
        table = Table(
            title=None,
            show_header=True,
            header_style="bold #FF00FF",
            show_lines=False,
            expand=False,
        )

        # Get unified block start time
        unified_start = snapshot.unified_block_start_time

        if self.config.display.aggregate_by_project:
            self._populate_project_table(table, snapshot, unified_start)
        else:
            self._populate_session_table(table, snapshot, unified_start)

        # Add empty row if no data
        self._add_empty_row_if_needed(table)

        # Set title based on aggregation mode
        title = self._get_table_title()

        return Panel(
            table,
            title=title,
            border_style="#00FF00",
        )

    def _populate_project_table(self, table: Table, snapshot: UsageSnapshot, unified_start: datetime | None) -> None:
        """Populate table with project aggregated data."""
        table.add_column("Project", style="#00FFFF")
        table.add_column("Model", style="green")
        table.add_column("Tokens", style="#FFFF00", justify="right")
        if self.config.display.show_tool_usage:
            table.add_column("Tools", style="#FF9900", justify="center")

        # Collect project data
        active_projects: list[tuple[Project, int, set[str], datetime | None, set[str], int]] = []
        for project in snapshot.active_projects:
            project_tokens = project.get_unified_block_tokens(unified_start)
            project_models = project.get_unified_block_models(unified_start)
            project_latest_activity = project.get_unified_block_latest_activity(unified_start)
            project_tools = (
                project.get_unified_block_tools(unified_start) if self.config.display.show_tool_usage else set()
            )
            project_tool_calls = (
                project.get_unified_block_tool_calls(unified_start) if self.config.display.show_tool_usage else 0
            )

            if project_tokens > 0:
                active_projects.append(
                    (
                        project,
                        project_tokens,
                        project_models,
                        project_latest_activity,
                        project_tools,
                        project_tool_calls,
                    )
                )

        # Sort projects by latest activity time (newest first)
        from datetime import datetime
        from zoneinfo import ZoneInfo

        utc = ZoneInfo("UTC")
        active_projects.sort(key=lambda x: x[3] if x[3] is not None else datetime.min.replace(tzinfo=utc), reverse=True)

        # Add rows for sorted projects
        for project, project_tokens, project_models, _, project_tools, project_tool_calls in active_projects:
            # Display models used
            from .token_calculator import get_model_display_name

            model_display = ", ".join(sorted({get_model_display_name(m) for m in project_models}))

            # Prepare tool display
            if self.config.display.show_tool_usage:
                if project_tools:
                    # Show tools and call count
                    tool_display = f"{', '.join(sorted(project_tools, key=str.lower))} ({project_tool_calls})"
                else:
                    tool_display = "-"

                table.add_row(
                    self._strip_project_name(project.name),
                    model_display,
                    format_token_count(project_tokens),
                    tool_display,
                )
            else:
                table.add_row(
                    self._strip_project_name(project.name),
                    model_display,
                    format_token_count(project_tokens),
                )

    def _populate_session_table(self, table: Table, snapshot: UsageSnapshot, unified_start: datetime | None) -> None:
        """Populate table with session data."""
        table.add_column("Project", style="#00FFFF")
        table.add_column("Session ID", style="dim")
        table.add_column("Model", style="green")
        table.add_column("Tokens", style="#FFFF00", justify="right")
        if self.config.display.show_tool_usage:
            table.add_column("Tools", style="#FF9900", justify="center")

        # Collect all active sessions with their data
        active_sessions: list[tuple[Project, Session, int, set[str], datetime | None, set[str], int]] = []
        for project in snapshot.active_projects:
            for session in project.active_sessions:
                session_data = self._calculate_session_data(session, unified_start)
                if session_data[0] > 0:  # session_tokens > 0
                    active_sessions.append((project, session, *session_data))

        # Sort sessions by latest activity time (newest first)
        from datetime import datetime
        from zoneinfo import ZoneInfo

        utc = ZoneInfo("UTC")
        active_sessions.sort(key=lambda x: x[4] if x[4] is not None else datetime.min.replace(tzinfo=utc), reverse=True)

        # Add rows for sorted sessions
        for project, session, session_tokens, session_models, _, session_tools, session_tool_calls in active_sessions:
            # Display models used
            from .token_calculator import get_model_display_name

            model_display = ", ".join(sorted({get_model_display_name(m) for m in session_models}))

            # Prepare tool display if needed
            if self.config.display.show_tool_usage:
                if session_tools:
                    # Show tools and call count
                    tool_display = f"{', '.join(sorted(session_tools, key=str.lower))} ({session_tool_calls})"
                else:
                    tool_display = "-"

                table.add_row(
                    self._strip_project_name(project.name),
                    session.session_id,
                    model_display,
                    format_token_count(session_tokens),
                    tool_display,
                )
            else:
                table.add_row(
                    self._strip_project_name(project.name),
                    session.session_id,
                    model_display,
                    format_token_count(session_tokens),
                )

    def _calculate_session_data(
        self, session: Session, unified_start: datetime | None
    ) -> tuple[int, set[str], datetime | None, set[str], int]:
        """Calculate session tokens, models, latest activity, tools, and tool calls."""
        session_tokens = 0
        session_models: set[str] = set()
        session_latest_activity = None
        session_tools: set[str] = set()
        session_tool_calls = 0

        for block in session.blocks:
            # Show any session with activity within the current unified block time window
            include_block = self._should_include_block(block, unified_start)

            if include_block:
                session_tokens += block.adjusted_tokens
                session_models.update(block.models_used)
                session_tools.update(block.tools_used)
                session_tool_calls += block.total_tool_calls
                # Track the latest activity time for this session (for sorting)
                latest_time = block.actual_end_time or block.start_time
                if session_latest_activity is None or latest_time > session_latest_activity:
                    session_latest_activity = latest_time

        return session_tokens, session_models, session_latest_activity, session_tools, session_tool_calls

    def _should_include_block(self, block: Any, unified_start: datetime | None) -> bool:
        """Determine if a block should be included based on unified block time window."""
        if not block.is_active:
            return False

        if unified_start is None:
            # No unified block, show all active blocks
            return True

        # Check if block has activity within the unified block time window
        from datetime import timedelta

        unified_end = unified_start + timedelta(hours=5)

        # Block is included if it overlaps with the unified block time window
        block_end = block.actual_end_time or block.end_time
        return (
            block.start_time < unified_end  # Block starts before unified block ends
            and block_end > unified_start  # Block ends after unified block starts
        )

    def _add_empty_row_if_needed(self, table: Table) -> None:
        """Add empty row if no data in table."""
        if table.row_count == 0:
            if self.config.display.aggregate_by_project:
                if self.config.display.show_tool_usage:
                    table.add_row(
                        "[dim italic]No active projects[/]",
                        "",
                        "",
                        "",
                    )
                else:
                    table.add_row(
                        "[dim italic]No active projects[/]",
                        "",
                        "",
                    )
            else:
                if self.config.display.show_tool_usage:
                    table.add_row(
                        "[dim italic]No active sessions[/]",
                        "",
                        "",
                        "",
                        "",
                    )
                else:
                    table.add_row(
                        "[dim italic]No active sessions[/]",
                        "",
                        "",
                        "",
                    )

    def _get_table_title(self) -> str:
        """Get the appropriate table title based on aggregation mode."""
        if self.config.display.aggregate_by_project:
            return "Projects with Activity in Current Block"
        else:
            return "Sessions with Activity in Current Block"

    def update(self, snapshot: UsageSnapshot) -> None:
        """Update the display with new data.

        Args:
            snapshot: Usage snapshot
        """
        self.layout["header"].update(self._create_header(snapshot))
        self.layout["block_progress"].update(self._create_block_progress(snapshot))
        self.layout["progress"].update(self._create_progress_bars(snapshot))
        # Update tool usage with dynamic height only if tool usage is enabled
        if self.show_tool_usage:
            tool_usage_height = self._calculate_tool_usage_height(snapshot)
            self.layout["tool_usage"].size = tool_usage_height
            self.layout["tool_usage"].update(self._create_tool_usage_table(snapshot))
        if self.show_sessions:
            self.layout["sessions"].update(self._create_sessions_table(snapshot))

    def render(self) -> Layout:
        """Get the renderable layout.

        Returns:
            Layout to render
        """
        return self.layout


class DisplayManager:
    """Manage the live display."""

    def __init__(
        self,
        console: Console | None = None,
        refresh_interval: float = 1.0,
        update_in_place: bool = True,
        show_sessions: bool = False,
        time_format: str = "24h",
        config: Any = None,
    ) -> None:
        """Initialize display manager.

        Args:
            console: Rich console instance
            refresh_interval: Refresh interval in seconds
            update_in_place: Whether to update in place
            show_sessions: Whether to show the sessions panel
            time_format: Time format ('12h' or '24h')
            config: Configuration object
        """
        self.console = console or Console()
        self.refresh_interval = refresh_interval
        self.update_in_place = update_in_place
        self.display = MonitorDisplay(self.console, show_sessions, time_format, config)
        self.live: Live | None = None

    def start(self) -> None:
        """Start the live display."""
        if self.update_in_place:
            self.live = Live(
                self.display.render(),
                console=self.console,
                refresh_per_second=1 / self.refresh_interval,
                transient=False,
            )
            self.live.start()

    def stop(self) -> None:
        """Stop the live display."""
        if self.live:
            self.live.stop()
            self.live = None

    def update(self, snapshot: UsageSnapshot) -> None:
        """Update the display with new data.

        Args:
            snapshot: Usage snapshot
        """
        self.display.update(snapshot)

        if self.update_in_place and self.live:
            self.live.update(self.display.render())
        else:
            self.console.clear()
            self.console.print(self.display.render())

    def __enter__(self) -> DisplayManager:
        """Enter context manager."""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        self.stop()


def create_error_display(error_message: str) -> Panel:
    """Create an error display panel.

    Args:
        error_message: Error message to display

    Returns:
        Error panel
    """
    return Panel(
        Text(error_message, style="bold red"),
        title="Error",
        border_style="#FF0000",
        expand=False,
    )


def create_info_display(info_message: str) -> Panel:
    """Create an info display panel.

    Args:
        info_message: Info message to display

    Returns:
        Info panel
    """
    return Panel(
        Text(info_message, style="bold #0000FF"),
        title="Info",
        border_style="#0000FF",
        expand=False,
    )
