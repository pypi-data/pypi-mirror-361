import subprocess
import json
from typing import Dict, Any

def render(options: Dict[str, Any]) -> bytes:
    """
    Renders a visualization using the gpt-vis-cli tool and returns the output as bytes.

    Args:
        options: A dictionary containing the visualization options.

    Returns:
        The raw bytes of the generated visualization (e.g., a PNG image).

    Raises:
        FileNotFoundError: If the 'gpt-vis-cli' executable is not found.
        subprocess.CalledProcessError: If the 'gpt-vis-cli' process returns a non-zero exit code.
    """
    json_options = json.dumps(options)

    try:
        process = subprocess.run(
            ['npx', '-y', 'gpt-vis-cli', json_options],
            capture_output=True,
            check=True,
            timeout=30
        )
        return process.stdout
    except FileNotFoundError:
        print(f"Error: The executable 'npx' was not found in the current directory.")
        raise
    except subprocess.CalledProcessError as e:
        print(f"Error executing gpt-vis-cli: {e}")
        print(f"Stderr: {e.stderr.decode()}")
        raise
    except subprocess.TimeoutExpired as e:
        print(f"Error: gpt-vis-cli timed out.")
        print(f"Stderr: {e.stderr.decode() if e.stderr else 'No stderr'}")
        raise
