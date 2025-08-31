"""
Lazy loading module for ML dependencies.
This allows the application to start without heavy ML packages and install them on-demand.
"""

import os
import subprocess
import sys
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


def is_pytorch_enabled() -> bool:
    """Check if PyTorch features should be enabled."""
    return os.getenv("ENABLE_PYTORCH", "false").lower() == "true"


def is_runtime_install_enabled() -> bool:
    """Check if runtime installation of PyTorch is allowed."""
    return os.getenv("RUNTIME_INSTALL_PYTORCH", "false").lower() == "true"


def ensure_pytorch() -> bool:
    """
    Ensure PyTorch is available, installing it on-demand if needed.

    Returns:
        bool: True if PyTorch is available, False otherwise
    """
    try:
        import torch

        logger.debug("PyTorch already available")
        return True
    except ImportError:
        # If PyTorch is explicitly disabled AND runtime install is not enabled, return False
        if not is_pytorch_enabled() and not is_runtime_install_enabled():
            logger.info(
                "PyTorch disabled via ENABLE_PYTORCH=false and RUNTIME_INSTALL_PYTORCH=false"
            )
            return False

        # If runtime install is disabled, return False
        if not is_runtime_install_enabled():
            logger.warning("PyTorch not available and RUNTIME_INSTALL_PYTORCH=false")
            return False

        logger.info("Installing PyTorch CPU-only at runtime...")

        # Check available memory before installation
        try:
            import psutil

            available_memory_gb = psutil.virtual_memory().available / (1024**3)
            logger.info(f"Available memory: {available_memory_gb:.1f}GB")

            if available_memory_gb < 2.0:
                logger.warning(
                    f"Low memory ({available_memory_gb:.1f}GB) - ML installation may fail"
                )
                logger.warning("Consider using OpenAI or AWS embeddings instead")
        except ImportError:
            logger.debug("psutil not available - cannot check memory")

        # Use a unique directory for this process to avoid conflicts
        import uuid

        # Create a unique writable directory in /tmp
        unique_id = str(uuid.uuid4())[:8]
        target_dir = f"/tmp/pytorch-{unique_id}"

        try:
            os.makedirs(target_dir, mode=0o755, exist_ok=True)

            # Add target directory to Python path
            if target_dir not in sys.path:
                sys.path.insert(0, target_dir)

            # Set up environment with unique cache directories
            env = os.environ.copy()
            env["UV_CACHE_DIR"] = f"/tmp/uv-cache-{unique_id}"
            env["PIP_CACHE_DIR"] = f"/tmp/pip-cache-{unique_id}"
            env["PIP_NO_WARN_SCRIPT_LOCATION"] = "1"

            # Create cache directories
            os.makedirs(env["UV_CACHE_DIR"], mode=0o755, exist_ok=True)
            os.makedirs(env["PIP_CACHE_DIR"], mode=0o755, exist_ok=True)

            logger.info(f"Attempting uv install to {target_dir}...")
            # Reduced timeout to prevent hanging during memory pressure
            result = subprocess.run(
                [
                    "uv",
                    "pip",
                    "install",
                    "--target",
                    target_dir,
                    "torch",
                    "torchvision",
                    "--index-url",
                    "https://download.pytorch.org/whl/cpu",
                    "--no-deps",
                    "--quiet",
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=180,  # Reduced from 300 to 180 seconds
            )

            if result.returncode == 0:
                logger.info(f"PyTorch installed successfully to {target_dir}")
                # Verify installation
                import torch

                logger.info(f"PyTorch {torch.__version__} available")
                return True
            else:
                logger.warning(f"uv install failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error("PyTorch installation timed out (possible memory pressure)")
            return False
        except Exception as e:
            logger.warning(f"uv install attempt failed: {e}")

        try:
            logger.info(f"Falling back to pip install to {target_dir}...")
            result = subprocess.run(
                [
                    "/app/.venv/bin/python",
                    "-m",
                    "pip",
                    "install",
                    "--target",
                    target_dir,
                    "torch",
                    "torchvision",
                    "--index-url",
                    "https://download.pytorch.org/whl/cpu",
                    "--no-deps",
                    "--quiet",
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=180,  # Reduced timeout
            )

            if result.returncode == 0:
                logger.info(f"PyTorch installed successfully via pip to {target_dir}")
                # Verify installation
                import torch

                logger.info(f"PyTorch {torch.__version__} available")
                return True
            else:
                logger.error(f"pip install failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error("Pip installation timed out (possible memory pressure)")
            return False
        except Exception as e:
            logger.error(f"pip install failed: {e}")

        logger.error("Failed to install PyTorch via both uv and pip")
        return False


def get_sentence_transformers() -> Optional[Any]:
    """
    Lazy import of sentence-transformers with PyTorch dependency.

    Returns:
        SentenceTransformer class if available, None otherwise
    """
    if not ensure_pytorch():
        logger.warning("Cannot load sentence-transformers: PyTorch not available")
        return None

    try:
        from sentence_transformers import SentenceTransformer

        logger.debug("sentence-transformers already available")
        return SentenceTransformer
    except ImportError:
        if not is_runtime_install_enabled():
            logger.warning(
                "sentence-transformers not available and runtime install disabled"
            )
            return None

        logger.info(
            "Installing sentence-transformers with all HuggingFace dependencies..."
        )

        # Check available memory before installation
        try:
            import psutil

            available_memory_gb = psutil.virtual_memory().available / (1024**3)
            logger.info(
                f"Available memory: {available_memory_gb:.1f}GB before HuggingFace installation"
            )

            if available_memory_gb < 3.0:
                logger.warning(
                    f"Low memory ({available_memory_gb:.1f}GB) - HuggingFace installation may fail"
                )
                logger.warning("Consider using OpenAI or AWS embeddings instead")
        except ImportError:
            logger.debug("psutil not available - cannot check memory")

        # Use a shared directory for all HuggingFace packages to avoid import conflicts
        import uuid

        # Create a shared writable directory for all HuggingFace packages
        unique_id = str(uuid.uuid4())[:8]
        target_dir = f"/tmp/huggingface-all-{unique_id}"

        try:
            os.makedirs(target_dir, mode=0o755, exist_ok=True)

            # Add target directory to Python path
            if target_dir not in sys.path:
                sys.path.insert(0, target_dir)

            # Set up environment with unique cache directories
            env = os.environ.copy()
            env["UV_CACHE_DIR"] = f"/tmp/uv-cache-{unique_id}"
            env["PIP_CACHE_DIR"] = f"/tmp/pip-cache-{unique_id}"
            env["PIP_NO_WARN_SCRIPT_LOCATION"] = "1"

            # Create cache directories
            os.makedirs(env["UV_CACHE_DIR"], mode=0o755, exist_ok=True)
            os.makedirs(env["PIP_CACHE_DIR"], mode=0o755, exist_ok=True)

            # Install ALL HuggingFace dependencies together to avoid import conflicts
            logger.info(f"Installing complete HuggingFace stack to {target_dir}...")
            result = subprocess.run(
                [
                    "/app/.venv/bin/python",
                    "-m",
                    "pip",
                    "install",
                    "--target",
                    target_dir,
                    "sentence-transformers",
                    "transformers",
                    "huggingface-hub",
                    "langchain-huggingface",
                    "--quiet",
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=600,  # Longer timeout for multiple packages
            )

            if result.returncode == 0:
                logger.info("Complete HuggingFace stack installed successfully")
                from sentence_transformers import SentenceTransformer

                return SentenceTransformer
            else:
                logger.error(f"pip install failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error(
                "HuggingFace installation timed out (possible memory pressure)"
            )
            return None
        except Exception as e:
            logger.error(f"Failed to install HuggingFace stack: {e}")

        logger.error("Failed to install sentence-transformers")
        return None


def get_transformers() -> Optional[tuple]:
    """
    Lazy import of transformers library.

    Returns:
        Tuple of (AutoTokenizer, AutoModel) if available, None otherwise
    """
    if not ensure_pytorch():
        logger.warning("Cannot load transformers: PyTorch not available")
        return None

    try:
        from transformers import AutoTokenizer, AutoModel

        logger.debug("transformers already available")
        return AutoTokenizer, AutoModel
    except ImportError:
        if not is_runtime_install_enabled():
            logger.warning("transformers not available and runtime install disabled")
            return None

        logger.info("Installing transformers at runtime...")

        # Use a unique directory similar to ensure_pytorch to avoid permission conflicts
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        target_dir = f"/tmp/transformers-{unique_id}"
        try:
            os.makedirs(target_dir, mode=0o755, exist_ok=True)
            if target_dir not in sys.path:
                sys.path.insert(0, target_dir)

            env = os.environ.copy()
            env["UV_CACHE_DIR"] = f"/tmp/uv-cache-{unique_id}"
            env["PIP_CACHE_DIR"] = f"/tmp/pip-cache-{unique_id}"
            env["PIP_NO_WARN_SCRIPT_LOCATION"] = "1"
            os.makedirs(env["UV_CACHE_DIR"], mode=0o755, exist_ok=True)
            os.makedirs(env["PIP_CACHE_DIR"], mode=0o755, exist_ok=True)

            # Try uv first
            try:
                logger.info(f"Installing transformers with uv to {target_dir}...")
                result = subprocess.run(
                    [
                        "uv",
                        "pip",
                        "install",
                        "--target",
                        target_dir,
                        "transformers",
                        "huggingface-hub",
                        "--quiet",
                    ],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if result.returncode == 0:
                    from transformers import AutoTokenizer, AutoModel

                    logger.info("transformers installed successfully via uv")
                    return AutoTokenizer, AutoModel
                else:
                    logger.warning(f"uv install failed: {result.stderr}")
            except Exception as e:
                logger.warning(f"uv install attempt failed: {e}")

            # Fallback to pip
            logger.info(f"Falling back to pip for transformers to {target_dir}...")
            result = subprocess.run(
                [
                    "/app/.venv/bin/python",
                    "-m",
                    "pip",
                    "install",
                    "--target",
                    target_dir,
                    "transformers",
                    "huggingface-hub",
                    "--quiet",
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                from transformers import AutoTokenizer, AutoModel

                logger.info("transformers installed successfully via pip")
                return AutoTokenizer, AutoModel
            else:
                logger.error(f"pip install failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Failed to install transformers: {e}")
        return None


def check_ml_capabilities() -> dict:
    """
    Check what ML capabilities are available.

    Returns:
        dict: Status of available ML libraries
    """
    status = {
        "pytorch_enabled": is_pytorch_enabled(),
        "runtime_install_enabled": is_runtime_install_enabled(),
        "pytorch_available": False,
        "sentence_transformers_available": False,
        "transformers_available": False,
    }

    # Check PyTorch
    try:
        import torch

        status["pytorch_available"] = True
        status["pytorch_version"] = torch.__version__
    except ImportError:
        pass

    # Check sentence-transformers
    try:
        import sentence_transformers

        status["sentence_transformers_available"] = True
        status["sentence_transformers_version"] = sentence_transformers.__version__
    except ImportError:
        pass

    # Check transformers
    try:
        import transformers

        status["transformers_available"] = True
        status["transformers_version"] = transformers.__version__
    except ImportError:
        pass

    return status


def get_langchain_huggingface() -> Optional[Any]:
    """
    Lazy import of langchain_huggingface.HuggingFaceEmbeddings.

    Returns:
        HuggingFaceEmbeddings class if available, None otherwise
    """
    if not ensure_pytorch():
        logger.warning("Cannot load langchain_huggingface: PyTorch not available")
        return None

    try:
        from langchain_huggingface import HuggingFaceEmbeddings

        logger.debug("langchain_huggingface already available")
        return HuggingFaceEmbeddings
    except ImportError:
        if not is_runtime_install_enabled():
            logger.warning(
                "langchain_huggingface not available and runtime install disabled"
            )
            return None

        logger.info("Installing langchain_huggingface with all dependencies...")

        # Check available memory before installation
        try:
            import psutil

            available_memory_gb = psutil.virtual_memory().available / (1024**3)
            logger.info(
                f"Available memory: {available_memory_gb:.1f}GB before HuggingFace installation"
            )

            if available_memory_gb < 3.0:
                logger.warning(
                    f"Low memory ({available_memory_gb:.1f}GB) - HuggingFace installation may fail"
                )
                logger.warning("Consider using OpenAI or AWS embeddings instead")
        except ImportError:
            logger.debug("psutil not available - cannot check memory")

        # Use a shared directory for all HuggingFace packages to avoid import conflicts
        import uuid

        # Create a shared writable directory for all HuggingFace packages
        unique_id = str(uuid.uuid4())[:8]
        target_dir = f"/tmp/huggingface-all-{unique_id}"

        try:
            os.makedirs(target_dir, mode=0o755, exist_ok=True)

            # Add target directory to Python path
            if target_dir not in sys.path:
                sys.path.insert(0, target_dir)

            # Set up environment with unique cache directories
            env = os.environ.copy()
            env["UV_CACHE_DIR"] = f"/tmp/uv-cache-{unique_id}"
            env["PIP_CACHE_DIR"] = f"/tmp/pip-cache-{unique_id}"
            env["PIP_NO_WARN_SCRIPT_LOCATION"] = "1"

            # Create cache directories
            os.makedirs(env["UV_CACHE_DIR"], mode=0o755, exist_ok=True)
            os.makedirs(env["PIP_CACHE_DIR"], mode=0o755, exist_ok=True)

            # Install ALL HuggingFace dependencies together to avoid import conflicts
            logger.info(f"Installing complete HuggingFace stack to {target_dir}...")
            result = subprocess.run(
                [
                    "/app/.venv/bin/python",
                    "-m",
                    "pip",
                    "install",
                    "--target",
                    target_dir,
                    "langchain-huggingface",
                    "sentence-transformers",
                    "transformers",
                    "huggingface-hub",
                    "--quiet",
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=600,  # Longer timeout for multiple packages
            )

            if result.returncode == 0:
                logger.info("Complete HuggingFace stack installed successfully")
                from langchain_huggingface import HuggingFaceEmbeddings

                return HuggingFaceEmbeddings
            else:
                logger.error(f"pip install failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error(
                "HuggingFace installation timed out (possible memory pressure)"
            )
            return None
        except Exception as e:
            logger.error(f"Failed to install HuggingFace stack: {e}")

        logger.error("Failed to install langchain_huggingface")
        return None


def get_huggingface_pipeline() -> Optional[Any]:
    """
    Lazy import of langchain_huggingface.HuggingFacePipeline.

    Returns:
        HuggingFacePipeline class if available, None otherwise
    """
    if not ensure_pytorch():
        logger.warning("Cannot load HuggingFacePipeline: PyTorch not available")
        return None

    try:
        from langchain_huggingface import HuggingFacePipeline

        logger.debug("HuggingFacePipeline already available")
        return HuggingFacePipeline
    except ImportError:
        if not is_runtime_install_enabled():
            logger.warning(
                "HuggingFacePipeline not available and runtime install disabled"
            )
            return None

        logger.info("Installing langchain_huggingface for pipeline...")
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        target_dir = f"/tmp/langchain-hf-pipeline-{unique_id}"
        try:
            os.makedirs(target_dir, mode=0o755, exist_ok=True)
            if target_dir not in sys.path:
                sys.path.insert(0, target_dir)
            env = os.environ.copy()
            env["UV_CACHE_DIR"] = f"/tmp/uv-cache-{unique_id}"
            env["PIP_CACHE_DIR"] = f"/tmp/pip-cache-{unique_id}"
            env["PIP_NO_WARN_SCRIPT_LOCATION"] = "1"
            os.makedirs(env["UV_CACHE_DIR"], mode=0o755, exist_ok=True)
            os.makedirs(env["PIP_CACHE_DIR"], mode=0o755, exist_ok=True)

            # Directly use pip (langchain-huggingface is light)
            result = subprocess.run(
                [
                    "/app/.venv/bin/python",
                    "-m",
                    "pip",
                    "install",
                    "--target",
                    target_dir,
                    "langchain-huggingface",
                    "--quiet",
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                from langchain_huggingface import HuggingFacePipeline

                logger.info("HuggingFacePipeline installed successfully")
                return HuggingFacePipeline
            else:
                logger.error(f"pip install failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Failed to install langchain_huggingface pipeline: {e}")
        return None


def get_transformers_pipeline() -> Optional[Any]:
    """
    Lazy import of transformers.pipeline.

    Returns:
        pipeline function if available, None otherwise
    """
    if not ensure_pytorch():
        logger.warning("Cannot load transformers pipeline: PyTorch not available")
        return None

    try:
        from transformers import pipeline

        logger.debug("transformers pipeline already available")
        return pipeline
    except ImportError:
        if not is_runtime_install_enabled():
            logger.warning(
                "transformers pipeline not available and runtime install disabled"
            )
            return None

        logger.info("Installing transformers for pipeline...")
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        target_dir = f"/tmp/transformers-pipeline-{unique_id}"
        try:
            os.makedirs(target_dir, mode=0o755, exist_ok=True)
            if target_dir not in sys.path:
                sys.path.insert(0, target_dir)
            env = os.environ.copy()
            env["UV_CACHE_DIR"] = f"/tmp/uv-cache-{unique_id}"
            env["PIP_CACHE_DIR"] = f"/tmp/pip-cache-{unique_id}"
            env["PIP_NO_WARN_SCRIPT_LOCATION"] = "1"
            os.makedirs(env["UV_CACHE_DIR"], mode=0o755, exist_ok=True)
            os.makedirs(env["PIP_CACHE_DIR"], mode=0o755, exist_ok=True)
            result = subprocess.run(
                [
                    "/app/.venv/bin/python",
                    "-m",
                    "pip",
                    "install",
                    "--target",
                    target_dir,
                    "transformers",
                    "--quiet",
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                from transformers import pipeline

                logger.info("transformers pipeline installed successfully")
                return pipeline
            else:
                logger.error(f"pip install failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Failed to install transformers pipeline: {e}")
        return None


def get_transformers_model_classes() -> Optional[tuple]:
    """
    Lazy import of transformers model classes.

    Returns:
        Tuple of (AutoModelForCausalLM, AutoTokenizer) if available, None otherwise
    """
    if not ensure_pytorch():
        logger.warning("Cannot load transformers model classes: PyTorch not available")
        return None

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        logger.debug("transformers model classes already available")
        return AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        if not is_runtime_install_enabled():
            logger.warning(
                "transformers model classes not available and runtime install disabled"
            )
            return None

        logger.info("Installing transformers for model classes...")
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        target_dir = f"/tmp/transformers-model-{unique_id}"
        try:
            os.makedirs(target_dir, mode=0o755, exist_ok=True)
            if target_dir not in sys.path:
                sys.path.insert(0, target_dir)
            env = os.environ.copy()
            env["UV_CACHE_DIR"] = f"/tmp/uv-cache-{unique_id}"
            env["PIP_CACHE_DIR"] = f"/tmp/pip-cache-{unique_id}"
            env["PIP_NO_WARN_SCRIPT_LOCATION"] = "1"
            os.makedirs(env["UV_CACHE_DIR"], mode=0o755, exist_ok=True)
            os.makedirs(env["PIP_CACHE_DIR"], mode=0o755, exist_ok=True)
            result = subprocess.run(
                [
                    "/app/.venv/bin/python",
                    "-m",
                    "pip",
                    "install",
                    "--target",
                    target_dir,
                    "transformers",
                    "--quiet",
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                from transformers import AutoModelForCausalLM, AutoTokenizer

                logger.info("transformers model classes installed successfully")
                return AutoModelForCausalLM, AutoTokenizer
            else:
                logger.error(f"pip install failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Failed to install transformers model classes: {e}")
        return None
