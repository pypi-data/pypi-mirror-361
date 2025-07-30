# dataset_tools/background_operations.py

"""Background operations and threading utilities.

This module handles long-running operations in background threads to keep
the UI responsive. Think of it as your retainer doing tasks while you
continue adventuring! 🎒⚡
"""

from collections.abc import Callable
from typing import Any

from PyQt6 import QtCore

from .file_operations import FileOperations
from .logger import get_logger

log = get_logger(__name__)


class BackgroundTask(QtCore.QThread):
    """Base class for background tasks.

    This provides a common interface for running tasks in the background
    while keeping the UI responsive. Like having different crafting jobs
    that all follow the same basic workflow! 🔨✨
    """

    # Signals that all background tasks can emit
    progress_updated = QtCore.pyqtSignal(int)  # Progress percentage (0-100)
    status_updated = QtCore.pyqtSignal(str)  # Status message
    error_occurred = QtCore.pyqtSignal(str)  # Error message
    task_completed = QtCore.pyqtSignal(object)  # Task result

    def __init__(self, parent=None):
        """Initialize the background task."""
        super().__init__(parent)
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self._should_cancel = False
        self._task_name = self.__class__.__name__

    def cancel(self) -> None:
        """Request cancellation of the task."""
        self.logger.info(f"Cancellation requested for {self._task_name}")
        self._should_cancel = True

    @property
    def is_cancelled(self) -> bool:
        """Check if the task has been cancelled."""
        return self._should_cancel

    def emit_progress(self, percentage: int, message: str = "") -> None:
        """Emit progress update.

        Args:
            percentage: Progress percentage (0-100)
            message: Optional status message

        """
        self.progress_updated.emit(max(0, min(100, percentage)))
        if message:
            self.status_updated.emit(message)

    def emit_status(self, message: str) -> None:
        """Emit status update.

        Args:
            message: Status message

        """
        self.logger.debug(f"{self._task_name}: {message}")
        self.status_updated.emit(message)

    def emit_error(self, error_message: str) -> None:
        """Emit error message.

        Args:
            error_message: Error description

        """
        self.logger.error(f"{self._task_name} error: {error_message}")
        self.error_occurred.emit(error_message)

    def emit_result(self, result: Any) -> None:
        """Emit task completion with result.

        Args:
            result: Task result

        """
        self.logger.info(f"{self._task_name} completed successfully")
        self.task_completed.emit(result)


class FileLoaderTask(BackgroundTask):
    """Background task for loading and categorizing files from a directory.

    This replaces the old FileLoader thread with better structure,
    progress reporting, and error handling. Like upgrading from a
    basic gathering class to a specialist! 📦⚡
    """

    def __init__(self, folder_path: str, file_to_select: str | None = None, parent=None):
        """Initialize the file loader task.

        Args:
            folder_path: Path to the folder to scan
            file_to_select: Optional file to select after loading
            parent: Parent QObject

        """
        super().__init__(parent)
        self.folder_path = folder_path
        self.file_to_select = file_to_select
        self.file_operations = FileOperations()
        self._task_name = "FileLoader"

    def run(self) -> None:
        """Run the file loading task."""
        try:
            self.emit_status(f"Starting scan of directory: {self.folder_path}")
            self.emit_progress(0, "Preparing to scan...")

            # Check if we should cancel before starting
            if self.is_cancelled:
                self.emit_status("Task cancelled before starting")
                return

            self.emit_progress(10, "Scanning directory...")

            # Perform the actual scan
            result = self.file_operations.scan_folder(self.folder_path)

            # Check for cancellation after scan
            if self.is_cancelled:
                self.emit_status("Task cancelled after scan")
                return

            if not result.scan_success:
                error_msg = result.error_message or "Unknown scan error"
                self.emit_error(f"Scan failed: {error_msg}")
                return

            self.emit_progress(90, "Finalizing results...")

            # Create the final result with selection info
            final_result = FileLoaderResult(
                images=result.images,
                texts=result.texts,
                models=result.models,
                folder_path=result.folder_path,
                file_to_select=self.file_to_select,
                total_files=result.total_files,
                scan_duration=result.scan_duration,
            )

            self.emit_progress(100, "Scan completed!")
            self.emit_result(final_result)

        except Exception as e:
            self.emit_error(f"Unexpected error during file loading: {e!s}")


