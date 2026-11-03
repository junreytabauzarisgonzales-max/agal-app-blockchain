import 'dart:convert';

import '../../core/models/enums.dart';
import '../local/database.dart';
import '../remote/agal_api_client.dart';

class SyncResult {
  final int pushed;
  final int errors;
  const SyncResult({required this.pushed, required this.errors});
  static const empty = SyncResult(pushed: 0, errors: 0);
}

/// Pushes the Farmer app's offline queues (unsynced rows in
/// `local_custody_events` and `local_messages`) to POST /sync in one
/// request. Safe to call repeatedly and concurrently-ish: the backend
/// dedupes by id, and rows are only marked synced once the server has
/// actually acknowledged them.
class SyncService {
  SyncService(this._db, this._api);
  final AppDatabase _db;
  final AgalApiClient _api;

  Future<SyncResult> syncPendingEvents(
    String farmerId, {
    String? accessToken,
  }) async {
    final pendingEvents = await _db.unsyncedEvents(farmerId);
    final pendingMessages = await _db.unsyncedMessages(farmerId);
    if (pendingEvents.isEmpty && pendingMessages.isEmpty)
      return SyncResult.empty;

    pendingEvents.sort((a, b) {
      final aCreation = a.eventType == CustodyEventType.batchCreated.value;
      final bCreation = b.eventType == CustodyEventType.batchCreated.value;
      if (aCreation != bCreation) return aCreation ? -1 : 1;
      final time = a.occurredAt.compareTo(b.occurredAt);
      return time == 0 ? a.id.compareTo(b.id) : time;
    });

    final items = [
      ...pendingEvents.map(_eventToSyncItem),
      ...pendingMessages.map(_messageToSyncItem),
    ];
    final results = await _api.sync(items, bearer: accessToken);

    final syncedIds = results
        .where((r) => r['status'] == 'created' || r['status'] == 'duplicate')
        .map((r) => r['id'] as String)
        .toSet();

    await _db.markSynced(
      pendingEvents.map((e) => e.id).where(syncedIds.contains),
    );
    await _db.markMessagesSynced(
      pendingMessages.map((m) => m.id).where(syncedIds.contains),
    );

    final errors = results.where((r) => r['status'] == 'error').length;
    return SyncResult(pushed: syncedIds.length, errors: errors);
  }

  Map<String, dynamic> _eventToSyncItem(LocalCustodyEvent event) {
    final payload = jsonDecode(event.payload) as Map<String, dynamic>;
    final occurredAt = event.occurredAt.toUtc().toIso8601String();

    if (event.eventType == CustodyEventType.batchCreated.value) {
      return {
        'type': 'batch_created',
        'id': event.id,
        'species': payload['species'],
        'estimated_weight_kg': payload['estimated_weight_kg'],
        'unit': payload['unit'],
        'harvest_latitude': payload['harvest_latitude'],
        'harvest_longitude': payload['harvest_longitude'],
        'harvested_at': occurredAt,
      };
    }

    return {
      'type': 'custody_event',
      'id': event.id,
      'batch_id': event.batchId,
      'event_type': event.eventType,
      'occurred_at': occurredAt,
      'payload': payload,
    };
  }

  Map<String, dynamic> _messageToSyncItem(LocalMessage message) {
    return {
      'type': 'message_sent',
      'id': message.id,
      'recipient_id': message.recipientId,
      'body': message.body,
      'occurred_at': message.occurredAt.toUtc().toIso8601String(),
    };
  }
}
