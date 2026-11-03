/// Base URL of the Agal FastAPI backend.
///
/// Defaults to the deployed backend, so the app works out of the box on a
/// real device without needing a dart-define. Override for local dev, e.g.:
///   flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000  # Android emulator -> host machine
class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://agal-api.vercel.app',
  );
}
