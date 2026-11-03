import 'package:flutter/widgets.dart';
import 'package:get/get.dart';

import '../auth/auth_controller.dart';
import '../models/enums.dart';
import 'app_routes.dart';

/// Gate applied to every page: logged-out users get bounced to /login,
/// logged-in users get bounced away from /login and /register, and (when
/// [allowedRoles] is set) away from another role's screens.
///
/// This is a defense-in-depth guard for direct navigation to a route --
/// the actual login/logout transitions are driven explicitly by
/// AuthController via Get.offAllNamed, not by this middleware reacting to
/// state changes (GetX middleware only re-runs on navigation, not
/// reactively when `session` changes on its own).
class AuthMiddleware extends GetMiddleware {
  AuthMiddleware({this.allowedRoles});
  final List<UserRole>? allowedRoles;

  @override
  int? get priority => 0;

  @override
  RouteSettings? redirect(String? route) {
    final session = Get.find<AuthController>().session.value;
    final onAuthRoute = route == Routes.login || route == Routes.register;

    if (session == null) {
      return onAuthRoute ? null : const RouteSettings(name: Routes.login);
    }
    if (onAuthRoute) {
      return RouteSettings(name: Routes.homeFor(session.role));
    }
    if (allowedRoles != null && !allowedRoles!.contains(session.role)) {
      return RouteSettings(name: Routes.homeFor(session.role));
    }
    return null;
  }
}
