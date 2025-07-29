#!/usr/bin/env python
import subprocess
import sys
import json

def main():
    if len(sys.argv) != 3:
        print("Usage: python gpt-vis.py <json_options> <output_path>")
        sys.exit(1)

    json_options = sys.argv[1]
    output_path = sys.argv[2]

    try:
        # Validate JSON
        json.loads(json_options)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON provided: {e}")
        sys.exit(1)

    try:
        process = subprocess.run(
            ['npx', '-y', 'gpt-vis-cli', json_options],
            capture_output=True,
            check=True
        )
        with open(output_path, 'wb') as f:
            f.write(process.stdout)
        print(f"Visualization saved to {output_path}")
    except FileNotFoundError:
        print("Error: npx command not found. Please ensure Node.js and npm are installed and in your PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error executing gpt-vis-cli: {e}")
        print(f"Stderr: {e.stderr.decode()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
