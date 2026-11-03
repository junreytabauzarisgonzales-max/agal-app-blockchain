import 'package:dio/dio.dart';

/// Builds the shared Dio instance, attaching the current access token (via
/// [tokenGetter], called fresh on every request) as a Bearer header.
Dio buildDioClient({
  required String baseUrl,
  required String? Function() tokenGetter,
}) {
  final dio = Dio(
    BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
    ),
  );

  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) {
        final token = tokenGetter();
        if (token != null && !options.headers.containsKey('Authorization')) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
    ),
  );

  return dio;
}
