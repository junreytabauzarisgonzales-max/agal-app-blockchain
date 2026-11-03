import '../models/enums.dart';

abstract class Routes {
  static const login = '/login';
  static const register = '/register';

  static const farmerHome = '/farmer';
  static const farmerNewBatch = '/farmer/new';
  static const farmerBatchDetail = '/farmer/batch/:id';

  static const supplierHome = '/supplier';
  static const buyerHome = '/buyer';
  static const buyingPrices = '/prices';
  static const pickups = '/supplier/pickups';
  static const shipments = '/supplier/shipments';
  static const batchHistory = '/batches/:id/history';

  // Settings and Messages are tabs inside each role's RoleShell, not
  // top-level pages -- only their sub-screens are pushed routes.
  static const accountSettings = '/settings/account';
  static const settings = '/settings';
  static const syncManagement = '/settings/sync';
  static const help = '/settings/help';
  static const verifyHandover = '/batches/:id/handover';
  static const about = '/settings/about';
  static const terms = '/settings/terms';
  static const privacy = '/settings/privacy';

  static const chatContactPicker = '/chat/new';
  static const chatThread = '/chat/thread/:counterpartId';

  static String farmerBatchDetailPath(String id) => '/farmer/batch/$id';
  static String chatThreadPath(String counterpartId) =>
      '/chat/thread/$counterpartId';
  static String batchHistoryPath(String id) => '/batches/$id/history';
  static String verifyHandoverPath(String id) => '/batches/$id/handover';

  /// The shell route each role lands on right after login/logout -- see
  /// AuthController.login()/logout(), which use this to force the
  /// navigation stack to reset instead of leaving a previous role's
  /// screens sitting underneath.
  static String homeFor(UserRole role) => switch (role) {
    UserRole.farmer => farmerHome,
    UserRole.supplier => supplierHome,
    UserRole.buyer => buyerHome,
  };
}
