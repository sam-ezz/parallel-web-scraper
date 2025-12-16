import platform

def handle_key_not_found(engine_name: str, link: str,suffix:str = '_API_KEY'):
    engine_name = engine_name.upper()
    var_name = f"{engine_name}{suffix}"

    system = platform.system()

    if system == "Windows":
        instructions = (
            "Windows (Command Prompt):\n"
            f"  setx {var_name} \"your_key_here\"\n\n"
            "Windows (PowerShell):\n"
            f"  setx {var_name} \"your_key_here\"\n"
        )
    elif system in ("Linux", "Darwin"):
        instructions = (
            "Linux / macOS:\n"
            f"  export {var_name}=your_key_here\n"
        )
    else:
        instructions = (
            "Set the environment variable in your system shell:\n"
            f"  {var_name}=your_key_here\n"
        )

    raise RuntimeError(
        f"{engine_name} API key not found.\n\n"
        f"Set it using:\n\n"
        f"{instructions}\n"
        f"Documentation:\n"
        f"{link}"
        f"\nIf you get this error even after setting environment variable close the terminal and open it again"
    )