import logging
import os
import sys
from pathlib import Path

from PySide6.QtCore import QObject, QSettings, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

# Assuming the core logic is in a function that can be imported
from geminiteacher.app.generate_course import create_course_with_progressive_save

# --- Worker and Logging Handler for Thread-Safe Operations ---

class QtLogHandler(logging.Handler):
    """A logging handler that emits a Qt signal for each log record."""
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def emit(self, record):
        msg = self.format(record)
        self.parent.log_message.emit(msg)

class Worker(QObject):
    """
    A worker object that runs a long-running task in a separate thread.
    """
    finished = Signal()
    progress = Signal(int)
    log_message = Signal(str)
    error = Signal(str)

    def __init__(self, params: dict):
        super().__init__()
        self.params = params

    @Slot()
    def run(self):
        """Execute the course generation task."""
        try:
            # --- Logging Setup ---
            # We will capture ALL logs and warnings and route them to the GUI.
            # 1. Capture warnings (like deprecation warnings) into the logging system.
            logging.captureWarnings(True)
            
            # 2. Get the root logger, which sees all logs from all modules.
            root_logger = logging.getLogger()
            
            # 3. Add our custom GUI handler to the root logger.
            gui_handler = QtLogHandler(self)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
            gui_handler.setFormatter(formatter)
            
            # Avoid adding the handler multiple times if the function is re-run
            if not any(isinstance(h, QtLogHandler) for h in root_logger.handlers):
                root_logger.addHandler(gui_handler)

            # 4. Set the root logger's level based on the verbose checkbox.
            log_level = logging.DEBUG if self.params.get('verbose') else logging.INFO
            root_logger.setLevel(log_level)
            
            # The core function can still get its own named logger, which will propagate to the root.
            self.params['logger'] = logging.getLogger("geminiteacher.app")
            
            # --- End Logging Setup ---

            self.log_message.emit("Starting course generation...")
            create_course_with_progressive_save(**self.params)
            self.log_message.emit("Course generation finished successfully.")

        except Exception as e:
            self.error.emit(f"An error occurred: {e}")
        finally:
            self.finished.emit()


