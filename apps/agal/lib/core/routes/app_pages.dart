import 'package:get/get.dart';

import '../../features/auth/login_screen.dart';
import '../../features/auth/register_screen.dart';
import '../../features/buyer/buyer_shell_screen.dart';
import '../../features/chat/chat_thread_screen.dart';
import '../../features/chat/contact_picker_screen.dart';
import '../../features/farmer/farmer_batch_detail_screen.dart';
import '../../features/farmer/farmer_create_batch_screen.dart';
import '../../features/farmer/farmer_shell_screen.dart';
import '../../features/settings/about_screen.dart';
import '../../features/settings/account_settings_screen.dart';
import '../../features/settings/privacy_screen.dart';
import '../../features/settings/terms_screen.dart';
import '../../features/settings/settings_screen.dart';
import '../../features/settings/sync_management_screen.dart';
import '../../features/settings/help_screen.dart';
import '../../features/shared/verify_handover_screen.dart';
import '../../features/shared/buying_prices_screen.dart';
import '../../features/shared/sourcing_screen.dart';
import '../../features/supplier/shipments_screen.dart';
import '../../features/shared/batch_history_screen.dart';
import '../../features/supplier/supplier_shell_screen.dart';
import '../models/enums.dart';
import 'app_routes.dart';
import 'auth_middleware.dart';

class AppPages {
  AppPages._();

  static final pages = <GetPage>[
    GetPage(
      name: Routes.buyingPrices,
      page: () => const BuyingPricesScreen(),
      middlewares: [AuthMiddleware()],
    ),
    GetPage(
      name: Routes.pickups,
      page: () => const SourcingScreen(supplier: true),
      middlewares: [
        AuthMiddleware(allowedRoles: [UserRole.supplier]),
      ],
    ),
    GetPage(
      name: Routes.shipments,
      page: () => const ShipmentsScreen(),
      middlewares: [
        AuthMiddleware(allowedRoles: [UserRole.supplier]),
      ],
    ),
    GetPage(
      name: Routes.settings,
      page: () => const SettingsScreen(),
      middlewares: [AuthMiddleware()],
    ),
    GetPage(
      name: Routes.syncManagement,
      page: () => const SyncManagementScreen(),
      middlewares: [
        AuthMiddleware(allowedRoles: [UserRole.farmer]),
      ],
    ),
    GetPage(
      name: Routes.help,
      page: () => const HelpScreen(),
      middlewares: [AuthMiddleware()],
    ),
    GetPage(
      name: Routes.verifyHandover,
      page: () => VerifyHandoverScreen(batchId: Get.parameters['id']!),
      middlewares: [
        AuthMiddleware(allowedRoles: [UserRole.supplier, UserRole.buyer]),
      ],
    ),
    GetPage(
      name: Routes.login,
      page: () => const LoginScreen(),
      middlewares: [AuthMiddleware()],
    ),
    GetPage(
      name: Routes.register,
      page: () => const RegisterScreen(),
      middlewares: [AuthMiddleware()],
    ),
    GetPage(
      name: Routes.farmerHome,
      page: () => const FarmerShellScreen(),
      middlewares: [
        AuthMiddleware(allowedRoles: [UserRole.farmer]),
      ],
    ),
    GetPage(
      name: Routes.farmerNewBatch,
      page: () => const FarmerCreateBatchScreen(),
      middlewares: [
        AuthMiddleware(allowedRoles: [UserRole.farmer]),
      ],
    ),
    GetPage(
      name: Routes.farmerBatchDetail,
      page: () => FarmerBatchDetailScreen(batchId: Get.parameters['id']!),
      middlewares: [
        AuthMiddleware(allowedRoles: [UserRole.farmer]),
      ],
    ),
    GetPage(
      name: Routes.supplierHome,
      page: () => const SupplierShellScreen(),
      middlewares: [
        AuthMiddleware(allowedRoles: [UserRole.supplier]),
      ],
    ),
    GetPage(
      name: Routes.buyerHome,
      page: () => const BuyerShellScreen(),
      middlewares: [
        AuthMiddleware(allowedRoles: [UserRole.buyer]),
      ],
    ),
    GetPage(
      name: Routes.batchHistory,
      page: () => BatchHistoryScreen(batchId: Get.parameters['id']!),
      middlewares: [
        AuthMiddleware(allowedRoles: [UserRole.supplier, UserRole.buyer]),
      ],
    ),
    GetPage(
      name: Routes.accountSettings,
      page: () => const AccountSettingsScreen(),
      middlewares: [AuthMiddleware()],
    ),
    GetPage(
      name: Routes.about,
      page: () => const AboutScreen(),
      middlewares: [AuthMiddleware()],
    ),
    GetPage(
      name: Routes.terms,
      page: () => const TermsScreen(),
      middlewares: [AuthMiddleware()],
    ),
    GetPage(
      name: Routes.privacy,
      page: () => const PrivacyScreen(),
      middlewares: [AuthMiddleware()],
    ),
    GetPage(
      name: Routes.chatContactPicker,
      page: () => const ContactPickerScreen(),
      middlewares: [AuthMiddleware()],
    ),
    GetPage(
      name: Routes.chatThread,
      page: () =>
          ChatThreadScreen(counterpartId: Get.parameters['counterpartId']!),
      middlewares: [AuthMiddleware()],
    ),
  ];
}
