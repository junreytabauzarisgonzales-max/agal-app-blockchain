import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:get_storage/get_storage.dart';

const _themeModeKey = 'theme_mode';

class ThemeController extends GetxController {
  final _box = GetStorage();
  final Rx<ThemeMode> themeMode = ThemeMode.dark.obs;

  @override
  void onInit() {
    super.onInit();
    final stored = _box.read<String>(_themeModeKey);
    themeMode.value = ThemeMode.values.firstWhere(
      (m) => m.name == stored,
      orElse: () => ThemeMode.dark,
    );
  }

  void setThemeMode(ThemeMode mode) {
    themeMode.value = mode;
    Get.changeThemeMode(mode);
    _box.write(_themeModeKey, mode.name);
  }
}