# --- Main Application Window ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeminiTeacher GUI")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # UI Elements
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        # Load previous settings (API key is not saved for security)
        self.load_settings()

    def create_widgets(self):
        """Create all the input widgets for the GUI."""
        # API Key
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Paste your Google API Key here")

        # Model Selection
        self.model_edit = QLineEdit("gemini-2.5-flash")

        # File/Folder Paths
        self.input_file_edit = QLineEdit()
        self.input_file_btn = QPushButton("Browse...")
        self.output_dir_edit = QLineEdit()
        self.output_dir_btn = QPushButton("Browse...")
        self.custom_prompt_edit = QLineEdit()
        self.custom_prompt_btn = QPushButton("Browse...")

        # Course Settings
        self.title_edit = QLineEdit("My Awesome Course")
        self.max_chapters_spin = QSpinBox(minimum=1, maximum=100, value=10)
        self.fixed_chapter_check = QCheckBox("Generate Exact Number of Chapters")

        # Generation Settings
        self.temperature_spin = QDoubleSpinBox(minimum=0.0, maximum=1.0, value=0.2, singleStep=0.1)
        
        # Parallel Settings
        self.parallel_check = QCheckBox("Enable Parallel Processing")
        self.max_workers_spin = QSpinBox(minimum=1, maximum=32, value=4)
        self.delay_min_spin = QDoubleSpinBox(minimum=0.0, maximum=10.0, value=0.2, singleStep=0.1)
        self.delay_max_spin = QDoubleSpinBox(minimum=0.0, maximum=10.0, value=0.8, singleStep=0.1)
        self.max_retries_spin = QSpinBox(minimum=0, maximum=10, value=3)

        # Other controls
        self.verbose_check = QCheckBox("Enable Verbose Logging")
        self.generate_btn = QPushButton("Generate Course")
        self.progress_bar = QProgressBar()
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)

    def create_layout(self):
        """Assemble widgets into a layout."""
        form_layout = QFormLayout()
        form_layout.addRow("Google API Key:", self.api_key_edit)
        form_layout.addRow("Model:", self.model_edit)
        form_layout.addRow("Input File:", self.create_file_input(self.input_file_edit, self.input_file_btn))
        form_layout.addRow("Output Directory:", self.create_file_input(self.output_dir_edit, self.output_dir_btn, is_folder=True))
        form_layout.addRow("Custom Prompt File:", self.create_file_input(self.custom_prompt_edit, self.custom_prompt_btn))
        form_layout.addRow("Course Title:", self.title_edit)
        form_layout.addRow("Max Chapters:", self.max_chapters_spin)
        form_layout.addRow(self.fixed_chapter_check)
        form_layout.addRow("Temperature:", self.temperature_spin)
        
        # Parallel processing group
        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.parallel_check)
        parallel_layout = QFormLayout()
        parallel_layout.addRow("Max Workers:", self.max_workers_spin)
        parallel_layout.addRow("Min Delay (s):", self.delay_min_spin)
        parallel_layout.addRow("Max Delay (s):", self.delay_max_spin)
        parallel_layout.addRow("Max Retries:", self.max_retries_spin)
        self.layout.addLayout(parallel_layout)

        self.layout.addWidget(self.verbose_check)
        self.layout.addWidget(self.generate_btn)
        self.layout.addWidget(QLabel("Progress:"))
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(QLabel("Logs:"))
        self.layout.addWidget(self.log_box)

    def create_file_input(self, line_edit, button, is_folder=False):
        """Helper to create a line edit + browse button combo."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(line_edit)
        layout.addWidget(button)
        
        if is_folder:
            button.clicked.connect(lambda: self.browse_folder(line_edit))
        else:
            button.clicked.connect(lambda: self.browse_file(line_edit))
            
        return widget

    def create_connections(self):
        """Connect widget signals to slots."""
        self.generate_btn.clicked.connect(self.start_generation)

    def browse_file(self, line_edit):
        """Open a file dialog and set the line edit's text."""
        filepath, _ = QFileDialog.getOpenFileName(self, "Select File")
        if filepath:
            line_edit.setText(filepath)

    def browse_folder(self, line_edit):
        """Open a folder dialog."""
        folderpath = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folderpath:
            line_edit.setText(folderpath)

    def closeEvent(self, event):
        """Save settings when the application closes."""
        self.save_settings()
        super().closeEvent(event)

    def save_settings(self):
        """Save widget values to QSettings."""
        settings = QSettings("GeminiTeacher", "GUI")
        settings.setValue("apiKey", self.api_key_edit.text())
        settings.setValue("model", self.model_edit.text())
        settings.setValue("inputFile", self.input_file_edit.text())
        settings.setValue("outputDir", self.output_dir_edit.text())
        settings.setValue("customPrompt", self.custom_prompt_edit.text())
        settings.setValue("title", self.title_edit.text())
        settings.setValue("maxChapters", self.max_chapters_spin.value())
        settings.setValue("fixedChapter", self.fixed_chapter_check.isChecked())
        settings.setValue("temperature", self.temperature_spin.value())
        settings.setValue("parallel", self.parallel_check.isChecked())
        settings.setValue("maxWorkers", self.max_workers_spin.value())
        settings.setValue("delayMin", self.delay_min_spin.value())
        settings.setValue("delayMax", self.delay_max_spin.value())
        settings.setValue("maxRetries", self.max_retries_spin.value())
        settings.setValue("verbose", self.verbose_check.isChecked())
        
    def load_settings(self):
        """Load widget values from QSettings."""
        settings = QSettings("GeminiTeacher", "GUI")
        self.api_key_edit.setText(settings.value("apiKey", ""))
        self.model_edit.setText(settings.value("model", "gemini-2.5-flash"))
        self.input_file_edit.setText(settings.value("inputFile", ""))
        self.output_dir_edit.setText(settings.value("outputDir", ""))
        self.custom_prompt_edit.setText(settings.value("customPrompt", ""))
        self.title_edit.setText(settings.value("title", "My Awesome Course"))
        self.max_chapters_spin.setValue(int(settings.value("maxChapters", 10)))
        self.fixed_chapter_check.setChecked(settings.value("fixedChapter", "false").lower() == 'true')
        self.temperature_spin.setValue(float(settings.value("temperature", 0.2)))
        self.parallel_check.setChecked(settings.value("parallel", "true").lower() == 'true')
        self.max_workers_spin.setValue(int(settings.value("maxWorkers", 4)))
        self.delay_min_spin.setValue(float(settings.value("delayMin", 0.2)))
        self.delay_max_spin.setValue(float(settings.value("delayMax", 0.8)))
        self.max_retries_spin.setValue(int(settings.value("maxRetries", 3)))
        self.verbose_check.setChecked(settings.value("verbose", "true").lower() == 'true')


    def start_generation(self):
        """Prepare and start the course generation in a worker thread."""
        # Set API Key from GUI if provided
        api_key = self.api_key_edit.text()
        if api_key:
            os.environ['GOOGLE_API_KEY'] = api_key
        elif 'GOOGLE_API_KEY' not in os.environ or not os.environ['GOOGLE_API_KEY']:
            self.log_box.appendPlainText("Error: No Google API Key provided. Please paste it into the API Key field or set the GOOGLE_API_KEY environment variable.")
            return

        self.generate_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_box.clear()

        # Gather parameters from the GUI to be passed to the core function.
        # The core function now handles file reading and logic.
        params = {
            "content": self.input_file_edit.text(),
            "course_title": self.title_edit.text(),
            "output_dir": self.output_dir_edit.text(),
            "temperature": self.temperature_spin.value(),
            "verbose": self.verbose_check.isChecked(),
            "max_chapters": self.max_chapters_spin.value(),
            "fixed_chapter_count": self.fixed_chapter_check.isChecked(),
            "custom_prompt": self.custom_prompt_edit.text(),
            "max_workers": self.max_workers_spin.value() if self.parallel_check.isChecked() else None,
            "delay_range": (self.delay_min_spin.value(), self.delay_max_spin.value()),
            "max_retries": self.max_retries_spin.value(),
            "model_name": self.model_edit.text(),
        }

        # Create and run the worker thread
        self.thread = QThread()
        self.worker = Worker(params)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.log_message.connect(self.log_box.appendPlainText)
        self.worker.error.connect(self.log_box.appendPlainText)
        self.worker.finished.connect(lambda: self.generate_btn.setEnabled(True))
        self.worker.finished.connect(lambda: self.progress_bar.setValue(100))

        self.thread.start() 