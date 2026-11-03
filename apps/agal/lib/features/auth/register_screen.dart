import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../core/auth/auth_controller.dart';
import '../../core/models/enums.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _fullNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _municipalityController = TextEditingController();
  UserRole _role = UserRole.farmer;
  bool _submitting = false;
  String? _error;
  bool _offlineDraft = false;

  @override
  void initState() {
    super.initState();
    if (Get.arguments is UserRole) _role = Get.arguments as UserRole;
    if (Get.arguments is Map) {
      _role = Get.arguments['role'] as UserRole? ?? UserRole.farmer;
      _offlineDraft = Get.arguments['offline'] == true;
    }
    _restoreDraft();
  }

  Future<void> _restoreDraft() async {
    final draft = await Get.find<AuthController>().registrationDraft();
    if (draft == null || !mounted) return;
    setState(() {
      _emailController.text = draft['email'] as String? ?? '';
      _passwordController.text = draft['password'] as String? ?? '';
      _fullNameController.text = draft['full_name'] as String? ?? '';
      _phoneController.text = draft['phone_number'] as String? ?? '';
      _municipalityController.text = draft['municipality'] as String? ?? '';
      _role = UserRole.fromValue(draft['role'] as String);
    });
  }

  Future<void> _saveDraft() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _submitting = true);
    try {
      await Get.find<AuthController>().saveRegistrationDraft({
        'email': _emailController.text.trim(),
        'password': _passwordController.text,
        'full_name': _fullNameController.text.trim(),
        'phone_number': _phoneController.text.trim(),
        'municipality': _municipalityController.text.trim(),
        'role': _role.value,
      });
      if (mounted)
        setState(
          () => _error = 'Draft saved securely. Return to Sign up when connected to activate your account.',
        );
    } catch (_) {
      if (mounted)
        setState(() => _error = 'Could not save this draft. Please try again.');
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  void dispose() {
    for (final controller in [
      _emailController,
      _passwordController,
      _fullNameController,
      _phoneController,
      _municipalityController,
    ]) {
      controller.dispose();
    }
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _submitting = true;
      _error = null;
    });
    try {
      await Get.find<AuthController>().register(
        email: _emailController.text.trim(),
        password: _passwordController.text,
        fullName: _fullNameController.text.trim(),
        role: _role,
        phoneNumber: _phoneController.text.trim().isEmpty
            ? null
            : _phoneController.text.trim(),
        municipality: _municipalityController.text.trim().isEmpty
            ? null
            : _municipalityController.text.trim(),
      );
    } catch (e) {
      if (mounted)
        setState(
          () => _error = 'Registration failed. Check your connection or use a different email.',
        );
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_offlineDraft ? 'Register Offline' : 'Create account'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (_offlineDraft)
                  const Padding(
                    padding: EdgeInsets.only(bottom: 20),
                    child: Text(
                      'Create a secure registration draft without a connection. Complete sign up online to activate the account.',
                      style: TextStyle(height: 1.5),
                    ),
                  ),
                Text(
                  'I am a...',
                  style: Theme.of(context).textTheme.labelLarge,
                ),
                const SizedBox(height: 8),
                _RoleSelector(
                  value: _role,
                  onChanged: (role) => setState(() => _role = role),
                ),
                const SizedBox(height: 20),
                TextFormField(
                  controller: _fullNameController,
                  decoration: const InputDecoration(
                    labelText: 'Full name',
                    prefixIcon: Icon(Icons.person_outline),
                  ),
                  validator: (v) =>
                      (v == null || v.isEmpty) ? 'Required' : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    prefixIcon: Icon(Icons.mail_outline),
                  ),
                  validator: (v) =>
                      (v == null || v.isEmpty) ? 'Required' : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _passwordController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'Password',
                    prefixIcon: Icon(Icons.lock_outline),
                  ),
                  validator: (v) => (v == null || v.length < 6)
                      ? 'At least 6 characters'
                      : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _phoneController,
                  keyboardType: TextInputType.phone,
                  decoration: const InputDecoration(
                    labelText: 'Phone number (optional)',
                    prefixIcon: Icon(Icons.call_outlined),
                    helperText: 'Lets other Agal users reach you over SMS',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _municipalityController,
                  decoration: const InputDecoration(
                    labelText: 'Municipality (optional)',
                    prefixIcon: Icon(Icons.place_outlined),
                  ),
                ),
                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    _error!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                ],
                const SizedBox(height: 24),
                FilledButton(
                  onPressed: _submitting
                      ? null
                      : _offlineDraft
                      ? _saveDraft
                      : _submit,
                  child: _submitting
                      ? const SizedBox(
                          height: 16,
                          width: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : Text(
                          _offlineDraft
                              ? 'Save Registration Draft'
                              : 'Register',
                        ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _RoleSelector extends StatelessWidget {
  const _RoleSelector({required this.value, required this.onChanged});
  final UserRole value;
  final ValueChanged<UserRole> onChanged;

  static const _labels = {
    UserRole.farmer: 'Farmer',
    UserRole.supplier: 'Supplier / Aggregator',
    UserRole.buyer: 'Buyer / Exporter',
  };

  static const _icons = {
    UserRole.farmer: Icons.grass_rounded,
    UserRole.supplier: Icons.inventory_2_outlined,
    UserRole.buyer: Icons.storefront_outlined,
  };

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Column(
      children: UserRole.values.map((role) {
        final selected = role == value;
        return Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: InkWell(
            borderRadius: BorderRadius.circular(14),
            onTap: () => onChanged(role),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
              decoration: BoxDecoration(
                color: selected
                    ? colors.primaryContainer
                    : colors.surfaceContainerLow,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: selected ? colors.primary : colors.outlineVariant,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    _icons[role],
                    color: selected
                        ? colors.onPrimaryContainer
                        : colors.onSurfaceVariant,
                  ),
                  const SizedBox(width: 12),
                  Text(
                    _labels[role]!,
                    style: TextStyle(
                      fontWeight: selected ? FontWeight.w600 : FontWeight.w400,
                      color: selected
                          ? colors.onPrimaryContainer
                          : colors.onSurface,
                    ),
                  ),
                  const Spacer(),
                  if (selected)
                    Icon(Icons.check_circle, color: colors.primary, size: 20),
                ],
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
