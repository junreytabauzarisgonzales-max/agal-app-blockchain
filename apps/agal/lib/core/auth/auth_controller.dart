import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:get/get.dart';
import 'package:local_auth/local_auth.dart';

import '../../data/remote/agal_api_client.dart';
import '../models/enums.dart';
import '../routes/app_routes.dart';
import 'session.dart';

const _sessionStorageKey = 'agal_session';

class AuthController extends GetxController {
  AuthController(this._storage);
  final FlutterSecureStorage _storage;

  final Rx<Session?> session = Rx<Session?>(null);
  final RxBool isLoading = RxBool(true);
  final RxBool biometricLogin = false.obs;

  /// Called once from main() and awaited *before* runApp, so the very
  /// first frame (and the router's auth middleware) already knows whether
  /// there's a logged-in session -- no splash screen needed to hide the
  /// gap while secure storage is read.
  Future<void> loadSession() async {
    biometricLogin.value =
        await _storage.read(key: 'biometric_login') == 'true';
    final raw = await _storage.read(key: _sessionStorageKey);
    if (raw != null && biometricLogin.value) {
      try {
        if (!await LocalAuthentication().authenticate(
          localizedReason: 'Unlock your Agal account',
          biometricOnly: true,
        )) {
          isLoading.value = false;
          return;
        }
      } catch (_) {
        isLoading.value = false;
        return;
      }
    }
    session.value = raw == null
        ? null
        : Session.fromJson(jsonDecode(raw) as Map<String, dynamic>);
    isLoading.value = false;
  }

  Future<void> setBiometricLogin(bool enabled) async {
    if (enabled) {
      final authentication = LocalAuthentication();
      if (!await authentication.isDeviceSupported() ||
          (await authentication.getAvailableBiometrics()).isEmpty) {
        throw StateError(
          'Set up fingerprint or face unlock in your device settings first.',
        );
      }
      if (!await authentication.authenticate(
        localizedReason: 'Enable biometric sign in for Agal',
        biometricOnly: true,
      ))
        return;
    }
    await _storage.write(key: 'biometric_login', value: '$enabled');
    biometricLogin.value = enabled;
  }

  Future<void> saveRegistrationDraft(Map<String, dynamic> values) =>
      _storage.write(key: 'registration_draft', value: jsonEncode(values));
  Future<Map<String, dynamic>?> registrationDraft() async {
    final raw = await _storage.read(key: 'registration_draft');
    return raw == null ? null : jsonDecode(raw) as Map<String, dynamic>;
  }

  Future<void> login(
    String email,
    String password, {
    UserRole? expectedRole,
  }) async {
    final api = Get.find<AgalApiClient>();
    final token = await api.login(email, password);
    final me = await api.meWithBearer(token);
    final newSession = _sessionFromMe(me, token);
    if (expectedRole != null && newSession.role != expectedRole) {
      throw StateError(
        'This is a ${newSession.role.value} account. Select that role to sign in.',
      );
    }
    await _persist(newSession);
    session.value = newSession;
    // Get.offAllNamed clears the *entire* navigation stack before landing
    // on the new role's home -- without this, a previous role's screens
    // (e.g. Supplier's) can still be sitting underneath in the stack and
    // resurface later, and login would otherwise never navigate anywhere
    // at all (GetX's route middleware only re-runs on navigation, not
    // reactively when `session` changes on its own).
    Get.offAllNamed(Routes.homeFor(newSession.role));
  }

  Future<void> register({
    required String email,
    required String password,
    required String fullName,
    required UserRole role,
    String? phoneNumber,
    String? municipality,
  }) async {
    final api = Get.find<AgalApiClient>();
    await api.register(
      email: email,
      password: password,
      fullName: fullName,
      role: role.value,
      phoneNumber: phoneNumber,
      municipality: municipality,
    );
    await _storage.delete(key: 'registration_draft');
    await login(email, password);
  }

  Future<void> updateProfile({
    String? fullName,
    String? phoneNumber,
    String? municipality,
  }) async {
    final api = Get.find<AgalApiClient>();
    final me = await api.updateMe(
      fullName: fullName,
      phoneNumber: phoneNumber,
      municipality: municipality,
    );
    final current = session.value;
    if (current == null) return;
    final updated = _sessionFromMe(me, current.accessToken);
    await _persist(updated);
    session.value = updated;
  }

  Future<void> logout() async {
    await _storage.delete(key: _sessionStorageKey);
    session.value = null;
    // Same reasoning as login(): clear the stack and force navigation to
    // /login, rather than leaving whatever screen called logout() on
    // screen with a now-null session (Settings, for one, renders blank
    // once session is null).
    Get.offAllNamed(Routes.login);
  }

  Session _sessionFromMe(Map<String, dynamic> me, String token) {
    return Session(
      userId: me['id'] as String,
      email: me['email'] as String,
      fullName: me['full_name'] as String,
      role: UserRole.fromValue(me['role'] as String),
      phoneNumber: me['phone_number'] as String?,
      municipality: me['municipality'] as String?,
      accessToken: token,
    );
  }

  Future<void> _persist(Session value) async {
    await _storage.write(
      key: _sessionStorageKey,
      value: jsonEncode(value.toJson()),
    );
  }
}
