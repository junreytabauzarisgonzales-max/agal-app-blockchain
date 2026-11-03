import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../core/auth/auth_controller.dart';
import '../../core/models/enums.dart';
import '../../core/routes/app_routes.dart';
import '../shared/agal_widgets.dart';
import 'widgets/theme_mode_picker.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Settings')),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        AgalSurface(
          padding: const EdgeInsets.symmetric(vertical: 10),
          child: Column(
            children: [
              _row(
                Icons.lock_outline,
                'Account & security',
                Routes.accountSettings,
              ),
              Obx(
                () => SwitchListTile(
                  secondary: const Icon(Icons.fingerprint),
                  title: const Text('Biometric login'),
                  subtitle: const Text(
                    'Unlock your saved session on this device',
                    style: TextStyle(fontSize: 11),
                  ),
                  value: Get.find<AuthController>().biometricLogin.value,
                  onChanged: (enabled) async {
                    try {
                      await Get.find<AuthController>().setBiometricLogin(
                        enabled,
                      );
                    } catch (e) {
                      if (context.mounted)
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(
                              e is StateError
                                  ? e.message
                                  : 'Biometric authentication is unavailable.',
                            ),
                          ),
                        );
                    }
                  },
                ),
              ),
              _row(
                Icons.privacy_tip_outlined,
                'Privacy & data',
                Routes.privacy,
              ),
              ListTile(
                leading: const Icon(Icons.language_outlined),
                title: const Text('Language'),
                trailing: const Text('English', style: TextStyle(fontSize: 12)),
                onTap: () => showDialog<void>(
                  context: context,
                  builder: (_) => const AlertDialog(
                    title: Text('Language'),
                    content: Text(
                      'English is the currently available language.',
                    ),
                  ),
                ),
              ),
              const ThemeModePicker(),
              if (Get.find<AuthController>().session.value?.role ==
                  UserRole.farmer) ...[
                _row(
                  Icons.cloud_sync_outlined,
                  'Offline & sync management',
                  Routes.syncManagement,
                ),
                const ListTile(
                  leading: Icon(Icons.offline_pin_outlined),
                  title: Text('Offline harvests'),
                  subtitle: Text('Always saved on this device'),
                  trailing: Icon(Icons.check_circle, color: Color(0xFF087960)),
                ),
              ],
              const Divider(indent: 16, endIndent: 16),
              _row(Icons.info_outline, 'About Agal', Routes.about),
              _row(Icons.description_outlined, 'Terms of use', Routes.terms),
              _row(Icons.help_outline, 'Help & support', Routes.help),
              ListTile(
                leading: const Icon(Icons.gavel_outlined),
                title: const Text('Open-source licenses'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () =>
                    showLicensePage(context: context, applicationName: 'Agal'),
              ),
            ],
          ),
        ),
      ],
    ),
  );
  Widget _row(IconData icon, String title, String route) => ListTile(
    leading: Icon(icon, size: 21),
    title: Text(title, style: const TextStyle(fontSize: 14)),
    trailing: const Icon(Icons.chevron_right, size: 19),
    onTap: () => Get.toNamed(route),
  );
}
