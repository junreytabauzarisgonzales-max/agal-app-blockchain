import 'package:flutter/material.dart';

/// Shows the light- or dark-background logo depending on the current
/// theme brightness. The app *icon* (home screen) always uses the dark
/// variant regardless of theme -- see pubspec.yaml's flutter_launcher_icons
/// config -- but in-app logo usage adapts, since it sits on a themed
/// background rather than a fixed launcher tray.
class AppLogo extends StatelessWidget {
  const AppLogo({super.key, this.size = 72, this.borderRadius});
  final double size;
  final BorderRadius? borderRadius;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final asset = isDark ? 'assets/agal_dark.jpg' : 'assets/agal_light.jpg';

    return ClipRRect(
      borderRadius: borderRadius ?? BorderRadius.circular(size / 2),
      child: Image.asset(asset, width: size, height: size, fit: BoxFit.cover),
    );
  }
}
