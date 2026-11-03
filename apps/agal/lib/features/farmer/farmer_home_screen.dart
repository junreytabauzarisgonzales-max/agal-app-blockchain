import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';

import '../../core/auth/auth_controller.dart';
import '../../core/models/enums.dart';
import '../../core/routes/app_routes.dart';
import '../../data/local/database.dart';
import '../../data/sync/sync_scheduler.dart';
import '../shared/batch_status_chip.dart';
import '../shared/agal_widgets.dart';

class FarmerHomeScreen extends StatefulWidget {
  const FarmerHomeScreen({super.key});

  @override
  State<FarmerHomeScreen> createState() => _FarmerHomeScreenState();
}

class _FarmerHomeScreenState extends State<FarmerHomeScreen> {
  @override
  void initState() {
    super.initState();
    // Starting the scheduler is idempotent, so it's safe to call every time
    // this screen is (re)built -- it only actually spins up once.
    Get.find<SyncScheduler>().start();
  }

  @override
  Widget build(BuildContext context) {
    final session = Get.find<AuthController>().session.value;
    if (session == null) return const SizedBox.shrink();

    final db = Get.find<AppDatabase>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Batches'),
        actions: [
          StreamBuilder<int>(
            stream: db.watchUnsyncedCount(),
            builder: (context, snapshot) {
              final pending = snapshot.data ?? 0;
              if (pending == 0) return const SizedBox.shrink();
              return Padding(
                padding: const EdgeInsets.only(right: 12),
                child: Center(
                  child: Chip(
                    label: Text('$pending pending'),
                    avatar: const Icon(Icons.cloud_upload_outlined, size: 16),
                    visualDensity: VisualDensity.compact,
                  ),
                ),
              );
            },
          ),
        ],
      ),
      body: StreamBuilder<List<LocalBatch>>(
        stream: db.watchBatchesForFarmer(session.userId),
        builder: (context, snapshot) {
          final batches = snapshot.data ?? [];
          if (batches.isEmpty) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.grass_rounded,
                    size: 48,
                    color: Theme.of(context).colorScheme.outline,
                  ),
                  const SizedBox(height: 12),
                  const Text('No batches yet. Tap + to log a harvest.'),
                ],
              ),
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 96),
            itemCount: batches.length,
            itemBuilder: (context, index) {
              final batch = batches[index];
              return Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: AgalSurface(
                  padding: const EdgeInsets.all(4),
                  child: ListTile(
                    title: Text(
                      batch.species,
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                    subtitle: Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Text(
                        '${batch.estimatedWeightKg} ${batch.unit} · ${DateFormat.yMMMd().format(batch.harvestedAt)}',
                      ),
                    ),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        BatchStatusChip(
                          status: BatchStatus.fromValue(batch.status),
                        ),
                        const SizedBox(width: 4),
                        const Icon(Icons.chevron_right),
                      ],
                    ),
                    onTap: () =>
                        Get.toNamed(Routes.farmerBatchDetailPath(batch.id)),
                  ),
                ),
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Get.toNamed(Routes.farmerNewBatch),
        icon: const Icon(Icons.add),
        label: const Text('Log harvest'),
      ),
    );
  }
}
