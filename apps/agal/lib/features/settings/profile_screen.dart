import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../core/auth/auth_controller.dart';
import '../../core/models/enums.dart';
import '../../core/routes/app_routes.dart';
import '../../core/theme/app_theme.dart';
import '../../data/local/database.dart';
import '../../data/remote/agal_api_client.dart';
import '../shared/agal_widgets.dart';
import '../shared/app_logo.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});
  @override
  Widget build(BuildContext context) {
    final session = Get.find<AuthController>().session.value!;
    final farmer = session.role == UserRole.farmer;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        centerTitle: false,
        actions: [
          IconButton(
            tooltip: 'Settings',
            onPressed: () => Get.toNamed(Routes.settings),
            icon: const Icon(Icons.settings_outlined),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Center(child: AppLogo(size: 104)),
          const SizedBox(height: 14),
          Text(
            session.fullName,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          Center(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 5),
              decoration: BoxDecoration(
                color: AgalColors.mint,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                session.role.value.capitalizeFirst!,
                style: const TextStyle(
                  color: AgalColors.deep,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
          const SizedBox(height: 10),
          Text(
            '⌖ ${session.municipality ?? 'Add your municipality'}',
            textAlign: TextAlign.center,
            style: const TextStyle(color: Color(0xFFACC8BD)),
          ),
          const SizedBox(height: 24),
          if (farmer)
            StreamBuilder<List<LocalBatch>>(
              stream: Get.find<AppDatabase>().watchBatchesForFarmer(
                session.userId,
              ),
              builder: (context, snapshot) => _stats(
                snapshot.data?.length ?? 0,
                snapshot.data?.fold<double>(
                      0,
                      (s, b) => s + b.estimatedWeightKg,
                    ) ??
                    0,
              ),
            )
          else
            FutureBuilder<List<Map<String, dynamic>>>(
              future: Get.find<AgalApiClient>().listBatches(
                holderId: session.userId,
              ),
              builder: (context, snapshot) => _stats(
                snapshot.data?.length ?? 0,
                snapshot.data?.fold<double>(
                      0,
                      (s, b) =>
                          s +
                          (double.tryParse('${b['estimated_weight_kg']}') ?? 0),
                    ) ??
                    0,
              ),
            ),
          const SizedBox(height: 16),
          AgalSurface(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Column(
              children: [
                _row(
                  Icons.person_outline,
                  'Personal information',
                  Routes.accountSettings,
                ),
                _row(
                  Icons.place_outlined,
                  'Farm location',
                  Routes.accountSettings,
                ),
                _row(Icons.palette_outlined, 'Appearance', Routes.settings),
                if (farmer)
                  _row(
                    Icons.cloud_sync_outlined,
                    'Sync management',
                    Routes.syncManagement,
                  ),
                _row(Icons.shield_outlined, 'Privacy & data', Routes.privacy),
                _row(Icons.help_outline, 'Help & support', Routes.help),
              ],
            ),
          ),
          const SizedBox(height: 20),
          OutlinedButton.icon(
            onPressed: () async {
              final confirmed = await showDialog<bool>(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('Log out?'),
                  content: const Text(
                    'Unsynced records stay safely on this device for your next sign in.',
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Get.back(result: false),
                      child: const Text('Cancel'),
                    ),
                    FilledButton(
                      onPressed: () => Get.back(result: true),
                      child: const Text('Log out'),
                    ),
                  ],
                ),
              );
              if (confirmed == true) await Get.find<AuthController>().logout();
            },
            icon: const Icon(Icons.logout),
            label: const Text('Log out'),
          ),
        ],
      ),
    );
  }

  Widget _row(IconData icon, String title, String route) => ListTile(
    leading: Icon(icon, size: 21),
    title: Text(title, style: const TextStyle(fontSize: 14)),
    trailing: const Icon(Icons.chevron_right, size: 19),
    onTap: () => Get.toNamed(route),
  );
  Widget _stats(int count, double weight) => AgalSurface(
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        Column(
          children: [
            Text(
              '$count',
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
            ),
            const Text(
              'Batches',
              style: TextStyle(color: AgalColors.muted, fontSize: 12),
            ),
          ],
        ),
        Container(width: 1, height: 35, color: const Color(0xFFCADBD3)),
        Column(
          children: [
            Text(
              (weight / 1000).toStringAsFixed(1),
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
            ),
            const Text(
              'Tons',
              style: TextStyle(color: AgalColors.muted, fontSize: 12),
            ),
          ],
        ),
      ],
    ),
  );
}
