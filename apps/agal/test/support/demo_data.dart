import 'package:dio/dio.dart';
import 'package:agal/data/remote/agal_api_client.dart';

const farmerId = '11111111-1111-4111-8111-111111111111';
const traderId = '22222222-2222-4222-8222-222222222222';
const exporterId = '33333333-3333-4333-8333-333333333333';
const batchId = '204a0100-0000-4000-8000-000000000001';
const batchTwoId = '198b0200-0000-4000-8000-000000000002';
const batchThreeId = '190c0300-0000-4000-8000-000000000003';

class DemoApi extends AgalApiClient {
  DemoApi() : super(Dio());
  final writes = <Map<String, dynamic>>[];
  final people = <Map<String, dynamic>>[
    {'id': farmerId, 'full_name': 'Junrey Gonzales', 'role': 'farmer', 'municipality': 'Bongao, Tawi-Tawi', 'phone_number': '+639170000001'},
    {'id': traderId, 'full_name': 'Hamsya Igasan', 'role': 'supplier', 'municipality': 'Bongao, Tawi-Tawi', 'phone_number': '+639170000002'},
    {'id': exporterId, 'full_name': 'Krishane Ann Remonde', 'role': 'buyer', 'municipality': 'Zamboanga City', 'phone_number': '+639170000003'},
  ];
  List<Map<String, dynamic>> get batches => [
    _batch(batchId, 'Eucheuma Cottonii (Sakol)', 180),
    _batch(batchTwoId, 'Kappaphycus Alvarezii (Tambalang)', 220),
    _batch(batchThreeId, 'Eucheuma Cottonii (Sakol)', 150),
  ];
  Map<String, dynamic> _batch(String id, String species, int weight) => {
    'id': id, 'farmer_id': farmerId, 'species': species, 'estimated_weight_kg': '$weight', 'unit': 'kg',
    'harvested_at': '2026-11-01T08:21:00+08:00', 'status': 'with_supplier', 'current_holder_id': traderId,
    'harvest_latitude': null, 'harvest_longitude': null,
  };
  @override
  Future<List<Map<String, dynamic>>> listBatches({String? farmerId, String? holderId, String? status}) async => batches.where((b) =>
    (farmerId == null || b['farmer_id'] == farmerId) && (holderId == null || b['current_holder_id'] == holderId) && (status == null || b['status'] == status)).toList();
  @override
  Future<Map<String, dynamic>> getBatch(String id) async => batches.firstWhere((b) => b['id'] == id);
  @override
  Future<List<Map<String, dynamic>>> listDirectory({String? role}) async => people.where((p) => role == null || p['role'] == role).toList();
  @override
  Future<Map<String, dynamic>> getUser(String id) async => people.firstWhere((p) => p['id'] == id);
  @override
  Future<List<Map<String, dynamic>>> listPrices({String? species, String? municipality}) async => [
    {'id': 'price-1', 'species': 'Eucheuma Cottonii (Sakol)', 'price_per_kg': '55.00', 'currency': 'PHP', 'grade': 'Premium dried',
      'municipality': 'Bongao', 'effective_date': DateTime.now().toIso8601String().substring(0, 10), 'notes': 'Buying offer from Hamsya Igasan · Moisture at or below 35%.'},
    {'id': 'price-2', 'species': 'Kappaphycus Alvarezii (Tambalang)', 'price_per_kg': '58.00', 'currency': 'PHP', 'grade': 'Good dried',
      'municipality': 'Simunul', 'effective_date': DateTime.now().toIso8601String().substring(0, 10), 'notes': 'Buying offer from Krishane Ann Remonde · Final grade on receipt.'},
  ];
  @override
  Future<List<Map<String, dynamic>>> listThreads() async => [
    {'counterpart_id': traderId, 'counterpart_name': 'Hamsya Igasan', 'counterpart_role': 'supplier', 'unread_count': 2,
      'last_message_body': 'Please confirm your pickup location.', 'last_message_at': '2026-11-03T09:15:00+08:00'},
  ];
  @override
  Future<List<Map<String, dynamic>>> getConversation(String counterpartId) async => [
    {'id': 'message-1', 'sender_id': traderId, 'body': 'Good morning, Junrey! We can pick up your 180 kg Cottonii batch today.', 'occurred_at': '2026-11-03T09:00:00+08:00'},
    {'id': 'message-2', 'sender_id': farmerId, 'body': 'Thank you, Hamsya. The harvest is ready for pickup.', 'occurred_at': '2026-11-03T09:05:00+08:00'},
    {'id': 'message-3', 'sender_id': traderId, 'body': 'Please confirm the exact location so our driver can find you.', 'occurred_at': '2026-11-03T09:15:00+08:00'},
  ];
  @override
  Future<void> markConversationRead(String counterpartId) async {}
  @override
  Future<List<Map<String, dynamic>>> getBatchEvents(String id) async {
    Map<String, dynamic> event(int n, String type, String actor, String role, String time, [Map<String, dynamic>? payload]) => {
      'id': '$id-event-$n', 'batch_id': id, 'event_type': type, 'actor_id': actor, 'actor_role': role,
      'occurred_at': time, 'payload': payload ?? {}, 'on_chain_status': 'anchored',
      'on_chain_tx_hash': '0x42a2f5e100000000000000000000000000000000000000000000000000008d7c9',
    };
    return [
      event(1, 'batch_created', farmerId, 'farmer', '2026-11-01T08:21:00+08:00', {'notes': 'Harvested in Bongao, Tawi-Tawi'}),
      event(2, 'drying_completed', farmerId, 'farmer', '2026-11-02T10:10:00+08:00'),
      event(3, 'quality_graded', traderId, 'supplier', '2026-11-03T09:20:00+08:00', {'quality_grade': 'excellent', 'moisture_percent': 22, 'verified_weight_kg': 175}),
      event(4, 'transferred_to_supplier', traderId, 'supplier', '2026-11-03T09:30:00+08:00'),
      event(5, 'payment_recorded', traderId, 'supplier', '2026-11-03T10:00:00+08:00', {'amount_php': id == batchId ? 30250 : 19000}),
      event(6, 'note_added', traderId, 'supplier', '2026-11-03T10:30:00+08:00', {'notes': 'Shipment AG-1103 · Destination: Krishane Ann Remonde, Zamboanga warehouse'}),
    ];
  }
  @override
  Future<Map<String, dynamic>> verifyCustodyEvent(String id) async => {'event_id': id, 'verified': true, 'on_chain_exists': true};
  @override
  Future<Map<String, dynamic>> createCustodyEvent(Map<String, dynamic> payload) async { writes.add(payload); return payload; }
}
