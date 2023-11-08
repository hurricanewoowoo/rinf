import os
import sys


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
    print("Use `python automate --help` to see all available operations.")

elif sys.argv[1] == "bridge-gen":
    # You must install `flutter_rust_bridge_codegen` version 1.80
    # with `cargo install flutter_rust_bridge_codegen --version ~1.80`

    # Temporarily add some packages
    # because `flutter_rust_bridge_codegen` wants it.
    os.chdir("./flutter_ffi_plugin/")
    command = "dart pub add ffi:'^2.0.1'"
    os.system(command)
    command = "dart pub add dev:ffigen:'^8.0.0'"
    os.system(command)
    os.chdir("../")

    # Delete previous bridge files.
    remove_files_in_folder(
        "./flutter_ffi_plugin/example/native/hub/src/bridge", "bridge"
    )
    remove_files_in_folder("./flutter_ffi_plugin/lib/src/bridge", "bridge")

    # Generate bridge files.
    command = "flutter_rust_bridge_codegen"
    command += (
        " --rust-input ./flutter_ffi_plugin/example/native/hub/src/bridge/interface.rs"
    )
    command += (
        " --rust-output ./flutter_ffi_plugin/example/native/hub/src/bridge/generated.rs"
    )
    command += " --dart-output ./flutter_ffi_plugin/lib/src/bridge/generated.dart"
    command += (
        " --dart-decl-output ./flutter_ffi_plugin/lib/src/bridge/definitions.dart"
    )
    command += " --class-name Bridge"
    command += " --wasm"
    os.system(command)

    # Remove an unnecessary root import.
    filepath = "./flutter_ffi_plugin/example/native/hub/src/lib.rs"
    with open(filepath, mode="r", encoding="utf8") as file:
        lines = file.readlines()
    for turn, line in enumerate(lines):
        if "AUTO INJECTED BY flutter_rust_bridge" in line:
            lines[turn] = ""
    with open(filepath, mode="w", encoding="utf8") as file:
        file.write("".join(lines))

    # Modify some code.
    directory_path = "./flutter_ffi_plugin/lib/src/bridge"
    search_string = "package:flutter_rust_bridge/flutter_rust_bridge.dart"
    replace_string = "../engine/exports.dart"
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
    search_string = "@internal"
    replace_string = ""
    replace_string_in_files(directory_path, search_string, replace_string)

    directory_path = "./flutter_ffi_plugin/example/native/hub/src/bridge"
    search_string = "flutter_rust_bridge::"
    replace_string = "rinf::engine::"
    replace_string_in_files(directory_path, search_string, replace_string)
    search_string = "FLUTTER_RUST_BRIDGE_HANDLER"
    replace_string = "BRIDGE_HANDLER"
    replace_string_in_files(directory_path, search_string, replace_string)
    search_string = "Generated by `flutter_rust_bridge`"
    replace_string = "Generated by flutter_rust_bridge_codegen"
    replace_string_in_files(directory_path, search_string, replace_string)
    search_string = "js_sys::"
    replace_string = "rinf::dependencies::js_sys::"
    replace_string_in_files(directory_path, search_string, replace_string)

    # Format code.
    command = "dart format ."
    os.system(command)
    command = "cargo fmt"
    os.system(command)
    command = "cargo clippy --fix --allow-dirty"
    os.system(command)

    # Remove temporarily added packages.
    os.chdir("./flutter_ffi_plugin/")
    command = "dart pub remove ffi"
    os.system(command)
    command = "dart pub remove ffigen"
    os.system(command)
    os.chdir("../")

elif sys.argv[1] == "cargokit-update":
    print("Updating CargoKit...")
    command = "git subtree pull"
    command += " --prefix flutter_ffi_plugin/cargokit"
    command += " https://github.com/irondash/cargokit.git"
    command += " main"
    os.system(command)

elif sys.argv[1] == "create-test-app":
    filepath = ".gitignore"
    with open(filepath, mode="r", encoding="utf8") as file:
        content: str = file.read()
    content += "\n/test_app/"
    with open(filepath, mode="w", encoding="utf8") as file:
        file.write(content)

    command = "flutter create test_app"
    os.system(command)

    os.chdir("./test_app/")

    command = "dart pub add \"rinf:{'path':'../flutter_ffi_plugin'}\""
    os.system(command)
    command = "rinf template"
    os.system(command)

    os.remove("Cargo.toml")

    os.chdir("../")

    filepath = "Cargo.toml"
    with open(filepath, mode="r", encoding="utf8") as file:
        content: str = file.read()
    content = content.replace(
        "flutter_ffi_plugin/example/native/*",
        "test_app/native/*",
    )
    with open(filepath, mode="w", encoding="utf8") as file:
        file.write(content)

elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
    print("Usage: python automate [arguments]")
    print("Arguments:")
    print("  -h, --help        Shows this usage information.")
    print("  bridge-gen        Generates bridge files.")
    print("  cargokit-update   Updates CargoKit.")
    print("  create-test-app   Creates a temporary test app.")

else:
    print("No such option for automation is available.")
    print("Use `python automate --help` to see all available operations.")

exit()