class FileLoaderResult:
    """Result from the file loader task.

    This contains all the information about loaded files, with additional
    metadata about the loading process.
    """

    def __init__(
        self,
        images: list[str],
        texts: list[str],
        models: list[str],
        folder_path: str,
        file_to_select: str | None = None,
        total_files: int = 0,
        scan_duration: float = 0.0,
    ):
        """Initialize the file loader result."""
        self.images = images
        self.texts = texts
        self.models = models
        self.folder_path = folder_path
        self.file_to_select = file_to_select
        self.total_files = total_files
        self.scan_duration = scan_duration

    @property
    def all_files(self) -> list[str]:
        """Get all files combined."""
        return self.images + self.texts + self.models

    @property
    def file_counts(self) -> dict[str, int]:
        """Get file counts by category."""
        return {
            "images": len(self.images),
            "texts": len(self.texts),
            "models": len(self.models),
            "total": self.total_files,
        }

    def has_file(self, filename: str) -> bool:
        """Check if a specific file was found."""
        return filename in self.all_files

    def get_category_for_file(self, filename: str) -> str | None:
        """Get the category for a specific file."""
        if filename in self.images:
            return "image"
        if filename in self.texts:
            return "text"
        if filename in self.models:
            return "model"
        return None


class MetadataLoaderTask(BackgroundTask):
    """Background task for loading metadata from multiple files.

    This can be used for batch metadata operations without blocking
    the UI. Like having a retainer process multiple items while you
    do other things! 📜⚡
    """

    def __init__(self, file_paths: list[str], metadata_loader: Callable[[str], Any], parent=None):
        """Initialize the metadata loader task.

        Args:
            file_paths: List of file paths to process
            metadata_loader: Function to load metadata from a file path
            parent: Parent QObject

        """
        super().__init__(parent)
        self.file_paths = file_paths
        self.metadata_loader = metadata_loader
        self._task_name = "MetadataLoader"

    def run(self) -> None:
        """Run the metadata loading task."""
        try:
            total_files = len(self.file_paths)
            if total_files == 0:
                self.emit_result({})
                return

            self.emit_status(f"Loading metadata for {total_files} files...")
            results = {}

            for i, file_path in enumerate(self.file_paths):
                if self.is_cancelled:
                    self.emit_status("Metadata loading cancelled")
                    return

                try:
                    progress = int((i / total_files) * 100)
                    self.emit_progress(
                        progress,
                        f"Processing {i + 1}/{total_files}: {Path(file_path).name}",
                    )

                    metadata = self.metadata_loader(file_path)
                    results[file_path] = metadata

                except Exception as e:
                    self.logger.warning(f"Error loading metadata for {file_path}: {e}")
                    results[file_path] = {"error": str(e)}

            self.emit_progress(100, "Metadata loading completed!")
            self.emit_result(results)

        except Exception as e:
            self.emit_error(f"Unexpected error during metadata loading: {e!s}")


