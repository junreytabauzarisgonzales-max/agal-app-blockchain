import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:agal/features/auth/login_screen.dart';

void main() {
  // Renders LoginScreen alone rather than the full AgalApp: booting the
  // whole app touches AuthController, which reads flutter_secure_storage
  // over a real platform channel with no implementation under
  // `flutter_tester`, and hangs rather than erroring. LoginScreen itself
  // only touches GetX-registered singletons inside _submit(), so it's safe
  // to render standalone as long as the test never taps "Log in".
  testWidgets('LoginScreen shows email/password fields and a login button', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MaterialApp(home: LoginScreen()));

    expect(find.text('Agal'), findsOneWidget);
    expect(find.widgetWithText(TextFormField, 'Email'), findsOneWidget);
    expect(find.widgetWithText(TextFormField, 'Password'), findsOneWidget);
    expect(find.widgetWithText(FilledButton, 'Log in'), findsOneWidget);
  });
}
