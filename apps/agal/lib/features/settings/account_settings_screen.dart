import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../core/auth/auth_controller.dart';
import '../shared/agal_widgets.dart';

class AccountSettingsScreen extends StatefulWidget {
  const AccountSettingsScreen({super.key});

  @override
  State<AccountSettingsScreen> createState() => _AccountSettingsScreenState();
}

class _AccountSettingsScreenState extends State<AccountSettingsScreen> {
  late final TextEditingController _fullNameController;
  late final TextEditingController _phoneController;
  late final TextEditingController _municipalityController;
  bool _saving = false;
  String? _message;

  @override
  void initState() {
    super.initState();
    final session = Get.find<AuthController>().session.value!;
    _fullNameController = TextEditingController(text: session.fullName);
    _phoneController = TextEditingController(text: session.phoneNumber ?? '');
    _municipalityController = TextEditingController(
      text: session.municipality ?? '',
    );
  }

  Future<void> _save() async {
    if (_fullNameController.text.trim().isEmpty) {
      setState(() => _message = 'Please enter your full name.');
      return;
    }
    setState(() {
      _saving = true;
      _message = null;
    });
    try {
      await Get.find<AuthController>().updateProfile(
        fullName: _fullNameController.text.trim(),
        phoneNumber: _phoneController.text.trim().isEmpty
            ? ''
            : _phoneController.text.trim(),
        municipality: _municipalityController.text.trim().isEmpty
            ? ''
            : _municipalityController.text.trim(),
      );
      if (mounted) setState(() => _message = 'Saved.');
    } catch (_) {
      if (mounted)
        setState(
          () => _message =
              'Could not save changes. Check your connection and try again.',
        );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  void dispose() {
    _fullNameController.dispose();
    _phoneController.dispose();
    _municipalityController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final session = Get.find<AuthController>().session.value!;

    return Scaffold(
      appBar: AppBar(title: const Text('Account')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: AgalSurface(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TextFormField(
                  initialValue: session.email,
                  enabled: false,
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    prefixIcon: Icon(Icons.mail_outline),
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _fullNameController,
                  decoration: const InputDecoration(
                    labelText: 'Full name',
                    prefixIcon: Icon(Icons.person_outline),
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _phoneController,
                  keyboardType: TextInputType.phone,
                  decoration: const InputDecoration(
                    labelText: 'Phone number',
                    prefixIcon: Icon(Icons.call_outlined),
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _municipalityController,
                  decoration: const InputDecoration(
                    labelText: 'Municipality',
                    prefixIcon: Icon(Icons.place_outlined),
                  ),
                ),
                if (_message != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    _message!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                ],
                const SizedBox(height: 24),
                FilledButton(
                  onPressed: _saving ? null : _save,
                  child: _saving
                      ? const SizedBox(
                          height: 16,
                          width: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Save changes'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
