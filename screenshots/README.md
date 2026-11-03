# Agal feature screenshots

These images are rendered from the Flutter app's real widgets using **mock data**.
They do not represent live trades, real payments, or live blockchain verification.

Mock accounts:
- Farmer: **Junrey Gonzales**
- Trader / supplier: **Hamsya Igasan**
- Exporter / buyer: **Krishane Ann Remonde**

The numbered PNG files are presentation boards. `raw/` contains the individual
full-resolution Flutter screen captures.

To regenerate the screen captures from `apps/agal`:

```sh
flutter test --dart-define=CAPTURE_SCREENSHOTS=true test/feature_screenshots_test.dart
python tool/compose_screenshots.py
```

The fixture only uses an in-memory database and a fake API client. No accounts or
records are created on the backend. On Windows, Segoe UI fonts are loaded for the
captures so that text is rendered normally in the Flutter test renderer.
