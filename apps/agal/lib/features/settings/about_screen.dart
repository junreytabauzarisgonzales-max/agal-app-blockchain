import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';

import '../shared/app_logo.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('About Agal')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const Center(child: AppLogo(size: 72)),
            const SizedBox(height: 16),
            Center(
              child: Text(
                'Agal',
                style: Theme.of(context).textTheme.headlineSmall
                    ?.copyWith(fontWeight: FontWeight.w700),
              ),
            ),
            const SizedBox(height: 4),
            FutureBuilder<PackageInfo>(
              future: PackageInfo.fromPlatform(),
              builder: (context, snapshot) {
                final version = snapshot.data;
                final label = version == null
                    ? ''
                    : 'Version ${version.version} (${version.buildNumber})';
                return Center(
                  child: Text(
                    label,
                    style: TextStyle(color: colors.onSurfaceVariant),
                  ),
                );
              },
            ),
            const SizedBox(height: 32),
            Text(
              'Agal gives seaweed farmers, aggregators, and exporters in Tawi-Tawi a shared, '
              'tamper-evident record of every harvest -- from the water to the buyer -- along '
              'with transparent, up-to-date price information.',
              style: TextStyle(color: colors.onSurfaceVariant, height: 1.5),
            ),
            const SizedBox(height: 24),
            const _InfoRow(
              icon: Icons.emoji_events_outlined,
              label: 'Built for the Philippine Startup Challenge',
            ),
            const _InfoRow(
              icon: Icons.cloud_sync_outlined,
              label:
                  'Offline-first for farmers, always-on for suppliers & buyers',
            ),
            const _InfoRow(
              icon: Icons.link_outlined,
              label: 'Every chain-of-custody event is anchored on a public blockchain ledger',
            ),
            const SizedBox(height: 24),
            Text('Developer', style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: 8),
            Text(
              'Designed and built by the Agal team as an entry to the Philippine Startup Challenge.',
              style: TextStyle(color: colors.onSurfaceVariant),
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.icon, required this.label});
  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: colors.primary),
          const SizedBox(width: 12),
          Expanded(child: Text(label)),
        ],
      ),
    );
  }
}
