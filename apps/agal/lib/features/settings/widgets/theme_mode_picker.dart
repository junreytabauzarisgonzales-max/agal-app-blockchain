import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../core/theme/theme_controller.dart';

class ThemeModePicker extends StatelessWidget {
  const ThemeModePicker({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.find<ThemeController>();

    return Obx(
      () => ListTile(
        leading: const Icon(Icons.dark_mode_outlined),
        title: const Text('Theme'),
        subtitle: Text(_label(controller.themeMode.value)),
        trailing: SegmentedButton<ThemeMode>(
          segments: const [
            ButtonSegment(
              value: ThemeMode.system,
              icon: Icon(Icons.brightness_auto, size: 18),
            ),
            ButtonSegment(
              value: ThemeMode.light,
              icon: Icon(Icons.light_mode_outlined, size: 18),
            ),
            ButtonSegment(
              value: ThemeMode.dark,
              icon: Icon(Icons.dark_mode_outlined, size: 18),
            ),
          ],
          selected: {controller.themeMode.value},
          showSelectedIcon: false,
          onSelectionChanged: (selection) =>
              controller.setThemeMode(selection.first),
        ),
      ),
    );
  }

  String _label(ThemeMode mode) => switch (mode) {
    ThemeMode.system => 'Match system',
    ThemeMode.light => 'Light',
    ThemeMode.dark => 'Dark',
  };
}
