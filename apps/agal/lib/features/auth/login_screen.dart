import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../core/auth/auth_controller.dart';
import '../../core/routes/app_routes.dart';
import '../../core/models/enums.dart';
import '../../core/theme/app_theme.dart';
import '../shared/app_logo.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _submitting = false;
  bool _obscure = true;
  UserRole _role = UserRole.farmer;
  String? _error;

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _submitting = true;
      _error = null;
    });
    try {
      await Get.find<AuthController>().login(
        _emailController.text.trim(),
        _passwordController.text,
        expectedRole: _role,
      );
    } catch (e) {
      if (mounted)
        setState(
          () => _error = e is StateError
              ? e.message
              : 'Login failed. Check your email/password and connection.',
        );
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Form(
                key: _formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Center(child: AppLogo(size: 118)),
                    const SizedBox(height: 20),
                    Text(
                      'Agal',
                      style: Theme.of(context).textTheme.headlineMedium
                          ?.copyWith(fontWeight: FontWeight.w700),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'FAIR PRICES. VERIFIED HARVESTS.\nEMPOWERING SEAWEED FARMERS\nFARM TO EXPORT.',
                      style: Theme.of(context).textTheme.bodyMedium
                          ?.copyWith(color: colors.onSurfaceVariant),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 28),
                    SegmentedButton<UserRole>(
                      segments: const [
                        ButtonSegment(
                          value: UserRole.farmer,
                          label: Text('Farmer'),
                        ),
                        ButtonSegment(
                          value: UserRole.supplier,
                          label: Text('Supplier'),
                        ),
                        ButtonSegment(
                          value: UserRole.buyer,
                          label: Text('Buyer'),
                        ),
                      ],
                      selected: {_role},
                      showSelectedIcon: false,
                      style: SegmentedButton.styleFrom(
                        selectedBackgroundColor: AgalColors.mint,
                        selectedForegroundColor: AgalColors.deep,
                        foregroundColor: Colors.white,
                      ),
                      onSelectionChanged: (v) =>
                          setState(() => _role = v.first),
                    ),
                    const SizedBox(height: 16),
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
                      obscureText: _obscure,
                      decoration: InputDecoration(
                        labelText: 'Password',
                        prefixIcon: const Icon(Icons.lock_outline),
                        suffixIcon: IconButton(
                          tooltip: _obscure ? 'Show password' : 'Hide password',
                          icon: Icon(
                            _obscure
                                ? Icons.visibility_outlined
                                : Icons.visibility_off_outlined,
                          ),
                          onPressed: () => setState(() => _obscure = !_obscure),
                        ),
                      ),
                      validator: (v) =>
                          (v == null || v.isEmpty) ? 'Required' : null,
                    ),
                    if (_error != null) ...[
                      const SizedBox(height: 12),
                      Text(_error!, style: TextStyle(color: colors.error)),
                    ],
                    const SizedBox(height: 24),
                    FilledButton(
                      onPressed: _submitting ? null : _submit,
                      child: _submitting
                          ? const SizedBox(
                              height: 16,
                              width: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Log in'),
                    ),
                    const SizedBox(height: 8),
                    OutlinedButton(
                      onPressed: () => Get.toNamed(
                        Routes.register,
                        arguments: {'role': _role, 'offline': true},
                      ),
                      child: const Text('Register Offline'),
                    ),
                    TextButton(
                      onPressed: () =>
                          Get.toNamed(Routes.register, arguments: _role),
                      child: const Text('Don’t have an account? Sign up'),
                    ),
                    const SizedBox(height: 20),
                    const Text(
                      'Harvests and messages work offline after sign in.',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Color(0xFFACC8BD), fontSize: 12),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
