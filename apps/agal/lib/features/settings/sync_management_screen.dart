import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';

import '../../core/theme/app_theme.dart';
import '../../data/sync/sync_scheduler.dart';
import '../shared/agal_widgets.dart';

class SyncManagementScreen extends StatefulWidget {
  const SyncManagementScreen({super.key});
  @override
  State<SyncManagementScreen> createState() => _SyncManagementScreenState();
}

class _SyncManagementScreenState extends State<SyncManagementScreen> {
  final sync = Get.find<SyncScheduler>();
  @override
  void initState() {
    super.initState();
    sync.refreshCounts();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Sync Management')),
    body: Padding(
      padding: const EdgeInsets.all(20),
      child: Obx(
        () => Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Container(
              padding: const EdgeInsets.all(22),
              decoration: BoxDecoration(
                color: !sync.online.value
                    ? AgalColors.orange
                    : sync.error.value != null
                    ? Colors.red.shade700
                    : sync.syncing.value
                    ? Colors.blue
                    : const Color(0xFF2DA96C),
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(20),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    !sync.online.value
                        ? Icons.cloud_off
                        : sync.syncing.value
                        ? Icons.sync
                        : Icons.cloud_done,
                    color: Colors.white,
                    size: 30,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          !sync.online.value
                              ? 'You are offline'
                              : sync.syncing.value
                              ? 'Syncing your records…'
                              : sync.error.value != null
                              ? 'Sync needs attention'
                              : 'You are connected',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w700,
                            fontSize: 17,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          '${sync.pending} records pending sync',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            AgalSurface(
              child: Column(
                children: [
                  _row(
                    Icons.inventory_2_outlined,
                    '${sync.pendingHarvests.value} Harvest Records',
                    sync.pendingHarvests.value == 0
                        ? 'All harvest records synced'
                        : 'Saved on this device',
                  ),
                  _row(
                    Icons.chat_bubble_outline,
                    '${sync.pendingMessages.value} Messages',
                    sync.pendingMessages.value == 0
                        ? 'All messages sent'
                        : 'Waiting to send',
                  ),
                  _row(
                    Icons.history,
                    'Last Sync',
                    sync.lastSync.value == null
                        ? 'No records synced yet'
                        : DateFormat('MMM d, yyyy · h:mm a')
                              .format(sync.lastSync.value!),
                  ),
                  if (sync.error.value != null)
                    Padding(
                      padding: const EdgeInsets.all(12),
                      child: Text(
                        sync.error.value!,
                        style: const TextStyle(color: Colors.red, fontSize: 12),
                      ),
                    ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton.icon(
                      onPressed: sync.syncing.value ? null : sync.syncNow,
                      icon: const Icon(Icons.cloud_upload_outlined),
                      label: Text(sync.syncing.value ? 'Syncing…' : 'Sync Now'),
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Records are encrypted in transit and synced automatically when a connection is available while Agal is open.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: AgalColors.muted,
                      fontSize: 12,
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    ),
  );
  Widget _row(IconData icon, String title, String subtitle) => ListTile(
    contentPadding: EdgeInsets.zero,
    leading: CircleAvatar(
      backgroundColor: const Color(0xFFDDEEE5),
      child: Icon(icon, color: AgalColors.ink),
    ),
    title: Text(
      title,
      style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
    ),
    subtitle: Text(
      subtitle,
      style: const TextStyle(fontSize: 12, color: AgalColors.muted),
    ),
  );
}
