import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:get/get.dart';
import 'package:get_storage/get_storage.dart';

import 'core/auth/auth_controller.dart';
import 'core/config/api_config.dart';
import 'core/network/dio_client.dart';
import 'core/routes/app_pages.dart';
import 'core/routes/app_routes.dart';
import 'core/theme/app_theme.dart';
import 'core/theme/theme_controller.dart';
import 'data/local/database.dart';
import 'data/remote/agal_api_client.dart';
import 'data/sync/sync_scheduler.dart';
import 'data/sync/sync_service.dart';
import 'features/supplier/shipment_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await GetStorage.init();

  const secureStorage = FlutterSecureStorage();
  Get.put<FlutterSecureStorage>(secureStorage, permanent: true);

  final database = AppDatabase();
  Get.put<AppDatabase>(database, permanent: true);

  final authController = AuthController(secureStorage);
  final dio = buildDioClient(
    baseUrl: ApiConfig.baseUrl,
    tokenGetter: () => authController.session.value?.accessToken,
  );
  Get.put<AgalApiClient>(AgalApiClient(dio), permanent: true);
  Get.put<ShipmentService>(
    ShipmentService(Get.find<AgalApiClient>(), storage: GetStorage()),
    permanent: true,
  );

  // Loaded before runApp so the very first frame -- and the router's auth
  // middleware -- already knows whether there's a session. No splash
  // screen needed to hide the gap while secure storage is read.
  await authController.loadSession();
  Get.put<AuthController>(authController, permanent: true);

  Get.put<SyncService>(
    SyncService(database, Get.find<AgalApiClient>()),
    permanent: true,
  );
  final scheduler = SyncScheduler(
    Get.find<SyncService>(),
    database,
    authController,
  );
  Get.put<SyncScheduler>(scheduler, permanent: true);
  scheduler.start();

  Get.put<ThemeController>(ThemeController(), permanent: true);

  runApp(const AgalApp());
}

class AgalApp extends StatelessWidget {
  const AgalApp({super.key});

  @override
  Widget build(BuildContext context) {
    final themeController = Get.find<ThemeController>();

    return GetMaterialApp(
      title: 'Agal',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: themeController.themeMode.value,
      // AuthMiddleware resolves this to the right home route (or /login)
      // on the very first navigation, based on whether a session loaded.
      initialRoute: Routes.login,
      getPages: AppPages.pages,
    );
  }
}
