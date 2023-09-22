import os
import sys
import re


def exit():
    print("")
    sys.exit()


def replace_string_in_files(directory: str, search_string: str, replace_string: str):
    for filename in os.listdir(directory):
        if not os.path.isdir(os.path.join(directory, filename)):
            filepath = os.path.join(directory, filename)
            with open(filepath, mode="r", encoding="utf8") as file:
                content: str = file.read()
            content = content.replace(search_string, replace_string)
            with open(filepath, mode="w", encoding="utf8") as file:
                file.write(content)


def remove_files_in_folder(directory: str, prefix: str):
    for filename in os.listdir(directory):
        if filename.startswith(prefix):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)


print("")

if len(sys.argv) == 1:
    print("Automation option is not provided.")

elif sys.argv[1] == "bridge-gen":
    # Temporarily add `ffi` package
    # because `flutter_rust_bridge_codegen` wants it,
    # though the generated code doesn't use it.
    command = "dart pub add ffi"
    os.system(command)

    # Delete previous bridge files.
    remove_files_in_folder("./example/native/hub/src/bridge", "bridge")
    remove_files_in_folder("./lib/src", "bridge")

    # Generate bridge files.
    command = "flutter_rust_bridge_codegen"
    command += " --rust-input ./example/native/hub/src/bridge/api.rs"
    command += " --rust-output ./example/native/hub/src/bridge/bridge_generated.rs"
    command += " --dart-output ./lib/src/bridge_generated.dart"
    command += " --dart-decl-output ./lib/src/bridge_definitions.dart"
    command += " --class-name Bridge"
    command += " --wasm"
    os.system(command)

    # Remove an unnecessary root import.
    filepath = "./example/native/hub/src/lib.rs"
    with open(filepath, mode="r", encoding="utf8") as file:
        lines = file.readlines()
    for turn, line in enumerate(lines):
        if "AUTO INJECTED BY flutter_rust_bridge" in line:
            lines[turn] = ""
    with open(filepath, mode="w", encoding="utf8") as file:
        file.write("".join(lines))

    # Modify some code.
    directory_path = "./lib/src/"
    search_string = "package:flutter_rust_bridge/flutter_rust_bridge.dart"
    replace_string = "bridge_engine/exports.dart"
    replace_string_in_files(directory_path, search_string, replace_string)
    search_string = "\nimport 'package:uuid/uuid.dart';"
    replace_string = ""
    replace_string_in_files(directory_path, search_string, replace_string)
    search_string = "generated by flutter_rust_bridge"
    replace_string = "generated by flutter_rust_bridge_codegen"
    replace_string_in_files(directory_path, search_string, replace_string)
    search_string = "import 'package:meta/meta.dart';"
    replace_string = ""
    replace_string_in_files(directory_path, search_string, replace_string)
    search_string = "@protected"
    replace_string = ""
    replace_string_in_files(directory_path, search_string, replace_string)

    directory_path = "./example/native/hub/src/bridge"
    search_string = "flutter_rust_bridge::"
    replace_string = "crate::bridge::bridge_engine::"
    replace_string_in_files(directory_path, search_string, replace_string)
    search_string = "crate::bridge::api_web::"
    replace_string = "crate::bridge::api::"
    replace_string_in_files(directory_path, search_string, replace_string)
    search_string = "FLUTTER_RUST_BRIDGE_HANDLER"
    replace_string = "BRIDGE_HANDLER"
    replace_string_in_files(directory_path, search_string, replace_string)
    search_string = "Generated by `flutter_rust_bridge`"
    replace_string = "Generated by flutter_rust_bridge_codegen"
    replace_string_in_files(directory_path, search_string, replace_string)

    # Format code.
    command = "cargo clippy --fix --allow-dirty"
    os.system(command)
    command = "dart format ."
    os.system(command)

    # Remove temporarily added `ffi` package.
    command = "dart pub remove ffi"
    os.system(command)

elif sys.argv[1] == "cargokit-update":
    print("Updating CargoKit...")
    command = "git subtree pull"
    command += " --prefix cargokit"
    command += " https://github.com/irondash/cargokit.git"
    command += " main"
    command += " --squash"
    os.system(command)

else:
    print("No such option for automation is available.")

exit()
