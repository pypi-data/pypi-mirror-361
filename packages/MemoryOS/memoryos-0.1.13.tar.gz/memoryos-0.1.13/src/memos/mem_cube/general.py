import os

from memos.configs.mem_cube import GeneralMemCubeConfig
from memos.configs.utils import get_json_file_model_schema
from memos.exceptions import ConfigurationError, MemCubeError
from memos.log import get_logger
from memos.mem_cube.base import BaseMemCube
from memos.mem_cube.utils import download_repo
from memos.memories.activation.base import BaseActMemory
from memos.memories.factory import MemoryFactory
from memos.memories.parametric.base import BaseParaMemory
from memos.memories.textual.base import BaseTextMemory


logger = get_logger(__name__)


class GeneralMemCube(BaseMemCube):
    """MemCube is a box for loading and dumping three types of memories."""

    def __init__(self, config: GeneralMemCubeConfig):
        """Initialize the MemCube with a configuration."""
        self.config = config
        self._text_mem: BaseTextMemory | None = (
            MemoryFactory.from_config(config.text_mem)
            if config.text_mem.backend != "uninitialized"
            else None
        )
        self._act_mem: BaseActMemory | None = (
            MemoryFactory.from_config(config.act_mem)
            if config.act_mem.backend != "uninitialized"
            else None
        )
        self._para_mem: BaseParaMemory | None = (
            MemoryFactory.from_config(config.para_mem)
            if config.para_mem.backend != "uninitialized"
            else None
        )

    def load(self, dir: str) -> None:
        """Load memories.
        Args:
            dir (str): The directory containing the memory files.
        """
        loaded_schema = get_json_file_model_schema(os.path.join(dir, self.config.config_filename))
        if loaded_schema != self.config.model_schema:
            raise ConfigurationError(
                f"Configuration schema mismatch. Expected {self.config.model_schema}, "
                f"but found {loaded_schema}."
            )
        self.text_mem.load(dir) if self.text_mem else None
        self.act_mem.load(dir) if self.act_mem else None
        self.para_mem.load(dir) if self.para_mem else None

        logger.info(f"MemCube loaded successfully from {dir}")

    def dump(self, dir: str) -> None:
        """Dump memories.
        Args:
            dir (str): The directory where the memory files will be saved.
        """
        if os.path.exists(dir) and os.listdir(dir):
            raise MemCubeError(
                f"Directory {dir} is not empty. Please provide an empty directory for dumping."
            )

        self.config.to_json_file(os.path.join(dir, self.config.config_filename))
        self.text_mem.dump(dir) if self.text_mem else None
        self.act_mem.dump(dir) if self.act_mem else None
        self.para_mem.dump(dir) if self.para_mem else None

        logger.info(f"MemCube dumped successfully to {dir}")

    @staticmethod
    def init_from_dir(dir: str) -> "GeneralMemCube":
        """Create a MemCube instance from a MemCube directory.

        Args:
            dir (str): The directory containing the memory files.

        Returns:
            MemCube: An instance of MemCube loaded with memories from the specified directory.
        """
        config_path = os.path.join(dir, "config.json")
        config = GeneralMemCubeConfig.from_json_file(config_path)
        mem_cube = GeneralMemCube(config)
        mem_cube.load(dir)
        return mem_cube

    @staticmethod
    def init_from_remote_repo(
        cube_id: str, base_url: str = "https://huggingface.co/datasets"
    ) -> "GeneralMemCube":
        """Create a MemCube instance from a remote repository.

        Args:
            repo (str): The repository name.
            base_url (str): The base URL of the remote repository.

        Returns:
            MemCube: An instance of MemCube loaded with memories from the specified remote repository.
        """
        dir = download_repo(cube_id, base_url)
        return GeneralMemCube.init_from_dir(dir)

    @property
    def text_mem(self) -> "BaseTextMemory | None":
        """Get the textual memory."""
        if self._text_mem is None:
            logger.warning("Textual memory is not initialized. Returning None.")
        return self._text_mem

    @text_mem.setter
    def text_mem(self, value: BaseTextMemory) -> None:
        """Set the textual memory."""
        if not isinstance(value, BaseTextMemory):
            raise TypeError(f"Expected BaseTextMemory, got {type(value).__name__}")
        self._text_mem = value

    @property
    def act_mem(self) -> "BaseActMemory | None":
        """Get the activation memory."""
        if self._act_mem is None:
            logger.warning("Activation memory is not initialized. Returning None.")
        return self._act_mem

    @act_mem.setter
    def act_mem(self, value: BaseActMemory) -> None:
        """Set the activation memory."""
        if not isinstance(value, BaseActMemory):
            raise TypeError(f"Expected BaseActMemory, got {type(value).__name__}")
        self._act_mem = value

    @property
    def para_mem(self) -> "BaseParaMemory | None":
        """Get the parametric memory."""
        if self._para_mem is None:
            logger.warning("Parametric memory is not initialized. Returning None.")
        return self._para_mem

    @para_mem.setter
    def para_mem(self, value: BaseParaMemory) -> None:
        """Set the parametric memory."""
        if not isinstance(value, BaseParaMemory):
            raise TypeError(f"Expected BaseParaMemory, got {type(value).__name__}")
        self._para_mem = value