class TaskManager(QtCore.QObject):
    """Manages multiple background tasks.

    This provides a central place to coordinate background operations,
    handle cancellation, and track progress. Like your party list
    in FFXIV showing everyone's status! 👥⚡
    """

    # Signals for overall task management
    all_tasks_completed = QtCore.pyqtSignal()
    task_count_changed = QtCore.pyqtSignal(int)  # Number of active tasks

    def __init__(self, parent=None):
        """Initialize the task manager."""
        super().__init__(parent)
        self.logger = get_logger(f"{__name__}.TaskManager")
        self.active_tasks: dict[str, BackgroundTask] = {}
        self._task_counter = 0

    def start_task(self, task: BackgroundTask, task_id: str | None = None) -> str:
        """Start a background task.

        Args:
            task: The task to start
            task_id: Optional custom task ID

        Returns:
            Task ID for tracking

        """
        if task_id is None:
            self._task_counter += 1
            task_id = f"task_{self._task_counter}"

        # Connect task signals
        task.task_completed.connect(lambda result: self._on_task_completed(task_id, result))
        task.error_occurred.connect(lambda error: self._on_task_error(task_id, error))
        task.finished.connect(lambda: self._cleanup_task(task_id))

        # Start the task
        self.active_tasks[task_id] = task
        task.start()

        self.logger.info(f"Started task {task_id}: {task.__class__.__name__}")
        self.task_count_changed.emit(len(self.active_tasks))

        return task_id

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a specific task.

        Args:
            task_id: ID of the task to cancel

        Returns:
            True if task was found and cancelled

        """
        task = self.active_tasks.get(task_id)
        if task:
            task.cancel()
            self.logger.info(f"Cancelled task {task_id}")
            return True
        return False

    def cancel_all_tasks(self) -> None:
        """Cancel all active tasks."""
        for task_id, task in self.active_tasks.items():
            task.cancel()
            self.logger.info(f"Cancelled task {task_id}")

    def get_active_task_count(self) -> int:
        """Get the number of active tasks."""
        return len(self.active_tasks)

    def is_task_active(self, task_id: str) -> bool:
        """Check if a specific task is still active."""
        return task_id in self.active_tasks

    def _on_task_completed(self, task_id: str, result: Any) -> None:
        """Handle task completion."""
        self.logger.info(f"Task {task_id} completed successfully")
        # The task will be cleaned up when finished signal is emitted

    def _on_task_error(self, task_id: str, error: str) -> None:
        """Handle task error."""
        self.logger.error(f"Task {task_id} failed with error: {error}")
        # The task will be cleaned up when finished signal is emitted

    def _cleanup_task(self, task_id: str) -> None:
        """Clean up a finished task."""
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
            self.logger.debug(f"Cleaned up task {task_id}")

            self.task_count_changed.emit(len(self.active_tasks))

            # Check if all tasks are done
            if len(self.active_tasks) == 0:
                self.all_tasks_completed.emit()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def load_files_in_background(
    folder_path: str,
    file_to_select: str | None = None,
    progress_callback: Callable[[int, str], None] | None = None,
    completion_callback: Callable[[FileLoaderResult], None] | None = None,
    error_callback: Callable[[str], None] | None = None,
    parent: QtCore.QObject | None = None,
) -> FileLoaderTask:
    """Convenience function to start file loading in background.

    Args:
        folder_path: Path to folder to scan
        file_to_select: Optional file to select after loading
        progress_callback: Optional progress callback (percentage, message)
        completion_callback: Optional completion callback
        error_callback: Optional error callback
        parent: Parent QObject for the task

    Returns:
        The FileLoaderTask instance

    """
    task = FileLoaderTask(folder_path, file_to_select, parent)

    # Connect callbacks if provided
    if progress_callback:
        task.progress_updated.connect(lambda p: progress_callback(p, ""))
        task.status_updated.connect(lambda s: progress_callback(-1, s))

    if completion_callback:
        task.task_completed.connect(completion_callback)

    if error_callback:
        task.error_occurred.connect(error_callback)

    # Start the task
    task.start()
    return task


def load_metadata_in_background(
    file_paths: list[str],
    metadata_loader: Callable[[str], Any],
    progress_callback: Callable[[int, str], None] | None = None,
    completion_callback: Callable[[dict], None] | None = None,
    error_callback: Callable[[str], None] | None = None,
    parent: QtCore.QObject | None = None,
) -> MetadataLoaderTask:
    """Convenience function to start metadata loading in background.

    Args:
        file_paths: List of file paths to process
        metadata_loader: Function to load metadata from a file path
        progress_callback: Optional progress callback (percentage, message)
        completion_callback: Optional completion callback
        error_callback: Optional error callback
        parent: Parent QObject for the task

    Returns:
        The MetadataLoaderTask instance

    """
    task = MetadataLoaderTask(file_paths, metadata_loader, parent)

    # Connect callbacks if provided
    if progress_callback:
        task.progress_updated.connect(lambda p: progress_callback(p, ""))
        task.status_updated.connect(lambda s: progress_callback(-1, s))

    if completion_callback:
        task.task_completed.connect(completion_callback)

    if error_callback:
        task.error_occurred.connect(error_callback)

    # Start the task
    task.start()
    return task


# ============================================================================
# TESTING UTILITIES
# ============================================================================


def test_background_operations():
    """Test the background operations system."""
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    logger = get_logger("BackgroundOperationsTest")

    logger.info("Testing background operations...")

    # Test task manager
    manager = TaskManager()

    def on_progress(percentage: int, message: str):
        if percentage >= 0:
            logger.info(f"Progress: {percentage}% - {message}")
        else:
            logger.info(f"Status: {message}")

    def on_completion(result: FileLoaderResult):
        logger.info(f"Completed! Found {len(result.all_files)} files")
        logger.info(f"Counts: {result.file_counts}")
        app.quit()

    def on_error(error: str):
        logger.error(f"Error: {error}")
        app.quit()

    # Test with current directory
    import os

    test_path = os.getcwd()

    task = load_files_in_background(
        test_path,
        progress_callback=on_progress,
        completion_callback=on_completion,
        error_callback=on_error,
    )

    task_id = manager.start_task(task, "test_file_load")
    logger.info(f"Started test task: {task_id}")

    # Run for a bit to see results
    QtCore.QTimer.singleShot(10000, app.quit)  # Auto-quit after 10 seconds
    app.exec()

    logger.info("Background operations test completed!")


if __name__ == "__main__":
    # Run tests if module is executed directly
    test_background_operations()
