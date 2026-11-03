import 'package:dio/dio.dart';

/// Thin wrapper around the Agal FastAPI backend. Returns decoded JSON
/// (Map/List) rather than typed models -- a pragmatic scaffold choice; swap
/// in typed DTOs later if the surface grows.
class AgalApiClient {
  AgalApiClient(this._dio);
  final Dio _dio;

  Future<String> login(String email, String password) async {
    final response = await _dio.post(
      '/auth/login',
      data: {'username': email, 'password': password},
      options: Options(contentType: Headers.formUrlEncodedContentType),
    );
    return response.data['access_token'] as String;
  }

  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String fullName,
    required String role,
    String? phoneNumber,
    String? municipality,
  }) async {
    final response = await _dio.post(
      '/auth/register',
      data: {
        'email': email,
        'password': password,
        'full_name': fullName,
        'role': role,
        'phone_number': phoneNumber,
        'municipality': municipality,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> me() async {
    final response = await _dio.get('/users/me');
    return response.data as Map<String, dynamic>;
  }

  /// Used only right after login, before the Dio interceptor's normal
  /// "read the current session" token source has a session to read --
  /// so the token is passed explicitly for this one call.
  Future<Map<String, dynamic>> meWithBearer(String token) async {
    final response = await _dio.get(
      '/users/me',
      options: Options(headers: {'Authorization': 'Bearer $token'}),
    );
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> updateMe({
    String? fullName,
    String? phoneNumber,
    String? municipality,
  }) async {
    final response = await _dio.patch(
      '/users/me',
      data: {
        'full_name': ?fullName,
        'phone_number': ?phoneNumber,
        'municipality': ?municipality,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getUser(String userId) async {
    final response = await _dio.get('/users/$userId');
    return response.data as Map<String, dynamic>;
  }

  Future<List<Map<String, dynamic>>> listDirectory({String? role}) async {
    final response = await _dio.get(
      '/users/directory',
      queryParameters: {'role': ?role},
    );
    return (response.data as List).cast<Map<String, dynamic>>();
  }

  Future<List<Map<String, dynamic>>> listPrices({
    String? species,
    String? municipality,
  }) async {
    final response = await _dio.get(
      '/prices',
      queryParameters: {'species': ?species, 'municipality': ?municipality},
    );
    return (response.data as List).cast<Map<String, dynamic>>();
  }

  Future<Map<String, dynamic>> createPrice(Map<String, dynamic> payload) async {
    final response = await _dio.post('/prices', data: payload);
    return response.data as Map<String, dynamic>;
  }

  Future<List<Map<String, dynamic>>> listBatches({
    String? farmerId,
    String? holderId,
    String? status,
  }) async {
    final response = await _dio.get(
      '/batches',
      queryParameters: {
        'farmer_id': ?farmerId,
        'holder_id': ?holderId,
        'status': ?status,
      },
    );
    return (response.data as List).cast<Map<String, dynamic>>();
  }

  Future<Map<String, dynamic>> getBatch(String id) async {
    final response = await _dio.get('/batches/$id');
    return response.data as Map<String, dynamic>;
  }

  Future<List<Map<String, dynamic>>> getBatchEvents(String id) async {
    final response = await _dio.get('/batches/$id/events');
    return (response.data as List).cast<Map<String, dynamic>>();
  }

  Future<Map<String, dynamic>> createCustodyEvent(
    Map<String, dynamic> payload,
  ) async {
    final response = await _dio.post('/custody-events', data: payload);
    return response.data as Map<String, dynamic>;
  }

  /// Independently checks one event against the live HarvestLedger
  /// contract on Sepolia -- not just the backend's cached status.
  Future<Map<String, dynamic>> verifyCustodyEvent(String eventId) async {
    final response = await _dio.get('/custody-events/$eventId/verify');
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> sendMessage(Map<String, dynamic> payload) async {
    final response = await _dio.post('/messages', data: payload);
    return response.data as Map<String, dynamic>;
  }

  Future<List<Map<String, dynamic>>> listThreads() async {
    final response = await _dio.get('/messages/threads');
    return (response.data as List).cast<Map<String, dynamic>>();
  }

  Future<List<Map<String, dynamic>>> getConversation(
    String counterpartId,
  ) async {
    final response = await _dio.get('/messages/with/$counterpartId');
    return (response.data as List).cast<Map<String, dynamic>>();
  }

  Future<void> markConversationRead(String counterpartId) async {
    await _dio.post('/messages/with/$counterpartId/read');
  }

  /// Idempotent bulk-apply used by the Farmer app's background sync queue.
  Future<List<Map<String, dynamic>>> sync(
    List<Map<String, dynamic>> items, {
    String? bearer,
  }) async {
    final response = await _dio.post(
      '/sync',
      data: {'items': items},
      options: bearer == null
          ? null
          : Options(headers: {'Authorization': 'Bearer $bearer'}),
    );
    return (response.data['results'] as List).cast<Map<String, dynamic>>();
  }
}
