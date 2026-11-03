import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../core/auth/auth_controller.dart';
import '../../core/routes/app_routes.dart';
import '../../core/theme/app_theme.dart';
import '../../data/local/database.dart';
import '../shared/agal_widgets.dart';
import '../shared/app_logo.dart';
import '../shared/sync_banner.dart';

class FarmerDashboardScreen extends StatelessWidget {
  const FarmerDashboardScreen({super.key});
  @override
  Widget build(BuildContext context) {
    final session = Get.find<AuthController>().session.value!;
    return Scaffold(
      appBar: AppBar(
        centerTitle: false,
        title: const Row(
          children: [
            AppLogo(size: 34),
            SizedBox(width: 10),
            Text(
              'Agal',
              style: TextStyle(fontSize: 25, fontWeight: FontWeight.w500),
            ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Account',
            onPressed: () => Get.toNamed(Routes.accountSettings),
            icon: const Icon(Icons.account_circle_outlined),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 4, 20, 24),
        children: [
          const SyncBanner(),
          const SizedBox(height: 24),
          const Text(
            'Welcome back,',
            style: TextStyle(color: Color(0xFFACC8BD), fontSize: 15),
          ),
          Text(
            session.fullName,
            style: const TextStyle(fontSize: 29, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 16),
          AgalSurface(
            padding: const EdgeInsets.all(14),
            child: InkWell(
              onTap: () => Get.toNamed(Routes.buyingPrices),
              child: const Row(
                children: [
                  Icon(Icons.trending_up, color: AgalColors.forest),
                  SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Today’s Buying Prices',
                          style: TextStyle(fontWeight: FontWeight.w700),
                        ),
                        SizedBox(height: 4),
                        Text(
                          'Check the latest price per kilo',
                          style: TextStyle(
                            fontSize: 12,
                            color: AgalColors.muted,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(Icons.chevron_right),
                ],
              ),
            ),
          ),
          const SizedBox(height: 22),
          StreamBuilder<List<LocalBatch>>(
            stream: Get.find<AppDatabase>().watchBatchesForFarmer(
              session.userId,
            ),
            builder: (context, snapshot) {
              final batches = snapshot.data ?? [];
              final totalWeight = batches.fold<double>(
                0,
                (sum, b) => sum + b.estimatedWeightKg,
              );
              return Column(
                children: [
                  Row(
                    children: [
                      Expanded(child: _Stat('${batches.length}', 'Batches')),
                      const SizedBox(width: 10),
                      Expanded(
                        child: _Stat(
                          (totalWeight / 1000).toStringAsFixed(1),
                          'Tons logged',
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: _Stat(
                          '${batches.where((b) => b.status == 'dried').length}',
                          'Ready',
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  if (batches.isEmpty)
                    const AgalSurface(
                      child: Column(
                        children: [
                          SeaweedArt(size: 94),
                          SizedBox(height: 16),
                          Text(
                            'Your harvest story starts here',
                            style: TextStyle(
                              fontSize: 19,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          SizedBox(height: 8),
                          Text(
                            'Log your first batch. Every step is saved on your phone, even without a connection.',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: AgalColors.muted,
                              height: 1.5,
                            ),
                          ),
                        ],
                      ),
                    )
                  else
                    ...batches
                        .take(3)
                        .map(
                          (batch) => Padding(
                            padding: const EdgeInsets.only(bottom: 14),
                            child: AgalSurface(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Expanded(
                                        child: Text(
                                          batchLabel(batch.id),
                                          style: const TextStyle(
                                            fontSize: 22,
                                            fontWeight: FontWeight.w800,
                                          ),
                                        ),
                                      ),
                                      SeaweedArt(
                                        size: 52,
                                        tambalang:
                                            speciesLabel(batch.species) ==
                                            'Tambalang',
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    'Species: ${speciesLabel(batch.species)}',
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    'Est. weight: ${batch.estimatedWeightKg.toStringAsFixed(1)} ${batch.unit}',
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    batch.harvestLatitude == null
                                        ? 'GPS: Not captured'
                                        : 'GPS: Saved (${session.municipality ?? 'farm location'})',
                                    style: const TextStyle(
                                      fontSize: 12,
                                      color: AgalColors.muted,
                                    ),
                                  ),
                                  BatchProgress(status: batch.status),
                                  SizedBox(
                                    width: double.infinity,
                                    child: FilledButton(
                                      style: FilledButton.styleFrom(
                                        backgroundColor: const Color(
                                          0xFF09283A,
                                        ),
                                        foregroundColor: Colors.white,
                                      ),
                                      onPressed: () => Get.toNamed(
                                        Routes.farmerBatchDetailPath(batch.id),
                                      ),
                                      child: const Text('Update status'),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                ],
              );
            },
          ),
          const SizedBox(height: 18),
          Row(
            children: [
              Expanded(
                child: FilledButton.icon(
                  onPressed: () => Get.toNamed(Routes.farmerNewBatch),
                  icon: const Icon(Icons.add),
                  label: const Text('Log New Harvest'),
                ),
              ),
              const SizedBox(width: 12),
              IconButton.filled(
                tooltip: 'New message',
                style: IconButton.styleFrom(
                  backgroundColor: AgalColors.mint,
                  foregroundColor: AgalColors.deep,
                  padding: const EdgeInsets.all(15),
                ),
                onPressed: () => Get.toNamed(Routes.chatContactPicker),
                icon: const Icon(Icons.chat_bubble_outline),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  const _Stat(this.value, this.label);
  final String value, label;
  @override
  Widget build(BuildContext context) => AgalSurface(
    padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 6),
    child: Column(
      children: [
        Text(
          value,
          style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(fontSize: 11, color: AgalColors.muted),
        ),
      ],
    ),
  );
}
