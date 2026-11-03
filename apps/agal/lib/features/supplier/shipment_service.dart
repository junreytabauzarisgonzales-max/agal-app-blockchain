import 'package:get_storage/get_storage.dart';
import 'package:uuid/uuid.dart';

import '../../data/remote/agal_api_client.dart';

/// A shipment is a local manifest whose membership is published as immutable
/// note events through the existing API. It does not imply custody transfer.
class ShipmentService {
  ShipmentService(this._api, {GetStorage? storage}) : _storage = storage;
  final AgalApiClient _api;
  final GetStorage? _storage;
  final Map<String, List<Map<String, dynamic>>> _memory = {};
  List<Map<String, dynamic>> list(String userId) {
    final saved = _storage?.read<List<dynamic>>('shipments_$userId');
    return saved == null
        ? List.of(_memory[userId] ?? [])
        : saved.map((v) => Map<String, dynamic>.from(v as Map)).toList();
  }

  Future<void> _save(String userId, List<Map<String, dynamic>> records) async {
    _memory[userId] = records;
    await _storage?.write('shipments_$userId', records);
  }

  Future<Map<String, dynamic>> draft(
    String userId,
    String destination,
    List<Map<String, dynamic>> batches,
  ) async {
    final id = const Uuid().v4();
    final manifest = <String, dynamic>{
      'id': id,
      'destination': destination,
      'created_at': DateTime.now().toIso8601String(),
      'batch_ids': batches.map((b) => b['id']).toList(),
      'total_weight_kg': batches.fold<double>(
        0,
        (s, b) => s + (double.tryParse('${b['estimated_weight_kg']}') ?? 0),
      ),
      'status': 'draft',
      'event_ids': {for (final b in batches) '${b['id']}': const Uuid().v4()},
    };
    await _save(userId, [manifest, ...list(userId)]);
    return manifest;
  }

  Future<void> publish(String userId, Map<String, dynamic> manifest) async {
    final ids = manifest['batch_ids'] as List;
    for (final id in ids) {
      await _api.createCustodyEvent({
        'id': (manifest['event_ids'] as Map)[id],
        'batch_id': id,
        'event_type': 'note_added',
        'occurred_at': manifest['created_at'],
        'payload': {
          'notes': 'Bundled into shipment ${manifest['id']}',
          'shipment_id': manifest['id'],
          'destination': manifest['destination'],
          'shipment_batch_ids': ids,
          'shipment_weight_kg': manifest['total_weight_kg'],
        },
      });
    }
    final records = list(userId);
    final index = records.indexWhere((r) => r['id'] == manifest['id']);
    if (index >= 0) records[index] = {...manifest, 'status': 'recorded'};
    await _save(userId, records);
  }
}
