import 'dart:async';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:get/get.dart';
import 'package:get_storage/get_storage.dart';

import '../../core/auth/auth_controller.dart';
import '../../core/models/enums.dart';
import '../local/database.dart';
import 'sync_service.dart';

class SyncScheduler {
  SyncScheduler(this._service, this._db, this._auth);
  final SyncService _service;
  final AppDatabase _db;
  final AuthController _auth;
  final online = true.obs;
  final syncing = false.obs;
  final pendingHarvests = 0.obs;
  final pendingMessages = 0.obs;
  final Rxn<DateTime> lastSync = Rxn<DateTime>();
  final RxnString error = RxnString();
  int get pending => pendingHarvests.value + pendingMessages.value;
  Timer? _timer;
  StreamSubscription<List<ConnectivityResult>>? _connectivitySub;
  Worker? _sessionWorker;

  void start() {
    if (_timer != null) return;
    _timer = Timer.periodic(const Duration(seconds: 30), (_) => _trigger());
    _connectivitySub = Connectivity().onConnectivityChanged.listen((results) {
      online.value = !results.contains(ConnectivityResult.none);
      if (online.value) unawaited(_trigger());
    });
    _sessionWorker = ever(_auth.session, (_) => unawaited(_trigger()));
    unawaited(_initialize());
  }

  Future<void> _initialize() async {
    try {
      final results = await Connectivity().checkConnectivity();
      online.value = !results.contains(ConnectivityResult.none);
    } catch (_) {
      /* A request still provides the definitive connectivity check. */
    }
    await _trigger();
  }

  void stop() {
    _timer?.cancel();
    _timer = null;
    _connectivitySub?.cancel();
    _connectivitySub = null;
    _sessionWorker?.dispose();
    _sessionWorker = null;
  }

  Future<void> refreshCounts() async {
    final session = _auth.session.value;
    if (session == null || session.role != UserRole.farmer) {
      pendingHarvests.value = pendingMessages.value = 0;
      lastSync.value = null;
      error.value = null;
      return;
    }
    pendingHarvests.value = (await _db.unsyncedEvents(session.userId)).length;
    pendingMessages.value = (await _db.unsyncedMessages(session.userId)).length;
    final saved = GetStorage().read<String>('last_sync_${session.userId}');
    lastSync.value = saved == null ? null : DateTime.tryParse(saved);
  }

  Future<void> syncNow() => _trigger();

  Future<void> _trigger() async {
    if (syncing.value) return;
    syncing.value = true;
    try {
      await refreshCounts();
      final session = _auth.session.value;
      if (session == null ||
          session.role != UserRole.farmer ||
          !online.value ||
          pending == 0)
        return;
      error.value = null;
      final result = await _service.syncPendingEvents(
        session.userId,
        accessToken: session.accessToken,
      );
      if (result.errors > 0) {
        error.value = '${result.errors} record(s) need another sync attempt.';
      } else if (result.pushed > 0) {
        lastSync.value = DateTime.now();
        await GetStorage().write(
          'last_sync_${session.userId}',
          lastSync.value!.toIso8601String(),
        );
      }
    } catch (_) {
      error.value = 'Could not connect. Your records are safe on this device.';
    } finally {
      await refreshCounts();
      syncing.value = false;
    }
  }
}
