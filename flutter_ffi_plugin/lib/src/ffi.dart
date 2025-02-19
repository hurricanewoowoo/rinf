import 'dart:io' as io;
import 'dart:ffi';
import 'bridge/generated.dart';
import 'bridge/definitions.dart';

final Bridge api = BridgeImpl(loadNativeLibrary());

DynamicLibrary loadNativeLibrary() {
  if (io.Platform.isLinux) {
    return DynamicLibrary.open('libhub.so'); // Dynamic library
  } else if (io.Platform.isAndroid) {
    return DynamicLibrary.open('libhub.so'); // Dynamic library
  } else if (io.Platform.isWindows) {
    return DynamicLibrary.open('hub.dll'); // Dynamic library
  } else if (io.Platform.isIOS) {
    return DynamicLibrary.executable(); // Static library
  } else if (io.Platform.isMacOS) {
    return DynamicLibrary.executable(); // Static library
  } else {
    return DynamicLibrary.executable(); // Dummy return value
  }
}
