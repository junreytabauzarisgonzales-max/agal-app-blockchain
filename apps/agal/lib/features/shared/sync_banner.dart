import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../core/theme/app_theme.dart';
import '../../core/routes/app_routes.dart';
import '../../data/sync/sync_scheduler.dart';

class SyncBanner extends StatelessWidget {
  const SyncBanner({super.key});
  @override
  Widget build(BuildContext context) {
    final sync = Get.find<SyncScheduler>();
    return Obx(() {
      final pending = sync.pending;
      final busy = sync.syncing.value;
      final offline = !sync.online.value;
      final failed = sync.error.value != null;
      final color = busy
          ? const Color(0xFF2196E8)
          : offline || pending > 0
          ? AgalColors.orange
          : failed
          ? const Color(0xFFD94444)
          : const Color(0xFF2DA96C);
      final label = busy
          ? 'Syncing… ($pending remaining)'
          : offline
          ? 'Offline mode ($pending pending sync)'
          : failed
          ? 'Sync failed · Tap to retry'
          : pending > 0
          ? '$pending records waiting to sync'
          : 'All data synced';
      return Material(
        color: color,
        borderRadius: BorderRadius.circular(10),
        child: InkWell(
          borderRadius: BorderRadius.circular(10),
          onTap: () => Get.toNamed(Routes.syncManagement),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
            child: Row(
              children: [
                Icon(
                  busy
                      ? Icons.sync
                      : offline
                      ? Icons.cloud_off_outlined
                      : failed
                      ? Icons.error_outline
                      : Icons.check_circle,
                  size: 18,
                  color: Colors.white,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    label,
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                ),
                const Icon(Icons.chevron_right, size: 17, color: Colors.white),
              ],
            ),
          ),
        ),
      );
    });
  }
}
